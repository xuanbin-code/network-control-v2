"""API v1 路由聚合"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    health,
    test_message,
    status,
    config,
    mode,
)

api_router = APIRouter(prefix="/api")

api_router.include_router(health.router)
api_router.include_router(test_message.router)
api_router.include_router(status.router)
api_router.include_router(config.router)
api_router.include_router(mode.router)
