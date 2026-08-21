from pydantic import BaseModel


class GraphState(BaseModel):
    session_id: str

    assistant_message: str | None = None
    user_input: str | None = None
    node_name: str = "initial_node"
