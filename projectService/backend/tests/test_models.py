import uuid
 
import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
 
from app.models import ProjectDetails, Project, ProjectStatus
 
 
def make_project(session, **kwargs):
    project = Project(
        owner_user_id=kwargs.pop("owner", uuid.uuid4()),
        name=kwargs.pop("name", "cube test"),
        blend_key=kwargs.pop("blend_key", f"projects/{uuid.uuid4()}.blend"),
        **kwargs,
    )
    session.add(project)
    session.commit()
    session.refresh(project)
    return project
 
 
def test_defaults_to_pending_upload(session):
    project = make_project(session)
    assert project.status is ProjectStatus.PENDING_UPLOAD
    assert project.blender_series is None
    assert project.created_at is not None
 
 
def test_blend_key_is_unique(session):
    make_project(session, blend_key="projects/same.blend")
    with pytest.raises(IntegrityError):
        make_project(session, blend_key="projects/same.blend")
 
 
def test_scan_round_trips_external_paths(session):
    project = make_project(session)
    session.add(ProjectDetails(
        project_id=project.id,
        engine="CYCLES",
        samples=128,
        external_paths=[{"type": "image", "name": "brick", "path": "//tex/brick.png"}],
    ))
    session.commit()
    session.refresh(project)
    assert project.project_details.samples == 128
    assert project.project_details.external_paths[0]["name"] == "brick"
 
 
def test_deleting_a_project_deletes_its_scan(session):
    project = make_project(session)
    session.add(ProjectDetails(project_id=project.id, engine="CYCLES"))
    session.commit()
    session.delete(project)
    session.commit()
    assert session.exec(select(ProjectDetails)).all() == []
