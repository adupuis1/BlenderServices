from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine
from common.config import settings

engine = create_engine(settings.DATABASE_URL)

def create_db_and_tables() -> None:
    import app.models                       # noqa: F401  - registers this service's tables
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]