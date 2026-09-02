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


def test_analysis_ends_when_no_questions_remain(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = {
        "output": "Hemos completado todas las preguntas. Gracias por participar.",
        "next_node": OfferInterviewConstants.END_EDGE,
        "reasoning": "No quedan preguntas disponibles.",
        "question": "¿Cómo diseñas una API?",
    }
    monkeypatch.setattr(
        node_module.LLMFactory, "get_llm", lambda **_: FakeLLM(response)
    )
    monkeypatch.setattr(
        node_module,
        "add_msg_to_conversation_history",
        lambda role, message, *, node_name: [{"role": role, "content": message}],
    )
    state = _state()
    state.job_offer_generated_info["questions"] = []

    result = user_input_analysis_node(state)

    assert result["conditional_edge"] == OfferInterviewConstants.END_EDGE
    assert result["counter_questions"] == 0
    assert "job_offer_generated_info" not in result
    assert result["assistant_message"] == response["output"]


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


def test_analysis_does_not_generate_a_new_question_at_the_retry_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = {
        "output": "Amplía los detalles técnicos.",
        "next_node": OfferInterviewConstants.NOT_COMPLETE_AND_COHERENT_EDGE,
        "reasoning": "Incomplete",
        "question": "Q1",
    }
    llm_calls: list[dict[str, object]] = []

    def fake_get_llm(**kwargs: object) -> FakeLLM:
        llm_calls.append(kwargs)
        return FakeLLM(response)

    monkeypatch.setattr(node_module.LLMFactory, "get_llm", fake_get_llm)
    monkeypatch.setattr(
        node_module,
        "add_msg_to_conversation_history",
        lambda role, message, *, node_name: [{"role": role, "content": message}],
    )
    state = _state()
    state.counter_questions = OfferInterviewConstants.MAX_DIALOG_ROUNDS - 1

    result = user_input_analysis_node(state)

    assert result["counter_questions"] == OfferInterviewConstants.MAX_DIALOG_ROUNDS
    assert result["assistant_message"] == response["output"]
    assert len(llm_calls) == 1


def test_analysis_generates_a_new_question_after_the_retry_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    analysis_response = {
        "output": "Amplía los detalles técnicos.",
        "next_node": OfferInterviewConstants.NOT_COMPLETE_AND_COHERENT_EDGE,
        "reasoning": "Incomplete",
        "question": "Q1",
    }
    generated_response = {
        "output": "Gracias. Continuemos con Q2.",
        "question": "Q2",
    }
    responses = iter([analysis_response, generated_response])
    monkeypatch.setattr(
        node_module.LLMFactory,
        "get_llm",
        lambda **_: FakeLLM(next(responses)),
    )
    monkeypatch.setattr(
        node_module,
        "add_msg_to_conversation_history",
        lambda role, message, *, node_name: [{"role": role, "content": message}],
    )
    state = _state()
    state.counter_questions = OfferInterviewConstants.MAX_DIALOG_ROUNDS

    result = user_input_analysis_node(state)

    assert result["counter_questions"] == 0
    assert result["assistant_message"] == generated_response["output"]
    assert result["job_offer_generated_info"]["questions"] == ["Q1"]
