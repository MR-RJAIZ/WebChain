from enum import Enum
from pydantic import BaseModel


class DeploymentStatus(str, Enum):
    DEPLOYED = "deployed"
    FAILED = "failed"


class Deployment(BaseModel):
    deployment_id: str
    status: DeploymentStatus
    message: str
    files: list[str]


class DeploymentFailure(BaseModel):
    status: DeploymentStatus
    message: str