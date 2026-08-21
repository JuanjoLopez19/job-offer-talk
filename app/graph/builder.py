from functools import partial

from langgraph.constants import END
from langgraph.graph import StateGraph

from app.graph.core.config import GraphState
from app.graph.nodes.common.hitl_node import human_node
from app.graph.nodes.offer_scraper.offer_scraper_subgraph import (
    build_offer_scraper_subgraph,
)
from app.graph.nodes.start import start_node
from app.graph.nodes.temp import temp_node

hitl_node = partial(human_node, node_name="initial_hitl_node")
base_builder = StateGraph(GraphState)
base_builder.set_entry_point("start")

build_offer_scraper_subgraph(base_builder)


base_builder.add_node("start", start_node)
base_builder.add_node("initial_hitl_node", hitl_node)

base_builder.add_edge("start", "job_offer_parser_hitl_node")
base_builder.add_edge("offer_scraper_node", "initial_hitl_node")
base_builder.add_edge("initial_hitl_node", "temp")


base_builder.add_node("temp", temp_node)
base_builder.add_edge("temp", END)
