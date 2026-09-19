import pytest
from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401  - registers the tables
from common.config import settings

# Same server as DATABASE_URL, separate database, so tests never touch real data.
TEST_URL = settings.DATABASE_URL.rsplit("/", 1)[0] + "/blender_test"


@pytest.fixture(name="engine", scope="session")
def engine_fixture():
    engine = create_engine(TEST_URL)
    with engine.begin() as conn:
        conn.execute(text('CREATE SCHEMA IF NOT EXISTS "project"'))
    yield engine
    engine.dispose()


@pytest.fixture(name="session")
def session_fixture(engine):
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session