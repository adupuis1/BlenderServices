from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

import app.models
from app.api.main import api_router
from common.config import settings
from common.db import create_db_and_tables
from common import storage
from common.errors import DomainError


app = FastAPI(
    title="projectService",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/api/docs",
    redoc_url=None,
)

create_db_and_tables("project")
storage.ensure_bucket()
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    return JSONResponse(statuscode=exc.status_code, content={"detail": str(BaseException)})