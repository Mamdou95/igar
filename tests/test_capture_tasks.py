import tempfile
from pathlib import Path

import pytest
from django.test import override_settings

from igar.apps.capture.models import CaptureUploadRecord
from igar.apps.capture.tasks import task_capture_ocr_process


@pytest.mark.django_db
def test_task_capture_ocr_process_marks_record_done_and_persists_text(monkeypatch):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"fake-image")
        source_path = Path(tmp.name)

    record = CaptureUploadRecord.objects.create(
        upload_id="upload-ocr-1",
        filename="scan.png",
        mime_type="image/png",
        size_bytes=123,
        storage_key="capture/scan.png",
        raw_metadata={"source_file_path": str(source_path), "ocr_language": "fra"},
        ocr_status=CaptureUploadRecord.OCR_STATUS_QUEUED,
    )

    sent_events: list[tuple[str, dict]] = []

    class DummyChannelLayer:
        def group_send(self, group_name: str, event: dict) -> None:
            sent_events.append((group_name, event))

    class DummyOCRBackend:
        def execute(self, file_object, language=None, transformations=None):
            assert language == "fra"
            assert file_object.read() == b"fake-image"
            return "texte extrait"

    monkeypatch.setattr("igar.apps.capture.tasks.get_channel_layer", lambda: DummyChannelLayer())
    monkeypatch.setattr("igar.apps.capture.tasks.async_to_sync", lambda fn: fn)
    monkeypatch.setattr("igar.apps.capture.tasks.OCRBackendBase.get_instance", lambda: DummyOCRBackend())

    with override_settings(IGAR_CAPTURE_OCR_ALLOWED_SOURCE_DIRS=[str(source_path.parent)]):
        task_capture_ocr_process(capture_record_id=record.pk)

    record.refresh_from_db()
    assert record.ocr_status == CaptureUploadRecord.OCR_STATUS_DONE
    assert record.ocr_text == "texte extrait"
    assert record.ocr_error == ""
    assert record.ocr_duration_ms is not None

    assert len(sent_events) == 2
    assert sent_events[0][1]["payload"]["status"] == "ocr_processing"
    assert sent_events[1][1]["payload"]["status"] == "ocr_done"

    source_path.unlink(missing_ok=True)


@pytest.mark.django_db
def test_task_capture_ocr_process_marks_record_failed_and_continues(monkeypatch):
    record = CaptureUploadRecord.objects.create(
        upload_id="upload-ocr-2",
        filename="scan.png",
        mime_type="image/png",
        size_bytes=123,
        storage_key="capture/scan2.png",
        raw_metadata={},
        ocr_status=CaptureUploadRecord.OCR_STATUS_QUEUED,
    )

    sent_events: list[tuple[str, dict]] = []

    class DummyChannelLayer:
        def group_send(self, group_name: str, event: dict) -> None:
            sent_events.append((group_name, event))

    monkeypatch.setattr("igar.apps.capture.tasks.get_channel_layer", lambda: DummyChannelLayer())
    monkeypatch.setattr("igar.apps.capture.tasks.async_to_sync", lambda fn: fn)

    task_capture_ocr_process(capture_record_id=record.pk)

    record.refresh_from_db()
    assert record.ocr_status == CaptureUploadRecord.OCR_STATUS_FAILED
    assert record.ocr_text == ""
    assert record.ocr_error == "OCR source file unavailable."
    assert record.ocr_duration_ms is not None

    assert len(sent_events) == 2
    assert sent_events[0][1]["payload"]["status"] == "ocr_processing"
    assert sent_events[1][1]["payload"]["status"] == "ocr_failed"


@pytest.mark.django_db
def test_task_capture_ocr_process_rejects_source_path_outside_allowed_dirs(monkeypatch):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"fake-image")
        source_path = Path(tmp.name)

    record = CaptureUploadRecord.objects.create(
        upload_id="upload-ocr-outside",
        filename="scan.png",
        mime_type="image/png",
        size_bytes=123,
        storage_key="capture/scan-outside.png",
        raw_metadata={"source_file_path": str(source_path)},
        ocr_status=CaptureUploadRecord.OCR_STATUS_QUEUED,
    )

    monkeypatch.setattr("igar.apps.capture.tasks.get_channel_layer", lambda: None)

    with override_settings(IGAR_CAPTURE_OCR_ALLOWED_SOURCE_DIRS=["/definitely-not-allowed"]):
        task_capture_ocr_process(capture_record_id=record.pk)

    record.refresh_from_db()
    assert record.ocr_status == CaptureUploadRecord.OCR_STATUS_FAILED
    assert record.ocr_error == "OCR source path is not allowed."
    source_path.unlink(missing_ok=True)


@pytest.mark.django_db
def test_task_capture_ocr_process_truncates_large_ocr_text(monkeypatch):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"fake-image")
        source_path = Path(tmp.name)

    record = CaptureUploadRecord.objects.create(
        upload_id="upload-ocr-truncate",
        filename="scan.png",
        mime_type="image/png",
        size_bytes=123,
        storage_key="capture/scan-truncate.png",
        raw_metadata={"source_file_path": str(source_path)},
        ocr_status=CaptureUploadRecord.OCR_STATUS_QUEUED,
    )

    class DummyOCRBackend:
        def execute(self, file_object, language=None, transformations=None):
            return "X" * 50

    monkeypatch.setattr("igar.apps.capture.tasks.get_channel_layer", lambda: None)
    monkeypatch.setattr("igar.apps.capture.tasks.OCRBackendBase.get_instance", lambda: DummyOCRBackend())

    with override_settings(
        IGAR_CAPTURE_OCR_ALLOWED_SOURCE_DIRS=[str(source_path.parent)],
        IGAR_CAPTURE_OCR_TEXT_MAX_LENGTH=10,
    ):
        task_capture_ocr_process(capture_record_id=record.pk)

    record.refresh_from_db()
    assert record.ocr_status == CaptureUploadRecord.OCR_STATUS_DONE
    assert record.ocr_text == "X" * 10
    source_path.unlink(missing_ok=True)
