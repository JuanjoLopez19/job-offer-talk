from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.routes.conversation_routes import conversation_router


def test_user_message_transcribes_a_complete_binary_audio_frame() -> None:
    class FakeSTT:
        audio: bytes | None = None

        def transcribe_bytes(self, audio: bytes) -> str:
            self.audio = audio
            return "Esta es mi respuesta"

    stt = FakeSTT()
    app = FastAPI()
    app.state.stt = stt
    app.include_router(conversation_router)

    with TestClient(app).websocket_connect("/session-1") as websocket:
        websocket.send_json({"event": "user_message"})
        websocket.send_bytes(b"complete-encoded-audio")

        assert websocket.receive_json() == {
            "event": "assistant_message",
            "message": "Esta es mi respuesta",
        }

    assert stt.audio == b"complete-encoded-audio"
