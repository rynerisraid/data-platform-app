import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID,ENUM
import datetime
from sqlalchemy import ForeignKey,Enum as SQLEnum
from pydantic import BaseModel
from app.config.db import Base
from app.models.resources import STATE_ENUM


class Workspaces(Base):
    __tablename__ = "workspaces"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    state = Column(SQLEnum('A', 'P', name="state_enum"), default='A')  # e.g., A, P
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def repr(self):
        return f'<Workspace {self.name}>'


# -------------------- Resources in Workspace --------------
class WorkspaceResources(Base):
    __tablename__ = "workspace_resources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey('workspaces.id'), nullable=False)
    resource_id = Column(UUID(as_uuid=True), ForeignKey('resources.id'), nullable=False)
    state = Column(STATE_ENUM, default='A')  # e.g., A, P
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def repr(self):
        return f'<WorkspaceResource {self.id}>'


# -------------------- Users in Workspace --------------
class WorkspaceUsers(Base):
    __tablename__ = "workspace_users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey('workspaces.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    state = Column(STATE_ENUM, default='A')  # e.g., A, P
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


    def repr(self):
        return f'<WorkspaceUser {self.id}>'


# -------------------- Pydantic Schemas --------------------

class WorkspaceBase(BaseModel):
    name: str
    description: str | None = None

class WorkspaceCreate(WorkspaceBase):
    pass

class WorkspaceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

class WorkspaceRead(WorkspaceBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True