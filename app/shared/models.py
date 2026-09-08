from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

MAX_SESSION_ID_LENGTH = 128


class GraphInput(BaseModel):
    session_id: str = Field(
        default_factory=lambda: str(uuid4()),
        min_length=1,
        max_length=MAX_SESSION_ID_LENGTH,
    )
    user_input: str | None = None


class GraphOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    assistant_message: str
    user_input: str | None = None
    node_name: str = "unknown"
    conditional_edge: str | None = None
    is_tts_message: bool = False
    session_id: str = ""
    job_offer_context: dict[str, Any] | None = None
    job_offer_generated_info: dict[str, Any] | None = None
