from app.graph.common.constants import NodeNames
from app.graph.core.config import GraphState
from app.graph.graphs.offer_interview.common.constants import OfferInterviewConstants
from app.graph.graphs.offer_interview.nodes.ask_for_new_question_node import (
    ask_for_new_question_node,
)


def test_ask_for_new_question_returns_the_follow_up_prompt() -> None:
    result = ask_for_new_question_node(GraphState(session_id="thread-1"))

    assert result["node_name"] == NodeNames.ASK_FOR_NEW_QUESTION_NODE
    assert result["conditional_edge"] == OfferInterviewConstants.NEXT_QUESTION_EDGE
    assert (
        result["assistant_message"] == "¿Quieres que te ayude a analizar la respuesta?"
    )
