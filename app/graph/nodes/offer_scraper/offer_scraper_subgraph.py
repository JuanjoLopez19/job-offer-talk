from functools import partial

from langgraph.graph import StateGraph

from app.graph.nodes.common.hitl_node import human_node
from app.graph.nodes.offer_scraper.nodes.offer_scraper_node import offer_scraper_node


def build_offer_scraper_subgraph(builder: StateGraph):
    hitl_node = partial(human_node, node_name="job_offer_parser_hitl_node")

    builder.add_node("job_offer_parser_hitl_node", hitl_node)

    builder.add_node("offer_scraper_node", offer_scraper_node)

    builder.add_edge("job_offer_parser_hitl_node", "offer_scraper_node")
