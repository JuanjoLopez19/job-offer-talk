from functools import partial

from langgraph.graph import StateGraph

from app.graph.common.constants import NodeNames
from app.graph.graphs.common.hitl_node import human_node
from app.graph.graphs.welcome.nodes.start import start_node


def build_welcome_subgraph(builder: StateGraph):
    hitl_node = partial(human_node, node_name=NodeNames.INITIAL_HITL_NODE)
    builder.add_node(NodeNames.INITIAL_HITL_NODE, hitl_node)

    builder.add_node(NodeNames.INITIAL_NODE, start_node)

    builder.add_edge(NodeNames.INITIAL_NODE, NodeNames.INITIAL_HITL_NODE)

    builder.add_edge(NodeNames.INITIAL_HITL_NODE, NodeNames.OFFER_SCRAPER_NODE)
