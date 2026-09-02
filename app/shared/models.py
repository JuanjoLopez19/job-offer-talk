from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class GraphInput(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    user_input: str | None = None


class GraphOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    assistant_message: str
    user_input: str | None = None
    node_name: str
    conditional_edge: str | None = None
    is_tts_message: bool = False
    session_id: str
