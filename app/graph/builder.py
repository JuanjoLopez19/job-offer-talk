from langgraph.graph import StateGraph

from app.graph.common.constants import NodeNames
from app.graph.core.config import GraphState
from app.graph.graphs.offer_interview.offer_interview_subgraph import (
    build_offer_interview_subgraph,
)
from app.graph.graphs.offer_scraper.offer_scraper_subgraph import (
    build_offer_scraper_subgraph,
)
from app.graph.graphs.welcome.welcome_subgraph import build_welcome_subgraph

base_builder = StateGraph(GraphState)
base_builder.set_entry_point(NodeNames.INITIAL_NODE)


build_welcome_subgraph(base_builder)
build_offer_scraper_subgraph(base_builder)
build_offer_interview_subgraph(base_builder)
