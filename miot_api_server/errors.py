from __future__ import annotations


class AppError(Exception):
    """应用层显式错误，统一带上 HTTP 状态码。"""

    status_code = 400
    error_code = "bad_request"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class AuthenticationRequiredError(AppError):
    status_code = 409
    error_code = "authentication_required"


class LoginSessionNotFoundError(AppError):
    status_code = 404
    error_code = "login_session_not_found"


class LoginSessionExpiredError(AppError):
    status_code = 410
    error_code = "login_session_expired"


class LoginPendingError(AppError):
    status_code = 408
    error_code = "login_pending"


class LoginProcessError(AppError):
    status_code = 400
    error_code = "login_process_error"


class DeviceNotFoundError(AppError):
    status_code = 404
    error_code = "device_not_found"


class DeviceCapabilityError(AppError):
    status_code = 400
    error_code = "device_capability_error"


class DeviceCapabilityNotSupportedError(AppError):
    status_code = 409
    error_code = "device_capability_not_supported"


class DeviceCapabilitySelectionRequiredError(AppError):
    status_code = 409
    error_code = "device_capability_selection_required"
