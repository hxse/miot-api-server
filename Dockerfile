FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock README.md ./
COPY miot_api_server ./miot_api_server

# 构建期安装锁定依赖与项目本体，避免运行期再依赖宿主机源码或包管理器状态。
RUN uv sync --locked --no-dev --no-editable


FROM python:3.12-slim AS runtime

ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MIOT_AUTH_PATH=/data/mijia/auth.json \
    MIOT_SPEC_CACHE_DIR=/data/mijia/spec-cache \
    MIOT_PORT=8000

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

EXPOSE 8000
VOLUME ["/data/mijia"]

# 容器内默认监听 0.0.0.0，端口映射是否对外暴露由 docker run -p 决定。
CMD ["sh", "-c", "exec python -m uvicorn miot_api_server.main:app --host 0.0.0.0 --port \"${MIOT_PORT:-8000}\""]
