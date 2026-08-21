from typing import Any, cast

import pytest
from langgraph.graph.state import CompiledStateGraph

from app.graph import manager as manager_module
from app.graph.manager import GraphManager


class FakeGraph:
    def __init__(self) -> None:
        self.input: dict[str, Any] | None = None
        self.config: dict[str, Any] | None = None

    def invoke(
        self,
        graph_input: dict[str, Any],
        *,
        config: dict[str, Any],
    ) -> dict[str, Any]:
        self.input = graph_input
        self.config = config
        return {"assistant_message": "Hello"}


def test_invoke_passes_thread_id_to_the_checkpointer() -> None:
    graph = FakeGraph()
    manager = GraphManager(graph=cast(CompiledStateGraph, graph))

    result = manager.invoke({}, thread_id="thread-1")

    assert result == "Hello"
    assert graph.input == {"session_id": "thread-1"}
    assert graph.config is not None
    assert graph.config["configurable"] == {"thread_id": "thread-1"}
    assert len(graph.config["callbacks"]) == 1


def test_langfuse_client_uses_the_application_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    received: dict[str, str] = {}

    class FakeLangfuse:
        def __init__(self, *, public_key: str, secret_key: str, base_url: str) -> None:
            received["public_key"] = public_key
            received["secret_key"] = secret_key
            received["base_url"] = base_url

    monkeypatch.setattr(manager_module, "Langfuse", FakeLangfuse)

    manager = GraphManager(graph=cast(CompiledStateGraph, FakeGraph()))

    assert received["public_key"] == manager.config.langfuse_public_key
    assert received["secret_key"] == manager.config.langfuse_secret_key
    assert received["base_url"] == manager.config.langfuse_base_url
