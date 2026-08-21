from app.graph.core.config import GraphState


def start_node(state: GraphState):
    return {
        "assistant_message": "Hello, how can I help you today?",
        "node_name": "start_node",
    }
