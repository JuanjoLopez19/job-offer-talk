from typing import Annotated

from fastapi import APIRouter, Path
from fastapi.websockets import WebSocket, WebSocketDisconnect
from pydantic import ValidationError
from starlette.concurrency import run_in_threadpool

from app.api.v1.connection_manager import connection_manager
from app.api.v1.conversation_protocol import (
    VoiceMessageMetadata,
    validate_audio_size,
)
from app.api.v1.routes.graph_routes import graph_manager
from app.core.logger import get_logger
from app.graph.core.config import GraphState
from app.services.stt.common.base import BaseSTT
from app.services.tts.common.base import BaseTTS
from app.shared.models import MAX_SESSION_ID_LENGTH, GraphInput
from app.shared.tools import is_tts_response

conversation_router = APIRouter(tags=["Conversation"])


async def send_voice_error(
    websocket: WebSocket, message: str, *, turn_id: str | None = None
) -> None:
    payload = {"event": "error", "message": message}
    if turn_id is not None:
        payload["turn_id"] = turn_id
    await websocket.send_json(payload)


@conversation_router.websocket("/{session_id}")
async def get_conversation(
    websocket: WebSocket,
    session_id: Annotated[str, Path(min_length=1, max_length=MAX_SESSION_ID_LENGTH)],
) -> None:
    await connection_manager.connect(session_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            try:
                metadata = VoiceMessageMetadata.model_validate(data)
            except ValidationError:
                await send_voice_error(websocket, "Metadatos de audio no válidos")
                await websocket.close(code=1008)
                return

            audio = await websocket.receive_bytes()
            try:
                validate_audio_size(audio)
            except ValueError as error:
                await send_voice_error(websocket, str(error), turn_id=metadata.turn_id)
                continue

            try:
                stt: BaseSTT = websocket.app.state.stt
                user_message = await run_in_threadpool(stt.transcribe_bytes, audio)
                get_logger().info(f"User message: {user_message}")
                await websocket.send_json(
                    {
                        "event": "user_message",
                        "message": user_message,
                        "turn_id": metadata.turn_id,
                    }
                )
                graph_response = await run_in_threadpool(
                    graph_manager.invoke,
                    GraphInput(session_id=session_id, user_input=user_message),
                    thread_id=session_id,
                )
                if isinstance(graph_response, GraphState) and is_tts_response(
                    graph_response
                ):
                    assistant_message = graph_response.assistant_message
                    if assistant_message is None:
                        get_logger().warn(
                            "The assistant message is empty, skipping TTS response"
                        )
                    else:
                        tts: BaseTTS = websocket.app.state.tts
                        response_audio = await run_in_threadpool(
                            tts.generate_bytes, assistant_message
                        )

                        await connection_manager.send_tts_message(
                            session_id,
                            assistant_message,
                            response_audio,
                            turn_id=metadata.turn_id,
                        )
                elif (
                    isinstance(graph_response, GraphState)
                    and graph_response.assistant_message
                ):
                    await websocket.send_json(
                        {
                            "event": "assistant_message",
                            "message": graph_response.assistant_message,
                            "turn_id": metadata.turn_id,
                        }
                    )
                else:
                    await send_voice_error(
                        websocket,
                        "No se recibió la respuesta del asistente",
                        turn_id=metadata.turn_id,
                    )
            except WebSocketDisconnect:
                raise
            except Exception:
                get_logger(__name__).exception("Error processing voice message")
                await send_voice_error(
                    websocket,
                    "No se pudo procesar el mensaje de voz",
                    turn_id=metadata.turn_id,
                )
    except WebSocketDisconnect:
        pass
    finally:
        connection_manager.disconnect(session_id, websocket)
