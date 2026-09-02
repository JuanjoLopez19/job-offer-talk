import pytest
from langgraph.constants import END

from app.graph.common.constants import NodeNames
from app.graph.core.config import GraphState
from app.graph.graphs.offer_interview.common.constants import OfferInterviewConstants
from app.graph.graphs.offer_interview.common.messages import (
    ENDING_WITHOUT_UNDERSTANDING_MESSAGE,
)
from app.graph.graphs.offer_interview.nodes import (
    ask_for_new_question_node as node_module,
)
from app.graph.graphs.offer_interview.nodes.ask_for_new_question_node import (
    ask_for_new_question_node,
)
from app.graph.graphs.offer_scraper.common.messages import (
    GENERATE_QUESTION_ERROR_MESSAGE,
    OFFER_CONTEXT_NOT_FOUND_MESSAGE,
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
        self.response = response

    def with_structured_output(self, _: object) -> FakeStructuredModel:
        return FakeStructuredModel(self.response)


def _state(*, counter_questions: int = 0) -> GraphState:
    return GraphState(
        session_id="thread-1",
        assistant_message="¿Cómo diseñas una API?",
        job_offer_generated_info={"questions": ["Q1", "Q2"]},
        conversation_history=[],
        counter_questions=counter_questions,
    )


def _patch_history(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        node_module,
        "add_msg_to_conversation_history",
        lambda role, message, *, node_name: [
            {"role": role, "content": message, "node_name": node_name}
        ],
    )


def test_ask_for_new_question_stops_when_offer_context_is_missing() -> None:
    result = ask_for_new_question_node(GraphState(session_id="thread-1"))

    assert result["node_name"] == NodeNames.ASK_FOR_NEW_QUESTION_NODE
    assert (
        result["conditional_edge"]
        == OfferInterviewConstants.OFFER_CONTEXT_NOT_FOUND_EDGE
    )
    assert result["assistant_message"] == OFFER_CONTEXT_NOT_FOUND_MESSAGE


def test_ask_for_new_question_continues_with_the_generated_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = {
        "output": "De acuerdo, continuemos con la pregunta.",
        "next_node": OfferInterviewConstants.CONTINUE_EDGE,
        "reasoning": "La intención está clara.",
        "question": "¿Cómo diseñas una API?",
    }
    monkeypatch.setattr(
        node_module.LLMFactory, "get_llm", lambda **_: FakeLLM(response)
    )
    _patch_history(monkeypatch)

    result = ask_for_new_question_node(
        _state(
            counter_questions=OfferInterviewConstants.MAX_DIALOG_ROUNDS_ASK_NEW_QUESTION
        )
    )

    assert result["assistant_message"] == response["output"]
    assert result["conditional_edge"] == OfferInterviewConstants.CONTINUE_EDGE
    assert result["counter_questions"] == 0
    assert result["is_tts_message"] is False
    assert result["conversation_history"] == [
        {
            "role": "assistant",
            "content": response["output"],
            "node_name": NodeNames.ASK_FOR_NEW_QUESTION_NODE,
        }
    ]


def test_ask_for_new_question_repeats_and_increments_the_counter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = {
        "output": "¿Prefieres continuar o cambiar de pregunta?",
        "next_node": OfferInterviewConstants.REPEAT_EDGE,
        "reasoning": "La intención no está clara.",
        "question": "¿Cómo diseñas una API?",
    }
    monkeypatch.setattr(
        node_module.LLMFactory, "get_llm", lambda **_: FakeLLM(response)
    )
    _patch_history(monkeypatch)

    result = ask_for_new_question_node(_state())

    assert result["conditional_edge"] == OfferInterviewConstants.REPEAT_EDGE
    assert result["counter_questions"] == 1
    assert result["assistant_message"] == response["output"]


def test_ask_for_new_question_ends_after_the_maximum_number_of_repeats(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = {
        "output": "¿Prefieres continuar o cambiar de pregunta?",
        "next_node": OfferInterviewConstants.REPEAT_EDGE,
        "reasoning": "La intención no está clara.",
        "question": "¿Cómo diseñas una API?",
    }
    monkeypatch.setattr(
        node_module.LLMFactory, "get_llm", lambda **_: FakeLLM(response)
    )
    _patch_history(monkeypatch)

    result = ask_for_new_question_node(
        _state(
            counter_questions=(
                OfferInterviewConstants.MAX_DIALOG_ROUNDS_ASK_NEW_QUESTION - 1
            )
        )
    )

    assert result["conditional_edge"] == END
    assert result["counter_questions"] == 0
    assert result["assistant_message"] == ENDING_WITHOUT_UNDERSTANDING_MESSAGE
    assert result["conversation_history"][0]["content"] == (
        ENDING_WITHOUT_UNDERSTANDING_MESSAGE
    )


def test_ask_for_new_question_returns_an_error_when_the_model_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        node_module.LLMFactory,
        "get_llm",
        lambda **_: FakeLLM(RuntimeError("model unavailable")),
    )

    result = ask_for_new_question_node(_state())

    assert result["conditional_edge"] == OfferInterviewConstants.ANALYSIS_ERROR_EDGE
    assert result["assistant_message"] == GENERATE_QUESTION_ERROR_MESSAGE
