from langgraph.constants import END
from langgraph.graph import StateGraph

from app.graph.common.constants import NodeNames
from app.graph.core.config import GraphState
from app.graph.graphs.offer_scraper.common.constants import OfferScraperConstants
from app.graph.graphs.offer_scraper.nodes.generate_question_node import (
    generate_question_node,
)
from app.graph.graphs.offer_scraper.nodes.offer_scraper_node import offer_scraper_node


def route_after_scraping(
    state: GraphState,
) -> str:
    if state.conditional_edge in [
        OfferScraperConstants.EMPTY_INPUT_EDGE,
        OfferScraperConstants.INVALID_URL_EDGE,
    ]:
        return NodeNames.INITIAL_HITL_NODE

    if state.conditional_edge in [OfferScraperConstants.SCRAPING_ERROR_EDGE]:
        return END

    return NodeNames.GENERATE_QUESTION_NODE


def route_after_generating_questions(
    state: GraphState,
) -> str:
    if state.conditional_edge in [OfferScraperConstants.OFFER_CONTEXT_NOT_FOUND_EDGE]:
        return NodeNames.INITIAL_HITL_NODE

    if state.conditional_edge in [OfferScraperConstants.GENERATE_QUESTION_ERROR_EDGE]:
        return END

    return NodeNames.USER_INPUT_ANALYSIS_HITL_NODE


def build_offer_scraper_subgraph(builder: StateGraph):
    builder.add_node(NodeNames.OFFER_SCRAPER_NODE, offer_scraper_node)
    builder.add_node(NodeNames.GENERATE_QUESTION_NODE, generate_question_node)
    builder.add_conditional_edges(
        NodeNames.OFFER_SCRAPER_NODE,
        route_after_scraping,
        [NodeNames.GENERATE_QUESTION_NODE, NodeNames.INITIAL_HITL_NODE, END],
    )

    builder.add_conditional_edges(
        NodeNames.GENERATE_QUESTION_NODE,
        route_after_generating_questions,
        [NodeNames.INITIAL_HITL_NODE, END, NodeNames.USER_INPUT_ANALYSIS_HITL_NODE],
    )
