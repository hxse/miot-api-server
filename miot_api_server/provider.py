from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import datetime, timedelta
from io import BytesIO
import time
import secrets
from typing import Any

import qrcode
from qrcode.image.svg import SvgImage
import requests
from mijiaAPI import LoginError, get_device_info, mijiaAPI, mijiaDevice

from miot_api_server.config import Settings
from miot_api_server.errors import (
    AuthenticationRequiredError,
    DeviceCapabilityError,
    DeviceCapabilityNotSupportedError,
    DeviceCapabilitySelectionRequiredError,
    DeviceNotFoundError,
    LoginProcessError,
    LoginPendingError,
    LoginSessionExpiredError,
    LoginSessionNotFoundError,
)
from miot_api_server.schemas import (
    DevicePowerCapability,
    DevicePowerCandidate,
    DeviceSummary,
)


POWER_PROPERTY_PRIORITY = ("on", "switch_status", "switch", "power", "status")
POWER_PROPERTY_NAMES = frozenset(POWER_PROPERTY_PRIORITY)


@dataclass(slots=True)
class PendingLoginSession:
    session_id: str
    login_url: str
    qr_image_url: str
    lp: str
    created_at: float
    auth_data: dict[str, Any]


class MijiaProvider:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.pending_logins: dict[str, PendingLoginSession] = {}

    def _new_api(self) -> mijiaAPI:
        return mijiaAPI(auth_data_path=str(self.settings.auth_path))

    def _require_api(self) -> mijiaAPI:
        api = self._new_api()
        if not api.available:
            raise AuthenticationRequiredError("米家账号尚未完成登录初始化")
        return api

    def auth_status(self) -> dict[str, Any]:
        api = self._new_api()
        return {
            "logged_in": api.available,
            "has_auth_file": self.settings.auth_path.exists(),
            "pending_login_session_count": len(self.pending_logins),
        }

    def reset_auth_state(self) -> dict[str, Any]:
        cleared_sessions = len(self.pending_logins)
        self.pending_logins.clear()

        auth_file_deleted = False
        if self.settings.auth_path.exists():
            self.settings.auth_path.unlink()
            auth_file_deleted = True

        return {
            "auth_file_deleted": auth_file_deleted,
            "pending_login_sessions_cleared": cleared_sessions,
        }

    def _build_qr_data_url(self, login_url: str) -> str:
        # 优先在服务端直接生成二维码，避免前端依赖第三方图链导致图片加载失败。
        image = qrcode.make(login_url, image_factory=SvgImage)
        buffer = BytesIO()
        image.save(buffer)
        encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
        return f"data:image/svg+xml;base64,{encoded}"

    def start_login(self) -> dict[str, Any]:
        api = self._new_api()
        if api.available:
            return {"already_logged_in": True}

        # 这里复用 mijiaAPI 现成扫码流程的内部步骤，因此要求当前依赖解析保持在已验证版本。
        location_data = api._get_location()
        if (
            location_data.get("code") == 0
            and location_data.get("message") == "刷新Token成功"
        ):
            api._save_auth_data()
            api._init_session()
            return {"already_logged_in": True}

        location_data.update(
            {
                "theme": "",
                "bizDeviceType": "",
                "_hasLogo": "false",
                "_qrsize": "240",
                "_dc": str(int(time.time() * 1000)),
            }
        )
        headers = {
            "User-Agent": api.user_agent,
            "Accept-Encoding": "gzip",
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "keep-alive",
        }
        login_ret = requests.get(
            api.login_url, headers=headers, params=location_data, timeout=30
        )
        login_data = api._handle_ret(login_ret)

        session_id = secrets.token_urlsafe(18)
        self.pending_logins[session_id] = PendingLoginSession(
            session_id=session_id,
            login_url=login_data["loginUrl"],
            qr_image_url=login_data["qr"],
            lp=login_data["lp"],
            created_at=time.time(),
            auth_data=api.auth_data.copy(),
        )
        return {
            "already_logged_in": False,
            "session_id": session_id,
            "login_url": login_data["loginUrl"],
            "qr_image_url": login_data["qr"],
            "qr_data_url": self._build_qr_data_url(login_data["loginUrl"]),
        }

    def finish_login(self, session_id: str, timeout_seconds: int) -> dict[str, Any]:
        pending = self.pending_logins.get(session_id)
        if pending is None:
            raise LoginSessionNotFoundError("未找到对应的登录会话")
        if time.time() - pending.created_at > 180:
            self.pending_logins.pop(session_id, None)
            raise LoginSessionExpiredError("登录会话已过期，请重新开始扫码登录")

        api = self._new_api()
        api.auth_data.update(pending.auth_data)
        headers = {
            "User-Agent": api.user_agent,
            "Accept-Encoding": "gzip",
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "keep-alive",
        }
        session = requests.Session()
        try:
            lp_ret = session.get(pending.lp, headers=headers, timeout=timeout_seconds)
            lp_data = api._handle_ret(lp_ret)
        except requests.exceptions.Timeout as exc:
            raise LoginPendingError(
                "二维码尚未确认，请继续在米家 APP 中完成扫码"
            ) from exc
        except LoginError as exc:
            raise LoginProcessError(str(exc)) from exc

        auth_keys = [
            "psecurity",
            "nonce",
            "ssecurity",
            "passToken",
            "userId",
            "cUserId",
        ]
        for key in auth_keys:
            api.auth_data[key] = lp_data[key]
        session.get(lp_data["location"], headers=headers, timeout=30)
        api.auth_data.update(session.cookies.get_dict())
        api.auth_data["expireTime"] = int(
            (datetime.now() + timedelta(days=30)).timestamp() * 1000
        )
        api._save_auth_data()
        api._init_session()
        self.pending_logins.pop(session_id, None)
        return {
            "user_id": api.auth_data["userId"],
            "c_user_id": api.auth_data["cUserId"],
            "expire_time": api.auth_data["expireTime"],
        }

    def _list_devices_raw(self) -> list[dict[str, Any]]:
        api = self._require_api()
        devices = api.get_devices_list() + api.get_shared_devices_list()
        deduped: dict[str, dict[str, Any]] = {}
        for device in devices:
            deduped[device["did"]] = device
        return list(deduped.values())

    def _is_power_property(self, prop: dict[str, Any]) -> bool:
        # 只把明确表达电源语义的可写布尔属性纳入 power，避免误控普通布尔开关。
        if prop.get("type") != "bool":
            return False
        if "w" not in prop.get("rw", ""):
            return False
        return prop.get("name") in POWER_PROPERTY_NAMES

    def _get_bool_power_candidates(self, model: str) -> list[DevicePowerCandidate]:
        spec = get_device_info(model, cache_path=self.settings.spec_cache_dir)
        candidates: list[DevicePowerCandidate] = []
        for prop in spec.get("properties", []):
            if not self._is_power_property(prop):
                continue
            candidates.append(
                DevicePowerCandidate(
                    name=prop["name"],
                    description=prop["description"],
                    siid=prop["method"]["siid"],
                    piid=prop["method"]["piid"],
                )
            )
        return candidates

    def _find_device(self, did: str) -> dict[str, Any]:
        for device in self._list_devices_raw():
            if device["did"] == did:
                return device
        raise DeviceNotFoundError(f"未找到 did={did} 的设备")

    def _resolve_default_power_property_name(
        self, candidates: list[DevicePowerCandidate]
    ) -> str | None:
        for name in POWER_PROPERTY_PRIORITY:
            for candidate in candidates:
                if candidate.name == name:
                    return candidate.name

        return None

    def _build_power_capability(self, model: str) -> DevicePowerCapability:
        candidates = self._get_bool_power_candidates(model)
        if not candidates:
            return DevicePowerCapability(
                supported=False,
                default_property_name=None,
                selection_required=False,
                candidates=[],
            )

        default_property_name = self._resolve_default_power_property_name(candidates)
        return DevicePowerCapability(
            supported=True,
            default_property_name=default_property_name,
            selection_required=default_property_name is None,
            candidates=candidates,
        )

    def _summarize_device(self, device: dict[str, Any]) -> DeviceSummary:
        return DeviceSummary(
            did=device["did"],
            name=device.get("name", device["did"]),
            model=device["model"],
            home_id=str(device.get("home_id", "")),
            is_online=bool(device.get("isOnline", False)),
            power=self._build_power_capability(device["model"]),
        )

    def list_devices(self) -> list[DeviceSummary]:
        return [self._summarize_device(device) for device in self._list_devices_raw()]

    def get_device(self, did: str) -> DeviceSummary:
        return self._summarize_device(self._find_device(did))

    def _select_power_property_name(
        self, model: str, preferred_name: str | None
    ) -> str:
        power = self._build_power_capability(model)
        if not power.supported:
            raise DeviceCapabilityNotSupportedError("该设备不支持 power 能力")

        candidate_names = [item.name for item in power.candidates]
        # 对外只接受属性名，不把 siid/piid 这些 MIoT 细节暴露给部署者手工填写。
        if preferred_name is not None:
            if preferred_name in candidate_names:
                return preferred_name
            raise DeviceCapabilityError(
                f"未找到 property_name={preferred_name}，可选值为 {candidate_names}"
            )

        if power.default_property_name is not None:
            return power.default_property_name

        raise DeviceCapabilitySelectionRequiredError(
            f"该设备存在多个 power 候选属性，请显式指定 property_name，可选值为 {candidate_names}"
        )

    def set_device_power(
        self, did: str, is_on: bool, preferred_name: str | None
    ) -> dict[str, Any]:
        device = self._find_device(did)
        power_property_name = self._select_power_property_name(
            device["model"], preferred_name
        )
        api = self._require_api()
        power_device = mijiaDevice(api=api, did=device["did"])
        power_device.set(power_property_name, is_on)
        return {
            "did": device["did"],
            "name": device.get("name", device["did"]),
            "model": device["model"],
            "power_property_name": power_property_name,
            "is_on": is_on,
        }
