import pytest
from langgraph.constants import END

from app.graph.common.constants import NodeNames
from app.graph.core.config import GraphState
from app.graph.graphs.offer_interview.common.constants import OfferInterviewConstants
from app.graph.graphs.offer_interview.offer_interview_subgraph import (
    route_after_analysis,
    route_after_ask_new_question,
)


@pytest.mark.parametrize(
    ("edge", "destination"),
    [
        (OfferInterviewConstants.OFFER_CONTEXT_NOT_FOUND_EDGE, END),
        (OfferInterviewConstants.ANALYSIS_ERROR_EDGE, END),
        (OfferInterviewConstants.END_EDGE, END),
        (
            OfferInterviewConstants.NOT_IN_CONTEXT_EDGE,
            NodeNames.USER_INPUT_ANALYSIS_HITL_NODE,
        ),
        (
            OfferInterviewConstants.NOT_COMPLETE_AND_COHERENT_EDGE,
            NodeNames.USER_INPUT_ANALYSIS_HITL_NODE,
        ),
        (
            OfferInterviewConstants.NEXT_QUESTION_EDGE,
            NodeNames.USER_INPUT_ANALYSIS_HITL_NODE,
        ),
        (
            OfferInterviewConstants.NOT_CORRECT_EDGE,
            NodeNames.ASK_FOR_NEW_QUESTION_HITL_NODE,
        ),
    ],
)
def test_route_after_analysis_selects_the_expected_destination(
    edge: str, destination: str
) -> None:
    assert (
        route_after_analysis(GraphState(session_id="thread-1", conditional_edge=edge))
        == destination
    )


@pytest.mark.parametrize(
    ("edge", "destination"),
    [
        (OfferInterviewConstants.OFFER_CONTEXT_NOT_FOUND_EDGE, END),
        (OfferInterviewConstants.ANALYSIS_ERROR_EDGE, END),
        (END, END),
        (
            OfferInterviewConstants.CONTINUE_EDGE,
            NodeNames.USER_INPUT_ANALYSIS_HITL_NODE,
        ),
        (
            OfferInterviewConstants.REPEAT_EDGE,
            NodeNames.ASK_FOR_NEW_QUESTION_HITL_NODE,
        ),
    ],
)
def test_route_after_ask_new_question_selects_the_expected_destination(
    edge: str, destination: str
) -> None:
    assert (
        route_after_ask_new_question(
            GraphState(session_id="thread-1", conditional_edge=edge)
        )
        == destination
    )
