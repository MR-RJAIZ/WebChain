from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.models.deployment import Deployment, DeploymentFailure
from app.services.deployment_service import (
    deploy_website,
    get_deployment as get_deployment_service,
    get_deployments,
    process_deployment,
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

    index_file = Path("deployments") / deployment_id / "index.html"

    if not index_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Website index.html not found"
        )

    return FileResponse(index_file)


@router.get("/site/{deployment_id}/{file_path:path}")
async def serve_deployment_file(
    deployment_id: str,
    file_path: str
):
    deployment = get_deployment_service(deployment_id)

    if deployment is None:
        raise HTTPException(
            status_code=404,
            detail="Deployment not found"
        )

    deployment_dir = Path("deployments") / deployment_id
    requested_file = deployment_dir / file_path

    if not requested_file.exists() or not requested_file.is_file():
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    return FileResponse(requested_file)
@router.post(
    "/deploy/{deployment_id}/process",
    response_model=Deployment
)
async def process(deployment_id: str):
    deployment = process_deployment(deployment_id)

    if deployment is None:
        raise HTTPException(
            status_code=404,
            detail="Deployment not found"
        )

    return deployment