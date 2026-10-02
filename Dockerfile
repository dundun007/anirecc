FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-install-project

COPY src/ ./src/
COPY README.md ./

RUN uv sync --frozen --no-dev

CMD ["uv", "run", "python", "src/anirecc/agent/agent.py"]
