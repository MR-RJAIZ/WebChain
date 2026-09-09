"""
API Router
----------

Application ke different API routes ko ek single router
ke andar register karta hai.

Architecture:

FastAPI
   ↓
api_router
   ├── health
   ├── upload
   └── deployment
"""

from fastapi import APIRouter

from app.api.routes import (
    health,
    upload,
    deployment,
    website,
    publish,
)


api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(upload.router)
api_router.include_router(deployment.router)
api_router.include_router(website.router)
api_router.include_router(publish.router)


# =============================================================
# REGISTER ROUTES
# =============================================================

# Health check endpoint
api_router.include_router(
    health.router
)


# Website upload endpoint
#
# POST /upload

api_router.include_router(
    upload.router
)


# Website deployment endpoint
#
# POST /deploy

api_router.include_router(
    deployment.router
)