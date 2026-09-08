import pytest

from app.graph.core.config import GraphState
from app.graph.graphs.common import hitl_node


def test_human_node_returns_the_resumed_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(hitl_node, "interrupt", lambda _: "https://example.com/job")

    result = hitl_node.human_node(GraphState(session_id="thread-1"), "url_input")

    assert result == {"user_input": "https://example.com/job", "node_name": "url_input"}


def test_human_node_adds_user_messages_to_the_history(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(hitl_node, "interrupt", lambda _: "Mi respuesta")
    monkeypatch.setattr(
        hitl_node,
        "add_msg_to_conversation_history",
        lambda role, message, *, node_name: [
            {"role": role, "content": message, "node_name": node_name}
        ],
    )

    result = hitl_node.human_node(
        GraphState(session_id="thread-1"), "analysis", add_to_conversation_history=True
    )

    assert result["conversation_history"] == [
        {"role": "user", "content": "Mi respuesta", "node_name": "analysis"}
    ]
