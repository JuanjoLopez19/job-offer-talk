from operator import add
from typing import Annotated, Any

from pydantic import BaseModel, Field


class GraphState(BaseModel):
    session_id: str

    assistant_message: str | None = None
    user_input: str | None = None
    node_name: str = "initial_node"
    conditional_edge: str | None = None

    job_offer_context: dict[str, Any] | None = None
    job_offer_generated_info: dict[str, Any] | None = None
    conversation_history: Annotated[list[dict[str, str]], add] = Field(
        default_factory=list
    )
    is_tts_message: bool = False
