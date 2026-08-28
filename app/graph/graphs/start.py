from app.graph.common.constants import NodeNames
from app.graph.common.messages import WELCOME_MESSAGE
from app.graph.core.config import GraphState


def start_node(state: GraphState):
    return {
        "assistant_message": "\n".join(WELCOME_MESSAGE),
        "node_name": NodeNames.INITIAL_NODE,
    }
