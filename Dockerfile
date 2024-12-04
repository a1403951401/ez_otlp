FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 禁用 venv
ENV UV_PROJECT_ENVIRONMENT="/usr/local/"

RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    apt-get install -y gcc g++ python3-dev

WORKDIR /app

RUN --mount=type=bind,source=./pyproject.toml,target=/app/pyproject.toml \
    --mount=type=bind,source=./uv.lock,target=/app/uv.lock \
    --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project
