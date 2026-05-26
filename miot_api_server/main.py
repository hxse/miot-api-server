from __future__ import annotations

from contextlib import asynccontextmanager
from functools import lru_cache
from pathlib import Path
import secrets

from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from miot_api_server.config import ensure_runtime_directories, get_settings
from miot_api_server.doc_pages import build_redoc_html, build_swagger_html
from miot_api_server.errors import AppError
from miot_api_server.login_page import build_login_html
from miot_api_server.provider import MijiaProvider
from miot_api_server.schemas import (
    AuthResetResponse,
    AuthStatusResponse,
    DevicePowerRequest,
    DevicePowerResponse,
    DeviceSummary,
    ErrorResponse,
    HealthResponse,
    LoginFinishRequest,
    LoginFinishResponse,
    LoginStartResponse,
)


STATIC_DIR = Path(__file__).parent / "static"
PUBLIC_PATHS = frozenset({"/", "/healthz", "/docs", "/redoc", "/login"})
DOCS_SECURITY_HEADERS = {
    # 文档页会处理浏览器会话 token，因此只允许加载同源脚本，避免第三方脚本读取 token。
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: blob:; "
        "connect-src 'self'; "
        "object-src 'none'; "
        "base-uri 'none'; "
        "frame-ancestors 'none'"
    ),
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动阶段先冻结配置；缺失 token 时直接拒绝启动，避免服务以不安全状态暴露到公网。
    app.state.settings = get_settings()
    ensure_runtime_directories(app.state.settings)
    app.state.provider = MijiaProvider(app.state.settings)
    yield


app = FastAPI(
    title="miot-api-server",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
)

# 静态资源只承载本地 vendor 文档脚本和样式，不包含认证文件、缓存或业务数据。
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def get_provider(request: Request) -> MijiaProvider:
    return request.app.state.provider


def is_public_path(path: str) -> bool:
    return path in PUBLIC_PATHS or path.startswith("/static/")


@app.exception_handler(AppError)
async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            detail=exc.message, error_code=exc.error_code
        ).model_dump(),
    )


@app.middleware("http")
async def require_bearer_token(request: Request, call_next):
    if is_public_path(request.url.path):
        return await call_next(request)

    authorization = request.headers.get("authorization", "")
    settings = get_settings()
    expected = f"Bearer {settings.app_token}"

    # 统一用 Bearer 头做最小鉴权，并使用常量时间比较减少直接字符串比较带来的泄露面。
    if not secrets.compare_digest(authorization, expected):
        return JSONResponse(
            status_code=401,
            content={"detail": "Unauthorized", "error_code": "unauthorized"},
        )

    return await call_next(request)


@lru_cache(maxsize=1)
def build_openapi_schema() -> dict[str, object]:
    # 文档 schema 仍由服务端统一生成，避免在文档页里手写第二份接口真值。
    return get_openapi(
        title=app.title,
        version="0.1.0",
        description="Thin FastAPI wrapper around mijia-api",
        routes=app.routes,
    )


@app.get("/healthz", response_model=HealthResponse, tags=["system"])
async def healthz() -> HealthResponse:
    # 健康检查只返回最小存活信息，不回显配置、设备状态或认证上下文。
    return HealthResponse(status="ok")


@app.get("/", include_in_schema=False)
async def index() -> RedirectResponse:
    # 根路径只做体验入口，避免用户直接访问时看到业务接口的鉴权 JSON。
    return RedirectResponse(url="/login", status_code=307)


#
# 这些业务路由当前都直接落到同步版 MijiaProvider 与 mijiaAPI。
# 统一保持为 def，让 FastAPI 在线程池里执行它们，避免在 async 路由里直接阻塞事件循环。
#
@app.get("/auth/status", response_model=AuthStatusResponse, tags=["auth"])
def auth_status(request: Request) -> AuthStatusResponse:
    return AuthStatusResponse(**get_provider(request).auth_status())


@app.post("/auth/reset", response_model=AuthResetResponse, tags=["auth"])
def auth_reset(request: Request) -> AuthResetResponse:
    # 该接口只清理本服务持久化的米家认证状态与待完成扫码会话，便于从头联调。
    return AuthResetResponse(**get_provider(request).reset_auth_state())


@app.post("/auth/login/start", response_model=LoginStartResponse, tags=["auth"])
def auth_login_start(request: Request) -> LoginStartResponse:
    return LoginStartResponse(**get_provider(request).start_login())


@app.post("/auth/login/finish", response_model=LoginFinishResponse, tags=["auth"])
def auth_login_finish(
    request: Request, payload: LoginFinishRequest
) -> LoginFinishResponse:
    result = get_provider(request).finish_login(
        payload.session_id, payload.timeout_seconds
    )
    return LoginFinishResponse(**result)


@app.get("/devices", response_model=list[DeviceSummary], tags=["devices"])
def list_devices(request: Request) -> list[DeviceSummary]:
    return get_provider(request).list_devices()


@app.get("/devices/{did}", response_model=DeviceSummary, tags=["devices"])
def get_device(request: Request, did: str) -> DeviceSummary:
    return get_provider(request).get_device(did)


@app.post(
    "/devices/{did}/power/on", response_model=DevicePowerResponse, tags=["devices"]
)
def turn_device_power_on(
    request: Request,
    did: str,
    payload: DevicePowerRequest | None = None,
) -> DevicePowerResponse:
    result = get_provider(request).set_device_power(
        did, True, payload.property_name if payload else None
    )
    return DevicePowerResponse(**result)


@app.post(
    "/devices/{did}/power/off", response_model=DevicePowerResponse, tags=["devices"]
)
def turn_device_power_off(
    request: Request,
    did: str,
    payload: DevicePowerRequest | None = None,
) -> DevicePowerResponse:
    result = get_provider(request).set_device_power(
        did, False, payload.property_name if payload else None
    )
    return DevicePowerResponse(**result)


@app.get("/openapi.json", include_in_schema=False)
async def openapi_json() -> JSONResponse:
    return JSONResponse(build_openapi_schema())


@app.get("/docs", include_in_schema=False)
async def swagger_docs() -> HTMLResponse:
    # 文档壳页可以打开，但只有输入正确 token 后才会加载真正的 schema。
    return HTMLResponse(build_swagger_html(), headers=DOCS_SECURITY_HEADERS)


@app.get("/redoc", include_in_schema=False)
async def redoc_docs() -> HTMLResponse:
    return HTMLResponse(build_redoc_html(), headers=DOCS_SECURITY_HEADERS)


@app.get("/login", include_in_schema=False)
async def login_page() -> HTMLResponse:
    # 登录页本身允许匿名访问，但内部所有实际操作仍然统一走 Bearer token 鉴权。
    return HTMLResponse(build_login_html())
