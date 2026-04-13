"""DRF serializers for the capture app."""

from django.conf import settings
from rest_framework import serializers

from igar.core.exceptions import CaptureFileTooLargeError, CaptureUnsupportedFileTypeError


DEFAULT_ALLOWED_MIME_TYPES = {
	"application/pdf",
	"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
	"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
	"application/vnd.openxmlformats-officedocument.presentationml.presentation",
	"image/jpeg",
	"image/png",
	"image/tiff",
	"message/rfc822",
	"application/vnd.ms-outlook",
	"audio/mpeg",
	"audio/wav",
	"video/mp4",
	"application/zip",
}


class TusUploadSerializer(serializers.Serializer):
	ID = serializers.CharField(max_length=128)
	Size = serializers.IntegerField(min_value=1)
	MetaData = serializers.DictField(child=serializers.CharField(), required=False, default=dict)

	def validate(self, attrs):
		metadata = attrs.get("MetaData") or {}
		filename = metadata.get("filename")
		mime_type = metadata.get("filetype")

		if not filename or not mime_type:
			raise serializers.ValidationError("Metadata must include filename and filetype.")

		if len(metadata) > 24:
			raise serializers.ValidationError("Metadata contains too many entries.")

		max_metadata_payload = 4096
		serialized_len = sum(len(str(k)) + len(str(v)) for k, v in metadata.items())
		if serialized_len > max_metadata_payload:
			raise serializers.ValidationError("Metadata payload exceeds allowed size.")

		allowed_mime_types = set(getattr(settings, "IGAR_CAPTURE_ALLOWED_MIME_TYPES", DEFAULT_ALLOWED_MIME_TYPES))
		if mime_type not in allowed_mime_types:
			raise CaptureUnsupportedFileTypeError(
				f"Unsupported MIME type: {mime_type}",
				mime_type=mime_type,
			)

		max_size_bytes = int(getattr(settings, "IGAR_CAPTURE_MAX_FILE_SIZE", 2 * 1024 * 1024 * 1024))
		if attrs["Size"] > max_size_bytes:
			raise CaptureFileTooLargeError(
				"File exceeds configured capture size limit.",
				size=attrs["Size"],
				max_size=max_size_bytes,
			)

		attrs["_filename"] = filename
		attrs["_mime_type"] = mime_type
		return attrs


class TusEventSerializer(serializers.Serializer):
	Upload = TusUploadSerializer()


class TusHookSerializer(serializers.Serializer):
	Type = serializers.CharField()
	Event = TusEventSerializer()

	def validate(self, attrs):
		if attrs["Type"] != "post-finish":
			raise serializers.ValidationError("Only post-finish hook events are supported.")
		return attrs
