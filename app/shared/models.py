from uuid import uuid4

from pydantic import BaseModel, Field


class GraphInput(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    user_input: str
