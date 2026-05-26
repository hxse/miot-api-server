from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path


class ConfigError(ValueError):
    """配置不合法时抛出的异常。"""


@dataclass(frozen=True, slots=True)
class Settings:
    app_token: str
    auth_path: Path
    spec_cache_dir: Path
    api_base_url: str
    cors_allowed_origins: tuple[str, ...]


def _require_app_token() -> str:
    raw_value = os.getenv("APP_TOKEN")
    if raw_value is None or not raw_value.strip():
        raise ConfigError("APP_TOKEN is required and cannot be blank")
    return raw_value.strip()


def _resolve_path(name: str, default: str) -> Path:
    raw_value = os.getenv(name, default).strip()
    if not raw_value:
        raise ConfigError(f"{name} is required and cannot be blank")
    return Path(raw_value)


def _resolve_url_base(name: str, default: str) -> str:
    raw_value = os.getenv(name, default).strip()
    if not raw_value:
        raise ConfigError(f"{name} is required and cannot be blank")
    return raw_value.rstrip("/") or "/"


def resolve_cors_allowed_origins() -> tuple[str, ...]:
    raw_value = os.getenv("MIOT_CORS_ALLOWED_ORIGINS", "")
    return tuple(
        item.strip().rstrip("/") for item in raw_value.split(",") if item.strip()
    )


def ensure_runtime_directories(settings: Settings) -> None:
    # 运行期统一确保认证文件父目录与 spec 缓存目录存在，避免把目录准备逻辑散落到不同启动入口。
    settings.auth_path.parent.mkdir(parents=True, exist_ok=True)
    settings.spec_cache_dir.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    # 统一在这里收口启动时必须满足的最小配置，避免路由层各自兜底。
    auth_path = _resolve_path("MIOT_AUTH_PATH", ".data/mijia/auth.json")
    spec_cache_dir = _resolve_path("MIOT_SPEC_CACHE_DIR", ".data/mijia/spec-cache")
    return Settings(
        app_token=_require_app_token(),
        auth_path=auth_path,
        spec_cache_dir=spec_cache_dir,
        api_base_url=_resolve_url_base("MIOT_API_BASE_URL", "/api"),
        cors_allowed_origins=resolve_cors_allowed_origins(),
    )
