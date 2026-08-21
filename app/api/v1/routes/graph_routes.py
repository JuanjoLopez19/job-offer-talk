from typing import Annotated, Any
from uuid import uuid4

from fastapi import APIRouter, Header, HTTPException, Response

from app.graph.manager import GraphManager

graph_router = APIRouter(tags=["Graph"])

graph_manager = GraphManager()
THREAD_ID_HEADER = "X-Thread-ID"


@graph_router.post("/")
async def get_graph(
    graph_input: dict[str, Any],
    response: Response,
    thread_id: Annotated[str | None, Header(alias=THREAD_ID_HEADER)] = None,
) -> Any:
    if not graph_input:
        raise HTTPException(status_code=400, detail="Input is required")

    resolved_thread_id = thread_id or str(uuid4())
    result = graph_manager.invoke(graph_input, thread_id=resolved_thread_id)
    response.headers[THREAD_ID_HEADER] = resolved_thread_id
    return result
