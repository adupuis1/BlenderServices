FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1  UV_COMPILE_BYTECODE=1

COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /uvx /bin/

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"

# Build context is the repo root, so both members of the workspace are available.
COPY pyproject.toml uv.lock ./
COPY common/ ./common/
COPY ./projectService/backend/pyproject.toml ./projectService/backend/pyproject.toml
 
RUN uv sync --frozen --no-dev --package projectservice
 
COPY projectService/backend/app/ ./app/
 
CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
