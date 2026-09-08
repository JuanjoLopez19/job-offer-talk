from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field


def conversation_history_reducer(
    current: list[dict[str, str]],
    update: list[dict[str, str]] | None,
) -> list[dict[str, str]]:
    if update is None:
        return []

    return current + update


class GraphState(BaseModel):
    model_config = ConfigDict(extra="allow")

    session_id: str

    assistant_message: str | None = None
    user_input: str | None = None
    node_name: str = "initial_node"
    conditional_edge: str | None = None

    job_offer_context: dict[str, Any] | None = None
    job_offer_generated_info: dict[str, Any] | None = None
    conversation_history: Annotated[
        list[dict[str, str]], conversation_history_reducer
    ] = Field(default_factory=list)
    is_tts_message: bool = True
    counter_questions: int = 0
