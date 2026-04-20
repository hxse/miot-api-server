from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


SessionId = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=128)
]
PowerPropertyName = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1)
]


class ErrorResponse(BaseModel):
    detail: str
    error_code: str


class HealthResponse(BaseModel):
    status: str


class AuthStatusResponse(BaseModel):
    logged_in: bool
    has_auth_file: bool
    pending_login_session_count: int


class AuthResetResponse(BaseModel):
    auth_file_deleted: bool
    pending_login_sessions_cleared: int


class LoginStartResponse(BaseModel):
    already_logged_in: bool = False
    session_id: str | None = None
    login_url: str | None = None
    qr_image_url: str | None = None
    qr_data_url: str | None = None


class LoginFinishRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: SessionId
    timeout_seconds: int = Field(default=120, ge=1, le=180)


class LoginFinishResponse(BaseModel):
    user_id: str
    c_user_id: str
    expire_time: int


class DevicePowerCandidate(BaseModel):
    name: str
    description: str
    siid: int
    piid: int


class DevicePowerCapability(BaseModel):
    supported: bool
    default_property_name: str | None
    selection_required: bool
    candidates: list[DevicePowerCandidate]


class DeviceSummary(BaseModel):
    did: str
    name: str
    model: str
    home_id: str
    is_online: bool
    power: DevicePowerCapability


class DevicePowerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    property_name: PowerPropertyName | None = None


class DevicePowerResponse(BaseModel):
    did: str
    name: str
    model: str
    power_property_name: str
    is_on: bool
