from pathlib import Path
from uuid import uuid4
from app.models.deployment import Deployment


UPLOAD_DIR = Path("uploads")

deployments = {}


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

    deployment = Deployment(
    deployment_id=deployment_id,
    status="deployed",
    message="Website deployment simulated successfully",
    files=[file.name for file in files]
)

    deployments[deployment_id] = deployment

    return deployment