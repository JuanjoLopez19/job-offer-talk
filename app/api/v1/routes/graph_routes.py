from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Body, Header, Request, Response
from starlette.concurrency import run_in_threadpool

from app.api.v1.connection_manager import connection_manager
from app.core.logger import get_logger
from app.graph.core.config import GraphState
from app.graph.manager import GraphManager
from app.services.tts.common.base import BaseTTS
from app.shared.models import MAX_SESSION_ID_LENGTH, GraphInput, GraphOutput
from app.shared.tools import is_tts_response

graph_router = APIRouter(tags=["Graph"])

graph_manager = GraphManager()
THREAD_ID_HEADER = "X-Thread-ID"


@graph_router.post("/", response_model_exclude_defaults=True)
async def get_graph(
    graph_input: Annotated[GraphInput | str, Body()],
    request: Request,
    response: Response,
    thread_id: Annotated[
        str | None,
        Header(
            alias=THREAD_ID_HEADER,
            min_length=1,
            max_length=MAX_SESSION_ID_LENGTH,
        ),
    ] = None,
) -> GraphOutput:
    if isinstance(graph_input, GraphInput):
        resolved_thread_id = thread_id or graph_input.session_id
    else:
        resolved_thread_id = thread_id or str(uuid4())

    result = await run_in_threadpool(
        graph_manager.invoke,
        graph_input,
        thread_id=resolved_thread_id,
    )
    response.headers[THREAD_ID_HEADER] = resolved_thread_id

    if (
        isinstance(result, GraphState)
        and is_tts_response(result)
        and connection_manager.is_connected(result.session_id)
    ):
        assistant_message = result.assistant_message
        if assistant_message is None:
            get_logger().warn("The assistant message is empty, skipping TTS response")
        else:
            tts: BaseTTS = request.app.state.tts
            audio = await run_in_threadpool(tts.generate_bytes, assistant_message)
            await connection_manager.send_tts_message(
                result.session_id, assistant_message, audio
            )

    result_data = result.model_dump() if isinstance(result, GraphState) else result
    return GraphOutput.model_validate(result_data)
