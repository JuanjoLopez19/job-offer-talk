from app.graph.core.config import GraphState, conversation_history_reducer


def test_conversation_history_reducer_appends_updates() -> None:
    current = [{"role": "assistant", "content": "Hola"}]
    update = [{"role": "user", "content": "Gracias"}]

    assert conversation_history_reducer(current, update) == current + update


def test_conversation_history_reducer_clears_history_with_none() -> None:
    assert conversation_history_reducer([{"role": "assistant"}], None) == []


def test_graph_state_keeps_langgraph_interrupt_metadata() -> None:
    interrupt = object()

    state = GraphState.model_validate(
        {"session_id": "thread-1", "__interrupt__": [interrupt]}
    )

    assert state.model_extra == {"__interrupt__": [interrupt]}
