from typing import Any, cast

from job_offer_scraper_mcp.shared.constants import JobOfferInfo
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from pytest import MonkeyPatch

from app.graph.common.constants import GraphStateFields
from app.graph.core.config import GraphState
from app.graph.graphs.offer_scraper.common.constants import OfferScraperConstants
from app.graph.graphs.offer_scraper.nodes import offer_scraper_node as node_module
from app.graph.graphs.offer_scraper.nodes.offer_scraper_node import offer_scraper_node


class FakeScraper:
    def extract(self) -> None:
        pass

    def get_job_offer_info(self) -> JobOfferInfo:
        return JobOfferInfo(
            url="https://example.com/jobs/1",
            title="Software Engineer",
            company_name="Example",
            location="Madrid",
            description="Build products.",
            criteria="Python",
        )


def test_serializes_job_offer_url_before_storing_it_in_the_graph_state(
    monkeypatch: MonkeyPatch,
) -> None:
    scraper = FakeScraper()
    monkeypatch.setattr(
        node_module.FactoryScrapper,
        "get_scrapper",
        lambda _: scraper,
    )

    result = offer_scraper_node(
        GraphState(session_id="session-1", user_input="https://example.com/jobs/1")
    )

    job_offer_context = cast(dict[str, Any], result[GraphStateFields.JOB_OFFER_CONTEXT])
    assert job_offer_context["url"] == "https://example.com/jobs/1"
    assert isinstance(job_offer_context["url"], str)

    serialized_type, serialized_data = JsonPlusSerializer().dumps_typed(result)

    assert serialized_type == "msgpack"
    assert serialized_data


def test_returns_the_input_error_when_no_url_is_available() -> None:
    result = offer_scraper_node(GraphState(session_id="session-1"))

    assert (
        cast(str, result[GraphStateFields.CONDITIONAL_EDGE])
        == OfferScraperConstants.EMPTY_INPUT_EDGE
    )


def test_returns_the_validation_error_for_an_invalid_url() -> None:
    result = offer_scraper_node(
        GraphState(session_id="session-1", user_input="not-a-url")
    )

    assert (
        cast(str, result[GraphStateFields.CONDITIONAL_EDGE])
        == OfferScraperConstants.INVALID_URL_EDGE
    )


def test_returns_a_scraping_error_when_the_scraper_cannot_be_selected(
    monkeypatch: MonkeyPatch,
) -> None:
    def raise_selection_error(_: object) -> FakeScraper:
        raise RuntimeError("unsupported site")

    monkeypatch.setattr(
        node_module.FactoryScrapper,
        "get_scrapper",
        raise_selection_error,
    )

    result = offer_scraper_node(
        GraphState(session_id="session-1", user_input="https://example.com/job")
    )

    assert (
        cast(str, result[GraphStateFields.CONDITIONAL_EDGE])
        == OfferScraperConstants.SCRAPING_ERROR_EDGE
    )
