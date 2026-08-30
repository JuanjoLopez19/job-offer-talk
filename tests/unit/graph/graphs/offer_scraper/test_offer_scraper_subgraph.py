import pytest
from langgraph.constants import END

from app.graph.common.constants import NodeNames
from app.graph.core.config import GraphState
from app.graph.graphs.offer_scraper.common.constants import OfferScraperConstants
from app.graph.graphs.offer_scraper.offer_scraper_subgraph import (
    route_after_generating_questions,
    route_after_scraping,
)


@pytest.mark.parametrize(
    ("edge", "destination"),
    [
        (OfferScraperConstants.EMPTY_INPUT_EDGE, NodeNames.INITIAL_HITL_NODE),
        (OfferScraperConstants.INVALID_URL_EDGE, NodeNames.INITIAL_HITL_NODE),
        (OfferScraperConstants.SCRAPING_ERROR_EDGE, END),
        (
            OfferScraperConstants.SCRAPING_COMPLETE_EDGE,
            NodeNames.GENERATE_QUESTION_NODE,
        ),
    ],
)
def test_route_after_scraping_selects_the_expected_destination(
    edge: str, destination: str
) -> None:
    assert (
        route_after_scraping(GraphState(session_id="thread-1", conditional_edge=edge))
        == destination
    )


@pytest.mark.parametrize(
    ("edge", "destination"),
    [
        (
            OfferScraperConstants.OFFER_CONTEXT_NOT_FOUND_EDGE,
            NodeNames.INITIAL_HITL_NODE,
        ),
        (OfferScraperConstants.GENERATE_QUESTION_ERROR_EDGE, END),
        (
            OfferScraperConstants.GENERATE_QUESTION_SUCCESS_EDGE,
            NodeNames.USER_INPUT_ANALYSIS_HITL_NODE,
        ),
    ],
)
def test_route_after_generating_questions_selects_the_expected_destination(
    edge: str, destination: str
) -> None:
    assert (
        route_after_generating_questions(
            GraphState(session_id="thread-1", conditional_edge=edge)
        )
        == destination
    )
