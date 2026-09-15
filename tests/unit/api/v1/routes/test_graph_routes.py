from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.routes import graph_routes
from app.graph.core.config import GraphState
from app.graph.manager import GraphManager


def test_graph_route_generates_and_returns_a_thread_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_invoke(
        _: GraphManager, graph_input: Any, *, thread_id: str
    ) -> dict[str, Any]:
        captured["graph_input"] = graph_input
        captured["thread_id"] = thread_id
        return {"assistant_message": "Hello"}

    monkeypatch.setattr(GraphManager, "invoke", fake_invoke)
    app = FastAPI()
    app.include_router(graph_routes.graph_router)

    response = TestClient(app).post("/", json={"session_id": "session-1"})

    assert response.status_code == 200
    assert response.json() == {"assistant_message": "Hello"}
    assert response.headers[graph_routes.THREAD_ID_HEADER] == captured["thread_id"]


def test_graph_route_reuses_the_supplied_thread_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_invoke(
        _: GraphManager, graph_input: Any, *, thread_id: str
    ) -> dict[str, Any]:
        captured["thread_id"] = thread_id
        return {"assistant_message": "Hello"}

    monkeypatch.setattr(GraphManager, "invoke", fake_invoke)
    app = FastAPI()
    app.include_router(graph_routes.graph_router)

    response = TestClient(app).post(
        "/",
        json={"session_id": "session-1"},
        headers={graph_routes.THREAD_ID_HEADER: "thread-1"},
    )

    assert response.status_code == 200
    assert captured["thread_id"] == "thread-1"
    assert response.headers[graph_routes.THREAD_ID_HEADER] == "thread-1"


def test_graph_route_forwards_a_scalar_human_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_invoke(
        _: GraphManager, graph_input: Any, *, thread_id: str
    ) -> dict[str, Any]:
        captured["graph_input"] = graph_input
        return {"assistant_message": "Hello"}

    monkeypatch.setattr(GraphManager, "invoke", fake_invoke)
    app = FastAPI()
    app.include_router(graph_routes.graph_router)

    response = TestClient(app).post(
        "/",
        json="continue",
        headers={graph_routes.THREAD_ID_HEADER: "thread-1"},
    )

    assert response.status_code == 200
    assert captured["graph_input"] == "continue"


def test_graph_route_sends_generated_audio_to_connected_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeTTS:
        def generate_bytes(self, text: str) -> bytes:
            assert text == "What interests you about this role?"
            return b"wav-audio"

    send_tts_message = AsyncMock(return_value=True)

    class FakeConnectionManager:
        def is_connected(self, session_id: str) -> bool:
            return session_id == "session-1"

        async def send_tts_message(
            self, session_id: str, text: str, audio: bytes
        ) -> bool:
            return await send_tts_message(session_id, text, audio)

    result = GraphState(
        session_id="session-1",
        assistant_message="What interests you about this role?",
        is_tts_active=True,
    )

    monkeypatch.setattr(GraphManager, "invoke", lambda *args, **kwargs: result)
    monkeypatch.setattr(graph_routes, "connection_manager", FakeConnectionManager())

    app = FastAPI()
    app.state.tts = FakeTTS()
    app.include_router(graph_routes.graph_router)

    response = TestClient(app).post("/", json={"session_id": "session-1"})

    assert response.status_code == 200
    send_tts_message.assert_awaited_once_with(
        "session-1",
        "What interests you about this role?",
        b"wav-audio",
    )
