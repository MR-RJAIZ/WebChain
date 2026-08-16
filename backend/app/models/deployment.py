from pydantic import BaseModel


class Deployment(BaseModel):
    deployment_id: str
    status: str
    message: str
    files: list[str]