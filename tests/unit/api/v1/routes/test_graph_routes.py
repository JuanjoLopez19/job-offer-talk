from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.routes import graph_routes
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
