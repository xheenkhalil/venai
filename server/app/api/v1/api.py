from fastapi import APIRouter
from app.api.v1.endpoints import auth, procurement_requests, vendors, agents, chat, analytics

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(procurement_requests.router, prefix="/procurement-requests", tags=["procurement_requests"])
api_router.include_router(vendors.router, prefix="/vendors", tags=["vendors"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
