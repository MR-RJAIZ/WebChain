from fastapi import APIRouter
from app.services.deployment_service import deploy_website

router = APIRouter()


@router.post("/deploy")
async def deploy():
    return deploy_website()