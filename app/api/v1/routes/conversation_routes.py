from fastapi import APIRouter
from fastapi.websockets import WebSocket, WebSocketDisconnect
from starlette.concurrency import run_in_threadpool

from app.api.v1.connection_manager import connection_manager
from app.services.stt.common.base import BaseSTT

conversation_router = APIRouter(tags=["Conversation"])


def is_allowed_event(event: str | None) -> bool:
    return event in ["user_message"]


@conversation_router.websocket("/{session_id}")
async def get_conversation(websocket: WebSocket, session_id: str) -> None:
    await connection_manager.connect(session_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            event: str | None = data.get("event")
            if not is_allowed_event(event):
                continue

            if event == "user_message":
                audio = await websocket.receive_bytes()
                stt: BaseSTT = websocket.app.state.stt
                user_message = await run_in_threadpool(stt.transcribe_bytes, audio)
                await websocket.send_json(
                    {
                        "event": "assistant_message",
                        "message": user_message,
                    }
                )
    except WebSocketDisconnect:
        pass
    finally:
        connection_manager.disconnect(session_id, websocket)
