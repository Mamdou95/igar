import pytest

from igar.apps.capture.models import CaptureUploadRecord
from igar.apps.capture.services import persist_post_finish_upload


def _valid_upload_payload(upload_id: str = "upload-42") -> dict:
    return {
        "ID": upload_id,
        "Size": 2048,
        "MetaData": {
            "filename": "facture.pdf",
            "filetype": "application/pdf",
            "storage_key": "capture/custom-key.pdf",
        },
        "_filename": "facture.pdf",
        "_mime_type": "application/pdf",
    }


@pytest.mark.django_db
def test_persist_post_finish_upload_publishes_normalized_upload_progress_event(monkeypatch):
    sent_events: list[tuple[str, dict]] = []

    class DummyChannelLayer:
        def group_send(self, group_name: str, event: dict) -> None:
            sent_events.append((group_name, event))

    class DummyTask:
        calls: list[dict] = []

        @classmethod
        def apply_async(cls, args: list, queue: str) -> None:
            cls.calls.append({"args": args, "queue": queue})

    monkeypatch.setattr("igar.apps.capture.services.get_channel_layer", lambda: DummyChannelLayer())
    monkeypatch.setattr("igar.apps.capture.services.async_to_sync", lambda fn: fn)
    monkeypatch.setattr("igar.apps.capture.services._increment_metric", lambda *args, **kwargs: None)
    monkeypatch.setattr("igar.apps.capture.tasks.task_capture_ocr_process", DummyTask)

    record = persist_post_finish_upload(_valid_upload_payload())

    assert record.upload_id == "upload-42"
    assert record.storage_key == "capture/custom-key.pdf"
    assert record.ocr_status == CaptureUploadRecord.OCR_STATUS_QUEUED

    assert len(sent_events) == 2
    group_name, event = sent_events[0]
    assert group_name == "upload_progress"
    assert event["type"] == "upload_progress"
    assert event["event_id"] == "upload-progress:upload-42:uploaded:100"
    assert event["payload"] == {
        "document_id": "upload-42",
        "upload_id": "upload-42",
        "filename": "facture.pdf",
        "progress": 1.0,
        "status": "uploaded",
    }

    _, ocr_event = sent_events[1]
    assert ocr_event["event_id"] == "upload-progress:upload-42:ocr_queued:0"
    assert ocr_event["payload"]["status"] == "ocr_queued"
    assert DummyTask.calls[0]["queue"] == "ocr"
    assert DummyTask.calls[0]["args"] == [record.pk]


@pytest.mark.django_db
def test_persist_post_finish_upload_builds_storage_key_fallback(monkeypatch):
    monkeypatch.setattr("igar.apps.capture.services._increment_metric", lambda *args, **kwargs: None)
    monkeypatch.setattr("igar.apps.capture.services.get_channel_layer", lambda: None)
    monkeypatch.setattr("igar.apps.capture.tasks.task_capture_ocr_process", type("T", (), {"apply_async": staticmethod(lambda **_: None)}))

    payload = _valid_upload_payload(upload_id="upload-fallback")
    payload["MetaData"].pop("storage_key")

    record = persist_post_finish_upload(payload)

    assert record.storage_key == "upload-fallback/facture.pdf"
    assert record.ocr_status == CaptureUploadRecord.OCR_STATUS_QUEUED


@pytest.mark.django_db
def test_persist_post_finish_upload_marks_ocr_failed_if_queueing_errors(monkeypatch):
    monkeypatch.setattr("igar.apps.capture.services._increment_metric", lambda *args, **kwargs: None)
    monkeypatch.setattr("igar.apps.capture.services.get_channel_layer", lambda: None)

    class FailingTask:
        @staticmethod
        def apply_async(args: list, queue: str) -> None:
            raise RuntimeError("broker unavailable")

    monkeypatch.setattr("igar.apps.capture.tasks.task_capture_ocr_process", FailingTask)

    record = persist_post_finish_upload(_valid_upload_payload(upload_id="upload-failed-queue"))
    record.refresh_from_db()

    assert record.ocr_status == CaptureUploadRecord.OCR_STATUS_FAILED
    assert record.ocr_error == "OCR queueing failed."
