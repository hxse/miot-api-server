from __future__ import annotations

from json import JSONDecodeError
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

import requests

from miot_api_server.config import Settings
from miot_api_server.errors import (
    AuthenticationRequiredError,
    LoginProcessError,
)
from miot_api_server.main import list_devices
from miot_api_server.provider import (
    MIJIA_AUTH_REFRESH_TIMEOUT_SECONDS,
    MijiaProvider,
)


class FakeMijiaApi:
    def __init__(self, *, available: bool, refresh_error: Exception | None = None):
        self.available = available
        self.refresh_error = refresh_error
        self.refresh_count = 0
        self.save_count = 0
        self.init_count = 0

    def _refresh_token(self) -> dict[str, str]:
        self.refresh_count += 1
        if self.refresh_error is not None:
            raise self.refresh_error
        self.available = True
        return {"serviceToken": "refreshed"}

    def _save_auth_data(self) -> None:
        self.save_count += 1

    def _init_session(self) -> None:
        self.init_count += 1
        self.available = True

    def get_devices_list(self) -> list[dict[str, object]]:
        return []

    def get_shared_devices_list(self) -> list[dict[str, object]]:
        return []


class MijiaProviderAuthRefreshTest(unittest.TestCase):
    def _settings(self, root: Path, *, auth_file_exists: bool = True) -> Settings:
        auth_path = root / "auth.json"
        if auth_file_exists:
            auth_path.write_text("{}", encoding="utf-8")
        return Settings(
            app_token="test-token",
            auth_path=auth_path,
            spec_cache_dir=root / "spec-cache",
        )

    def test_require_api_requires_login_when_auth_file_missing(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            provider = MijiaProvider(
                self._settings(Path(raw_root), auth_file_exists=False)
            )

            with self.assertRaises(AuthenticationRequiredError):
                provider._require_api()

    def test_require_api_requires_login_when_auth_file_is_invalid_json(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            provider = MijiaProvider(self._settings(Path(raw_root)))

            with patch(
                "miot_api_server.provider.mijiaAPI",
                side_effect=JSONDecodeError("invalid", "{", 0),
            ):
                with self.assertRaises(AuthenticationRequiredError):
                    provider._require_api()

    def test_require_api_requires_login_when_auth_file_misses_fields(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            provider = MijiaProvider(self._settings(Path(raw_root)))

            with patch(
                "miot_api_server.provider.mijiaAPI",
                side_effect=KeyError("serviceToken"),
            ):
                with self.assertRaises(AuthenticationRequiredError):
                    provider._require_api()

    def test_require_api_returns_available_api_without_refresh(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            fake_api = FakeMijiaApi(available=True)
            provider = MijiaProvider(self._settings(Path(raw_root)))

            with patch("miot_api_server.provider.mijiaAPI", return_value=fake_api):
                result = provider._require_api()

            self.assertIs(result, fake_api)
            self.assertEqual(fake_api.refresh_count, 0)

    def test_require_api_refreshes_unavailable_api(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            fake_api = FakeMijiaApi(available=False)
            provider = MijiaProvider(self._settings(Path(raw_root)))

            with (
                patch("miot_api_server.provider.mijiaAPI", return_value=fake_api),
                patch.object(
                    provider,
                    "_request_auth_refresh_location",
                    return_value={"code": 0, "message": "刷新Token成功"},
                ),
            ):
                result = provider._require_api()

            self.assertIs(result, fake_api)
            self.assertTrue(fake_api.available)
            self.assertEqual(fake_api.refresh_count, 0)
            self.assertEqual(fake_api.save_count, 1)
            self.assertEqual(fake_api.init_count, 1)

    def test_require_api_requires_login_when_refresh_fails(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            fake_api = FakeMijiaApi(available=False)
            provider = MijiaProvider(self._settings(Path(raw_root)))

            with (
                patch("miot_api_server.provider.mijiaAPI", return_value=fake_api),
                patch.object(
                    provider,
                    "_request_auth_refresh_location",
                    return_value={"sid": "mijia"},
                ),
            ):
                with self.assertRaises(AuthenticationRequiredError):
                    provider._require_api()

            self.assertEqual(fake_api.refresh_count, 0)
            self.assertEqual(fake_api.save_count, 0)
            self.assertEqual(fake_api.init_count, 0)

    def test_require_api_reports_refresh_network_error(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            fake_api = FakeMijiaApi(available=False)
            provider = MijiaProvider(self._settings(Path(raw_root)))

            with (
                patch("miot_api_server.provider.mijiaAPI", return_value=fake_api),
                patch.object(
                    provider,
                    "_request_auth_refresh_location",
                    side_effect=requests.exceptions.ConnectionError("offline"),
                ),
            ):
                with self.assertRaises(LoginProcessError):
                    provider._require_api()

            self.assertEqual(fake_api.refresh_count, 0)

    def test_devices_route_refreshes_before_listing_devices(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            root = Path(raw_root)
            fake_api = FakeMijiaApi(available=False)
            provider = MijiaProvider(self._settings(root))
            request = SimpleNamespace(
                app=SimpleNamespace(state=SimpleNamespace(provider=provider))
            )

            with (
                patch("miot_api_server.provider.mijiaAPI", return_value=fake_api),
                patch.object(
                    provider,
                    "_request_auth_refresh_location",
                    return_value={"code": 0, "message": "刷新Token成功"},
                ),
            ):
                result = list_devices(request)

            self.assertEqual(result, [])
            self.assertEqual(fake_api.refresh_count, 0)
            self.assertEqual(fake_api.save_count, 1)
            self.assertEqual(fake_api.init_count, 1)

    def test_refresh_location_request_uses_explicit_timeouts(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            provider = MijiaProvider(self._settings(Path(raw_root)))
            session = SimpleNamespace()
            session.cookies = SimpleNamespace(
                get_dict=lambda: {"serviceToken": "new-token"}
            )
            session_timeout: dict[str, object] = {}

            def session_get(url: str, *, timeout: int) -> SimpleNamespace:
                session_timeout["url"] = url
                session_timeout["timeout"] = timeout
                return SimpleNamespace(status_code=200, text="ok")

            session.get = session_get
            api = SimpleNamespace(
                user_agent="ua",
                deviceId="device-id",
                pass_o="pass-o",
                auth_data={
                    "passToken": "pass-token",
                    "userId": "user-id",
                    "cUserId": "c-user-id",
                },
                locale="zh_CN",
                service_login_url="https://account.example/serviceLogin",
                session=session,
                _handle_ret=lambda response, verify_code: {
                    "code": 0,
                    "location": "https://sts.example/callback",
                    "ssecurity": "new-security",
                },
            )

            with patch("miot_api_server.provider.requests.get") as get_mock:
                result = provider._request_auth_refresh_location(api)

            get_mock.assert_called_once_with(
                "https://account.example/serviceLogin",
                headers=unittest.mock.ANY,
                timeout=MIJIA_AUTH_REFRESH_TIMEOUT_SECONDS,
            )
            self.assertEqual(result, {"code": 0, "message": "刷新Token成功"})
            self.assertEqual(
                session_timeout["timeout"], MIJIA_AUTH_REFRESH_TIMEOUT_SECONDS
            )
            self.assertEqual(session_timeout["url"], "https://sts.example/callback")
            self.assertEqual(api.auth_data["serviceToken"], "new-token")
            self.assertEqual(api.auth_data["ssecurity"], "new-security")


if __name__ == "__main__":
    unittest.main()
