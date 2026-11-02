from enum import Enum
from pydantic import BaseModel


class DeploymentStatus(str, Enum):
    PENDING = "pending"
    DEPLOYED = "deployed"
    FAILED = "failed"


class Deployment(BaseModel):
    deployment_id: str
    status: DeploymentStatus
    message: str
    files: list[str]

    site_url: str | None = None

    cid: str | None = None
    transaction_hash: str | None = None


class DeploymentFailure(BaseModel):
    status: DeploymentStatus
    message: str

class MessageResponse(BaseModel):
    message: str