from app.graph.core.config import GraphState


def temp_node(state: GraphState):
    return {
        "assistant_message": f"Hello, how can I help you todayyyyyyyyyy? {state.user_input}",
        "node_name": "temp_node",
    }
