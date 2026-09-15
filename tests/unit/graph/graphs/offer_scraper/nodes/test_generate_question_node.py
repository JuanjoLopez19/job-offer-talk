import pytest
from job_offer_scraper_mcp.shared.constants import JobOfferInfo
from langchain_core.messages import HumanMessage, SystemMessage

from app.graph.core.config import GraphState
from app.graph.graphs.offer_scraper.common.constants import OfferScraperConstants
from app.graph.graphs.offer_scraper.nodes import generate_question_node as node_module
from app.graph.graphs.offer_scraper.nodes.generate_question_node import (
    generate_question_node,
)


def _job_offer_context() -> dict[str, object]:
    return JobOfferInfo(
        url="https://example.com/job",
        title="Backend Engineer",
        company_name="Example",
        location="Madrid",
        description="Construir servicios.",
        criteria="Python",
    ).model_dump(mode="json")


class FakeStructuredModel:
    def __init__(self, response: object) -> None:
        self.response = response
        self.invocation: object | None = None

    def invoke(self, invocation: object) -> object:
        self.invocation = invocation
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


class FakeLLM:
    def __init__(self, response: object) -> None:
        self.structured_model = FakeStructuredModel(response)

    def with_structured_output(self, _: object) -> FakeStructuredModel:
        return self.structured_model


def _llm_response() -> dict[str, object]:
    return {
        "keywords": ["Python"],
        "questions": ["¿Qué experiencia tienes con Python?"],
        "reasoning": "Python es un requisito principal.",
        "summary": "La empresa busca una persona experta en Python.",
    }


def test_generate_question_returns_the_first_question_and_queues_the_rest(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = {
        "keywords": ["Python"],
        "questions": ["¿Qué experiencia tienes con Python?", "¿Cómo pruebas APIs?"],
        "reasoning": "Relevant skills",
        "summary": "Backend role",
    }
    monkeypatch.setattr(
        node_module.LLMFactory, "get_llm", lambda **_: FakeLLM(response)
    )
    monkeypatch.setattr(
        node_module,
        "add_msg_to_conversation_history",
        lambda role, message, *, node_name: [
            {"role": role, "content": message, "node_name": node_name}
        ],
    )

    result = generate_question_node(
        GraphState(session_id="thread-1", job_offer_context=_job_offer_context())
    )

    assert result["assistant_message"] == "¿Qué experiencia tienes con Python?"
    assert result["job_offer_generated_info"]["questions"] == ["¿Cómo pruebas APIs?"]
    assert (
        result["conditional_edge"]
        == OfferScraperConstants.GENERATE_QUESTION_SUCCESS_EDGE
    )
    assert result["conversation_history"][0]["role"] == "assistant"


def test_generate_question_sends_language_rules_as_a_system_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_llm = FakeLLM(_llm_response())
    monkeypatch.setattr(node_module.LLMFactory, "get_llm", lambda **_: fake_llm)

    generate_question_node(
        GraphState(session_id="thread-1", job_offer_context=_job_offer_context())
    )

    invocation = fake_llm.structured_model.invocation
    assert isinstance(invocation, list)
    assert len(invocation) == 2
    assert isinstance(invocation[0], SystemMessage)
    assert "Español de España" in invocation[0].content
    assert isinstance(invocation[1], HumanMessage)
    assert "## Oferta de trabajo" in invocation[1].content


def test_generate_question_uses_a_low_temperature(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    received_options: dict[str, object] = {}

    def get_llm(**options: object) -> FakeLLM:
        received_options.update(options)
        return FakeLLM(_llm_response())

    monkeypatch.setattr(node_module.LLMFactory, "get_llm", get_llm)

    generate_question_node(
        GraphState(session_id="thread-1", job_offer_context=_job_offer_context())
    )

    assert received_options["temperature"] == 0.2


def test_generate_question_stops_when_the_offer_context_is_missing() -> None:
    result = generate_question_node(GraphState(session_id="thread-1"))

    assert (
        result["conditional_edge"] == OfferScraperConstants.OFFER_CONTEXT_NOT_FOUND_EDGE
    )


def test_generate_question_returns_an_error_when_the_llm_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        node_module.LLMFactory,
        "get_llm",
        lambda **_: FakeLLM(RuntimeError("unavailable")),
    )

    result = generate_question_node(
        GraphState(session_id="thread-1", job_offer_context=_job_offer_context())
    )

    assert (
        result["conditional_edge"] == OfferScraperConstants.GENERATE_QUESTION_ERROR_EDGE
    )


def test_generate_question_returns_an_error_when_the_llm_returns_no_questions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = {
        "keywords": ["Python"],
        "questions": [],
        "reasoning": "No questions generated",
        "summary": "Backend role",
    }
    monkeypatch.setattr(
        node_module.LLMFactory, "get_llm", lambda **_: FakeLLM(response)
    )

    result = generate_question_node(
        GraphState(session_id="thread-1", job_offer_context=_job_offer_context())
    )

    assert (
        result["conditional_edge"] == OfferScraperConstants.GENERATE_QUESTION_ERROR_EDGE
    )
