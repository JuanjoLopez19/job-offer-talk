from dataclasses import dataclass, field

from fastapi import WebSocket, WebSocketDisconnect


@dataclass(slots=True)
class ConnectionManager:
    _connections: dict[str, WebSocket] = field(default_factory=dict)

    async def connect(self, session_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[session_id] = websocket

    def disconnect(self, session_id: str, websocket: WebSocket) -> None:
        if self._connections.get(session_id) is websocket:
            self._connections.pop(session_id, None)

    def is_connected(self, session_id: str) -> bool:
        return session_id in self._connections

    async def send_tts_message(
        self,
        session_id: str,
        text: str,
        audio: bytes,
        *,
        turn_id: str | None = None,
    ) -> bool:
        websocket = self._connections.get(session_id)
        if websocket is None:
            return False

        try:
            metadata = {
                "type": "tts_message",
                "text": text,
                "content_type": "audio/wav",
            }
            if turn_id is not None:
                metadata["turn_id"] = turn_id
            await websocket.send_json(metadata)
            await websocket.send_bytes(audio)
        except (RuntimeError, WebSocketDisconnect):
            self.disconnect(session_id, websocket)
            return False

        return True


connection_manager = ConnectionManager()
