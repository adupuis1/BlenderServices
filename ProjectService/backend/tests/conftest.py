import pytest
from sqlmodel import Session, SQLModel, create_engine
 
from common.config import settings
 
TEST_URL = "postgresql+psycopg://blender:dev@localhost:5433/blender_test"
 
 
@pytest.fixture(name="session")
def session_fixture():
    import app.models  # noqa: F401
    engine = create_engine(TEST_URL)
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()
