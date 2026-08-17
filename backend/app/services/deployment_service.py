from pathlib import Path
from uuid import uuid4
import json

from app.database import SessionLocal
from app.db_models import DeploymentDB
from app.models.deployment import Deployment


UPLOAD_DIR = Path("uploads")


def get_deployment(deployment_id: str):
    db = SessionLocal()

    try:
        deployment = (
            db.query(DeploymentDB)
            .filter(DeploymentDB.deployment_id == deployment_id)
            .first()
        )

        if deployment is None:
            return None

        return Deployment(
            deployment_id=deployment.deployment_id,
            status=deployment.status,
            message=deployment.message,
            files=json.loads(deployment.files)
        )
    finally:
        db.close()


def get_deployments():
    db = SessionLocal()

    try:
        deployments = db.query(DeploymentDB).all()

        return [
            Deployment(
                deployment_id=deployment.deployment_id,
                status=deployment.status,
                message=deployment.message,
                files=json.loads(deployment.files)
            )
            for deployment in deployments
        ]
    finally:
        db.close()


def deploy_website():
    files = [
        file for file in UPLOAD_DIR.iterdir()
        if file.name != ".gitkeep"
    ]

    if not files:
        return {
            "status": "failed",
            "message": "No website files found"
        }

    deployment_id = str(uuid4())

    deployment = DeploymentDB(
        deployment_id=deployment_id,
        status="deployed",
        message="Website deployment simulated successfully",
        files=json.dumps([file.name for file in files])
    )

    db = SessionLocal()

    try:
        db.add(deployment)
        db.commit()
        db.refresh(deployment)
    finally:
        db.close()

    return Deployment(
        deployment_id=deployment.deployment_id,
        status=deployment.status,
        message=deployment.message,
        files=json.loads(deployment.files)
    )