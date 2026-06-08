from __future__ import annotations

from contextlib import contextmanager
from collections.abc import Iterator
import threading
from typing import Any

import requests


MIJIA_NETWORK_TIMEOUT_SECONDS = 30
MIJIA_AUTH_REFRESH_TIMEOUT_SECONDS = MIJIA_NETWORK_TIMEOUT_SECONDS
_REQUESTS_GET_PATCH_LOCK = threading.RLock()


class TimeoutSession(requests.Session):
    def __init__(
        self,
        default_timeout: int = MIJIA_NETWORK_TIMEOUT_SECONDS,
        source: requests.Session | None = None,
    ):
        super().__init__()
        self.default_timeout = default_timeout
        if source is not None:
            self._copy_session_state(source)

    def _copy_session_state(self, source: requests.Session) -> None:
        # 复制第三方库初始化好的 headers/cookies，避免替换 session 时丢认证上下文。
        self.headers.update(source.headers)
        self.cookies.update(source.cookies)
        self.auth = source.auth
        self.proxies = source.proxies.copy()
        self.hooks = {key: value[:] for key, value in source.hooks.items()}
        self.params = source.params.copy()
        self.verify = source.verify
        self.cert = source.cert
        self.trust_env = source.trust_env
        self.max_redirects = source.max_redirects
        self.adapters = source.adapters.copy()

    def request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        kwargs.setdefault("timeout", self.default_timeout)
        return super().request(method, url, **kwargs)


def install_timeout_session(api: Any) -> None:
    session = getattr(api, "session", None)
    if session is None:
        api.session = TimeoutSession()
        return
    if isinstance(session, TimeoutSession):
        return
    if isinstance(session, requests.Session):
        api.session = TimeoutSession(source=session)


@contextmanager
def scoped_requests_get_timeout(
    requests_module: Any,
    default_timeout: int = MIJIA_NETWORK_TIMEOUT_SECONDS,
) -> Iterator[None]:
    # 第三方 spec helper 不接收 session，只能在同步调用窗口内补齐 requests.get timeout。
    with _REQUESTS_GET_PATCH_LOCK:
        original_get = requests_module.get

        def get_with_timeout(*args: Any, **kwargs: Any):
            kwargs.setdefault("timeout", default_timeout)
            return original_get(*args, **kwargs)

        requests_module.get = get_with_timeout
        try:
            yield
        finally:
            requests_module.get = original_get
