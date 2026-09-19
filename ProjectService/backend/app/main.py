from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

import app.models
from app.api.main import api_router
from common.config import settings
from common.db import create_db_and_tables
from common import storage
from common.errors import DomainError

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables("project")
    storage.ensure_bucket()
    yield

app = FastAPI(
    title="projectService",
    openapi_url=f"{settings.API_V1_STR}/projects/openapi.json",
    docs_url=f"{settings.API_V1_STR}/projects/api/docs",
    redoc_url=None,
    lifespan=lifespan,
)
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})

