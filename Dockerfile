# Use the official Python 3.13 slim image
FROM python:3.13-slim

# Install the 'uv' package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory inside the container
WORKDIR /app

# Copy dependency files first (for fast caching)
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# Copy all the python code into the container
COPY src/ ./src/

# Tell the container what command to run when it starts
CMD ["uv", "run", "python", "src/anirecc/agent/agent.py"]
