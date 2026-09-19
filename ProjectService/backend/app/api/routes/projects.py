import uuid

from fastapi import APIRouter, Response, Query
from sqlmodel import select

from common.deps import CurrentCaller

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


@router.get("", response_model=list[ProjectPublic])
def get_projects(caller: CurrentCaller, session: SessionDep, limit: int = Query(100, ge=1, le=500)):
    return session.exec(
        select(Project)
        .where(Project.owner_user_id == caller.id)
        .order_by(Project.created_at.desc())
        .limit(limit)
    ).all()


@router.get("/{project_id}")
def get_project(project_id: uuid.UUID, caller: CurrentCaller, session: SessionDep):
    project = owned(session, project_id, caller.id)
    return {
        "project": ProjectPublic.model_validate(project, from_attributes=True),
        "details": project.project_details
    }

@router.patch("/{project_id}")
def path_project(project_id: uuid.UUID, caller: CurrentCaller, body: ProjectUpdate, session: SessionDep):
    project = owned(session, project_id, caller.id)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    session.add(project)
    session.commit()
    session.refresh(project)

@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: uuid.UUID, caller: CurrentCaller, session: SessionDep):
    project = owned(session, project_id, caller.id)
    if project.status is ProjectStatus.SCANNING:
        raise Conflict("Cannot delete a project while it is being scanned")
    session.delete(project)
    session.commit()
    return Response(status_code=204)

@router.post("/{project_id}/complete", response_model=ProjectPublic)
def complete_upload(project_id: uuid.UUID, caller: CurrentCaller, session: SessionDep):
    project = owned(session, project_id, caller.id)
    if project.status is not ProjectStatus.PENDING_UPLOAD:
        raise Conflict(f"Project is already {project.status.value}")
    if not storage.exists(project.blend_key):
        raise DomainError("File has not been uploaded yet")
    project.status = ProjectStatus.SCANNING
    session.add(project)
    session.commit()
    session.refresh(project)
    return project