from pathlib import Path
from uuid import uuid4
import shutil
import json

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.db_models import DeploymentDB
from app.models.deployment import Deployment


UPLOAD_DIR = Path("uploads")
DEPLOYMENTS_DIR = Path("deployments")


def get_deployment(deployment_id: str):
    db: Session = SessionLocal()

    try:
        deployment = db.query(DeploymentDB).filter(
            DeploymentDB.deployment_id == deployment_id
        ).first()

        if deployment is None:
            return None

        return Deployment(
            deployment_id=deployment.deployment_id,
            status=deployment.status,
            message=deployment.message,
            files=json.loads(deployment.files),
        )
    finally:
        db.close()


def get_deployments():
    db: Session = SessionLocal()

    try:
        deployments = db.query(DeploymentDB).all()

        return [
            Deployment(
                deployment_id=deployment.deployment_id,
                status=deployment.status,
                message=deployment.message,
                files=json.loads(deployment.files),
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

    deployment_dir = DEPLOYMENTS_DIR / deployment_id
    deployment_dir.mkdir(parents=True, exist_ok=True)

    for file in files:
        shutil.copy2(file, deployment_dir / file.name)

    deployment = Deployment(
        deployment_id=deployment_id,
        status="deployed",
        message="Website deployment simulated successfully",
        files=[file.name for file in files],
    )

    db: Session = SessionLocal()

    try:
        db_deployment = DeploymentDB(
            deployment_id=deployment.deployment_id,
            status=deployment.status,
            message=deployment.message,
            files=json.dumps(deployment.files),
        )

        db.add(db_deployment)
        db.commit()
    finally:
        db.close()

    return deployment