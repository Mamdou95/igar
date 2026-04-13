"""Models for the capture app."""

from django.db import models


class CaptureUploadRecord(models.Model):
	"""Stores metadata emitted by tusd post-finish webhooks."""

	STATUS_RECEIVED = "received"
	STATUS_ERROR = "error"

	STATUS_CHOICES = (
		(STATUS_RECEIVED, "Received"),
		(STATUS_ERROR, "Error"),
	)

	OCR_STATUS_PENDING = "pending"
	OCR_STATUS_QUEUED = "queued"
	OCR_STATUS_PROCESSING = "processing"
	OCR_STATUS_DONE = "done"
	OCR_STATUS_FAILED = "failed"

	OCR_STATUS_CHOICES = (
		(OCR_STATUS_PENDING, "Pending"),
		(OCR_STATUS_QUEUED, "Queued"),
		(OCR_STATUS_PROCESSING, "Processing"),
		(OCR_STATUS_DONE, "Done"),
		(OCR_STATUS_FAILED, "Failed"),
	)

	upload_id = models.CharField(max_length=128, unique=True)
	filename = models.CharField(max_length=255)
	mime_type = models.CharField(max_length=150)
	size_bytes = models.BigIntegerField()
	bucket = models.CharField(max_length=63, default="igar-temp")
	storage_key = models.CharField(max_length=512)
	raw_metadata = models.JSONField(default=dict, blank=True)
	status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_RECEIVED)
	ocr_status = models.CharField(max_length=16, choices=OCR_STATUS_CHOICES, default=OCR_STATUS_PENDING)
	ocr_text = models.TextField(blank=True, default="")
	ocr_duration_ms = models.PositiveIntegerField(null=True, blank=True)
	ocr_error = models.TextField(blank=True, default="")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ("-created_at",)

	def __str__(self):
		return f"{self.upload_id}:{self.filename}"
