from app.graph.common.constants import GraphStateFields, NodeNames
from app.graph.common.messages import WELCOME_MESSAGE
from app.graph.core.config import GraphState


def start_node(state: GraphState):
    return {
        GraphStateFields.ASSISTANT_MESSAGE: WELCOME_MESSAGE,
        GraphStateFields.NODE_NAME: NodeNames.INITIAL_NODE,
    }
