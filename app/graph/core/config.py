from pydantic import BaseModel


class GraphState(BaseModel):
    session_id: str

    assistant_message: str | None = None
