import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.routes import conversation_routes
from app.graph.core.config import GraphState
from app.graph.manager import GraphManager
from app.shared.models import GraphInput


def test_user_message_sends_transcript_then_assistant_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeSTT:
        audio: bytes | None = None

        def transcribe_bytes(self, audio: bytes) -> str:
            self.audio = audio
            return "Esta es mi respuesta"

    def fake_invoke(
        _: GraphManager,
        graph_input: GraphInput,
        *,
        thread_id: str,
    ) -> GraphState:
        assert graph_input.user_input == "Esta es mi respuesta"
        assert thread_id == "session-1"
        return GraphState(
            session_id=thread_id,
            assistant_message="¿Qué experiencia tienes?",
            is_tts_message=False,
        )

    stt = FakeSTT()
    monkeypatch.setattr(GraphManager, "invoke", fake_invoke)
    app = FastAPI()
    app.state.stt = stt
    app.include_router(conversation_routes.conversation_router)

    with TestClient(app).websocket_connect("/session-1") as websocket:
        websocket.send_json(
            {
                "event": "user_message",
                "content_type": "audio/webm;codecs=opus",
                "turn_id": "turn-1",
            }
        )
        websocket.send_bytes(b"complete-encoded-audio")

        assert websocket.receive_json() == {
            "event": "user_message",
            "message": "Esta es mi respuesta",
            "turn_id": "turn-1",
        }
        assert websocket.receive_json() == {
            "event": "assistant_message",
            "message": "¿Qué experiencia tienes?",
            "turn_id": "turn-1",
        }

    assert stt.audio == b"complete-encoded-audio"


def test_invalid_voice_metadata_returns_an_error_and_closes_connection() -> None:
    app = FastAPI()
    app.include_router(conversation_routes.conversation_router)

    with TestClient(app).websocket_connect("/session-1") as websocket:
        websocket.send_json({"event": "unsupported"})

        assert websocket.receive_json() == {
            "event": "error",
            "message": "Metadatos de audio no válidos",
        }
