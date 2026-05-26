from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import datetime, timedelta
from html import unescape
from io import BytesIO
import json
from json import JSONDecodeError
import logging
import re
import time
import secrets
from typing import Any

import qrcode
from qrcode.image.svg import SvgImage
import requests
from mijiaAPI import (
    APIError,
    GetDeviceInfoError,
    LoginError,
    get_device_info,
    mijiaAPI,
)

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
MIOT_SPEC_URL = "https://home.miot-spec.com/spec/"
LOGGER = logging.getLogger(__name__)


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
        try:
            devices = api.get_devices_list() + api.get_shared_devices_list()
        except LoginError as exc:
            raise AuthenticationRequiredError(
                "米家认证状态已失效，请重置测试状态后重新扫码登录"
            ) from exc
        except requests.exceptions.RequestException as exc:
            raise LoginProcessError(f"米家设备列表请求失败：{exc}") from exc

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

    def _normalize_miot_property_type(self, prop: dict[str, Any]) -> str:
        prop_format = str(prop.get("format", ""))
        if prop_format.startswith("int"):
            return "int"
        if prop_format.startswith("uint"):
            return "uint"
        return prop_format

    def _build_spec_from_current_page(
        self, model: str, page_data: dict[str, Any]
    ) -> dict[str, Any]:
        props = page_data["props"]
        product = props.get("product") or {}
        tree = props["tree"]
        result: dict[str, Any] = {
            "name": product.get("name") or props.get("spec", {}).get("model", model),
            "model": product.get("model") or model,
            "properties": [],
            "actions": [],
        }

        property_names: set[str] = set()
        action_names: set[str] = set()
        for service in tree.get("services", []):
            siid = int(service["iid"])
            service_name = service.get("type") or f"service-{siid}"
            for prop in service.get("properties", []):
                name = prop["type"]
                if name in property_names:
                    name = f"{service_name}-{name}"
                property_names.add(name)

                access = prop.get("access", [])
                item = {
                    "name": name,
                    "description": prop.get("description", ""),
                    "type": self._normalize_miot_property_type(prop),
                    "rw": "".join(
                        [
                            "r" if "read" in access else "",
                            "w" if "write" in access else "",
                        ]
                    ),
                    "unit": prop.get("unit"),
                    "range": prop.get("valueRange"),
                    "value-list": prop.get("valueList"),
                    "method": {
                        "siid": siid,
                        "piid": int(prop["iid"]),
                    },
                }
                result["properties"].append(
                    {
                        key: None if value == "none" else value
                        for key, value in item.items()
                    }
                )

            for action in service.get("actions", []):
                name = action["type"]
                if name in action_names:
                    name = f"{service_name}-{name}"
                action_names.add(name)
                result["actions"].append(
                    {
                        "name": name,
                        "description": action.get("description", ""),
                        "method": {
                            "siid": siid,
                            "aiid": int(action["iid"]),
                        },
                    }
                )

        return result

    def _fetch_device_info_from_current_spec_page(self, model: str) -> dict[str, Any]:
        response = requests.get(
            f"{MIOT_SPEC_URL}{model}",
            headers={"User-Agent": "miot-api-server/spec-parser"},
            timeout=30,
        )
        response.raise_for_status()

        # home.miot-spec.com 当前把页面状态放在 script 文本里，而不是旧版 data-page 属性值里。
        match = re.search(
            r'<script[^>]*data-page="app"[^>]*type="application/json"[^>]*>'
            r"(.*?)</script>",
            response.text,
            flags=re.S,
        )
        if match is None:
            raise GetDeviceInfoError(model)

        page_data = json.loads(unescape(match.group(1)))
        result = self._build_spec_from_current_page(model, page_data)
        cache_dir = self.settings.spec_cache_dir
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / f"{model}.json"
        with cache_file.open("w", encoding="utf-8") as file:
            json.dump(result, file, indent=2, ensure_ascii=False)
        return result

    def _get_device_info(self, model: str) -> dict[str, Any]:
        try:
            return get_device_info(model, cache_path=self.settings.spec_cache_dir)
        except (JSONDecodeError, GetDeviceInfoError):
            LOGGER.info(
                "Falling back to current MIoT spec page parser for model %s", model
            )
            return self._fetch_device_info_from_current_spec_page(model)

    def _get_bool_power_candidates(self, model: str) -> list[DevicePowerCandidate]:
        try:
            spec = self._get_device_info(model)
        except JSONDecodeError as exc:
            # 米家 spec 服务偶尔会返回非 JSON 内容；设备列表仍应可用，只降级该型号的能力探测。
            LOGGER.warning("Failed to parse MIoT spec for model %s: %s", model, exc)
            return []
        except requests.exceptions.RequestException as exc:
            # spec 查询失败不代表设备列表不可用，避免单个型号能力探测拖垮整页。
            LOGGER.warning("Failed to fetch MIoT spec for model %s: %s", model, exc)
            return []

        candidates: list[DevicePowerCandidate] = []
        for prop in spec.get("properties", []):
            if not self._is_power_property(prop):
                continue
            method = prop.get("method")
            if (
                not isinstance(method, dict)
                or "siid" not in method
                or "piid" not in method
            ):
                continue
            candidates.append(
                DevicePowerCandidate(
                    name=prop["name"],
                    description=prop.get("description", prop["name"]),
                    siid=method["siid"],
                    piid=method["piid"],
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

    def _select_power_candidate(
        self, model: str, preferred_name: str | None
    ) -> DevicePowerCandidate:
        power = self._build_power_capability(model)
        if not power.supported:
            raise DeviceCapabilityNotSupportedError("该设备不支持 power 能力")

        candidate_names = [item.name for item in power.candidates]
        # 对外只接受属性名，不把 siid/piid 这些 MIoT 细节暴露给部署者手工填写。
        if preferred_name is not None:
            for candidate in power.candidates:
                if preferred_name == candidate.name:
                    return candidate
            raise DeviceCapabilityError(
                f"未找到 property_name={preferred_name}，可选值为 {candidate_names}"
            )

        if power.default_property_name is not None:
            for candidate in power.candidates:
                if power.default_property_name == candidate.name:
                    return candidate

        raise DeviceCapabilitySelectionRequiredError(
            f"该设备存在多个 power 候选属性，请显式指定 property_name，可选值为 {candidate_names}"
        )

    def _set_miot_property(
        self, api: mijiaAPI, did: str, candidate: DevicePowerCandidate, value: bool
    ) -> None:
        payload = {
            "did": did,
            "siid": candidate.siid,
            "piid": candidate.piid,
            "value": value,
        }
        try:
            result = api.set_devices_prop(payload)
        except LoginError as exc:
            raise AuthenticationRequiredError(
                "米家认证状态已失效，请重置测试状态后重新扫码登录"
            ) from exc
        except APIError as exc:
            raise DeviceCapabilityError(f"米家设备控制请求失败：{exc}") from exc
        except requests.exceptions.RequestException as exc:
            raise DeviceCapabilityError(f"米家设备控制网络请求失败：{exc}") from exc

        if not isinstance(result, dict):
            raise DeviceCapabilityError(f"米家设备控制返回格式异常：{result}")

        code = result.get("code", 0)
        if code == 1:
            # 米家网关已接收但不保证立即完成，仍按成功返回并在日志里保留真实结果。
            LOGGER.warning("MIoT property set accepted by gateway: %s", result)
            return
        if code != 0:
            message = result.get("message", "未知错误")
            raise DeviceCapabilityError(
                f"米家设备控制失败：code={code}, message={message}"
            )

    def set_device_power(
        self, did: str, is_on: bool, preferred_name: str | None
    ) -> dict[str, Any]:
        device = self._find_device(did)
        power_candidate = self._select_power_candidate(device["model"], preferred_name)
        api = self._require_api()
        self._set_miot_property(api, device["did"], power_candidate, is_on)
        return {
            "did": device["did"],
            "name": device.get("name", device["did"]),
            "model": device["model"],
            "power_property_name": power_candidate.name,
            "is_on": is_on,
        }
