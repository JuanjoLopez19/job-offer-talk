from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command

from app.graph import manager as manager_module
from app.graph.builder import base_builder
from app.graph.graphs.offer_scraper.common.messages import INVALID_URL_MESSAGE
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
        return {"session_id": "thread-1", "assistant_message": "Hello"}


def test_invoke_passes_thread_id_to_the_checkpointer() -> None:
    graph = FakeGraph()
    manager = GraphManager(graph=cast(CompiledStateGraph, graph))

    result = manager.invoke({}, thread_id="thread-1")

    assert result.session_id == "thread-1"
    assert result.assistant_message == "Hello"
    assert graph.input == {"session_id": "thread-1"}
    assert graph.config is not None
    assert graph.config["configurable"] == {"thread_id": "thread-1"}
    assert graph.config["metadata"] == {"langfuse_session_id": "thread-1"}
    assert graph.config["run_name"] == "job-offer-talk.graph.invoke"
    assert len(graph.config["callbacks"]) == 1


def test_invoke_sets_custom_langfuse_trace_attributes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    received: dict[str, Any] = {}

    class CompleteFakeGraph(FakeGraph):
        def invoke(
            self,
            graph_input: Any,
            *,
            config: dict[str, Any],
        ) -> dict[str, Any]:
            super().invoke(graph_input, config=config)
            return {"session_id": "thread-1", "assistant_message": "Hello"}

    @contextmanager
    def fake_propagate_attributes(**kwargs: Any):
        received.update(kwargs)
        yield

    monkeypatch.setattr(
        manager_module, "propagate_attributes", fake_propagate_attributes
    )
    manager = GraphManager(graph=cast(CompiledStateGraph, CompleteFakeGraph()))
    manager.config.langfuse_trace_name = "job-offer-conversation"

    manager.invoke({}, thread_id="thread-1")

    assert received == {
        "trace_name": "job-offer-conversation",
        "session_id": "thread-1",
        "tags": ["job-offer-talk", "langgraph"],
        "metadata": {
            "environment": manager.config.environment,
            "framework": "langgraph",
            "version": manager.config.version,
        },
    }


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
        def __init__(
            self,
            *,
            public_key: str,
            secret_key: str,
            base_url: str,
            environment: str,
            release: str,
        ) -> None:
            received["public_key"] = public_key
            received["secret_key"] = secret_key
            received["base_url"] = base_url
            received["environment"] = environment
            received["release"] = release

    monkeypatch.setattr(manager_module, "Langfuse", FakeLangfuse)

    manager = GraphManager(graph=cast(CompiledStateGraph, FakeGraph()))

    assert received["public_key"] == manager.config.langfuse_public_key
    assert received["secret_key"] == manager.config.langfuse_secret_key
    assert received["base_url"] == manager.config.langfuse_base_url
    assert received["environment"] == manager.config.environment
    assert received["release"] == manager.config.version


def test_export_graph_writes_a_local_mermaid_file(tmp_path: Path) -> None:
    graph = base_builder.compile(checkpointer=InMemorySaver())
    manager = GraphManager(graph=graph)

    output_path = manager.export_graph(tmp_path / "graph.mmd")

    assert output_path.read_text(encoding="utf-8").startswith("---")
    assert "offer_scraper" in output_path.read_text(encoding="utf-8")


def test_initial_graph_invocation_interrupts_for_a_job_offer_url() -> None:
    graph = base_builder.compile(checkpointer=InMemorySaver())
    manager = GraphManager(graph=graph)

    result = manager.invoke({}, thread_id="thread-1")

    assert result.session_id == "thread-1"
    assert result.model_extra is not None
    assert result.model_extra["__interrupt__"]


def test_invalid_url_interrupts_again_with_validation_message() -> None:
    graph = base_builder.compile(checkpointer=InMemorySaver())
    manager = GraphManager(graph=graph)

    manager.invoke({}, thread_id="thread-1")
    invalid_result = manager.invoke("not-a-url", thread_id="thread-1")

    assert invalid_result.model_extra is not None
    interrupt_payload = invalid_result.model_extra["__interrupt__"][0].value
    assert interrupt_payload["assistant_message"] == INVALID_URL_MESSAGE
