from fastapi import APIRouter
from routes import projects

api_router = APIRouter()
api_router.include_router(projects.router)