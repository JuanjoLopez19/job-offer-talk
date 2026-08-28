from typing import Annotated, Any
from uuid import uuid4

from fastapi import APIRouter, Body, Header, Request, Response
from starlette.concurrency import run_in_threadpool

from app.api.v1.connection_manager import connection_manager
from app.graph.core.config import GraphState
from app.graph.manager import GraphManager
from app.services.tts.common.base import BaseTTS
from app.shared.models import GraphInput

graph_router = APIRouter(tags=["Graph"])

graph_manager = GraphManager()
THREAD_ID_HEADER = "X-Thread-ID"


@graph_router.post("/")
async def get_graph(
    graph_input: Annotated[GraphInput | str, Body()],
    request: Request,
    response: Response,
    thread_id: Annotated[str | None, Header(alias=THREAD_ID_HEADER)] = None,
) -> Any:
    if isinstance(graph_input, GraphInput):
        resolved_thread_id = thread_id or graph_input.session_id
    else:
        resolved_thread_id = thread_id or str(uuid4())

    result = graph_manager.invoke(graph_input, thread_id=resolved_thread_id)
    response.headers[THREAD_ID_HEADER] = resolved_thread_id

    if (
        isinstance(result, GraphState)
        and result.is_tts_message
        and result.assistant_message
        and connection_manager.is_connected(result.session_id)
    ):
        tts: BaseTTS = request.app.state.tts
        audio = await run_in_threadpool(tts.generate_wav, result.assistant_message)
        await connection_manager.send_tts_message(
            result.session_id, result.assistant_message, audio
        )

    return result
