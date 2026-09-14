"""
API Router
----------

Application ke different API routes ko ek single router
ke andar register karta hai.

Architecture:

FastAPI
   ↓
api_router
   ├── /health          GET  — service health check
   ├── /publish         POST — full deploy (files → IPFS → blockchain)
   ├── /upload          POST — file upload only (returns deployment_id)
   ├── /website/{id}    GET  — get website metadata from blockchain
   ├── /website/{id}/verify  GET  — verify CID against blockchain
   └── /website/{id}    PUT  — update CID (owner only)
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

# Health check
api_router.include_router(health.router)

# Full publish flow: files → IPFS → blockchain → website_id
api_router.include_router(publish.router)

# File upload only (no IPFS/blockchain step)
api_router.include_router(upload.router)

# Deployment simulation (legacy, kept for compatibility)
api_router.include_router(deployment.router)

# Website metadata retrieval, verification, and update
api_router.include_router(website.router)