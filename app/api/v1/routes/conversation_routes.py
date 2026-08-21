from fastapi import APIRouter
from fastapi.websockets import WebSocket, WebSocketDisconnect

conversation_router = APIRouter(tags=["Conversation"])


@conversation_router.websocket("/{conversation_id}")
async def get_conversation(websocket: WebSocket, conversation_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            print(data)
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    return {"message": conversation_id}
