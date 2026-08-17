from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.models.deployment import Deployment, DeploymentFailure
from app.services.deployment_service import (
    deploy_website,
    get_deployment as get_deployment_service,
    get_deployments,
)


router = APIRouter()


@router.post(
    "/deploy",
    response_model=Deployment | DeploymentFailure
)
async def deploy():
    return deploy_website()


@router.get(
    "/deploy/{deployment_id}",
    response_model=Deployment
)
async def get_deployment(deployment_id: str):
    deployment = get_deployment_service(deployment_id)

    if deployment is None:
        raise HTTPException(
            status_code=404,
            detail="Deployment not found"
        )

    return deployment


@router.get(
    "/deployments",
    response_model=list[Deployment]
)
async def get_all_deployments():
    return get_deployments()


@router.get("/site/{deployment_id}")
async def serve_website(deployment_id: str):
    deployment = get_deployment_service(deployment_id)

    if deployment is None:
        raise HTTPException(
            status_code=404,
            detail="Deployment not found"
        )

    index_file = "uploads/index.html"

    return FileResponse(index_file)