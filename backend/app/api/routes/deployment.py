from pathlib import Path

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, RedirectResponse
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, RedirectResponse

from app.models.deployment import (
    Deployment,
    DeploymentFailure,
    MessageResponse,
)
from app.services.deployment_service import (
    deploy_website,
    get_deployment as get_deployment_service,
    get_deployments,
    process_deployment,
    delete_deployment,
)

router = APIRouter()


@router.post(
    "/deploy",
    response_model=Deployment | DeploymentFailure
)
async def deploy(background_tasks: BackgroundTasks):
    deployment = deploy_website()

    if isinstance(deployment, Deployment):
        background_tasks.add_task(
            process_deployment,
            deployment.deployment_id
        )

    return deployment


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

    if deployment.status != "deployed":
        raise HTTPException(
            status_code=409,
            detail="Deployment is not ready"
        )

    return RedirectResponse(
        url=f"/site/{deployment_id}/"
    )


@router.get("/site/{deployment_id}/")
async def serve_website_index(deployment_id: str):
    deployment = get_deployment_service(deployment_id)

    if deployment is None:
        raise HTTPException(
            status_code=404,
            detail="Deployment not found"
        )

    if deployment.status != "deployed":
        raise HTTPException(
            status_code=409,
            detail="Deployment is not ready"
        )

    index_file = (
        Path("deployments")
        / deployment_id
        / "index.html"
    )

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

    if deployment.status != "deployed":
        raise HTTPException(
            status_code=409,
            detail="Deployment is not ready"
        )

    deployment_dir = (
        Path("deployments") / deployment_id
    ).resolve()

    requested_file = (
        deployment_dir / file_path
    ).resolve()

    try:
        requested_file.relative_to(deployment_dir)
    except ValueError:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

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


@router.delete(
    "/deploy/{deployment_id}",
    response_model=MessageResponse
)
async def remove_deployment(deployment_id: str):
    deleted = delete_deployment(deployment_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Deployment not found"
        )

    return {
        "message": "Deployment deleted successfully"
    }