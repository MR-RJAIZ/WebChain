"""
WebChain FastAPI Application
-----------------------------

Entry point for the WebChain backend.

Architecture:

Browser/Frontend
   ↓
FastAPI (this file)
   ↓
api_router
   ├── POST /publish         → full deploy (IPFS + blockchain)
   ├── POST /upload          → file upload only
   ├── GET  /website/{id}    → get website metadata
   ├── GET  /website/{id}/verify → verify CID
   ├── PUT  /website/{id}    → update CID (owner only)
   └── GET  /health          → service health check

To start the backend:
    cd backend
    uvicorn app.main:app --reload

API documentation:
    http://127.0.0.1:8000/docs
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router


# Configure logging so we can see useful server-side messages.
# IMPORTANT: Private keys and secrets are NEVER logged.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


# =========================================================
# APPLICATION
# =========================================================

app = FastAPI(
    title="WebChain API",
    version="1.0.0",
    description=(
        "WebChain decentralized website hosting API.\n\n"
        "Deploy static websites to IPFS and register them "
        "on the blockchain with a single POST /publish call."
    ),
)


# =========================================================
# CORS
# =========================================================

# Allow requests from the Vite frontend dev server.
# In production, replace '*' with your actual frontend domain.

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# API ROUTES
# =========================================================

app.include_router(api_router)


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    """
    Root endpoint — confirms the backend is running.
    """

    return {
        "message": "WebChain backend is running",
        "version": "1.0.0",
        "docs": "/docs",
    }