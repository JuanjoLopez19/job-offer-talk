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

    async def send_tts_message(self, session_id: str, text: str, audio: bytes) -> bool:
        websocket = self._connections.get(session_id)
        if websocket is None:
            return False

        try:
            await websocket.send_json(
                {
                    "type": "tts_message",
                    "text": text,
                    "content_type": "audio/wav",
                }
            )
            await websocket.send_bytes(audio)
        except (RuntimeError, WebSocketDisconnect):
            self.disconnect(session_id, websocket)
            return False

        return True


connection_manager = ConnectionManager()
