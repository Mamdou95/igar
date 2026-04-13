import json
from types import SimpleNamespace
from unittest.mock import AsyncMock
from typing import Any, cast

from asgiref.sync import async_to_sync

from igar.core.websocket import UploadProgressConsumer


def test_upload_progress_consumer_connects_and_disconnects_with_structured_logs(monkeypatch):
    info_calls: list[tuple[str, dict]] = []

    def fake_info(event_name: str, **kwargs):
        info_calls.append((event_name, kwargs))

    monkeypatch.setattr("igar.core.websocket.logger", SimpleNamespace(info=fake_info, debug=lambda *args, **kwargs: None))

    consumer = UploadProgressConsumer()
    group_add = AsyncMock()
    group_discard = AsyncMock()
    consumer.channel_layer = cast(Any, SimpleNamespace(group_add=group_add, group_discard=group_discard))
    consumer.channel_name = "test-channel"
    consumer.accept = AsyncMock()
    consumer.send = AsyncMock()

    async_to_sync(consumer.connect)()

    group_add.assert_awaited_once_with("upload_progress", "test-channel")
    consumer.accept.assert_awaited_once()
    consumer.send.assert_awaited_once()
    send_args = consumer.send.await_args
    assert send_args is not None
    connected_payload = json.loads(send_args.kwargs["text_data"])
    assert connected_payload == {
        "event": "socket.connected",
        "payload": {"group": "upload_progress"},
    }

    async_to_sync(consumer.disconnect)(1000)

    group_discard.assert_awaited_once_with("upload_progress", "test-channel")
    assert info_calls[0][0] == "capture.ws.connected"
    assert info_calls[1][0] == "capture.ws.disconnected"


def test_upload_progress_consumer_forwards_upload_progress_event(monkeypatch):
    debug_calls: list[tuple[str, dict]] = []

    def fake_debug(log_event: str, **kwargs):
        debug_calls.append((log_event, kwargs))

    monkeypatch.setattr("igar.core.websocket.logger", SimpleNamespace(info=lambda *args, **kwargs: None, debug=fake_debug))

    consumer = UploadProgressConsumer()
    consumer.channel_name = "test-channel"
    consumer.send = AsyncMock()

    async_to_sync(consumer.upload_progress)(
        {
            "event_id": "upload-progress:upload-42:uploaded:100",
            "payload": {
                "document_id": "upload-42",
                "upload_id": "upload-42",
                "filename": "facture.pdf",
                "progress": 1.0,
                "status": "uploaded",
            },
        }
    )

    consumer.send.assert_awaited_once()
    send_args = consumer.send.await_args
    assert send_args is not None
    message = json.loads(send_args.kwargs["text_data"])
    assert message["event"] == "upload.progress"
    assert message["event_id"] == "upload-progress:upload-42:uploaded:100"
    assert message["payload"]["document_id"] == "upload-42"
    assert debug_calls[0][0] == "capture.ws.event_forwarded"
