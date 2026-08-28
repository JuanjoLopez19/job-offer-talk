from fastapi import APIRouter
from fastapi.websockets import WebSocket, WebSocketDisconnect

from app.api.v1.connection_manager import connection_manager

conversation_router = APIRouter(tags=["Conversation"])


@conversation_router.websocket("/{session_id}")
async def get_conversation(websocket: WebSocket, session_id: str) -> None:
    await connection_manager.connect(session_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        pass
    finally:
        connection_manager.disconnect(session_id, websocket)
