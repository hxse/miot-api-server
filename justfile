app_token := trim(env("APP_TOKEN", ""))
app_module := env("MIOT_APP_MODULE", "miot_api_server.main:app")
uv_run_host := env("MIOT_UV_RUN_HOST", "0.0.0.0")
port := env("MIOT_PORT", "8000")
uv_auth_path := env("MIOT_AUTH_PATH", ".data/mijia/auth.json")
uv_spec_cache_dir := env("MIOT_SPEC_CACHE_DIR", ".data/mijia/spec-cache")

default:
    @just --list

# 使用 uv 直接启动；当前 recipe 默认绑定 0.0.0.0，便于本机和局域网联调。
uv-run:
    test -n "{{app_token}}" || (echo "APP_TOKEN is required and cannot be blank" >&2 && exit 1)
    APP_TOKEN="{{app_token}}" MIOT_AUTH_PATH="{{uv_auth_path}}" MIOT_SPEC_CACHE_DIR="{{uv_spec_cache_dir}}" uv run --no-project uvicorn "{{app_module}}" --host "{{uv_run_host}}" --port "{{port}}"

# 运行类型检查。
check:
    uvx ty check

# 统一格式化代码。
format:
    uvx ruff format

# 构建 Docker 镜像。
docker-build:
    docker build -t miot-api-server:local .

# 用当前镜像启动本地容器调试。
docker-run:
    test -n "{{app_token}}" || (echo "APP_TOKEN is required and cannot be blank" >&2 && exit 1)
    docker run --rm --name miot-api-server -p 8000:8000 -e APP_TOKEN="{{app_token}}" -v miot-api-server-data:/data/mijia miot-api-server:local
