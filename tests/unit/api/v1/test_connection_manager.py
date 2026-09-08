import asyncio
from unittest.mock import AsyncMock

from fastapi import WebSocket

from app.api.v1.connection_manager import ConnectionManager


def test_connection_manager_sends_tts_metadata_and_audio() -> None:
    manager = ConnectionManager()
    websocket = AsyncMock(spec=WebSocket)

    async def send_message() -> bool:
        await manager.connect("session-1", websocket)
        return await manager.send_tts_message("session-1", "Hello", b"wav-audio")

    sent = asyncio.run(send_message())

    assert sent is True
    websocket.accept.assert_awaited_once()
    websocket.send_json.assert_awaited_once_with(
        {
            "type": "tts_message",
            "text": "Hello",
            "content_type": "audio/wav",
        }
    )
    websocket.send_bytes.assert_awaited_once_with(b"wav-audio")


def test_connection_manager_ignores_unknown_session() -> None:
    manager = ConnectionManager()

    sent = asyncio.run(manager.send_tts_message("missing-session", "Hello", b"audio"))

    assert sent is False


def test_connection_manager_correlates_voice_tts_with_its_turn() -> None:
    manager = ConnectionManager()
    websocket = AsyncMock(spec=WebSocket)

    async def send_message() -> bool:
        await manager.connect("session-1", websocket)
        return await manager.send_tts_message(
            "session-1", "Hello", b"wav-audio", turn_id="turn-1"
        )

    assert asyncio.run(send_message()) is True
    websocket.send_json.assert_awaited_once_with(
        {
            "type": "tts_message",
            "text": "Hello",
            "content_type": "audio/wav",
            "turn_id": "turn-1",
        }
    )
