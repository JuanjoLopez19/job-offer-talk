from fastapi import APIRouter

from app.api.v1.routes.conversation_routes import conversation_router
from app.api.v1.routes.graph_routes import graph_router

main_router = APIRouter(prefix="/v1")
main_router.include_router(graph_router, prefix="/graph")
main_router.include_router(conversation_router, prefix="/conversation")
