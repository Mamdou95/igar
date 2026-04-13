"""WebSocket URL routing for Igar platform."""

from django.urls import path

from igar.core.websocket import HealthWebSocketConsumer, UploadProgressConsumer

websocket_urlpatterns = [
	path("ws/", HealthWebSocketConsumer.as_asgi()),
	path("ws/uploads/progress/", UploadProgressConsumer.as_asgi()),
]
