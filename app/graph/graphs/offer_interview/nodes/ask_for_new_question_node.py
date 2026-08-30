from app.graph.common.constants import GraphStateFields, NodeNames
from app.graph.core.config import GraphState
from app.graph.graphs.offer_interview.common.constants import OfferInterviewConstants


def ask_for_new_question_node(state: GraphState):
    # TODO: When the logic is thought
    return {
        GraphStateFields.ASSISTANT_MESSAGE: "¿Quieres que te ayude a analizar la respuesta?",
        GraphStateFields.NODE_NAME: NodeNames.ASK_FOR_NEW_QUESTION_NODE,
        GraphStateFields.CONDITIONAL_EDGE: OfferInterviewConstants.NEXT_QUESTION_EDGE,
    }
