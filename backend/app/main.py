import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.database import Base, engine
from app.db_models import DeploymentDB


load_dotenv()


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="WebChain API",
    version="0.1.0"
)


frontend_origin = os.getenv(
    "FRONTEND_ORIGIN",
    "http://localhost:3000"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router)


@app.get("/")
def root():
    return {
        "message": "WebChain backend is running"
    }