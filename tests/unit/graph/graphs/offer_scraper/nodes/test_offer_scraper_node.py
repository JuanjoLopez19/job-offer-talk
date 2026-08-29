from job_offer_scraper_mcp.shared.constants import JobOfferInfo
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from pytest import MonkeyPatch

from app.graph.core.config import GraphState
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

    assert result["job_offer_context"]["url"] == "https://example.com/jobs/1"
    assert isinstance(result["job_offer_context"]["url"], str)

    serialized_type, serialized_data = JsonPlusSerializer().dumps_typed(result)

    assert serialized_type == "msgpack"
    assert serialized_data
