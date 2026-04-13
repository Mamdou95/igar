"""API views for the capture app."""

import structlog
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from igar.apps.capture.serializers import TusHookSerializer
from igar.apps.capture.services import persist_post_finish_upload
from igar.core.exceptions import InvalidRequestError

logger = structlog.get_logger("igar.capture")


class TusHookAPIView(APIView):
	"""Receives post-finish webhook events emitted by tusd."""

	permission_classes = [AllowAny]
	authentication_classes = []

	def post(self, request, *args, **kwargs):
		serializer = TusHookSerializer(data=request.data)
		if not serializer.is_valid():
			logger.warning(
				"capture.hook.validation_failed",
				errors=serializer.errors,
			)
			raise InvalidRequestError("Invalid tus hook payload.", errors=serializer.errors)

		upload_payload = serializer.validated_data["Event"]["Upload"]
		record = persist_post_finish_upload(upload_payload)

		logger.info(
			"capture.hook.accepted",
			upload_id=record.upload_id,
			filename=record.filename,
			mime_type=record.mime_type,
			size_bytes=record.size_bytes,
			storage_key=record.storage_key,
		)

		return Response(
			{
				"status": "accepted",
				"upload_id": record.upload_id,
				"storage_key": record.storage_key,
			},
			status=200,
		)
