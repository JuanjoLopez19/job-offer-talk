from types import SimpleNamespace
from typing import Any, cast

import pytest
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command

from app.graph import manager as manager_module
from app.graph.manager import GraphManager


class FakeGraph:
    def __init__(self, *, interrupted: bool = False) -> None:
        self.input: Any = None
        self.config: dict[str, Any] | None = None
        self.interrupted = interrupted

    def get_state(self, _: dict[str, Any]) -> SimpleNamespace:
        interrupts = (object(),) if self.interrupted else ()
        return SimpleNamespace(interrupts=interrupts)

    def invoke(
        self,
        graph_input: Any,
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

    assert result == {"assistant_message": "Hello"}
    assert graph.input == {"session_id": "thread-1"}
    assert graph.config is not None
    assert graph.config["configurable"] == {"thread_id": "thread-1"}
    assert len(graph.config["callbacks"]) == 1


def test_invoke_resumes_a_pending_human_interaction() -> None:
    graph = FakeGraph(interrupted=True)
    manager = GraphManager(graph=cast(CompiledStateGraph, graph))

    manager.invoke("continue", thread_id="thread-1")

    assert isinstance(graph.input, Command)
    assert graph.input.resume == "continue"


def test_invoke_requires_an_object_to_start_a_new_interaction() -> None:
    manager = GraphManager(graph=cast(CompiledStateGraph, FakeGraph()))

    with pytest.raises(ValueError, match="initial graph input"):
        manager.invoke("continue", thread_id="thread-1")


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
