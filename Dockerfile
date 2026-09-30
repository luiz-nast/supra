FROM ghcr.io/astral-sh/uv:python3.13-alpine
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
COPY app.py ./
COPY static ./static
CMD ["uv", "run", "--no-sync", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
