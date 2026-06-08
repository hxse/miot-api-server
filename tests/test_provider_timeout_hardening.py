from __future__ import annotations

from json import JSONDecodeError
from pathlib import Path
from types import SimpleNamespace
import tempfile
import time
import unittest
from unittest.mock import patch

import requests

from miot_api_server.config import Settings
from miot_api_server.errors import LoginProcessError
from miot_api_server.provider import (
    LoginError,
    MIJIA_NETWORK_TIMEOUT_SECONDS,
    MijiaProvider,
    PendingLoginSession,
    TimeoutSession,
    mijia_devices,
)


class TimeoutHardeningTest(unittest.TestCase):
    def _settings(self, root: Path, *, auth_file_exists: bool = True) -> Settings:
        auth_path = root / "auth.json"
        if auth_file_exists:
            auth_path.write_text("{}", encoding="utf-8")
        return Settings(
            app_token="test-token",
            auth_path=auth_path,
            spec_cache_dir=root / "spec-cache",
        )

    def test_timeout_session_injects_default_timeout_for_get_and_post(self) -> None:
        session = TimeoutSession()
        with patch.object(
            requests.Session,
            "request",
            return_value=SimpleNamespace(status_code=200),
        ) as request_mock:
            session.get("https://example.test/get")
            session.post("https://example.test/post")

        self.assertEqual(
            request_mock.call_args_list[0].kwargs["timeout"],
            MIJIA_NETWORK_TIMEOUT_SECONDS,
        )
        self.assertEqual(
            request_mock.call_args_list[1].kwargs["timeout"],
            MIJIA_NETWORK_TIMEOUT_SECONDS,
        )

    def test_timeout_session_preserves_explicit_timeout(self) -> None:
        session = TimeoutSession()
        with patch.object(
            requests.Session,
            "request",
            return_value=SimpleNamespace(status_code=200),
        ) as request_mock:
            session.get("https://example.test/get", timeout=7)

        self.assertEqual(request_mock.call_args.kwargs["timeout"], 7)

    def test_new_api_installs_timeout_session(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            source_session = requests.Session()
            source_session.headers["X-Test"] = "kept"
            fake_api = SimpleNamespace(session=source_session)
            provider = MijiaProvider(self._settings(Path(raw_root)))

            with patch("miot_api_server.provider.mijiaAPI", return_value=fake_api):
                result = provider._new_api()

            self.assertIs(result, fake_api)
            self.assertIsInstance(fake_api.session, TimeoutSession)
            self.assertEqual(fake_api.session.headers["X-Test"], "kept")

    def test_init_api_session_reinstalls_timeout_session(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            provider = MijiaProvider(self._settings(Path(raw_root)))
            api = SimpleNamespace(session=TimeoutSession(), init_count=0)

            def init_session() -> None:
                api.init_count += 1
                api.session = requests.Session()

            api._init_session = init_session
            provider._init_api_session(api)

            self.assertEqual(api.init_count, 1)
            self.assertIsInstance(api.session, TimeoutSession)

    def test_require_api_available_network_error_maps_to_login_process_error(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            provider = MijiaProvider(self._settings(Path(raw_root)))

            class FakeApi:
                def __init__(self) -> None:
                    self.session = requests.Session()

                @property
                def available(self) -> bool:
                    raise requests.exceptions.Timeout("available timeout")

            with patch("miot_api_server.provider.mijiaAPI", return_value=FakeApi()):
                with self.assertRaises(LoginProcessError):
                    provider._require_api()

    def test_start_login_uses_timeout_refresh_helper(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            provider = MijiaProvider(self._settings(Path(raw_root)))
            fake_api = SimpleNamespace(
                available=False,
                session=requests.Session(),
                save_count=0,
                init_count=0,
            )

            def save_auth_data() -> None:
                fake_api.save_count += 1

            def init_session() -> None:
                fake_api.init_count += 1
                fake_api.session = requests.Session()

            def forbidden_get_location() -> None:
                raise AssertionError("start_login must not call _get_location")

            fake_api._save_auth_data = save_auth_data
            fake_api._init_session = init_session
            fake_api._get_location = forbidden_get_location

            with (
                patch("miot_api_server.provider.mijiaAPI", return_value=fake_api),
                patch.object(
                    provider,
                    "_request_auth_refresh_location",
                    return_value={"code": 0, "message": "刷新Token成功"},
                ),
            ):
                result = provider.start_login()

            self.assertEqual(result, {"already_logged_in": True})
            self.assertEqual(fake_api.save_count, 1)
            self.assertEqual(fake_api.init_count, 1)
            self.assertIsInstance(fake_api.session, TimeoutSession)

    def test_start_login_available_network_error_maps_to_login_process_error(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            provider = MijiaProvider(self._settings(Path(raw_root)))

            class FakeApi:
                def __init__(self) -> None:
                    self.session = requests.Session()

                @property
                def available(self) -> bool:
                    raise requests.exceptions.Timeout("available timeout")

            with patch("miot_api_server.provider.mijiaAPI", return_value=FakeApi()):
                with self.assertRaises(LoginProcessError):
                    provider.start_login()

    def test_start_login_invalid_auth_file_maps_to_login_process_error(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            provider = MijiaProvider(self._settings(Path(raw_root)))

            with patch(
                "miot_api_server.provider.mijiaAPI",
                side_effect=JSONDecodeError("invalid", "{", 0),
            ):
                with self.assertRaises(LoginProcessError):
                    provider.start_login()

    def test_start_login_qr_request_timeout_maps_to_login_process_error(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            provider = MijiaProvider(self._settings(Path(raw_root)))
            fake_api = SimpleNamespace(
                available=False,
                login_url="https://login.example/qr",
                user_agent="ua",
                auth_data={},
            )

            with (
                patch("miot_api_server.provider.mijiaAPI", return_value=fake_api),
                patch.object(
                    provider,
                    "_request_auth_refresh_location",
                    return_value={"sid": "mijia"},
                ),
                patch(
                    "miot_api_server.provider.requests.get",
                    side_effect=requests.exceptions.Timeout("qr timeout"),
                ) as get_mock,
            ):
                with self.assertRaises(LoginProcessError):
                    provider.start_login()

            self.assertEqual(
                get_mock.call_args.kwargs["timeout"], MIJIA_NETWORK_TIMEOUT_SECONDS
            )

    def test_start_login_qr_response_login_error_maps_to_login_process_error(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            provider = MijiaProvider(self._settings(Path(raw_root)))
            fake_api = SimpleNamespace(
                available=False,
                login_url="https://login.example/qr",
                user_agent="ua",
                auth_data={},
                _handle_ret=lambda response: (_ for _ in ()).throw(
                    LoginError(1, "qr login failed")
                ),
            )

            with (
                patch("miot_api_server.provider.mijiaAPI", return_value=fake_api),
                patch.object(
                    provider,
                    "_request_auth_refresh_location",
                    return_value={"sid": "mijia"},
                ),
                patch(
                    "miot_api_server.provider.requests.get",
                    return_value=SimpleNamespace(status_code=200, text="bad"),
                ),
            ):
                with self.assertRaises(LoginProcessError):
                    provider.start_login()

    def test_start_login_qr_response_parse_errors_map_to_login_process_error(
        self,
    ) -> None:
        error_cases = [
            ("json", lambda: JSONDecodeError("invalid", "{", 0)),
            ("key", lambda: KeyError("loginUrl")),
            ("type", lambda: TypeError("bad qr payload")),
        ]

        for label, make_error in error_cases:
            with self.subTest(label=label):
                with tempfile.TemporaryDirectory() as raw_root:
                    provider = MijiaProvider(self._settings(Path(raw_root)))

                    def handle_ret(_: object) -> dict[str, object]:
                        raise make_error()

                    fake_api = SimpleNamespace(
                        available=False,
                        login_url="https://login.example/qr",
                        user_agent="ua",
                        auth_data={},
                        _handle_ret=handle_ret,
                    )

                    with (
                        patch(
                            "miot_api_server.provider.mijiaAPI",
                            return_value=fake_api,
                        ),
                        patch.object(
                            provider,
                            "_request_auth_refresh_location",
                            return_value={"sid": "mijia"},
                        ),
                        patch(
                            "miot_api_server.provider.requests.get",
                            return_value=SimpleNamespace(status_code=200, text="bad"),
                        ),
                    ):
                        with self.assertRaises(LoginProcessError):
                            provider.start_login()

    def test_start_login_qr_response_missing_fields_maps_to_login_process_error(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            provider = MijiaProvider(self._settings(Path(raw_root)))
            fake_api = SimpleNamespace(
                available=False,
                login_url="https://login.example/qr",
                user_agent="ua",
                auth_data={},
                _handle_ret=lambda response: {},
            )

            with (
                patch("miot_api_server.provider.mijiaAPI", return_value=fake_api),
                patch.object(
                    provider,
                    "_request_auth_refresh_location",
                    return_value={"sid": "mijia"},
                ),
                patch(
                    "miot_api_server.provider.requests.get",
                    return_value=SimpleNamespace(status_code=200, text="bad"),
                ),
            ):
                with self.assertRaises(LoginProcessError):
                    provider.start_login()

    def test_finish_login_callback_network_error_maps_to_login_process_error(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            provider = MijiaProvider(self._settings(Path(raw_root)))
            provider.pending_logins["session"] = PendingLoginSession(
                session_id="session",
                login_url="https://login.example",
                qr_image_url="https://qr.example",
                lp="https://lp.example",
                created_at=time.time(),
                auth_data={},
            )
            fake_api = SimpleNamespace(
                auth_data={},
                user_agent="ua",
                session=requests.Session(),
                _handle_ret=lambda response: {
                    "psecurity": "psecurity",
                    "nonce": "nonce",
                    "ssecurity": "ssecurity",
                    "passToken": "passToken",
                    "userId": "userId",
                    "cUserId": "cUserId",
                    "location": "https://callback.example",
                },
                _save_auth_data=lambda: None,
                _init_session=lambda: None,
            )
            calls: list[str] = []

            def session_get(url: str, **__: object) -> SimpleNamespace:
                calls.append(url)
                if len(calls) == 1:
                    return SimpleNamespace(status_code=200, text="lp")
                raise requests.exceptions.ConnectionError("callback failed")

            with (
                patch("miot_api_server.provider.mijiaAPI", return_value=fake_api),
                patch.object(requests.Session, "get", side_effect=session_get),
            ):
                with self.assertRaises(LoginProcessError):
                    provider.finish_login("session", 1)

            self.assertEqual(calls, ["https://lp.example", "https://callback.example"])

    def test_auth_status_handles_invalid_auth_file(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            provider = MijiaProvider(self._settings(Path(raw_root)))
            with patch(
                "miot_api_server.provider.mijiaAPI",
                side_effect=JSONDecodeError("invalid", "{", 0),
            ):
                result = provider.auth_status()

            self.assertEqual(
                result,
                {
                    "logged_in": False,
                    "has_auth_file": True,
                    "pending_login_session_count": 0,
                },
            )

    def test_auth_status_handles_network_error(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            provider = MijiaProvider(self._settings(Path(raw_root)))

            class FakeApi:
                session = TimeoutSession()

                @property
                def available(self) -> bool:
                    raise requests.exceptions.Timeout("status timeout")

            with (
                patch("miot_api_server.provider.mijiaAPI", return_value=FakeApi()),
                patch("miot_api_server.provider.LOGGER.warning") as warning_mock,
            ):
                result = provider.auth_status()

            warning_mock.assert_called_once()
            self.assertEqual(
                result,
                {
                    "logged_in": False,
                    "has_auth_file": True,
                    "pending_login_session_count": 0,
                },
            )

    def test_miot_spec_dependency_requests_get_uses_default_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            provider = MijiaProvider(self._settings(Path(raw_root)))

            def fake_get(url: str, **kwargs: object) -> SimpleNamespace:
                return SimpleNamespace(url=url, kwargs=kwargs)

            with patch(
                "miot_api_server.provider.mijia_devices.requests.get",
                side_effect=fake_get,
            ):
                with provider._miot_spec_requests_timeout():
                    response = mijia_devices.requests.get("https://spec.example")

            self.assertEqual(
                response.kwargs["timeout"], MIJIA_NETWORK_TIMEOUT_SECONDS
            )


if __name__ == "__main__":
    unittest.main()
