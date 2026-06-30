"""API v1 路由聚合"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    health,
    server,
    machines,
    network,
    scan,
    rules,
    browsing,
    settings,
    test,
)

api_router = APIRouter(prefix="/api")

api_router.include_router(health.router)
api_router.include_router(server.router)
api_router.include_router(machines.router)
api_router.include_router(network.router)
api_router.include_router(scan.router)
api_router.include_router(rules.router)
api_router.include_router(browsing.router)
api_router.include_router(settings.router)
api_router.include_router(test.router)
