import uuid
from datetime import UTC, datetime
from typing import Optional
from enum import StrEnum
from sqlalchemy import DateTime, JSON
from sqlmodel import Field, Relationship, SQLModel

def utc_now() -> datetime:
    return datetime.now(UTC)

TS = DateTime(timezone=True)

class ProjectStatus(StrEnum):
    PENDING_UPLOAD = "pending_upload"
    SCANNING="scanning"
    READY="ready"
    REJECTED="rejected"

class Project(SQLModel, table=True):
    __table_args__ = {"schema": "project"}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_user_id: uuid.UUID = Field(index=True)
    name: str = Field(min_length=1, max_length=200)
    blend_key: str = Field(unique=True, index=True)
    status: ProjectStatus = Field(default=ProjectStatus.PENDING_UPLOAD, index=True)
    created_at: datetime = Field(default_factory=utc_now, sa_type=TS)
    blender_series: str |None = Field(default=None, max_length=8)
    reject_reason: str | None = Field(default=None, max_length=500)
    
    project_details: Optional["ProjectDetails"] = Relationship(
        back_populates="project",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "uselist": False},
    )

class ProjectDetails(SQLModel, table =True):
    __table_args__ = {"schema": "project"}

    project_id: uuid.UUID = Field(
        foreign_key="project.project.id", primary_key=True, ondelete="CASCADE"
    )
    engine: str | None = None
    samples: int | None = None
    resolution_x: int | None = None
    resolution_y: int | None = None
    frame_start: int | None = None
    frame_end: int | None = None
    poly_count: int  | None = None
    external_paths: list[dict] = Field(default_factory=list, sa_type=JSON)
    scanned_at: datetime = Field(default_factory=utc_now, sa_type=TS)
    file_size_bytes: int | None = None
    addons: list[str] = Field(default_factory=list, sa_type=JSON)

    # Security flags. Any of these rejects the project.
    has_registered_scripts: bool = False
    has_python_drivers: bool = False
    freestyle_enabled: bool = False

    project: Project | None = Relationship(back_populates="project_details")


class ProjectCreate(SQLModel):
    name: str = Field(min_length=1, max_length=200)

class ProjectUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)

class ProjectPublic(SQLModel):
    id: uuid.UUID
    name: str
    status: ProjectStatus
    blender_series: str | None
    reject_reason: str | None
    created_at: datetime
