from typing import Annotated, Any
from uuid import uuid4

from fastapi import APIRouter, Body, Response

from app.graph.manager import GraphManager
from app.shared.models import GraphInput

graph_router = APIRouter(tags=["Graph"])

graph_manager = GraphManager()
THREAD_ID_HEADER = "X-Thread-ID"


@graph_router.post("/")
async def get_graph(
    graph_input: Annotated[GraphInput, Body()],
    response: Response,
) -> Any:

    resolved_thread_id = graph_input.session_id or str(uuid4())
    result = graph_manager.invoke(graph_input, thread_id=resolved_thread_id)
    return result
