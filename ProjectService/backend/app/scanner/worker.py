import logging
import tempfile
import time
from pathlib import Path

from botocore.exceptions import BotoCoreError, ClientError
from sqlmodel import Session, select

import app.models  # noqa: F401
from app.models import Project, ProjectDetails, ProjectStatus
from app.scanner.run_one import scan_file
from app.services.rules import rejection_reason
from common import storage
from common.db import engine

logging.basicConfig(level=logging.INFO)


def process_one(session: Session) -> bool:
    """Scan one waiting project. False when there was nothing to do."""
    project = session.exec(
        select(Project)
        .where(Project.status == ProjectStatus.SCANNING)
        .order_by(Project.created_at)
        .with_for_update(skip_locked=True)
        .limit(1)
    ).first()
    if project is None:
        return False

    logging.info("Scanning project %s", project.id)
    with tempfile.TemporaryDirectory() as tmp:
        local = Path(tmp) / "scene.blend"
        try:
            storage.internal.download_file(storage.BUCKET, project.blend_key, str(local))
        except (ClientError, BotoCoreError) as exc:
            # Not the file's fault. Roll back so it stays 'scanning' and retries.
            logging.error("Storage unavailable for %s: %s", project.id, exc)
            session.rollback()
            return False
        try:
            data = scan_file(local)
        except Exception as exc:
            logging.warning("Rejecting project %s: %s", project.id, exc)
            project.status = ProjectStatus.REJECTED
            project.reject_reason = str(exc)[:500]
            session.add(project)
            session.commit()
            return True

    series = data.pop("blender_series")
    details = ProjectDetails(project_id=project.id, **data)
    session.add(details)

    reason = rejection_reason(details)
    project.blender_series = series
    project.status = ProjectStatus.REJECTED if reason else ProjectStatus.READY
    project.reject_reason = reason
    session.add(project)
    session.commit()
    return True


def main():
    while True:
        try:
            with Session(engine) as session:
                if not process_one(session):
                    time.sleep(5)
        except Exception:
            logging.exception("Scanner error")
            time.sleep(10)


if __name__ == "__main__":
    main()