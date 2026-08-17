from sqlalchemy import Column, String, Text

from app.database import Base


class DeploymentDB(Base):
    __tablename__ = "deployments"

    deployment_id = Column(String, primary_key=True, index=True)
    status = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    files = Column(Text, nullable=False)