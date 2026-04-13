"""Minimal websocket consumer used for infrastructure connectivity checks."""

import json
import structlog

from channels.generic.websocket import AsyncWebsocketConsumer

logger = structlog.get_logger("igar.capture.websocket")


class HealthWebSocketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({"status": "connected"}))

    async def receive(self, text_data=None, bytes_data=None):
        # Echo messages to make proxy and channel behavior observable in dev.
        if text_data is not None:
            await self.send(text_data=text_data)

    async def disconnect(self, close_code):
        return None


class UploadProgressConsumer(AsyncWebsocketConsumer):
    group_name = "upload_progress"

    async def connect(self):
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info(
            "capture.ws.connected",
            channel=self.channel_name,
            group=self.group_name,
        )
        await self.send(
            text_data=json.dumps(
                {
                    "event": "socket.connected",
                    "payload": {"group": self.group_name},
                }
            )
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.info(
            "capture.ws.disconnected",
            channel=self.channel_name,
            group=self.group_name,
            close_code=close_code,
        )

    async def upload_progress(self, event):
        logger.debug(
            "capture.ws.event_forwarded",
            channel=self.channel_name,
            event_id=event.get("event_id"),
            event_name="upload.progress",
        )
        await self.send(
            text_data=json.dumps(
                {
                    "event": "upload.progress",
                    "event_id": event.get("event_id"),
                    "payload": event.get("payload", {}),
                }
            )
        )
