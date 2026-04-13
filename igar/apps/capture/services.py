"""Business logic services for the capture app."""

import structlog
from celery.exceptions import CeleryError
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.cache import cache
from django.db import IntegrityError

from igar.apps.capture.models import CaptureUploadRecord
from igar.core.exceptions import IntegrityViolationError

logger = structlog.get_logger("igar.capture")


def _sanitize_queue_error(exc: Exception) -> str:
	if isinstance(exc, CeleryError):
		return "OCR queue unavailable."
	return "OCR queueing failed."


def _increment_metric(metric_key: str, amount: int = 1) -> None:
	current_value = cache.get(metric_key, 0)
	cache.set(metric_key, int(current_value) + amount, None)


def _publish_upload_progress(*, upload_id: str, filename: str, progress: float, status: str) -> None:
	channel_layer = get_channel_layer()
	if channel_layer is None:
		logger.warning(
			"capture.upload.progress_publish_skipped",
			upload_id=upload_id,
			status=status,
			reason="missing_channel_layer",
		)
		return

	event = {
		"type": "upload_progress",
		"event_id": f"upload-progress:{upload_id}:{status}:{int(progress * 100)}",
		"payload": {
			"document_id": upload_id,
			"upload_id": upload_id,
			"filename": filename,
			"progress": progress,
			"status": status,
		},
	}

	try:
		async_to_sync(channel_layer.group_send)("upload_progress", event)
		logger.info(
			"capture.upload.progress_published",
			upload_id=upload_id,
			filename=filename,
			progress=progress,
			status=status,
			event_id=event["event_id"],
		)
	except Exception as exc:  # pragma: no cover - defensive logging
		logger.exception(
			"capture.upload.progress_publish_failed",
			upload_id=upload_id,
			status=status,
			error=str(exc),
		)


def _enqueue_ocr_processing(record: CaptureUploadRecord) -> None:
	"""Queue OCR processing on the dedicated ocr worker queue."""
	record.ocr_status = CaptureUploadRecord.OCR_STATUS_QUEUED
	record.save(update_fields=["ocr_status", "updated_at"])

	_publish_upload_progress(
		upload_id=record.upload_id,
		filename=record.filename,
		progress=0.0,
		status="ocr_queued",
	)

	try:
		from igar.apps.capture.tasks import task_capture_ocr_process

		task_capture_ocr_process.apply_async(args=[record.pk], queue="ocr")
		logger.info(
			"capture.ocr.queued",
			document_uuid=record.upload_id,
			upload_id=record.upload_id,
			storage_key=record.storage_key,
			queue="ocr",
		)
	except (CeleryError, RuntimeError, ValueError) as exc:
		record.ocr_status = CaptureUploadRecord.OCR_STATUS_FAILED
		record.ocr_error = _sanitize_queue_error(exc)
		record.save(update_fields=["ocr_status", "ocr_error", "updated_at"])
		_publish_upload_progress(
			upload_id=record.upload_id,
			filename=record.filename,
			progress=0.0,
			status="ocr_failed",
		)
		logger.exception(
			"capture.ocr.queue_failed",
			document_uuid=record.upload_id,
			upload_id=record.upload_id,
			error=str(exc),
		)


def persist_post_finish_upload(upload_payload: dict) -> CaptureUploadRecord:
	"""Persist a validated tusd post-finish upload payload."""

	metadata = upload_payload.get("MetaData") or {}
	upload_id = upload_payload["ID"]
	filename = upload_payload["_filename"]
	mime_type = upload_payload["_mime_type"]
	size_bytes = upload_payload["Size"]

	# tusd writes into igar-temp bucket; keep deterministic key for downstream workers.
	storage_key = metadata.get("storage_key") or f"{upload_id}/{filename}"

	try:
		record = CaptureUploadRecord.objects.create(
			upload_id=upload_id,
			filename=filename,
			mime_type=mime_type,
			size_bytes=size_bytes,
			storage_key=storage_key,
			raw_metadata=metadata,
		)
		_increment_metric("capture.uploads.received_total", 1)
		_increment_metric("capture.uploads.received_bytes_total", int(size_bytes))
		_publish_upload_progress(
			upload_id=upload_id,
			filename=filename,
			progress=1.0,
			status="uploaded",
		)
		_enqueue_ocr_processing(record)
		return record
	except IntegrityError as exc:
		_increment_metric("capture.uploads.error_total", 1)
		raise IntegrityViolationError(
			"Upload already recorded.",
			upload_id=upload_id,
		) from exc
