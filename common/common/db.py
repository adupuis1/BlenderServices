from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine
from common.config import settings

engine = create_engine(settings.DATABASE_URL)

def create_db_and_tables(schema: str) -> None:
    """Create this service's schema, then its tables inside it.

    The caller imports its own app.models first, so the tables are
    registered on SQLModel.metadata before create_all runs.
    """
    with engine.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]