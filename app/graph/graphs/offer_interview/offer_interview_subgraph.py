from functools import partial

from langgraph.constants import END
from langgraph.graph.state import StateGraph

from app.graph.common.constants import NodeNames
from app.graph.core.config import GraphState
from app.graph.graphs.common.hitl_node import human_node
from app.graph.graphs.offer_interview.common.constants import OfferInterviewConstants
from app.graph.graphs.offer_interview.nodes.user_input_analysis_node import (
    user_input_analysis_node,
)


def route_after_analysis(
    state: GraphState,
) -> str:
    if state.conditional_edge in [
        OfferInterviewConstants.OFFER_CONTEXT_NOT_FOUND_EDGE,
        OfferInterviewConstants.ANALYSIS_ERROR_EDGE,
    ]:
        return END

    if state.conditional_edge in [
        OfferInterviewConstants.NOT_IN_CONTEXT_EDGE,
        OfferInterviewConstants.NOT_COMPLETE_AND_COHERENT_EDGE,
        OfferInterviewConstants.NEXT_QUESTION_EDGE,
    ]:
        return NodeNames.USER_INPUT_ANALYSIS_HITL_NODE

    if state.conditional_edge == OfferInterviewConstants.NOT_CORRECT_EDGE:
        return END

    return NodeNames.USER_INPUT_ANALYSIS_HITL_NODE


def build_offer_interview_subgraph(builder: StateGraph):
    builder.add_node(NodeNames.USER_INPUT_ANALYSIS_NODE, user_input_analysis_node)

    hitl_node = partial(
        human_node,
        node_name=NodeNames.USER_INPUT_ANALYSIS_HITL_NODE,
        add_to_conversation_history=True,
    )
    builder.add_node(NodeNames.USER_INPUT_ANALYSIS_HITL_NODE, hitl_node)

    builder.add_conditional_edges(
        NodeNames.USER_INPUT_ANALYSIS_NODE,
        route_after_analysis,
        [NodeNames.USER_INPUT_ANALYSIS_HITL_NODE, END],
    )

    builder.add_edge(
        NodeNames.USER_INPUT_ANALYSIS_HITL_NODE, NodeNames.USER_INPUT_ANALYSIS_NODE
    )
