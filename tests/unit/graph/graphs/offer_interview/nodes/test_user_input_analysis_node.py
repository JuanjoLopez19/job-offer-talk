import pytest

from app.graph.core.config import GraphState
from app.graph.graphs.offer_interview.common.constants import OfferInterviewConstants
from app.graph.graphs.offer_interview.nodes import (
    user_input_analysis_node as node_module,
)
from app.graph.graphs.offer_interview.nodes.user_input_analysis_node import (
    user_input_analysis_node,
)


class FakeStructuredModel:
    def __init__(self, response: object) -> None:
        self.response = response

    def invoke(self, _: object) -> object:
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


class FakeLLM:
    def __init__(self, response: object) -> None:
        self.structured_model = FakeStructuredModel(response)

    def with_structured_output(self, _: object) -> FakeStructuredModel:
        return self.structured_model


def _state() -> GraphState:
    return GraphState(
        session_id="thread-1",
        assistant_message="¿Cómo diseñas una API?",
        user_input="Primero defino el contrato.",
        job_offer_generated_info={"summary": "Backend role", "questions": ["Q1", "Q2"]},
    )


def test_analysis_stops_when_generated_offer_information_is_missing() -> None:
    result = user_input_analysis_node(GraphState(session_id="thread-1"))

    assert (
        result["conditional_edge"]
        == OfferInterviewConstants.OFFER_CONTEXT_NOT_FOUND_EDGE
    )


def test_analysis_removes_the_answered_question_after_a_successful_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = {
        "output": "Buena respuesta. Vamos con la siguiente.",
        "next_node": OfferInterviewConstants.NEXT_QUESTION_EDGE,
        "reasoning": "Complete",
        "question": "Q1",
    }
    monkeypatch.setattr(
        node_module.LLMFactory, "get_llm", lambda **_: FakeLLM(response)
    )
    monkeypatch.setattr(
        node_module,
        "add_msg_to_conversation_history",
        lambda role, message, *, node_name: [{"role": role, "content": message}],
    )

    result = user_input_analysis_node(_state())

    assert result["conditional_edge"] == OfferInterviewConstants.NEXT_QUESTION_EDGE
    assert result["counter_questions"] == 0
    assert result["job_offer_generated_info"]["questions"] == ["Q2"]
    assert result["conversation_history"] == [
        {"role": "assistant", "content": "Buena respuesta. Vamos con la siguiente."}
    ]


def test_analysis_increments_the_retry_counter_for_an_incomplete_answer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = {
        "output": "Amplía los detalles técnicos.",
        "next_node": OfferInterviewConstants.NOT_COMPLETE_AND_COHERENT_EDGE,
        "reasoning": "Incomplete",
        "question": "Q1",
    }
    monkeypatch.setattr(
        node_module.LLMFactory, "get_llm", lambda **_: FakeLLM(response)
    )
    monkeypatch.setattr(
        node_module,
        "add_msg_to_conversation_history",
        lambda role, message, *, node_name: [{"role": role, "content": message}],
    )

    result = user_input_analysis_node(_state())

    assert (
        result["conditional_edge"]
        == OfferInterviewConstants.NOT_COMPLETE_AND_COHERENT_EDGE
    )
    assert result["counter_questions"] == 1
