import uuid

from fastapi import APIRouter, Response
from sqlmodel import select

from app.api.deps import CurrentCaller

from app.models import (
    Project, ProjectCreate, ProjectDetails, ProjectPublic, ProjectStatus, ProjectUpdate
)
from common import storage
from common.db import SessionDep
from common.errors import Conflict, DomainError, NotFound

router = APIRouter(prefix="/projects", tags=["prjects"])

def owned(session: SessionDep, project_id: uuid.UUID, user_id: uuid.UUID
          )-> Project:
    project = session.get(Project, project_id)
    # 404 rather than 403 for someone else's project: a 403 confirms the id
    # exists and belongs to somebody, so enumeration learns something.
    if project is None or project.owner_user_id != user_id:
        raise NotFound("Project not found")
    return project


@router.post("", status_code=201)
def add_project(body: ProjectCreate, caller: CurrentCaller, session: SessionDep):
    project = Project(
        owner_user_id=caller.id,
        name=body.name,
        blend_key=f"projects/{caller.id}/{uuid.uuid4()}.blend"
    )
    session.add(project)
    session.commit()
    session.refresh(project)
    return {
        "project": ProjectPublic.model_validate(project, from_attributes=True),
        "upload_url": storage.upload_url(project.blend_key),
    }

