"""Celery tasks for the capture app."""

from __future__ import annotations

import tempfile
import time
from pathlib import Path

import structlog
from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
from django.conf import settings

from igar.apps.capture.models import CaptureUploadRecord
from mayan.apps.ocr.classes import OCRBackendBase

logger = structlog.get_logger("igar.capture.ocr")


def _get_allowed_source_dirs() -> list[Path]:
	configured_dirs = getattr(settings, "IGAR_CAPTURE_OCR_ALLOWED_SOURCE_DIRS", None)
	if configured_dirs:
		return [Path(item).expanduser().resolve() for item in configured_dirs]

	# Default to the system temp dir used by tusd in development.
	return [Path(tempfile.gettempdir()).resolve()]


def _is_within(path: Path, parent: Path) -> bool:
	try:
		path.relative_to(parent)
		return True
	except ValueError:
		return False


def _resolve_safe_source_path(record: CaptureUploadRecord) -> Path:
	metadata = record.raw_metadata or {}
	source_file_path = metadata.get("source_file_path")
	if not source_file_path:
		raise FileNotFoundError("Missing source_file_path in capture metadata.")

	candidate = Path(str(source_file_path)).expanduser()
	resolved = candidate.resolve(strict=True)
	if not resolved.is_file():
		raise FileNotFoundError("Source file path does not point to a file.")

	allowed_dirs = _get_allowed_source_dirs()
	if not any(_is_within(resolved, allowed_dir) for allowed_dir in allowed_dirs):
		raise PermissionError("Source file path is not allowed.")

	return resolved


def _sanitize_ocr_error(exc: Exception) -> str:
	if isinstance(exc, FileNotFoundError):
		return "OCR source file unavailable."
	if isinstance(exc, PermissionError):
		return "OCR source path is not allowed."
	return "OCR processing failed."


def _trim_ocr_text(ocr_text: str) -> tuple[str, bool]:
	max_len = int(getattr(settings, "IGAR_CAPTURE_OCR_TEXT_MAX_LENGTH", 200_000))
	if max_len < 1:
		return "", bool(ocr_text)

	if len(ocr_text) <= max_len:
		return ocr_text, False

	return ocr_text[:max_len], True


def _publish_ocr_progress(*, record: CaptureUploadRecord, status: str, progress: float) -> None:
	channel_layer = get_channel_layer()
	if channel_layer is None:
		logger.warning(
			"capture.ocr.progress_publish_skipped",
			document_uuid=record.upload_id,
			status=status,
			reason="missing_channel_layer",
		)
		return

	event = {
		"type": "upload_progress",
		"event_id": f"upload-progress:{record.upload_id}:{status}:{int(progress * 100)}",
		"payload": {
			"document_id": record.upload_id,
			"upload_id": record.upload_id,
			"filename": record.filename,
			"progress": progress,
			"status": status,
		},
	}

	async_to_sync(channel_layer.group_send)("upload_progress", event)


@shared_task(bind=True, ignore_result=True)
def task_capture_ocr_process(self, capture_record_id: int) -> None:
	record = CaptureUploadRecord.objects.get(pk=capture_record_id)
	started_at = time.perf_counter()

	record.ocr_status = CaptureUploadRecord.OCR_STATUS_PROCESSING
	record.save(update_fields=["ocr_status", "updated_at"])
	_publish_ocr_progress(record=record, status="ocr_processing", progress=0.25)

	metadata = record.raw_metadata or {}
	ocr_language = metadata.get("ocr_language") or None

	try:
		source_file_path = _resolve_safe_source_path(record)

		with open(source_file_path, "rb") as file_object:
			ocr_text = OCRBackendBase.get_instance().execute(
				file_object=file_object,
				language=ocr_language,
			)

		stored_text, was_truncated = _trim_ocr_text(ocr_text)
		if was_truncated:
			logger.warning(
				"capture.ocr.text_truncated",
				event_name="capture.ocr.text_truncated",
				document_uuid=record.upload_id,
				max_length=len(stored_text),
			)

		duration_ms = int((time.perf_counter() - started_at) * 1000)
		record.ocr_status = CaptureUploadRecord.OCR_STATUS_DONE
		record.ocr_text = stored_text
		record.ocr_error = ""
		record.ocr_duration_ms = duration_ms
		record.save(update_fields=["ocr_status", "ocr_text", "ocr_error", "ocr_duration_ms", "updated_at"])

		_publish_ocr_progress(record=record, status="ocr_done", progress=1.0)
		logger.info(
			"capture.ocr.processed",
			event_name="capture.ocr.processed",
			document_uuid=record.upload_id,
			status="ocr_done",
			duree_ms=duration_ms,
		)
	except Exception as exc:  # pragma: no cover - defensive + external dependencies
		duration_ms = int((time.perf_counter() - started_at) * 1000)
		record.ocr_status = CaptureUploadRecord.OCR_STATUS_FAILED
		record.ocr_text = ""
		record.ocr_error = _sanitize_ocr_error(exc)
		record.ocr_duration_ms = duration_ms
		record.save(update_fields=["ocr_status", "ocr_text", "ocr_error", "ocr_duration_ms", "updated_at"])

		_publish_ocr_progress(record=record, status="ocr_failed", progress=1.0)
		logger.warning(
			"capture.ocr.failed",
			event_name="capture.ocr.failed",
			document_uuid=record.upload_id,
			status="ocr_failed",
			duree_ms=duration_ms,
			error_type=exc.__class__.__name__,
		)
