from langgraph.types import interrupt

from app.graph.core.config import GraphState


def human_node(state: GraphState, node_name: str):

    user_input = interrupt("hello")

    return {"user_input": user_input, "node_name": node_name}
