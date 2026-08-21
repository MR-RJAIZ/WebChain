from app.services.ipfs_service import upload_to_ipfs
from pathlib import Path
from uuid import uuid4
import json
import shutil

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.db_models import DeploymentDB
from app.models.deployment import Deployment, DeploymentStatus


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
            status=DeploymentStatus(deployment.status),
            message=deployment.message,
            files=json.loads(deployment.files),
	    cid=deployment.cid,
	    transaction_hash=deployment.transaction_hash,
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
                status=DeploymentStatus(deployment.status),
                message=deployment.message,
                files=json.loads(deployment.files),
		cid=deployment.cid,
	        transaction_hash=deployment.transaction_hash,
            )
            for deployment in deployments
        ]
    finally:
        db.close()


def deploy_website():
    files = [
        file
        for file in UPLOAD_DIR.rglob("*")
        if file.is_file() and file.name != ".gitkeep"
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
        relative_path = file.relative_to(UPLOAD_DIR)
        destination = deployment_dir / relative_path

        destination.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        shutil.copy2(file, destination)

    deployment = Deployment(
        deployment_id=deployment_id,
        status=DeploymentStatus.PENDING,
        message="Deployment created and waiting for processing",
        files=[
            file.relative_to(UPLOAD_DIR).as_posix()
            for file in files
        ],
        cid=None,
        transaction_hash=None,
    )

    db: Session = SessionLocal()

    try:
        db_deployment = DeploymentDB(
            deployment_id=deployment.deployment_id,
            status=deployment.status.value,
            message=deployment.message,
            files=json.dumps(deployment.files),
            cid=deployment.cid,
            transaction_hash=deployment.transaction_hash,
        )

        db.add(db_deployment)
        db.commit()

    finally:
        db.close()

    return deployment


def process_deployment(deployment_id: str):
    db: Session = SessionLocal()

    try:
        deployment = db.query(DeploymentDB).filter(
            DeploymentDB.deployment_id == deployment_id
        ).first()

        if deployment is None:
            return None

        try:
            deployment_dir = DEPLOYMENTS_DIR / deployment_id
            index_file = deployment_dir / "index.html"

            if not deployment_dir.exists():
                raise FileNotFoundError(
                    "Deployment directory not found"
                )

            if not index_file.exists():
                raise FileNotFoundError(
                    "index.html not found"
                )

            cid = upload_to_ipfs(deployment_dir)

            if cid is not None:
                deployment.cid = cid

            deployment.status = DeploymentStatus.DEPLOYED.value
            deployment.message = (
                "Website deployment completed successfully"
            )

        except Exception as exc:
            deployment.status = DeploymentStatus.FAILED.value
            deployment.message = f"Deployment failed: {exc}"

        db.commit()
        db.refresh(deployment)

        return Deployment(
            deployment_id=deployment.deployment_id,
            status=DeploymentStatus(deployment.status),
            message=deployment.message,
            files=json.loads(deployment.files),
            cid=deployment.cid,
            transaction_hash=deployment.transaction_hash,
        )

    finally:
        db.close()