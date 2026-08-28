from langgraph.types import interrupt

from app.graph.core.config import GraphState


def human_node(state: GraphState, node_name: str):
    user_input = interrupt(
        {
            "message": state.assistant_message,
            "node_name": node_name,
        }
    )

    return {"user_input": user_input, "node_name": node_name}
