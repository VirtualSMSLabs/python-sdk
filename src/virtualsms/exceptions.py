from __future__ import annotations

from typing import Optional


class VirtualSMSException(Exception):
    def __init__(
        self,
        message: str,
        error_code: str,
        http_status: int,
        retry_after: Optional[int] = None,
    ):
        super().__init__(message)
        self.error_code = error_code
        self.http_status = http_status
        self.retry_after = retry_after

    @staticmethod
    def from_error_code(
        error_code: str,
        http_status: int,
        retry_after: Optional[int] = None,
        rate_limit_limit: Optional[int] = None,
        rate_limit_remaining: Optional[int] = None,
    ) -> "VirtualSMSException":
        message = VirtualSMSException._message_for_code(error_code)

        if error_code in ("BAD_KEY", "BANNED", "PURCHASE_RESTRICTED", "SERVICE_RESTRICTED"):
            if http_status == 429:
                return RateLimitException(
                    message, error_code, http_status,
                    retry_after=retry_after or 0,
                    rate_limit_limit=rate_limit_limit,
                    rate_limit_remaining=rate_limit_remaining,
                )
            return AuthenticationException(message, error_code, http_status)

        if error_code == "NO_BALANCE":
            return InsufficientBalanceException(message, error_code, http_status)

        if error_code == "NO_NUMBERS":
            return NoNumbersException(message, error_code, http_status)

        if error_code in (
            "WRONG_SERVICE",
            "WRONG_COUNTRY",
            "BAD_ACTION",
            "BAD_STATUS",
            "NO_PRICES",
            "INVALID_PROVIDER",
            "WRONG_EXCEPTION_PHONE",
            "WRONG_SECURITY",
        ):
            return ValidationException(message, error_code, http_status)

        if error_code in (
            "NO_ACTIVATION",
            "WRONG_ACTIVATION_ID",
            "EARLY_CANCEL_DENIED",
            "RENEW_ACTIVATION_NOT_AVAILABLE",
            "NEW_ACTIVATION_IMPOSSIBLE",
            "SIM_OFFLINE",
        ):
            return ActivationException(message, error_code, http_status)

        if error_code == "CONCURRENT_LIMIT":
            return RateLimitException(
                message, error_code, http_status,
                retry_after=retry_after or 0,
                rate_limit_limit=rate_limit_limit,
                rate_limit_remaining=rate_limit_remaining,
            )

        return ServerException(message, error_code, http_status)

    @staticmethod
    def _message_for_code(error_code: str) -> str:
        messages = {
            "BAD_KEY": "Invalid or missing API key.",
            "BANNED": "Account is banned or IP is blocked.",
            "PURCHASE_RESTRICTED": "User is restricted from purchasing numbers.",
            "SERVICE_RESTRICTED": "This service is restricted for your account.",
            "NO_BALANCE": "Insufficient balance to complete the operation.",
            "NO_NUMBERS": "No phone numbers available for the requested service and country.",
            "WRONG_SERVICE": "Invalid or missing service code.",
            "WRONG_COUNTRY": "Invalid or missing country ID.",
            "BAD_ACTION": "Invalid or unknown action.",
            "BAD_STATUS": "Invalid status code provided to setStatus.",
            "NO_PRICES": "No pricing data available for the requested parameters.",
            "INVALID_PROVIDER": "The specified pool provider was not found or is disabled.",
            "WRONG_EXCEPTION_PHONE": "Invalid phone exception parameter.",
            "WRONG_SECURITY": "Security validation failed.",
            "NO_ACTIVATION": "Activation not found or does not belong to this account.",
            "WRONG_ACTIVATION_ID": "Invalid activation ID.",
            "EARLY_CANCEL_DENIED": "Cannot cancel within the first 5 minutes of activation.",
            "RENEW_ACTIVATION_NOT_AVAILABLE": "This number is not available for reactivation.",
            "NEW_ACTIVATION_IMPOSSIBLE": "Cannot create an additional activation on this number.",
            "SIM_OFFLINE": "The SIM card is currently offline.",
            "CONCURRENT_LIMIT": "Too many concurrent activations.",
            "ERROR_SQL": "An internal server error occurred.",
            "NO_METRICS": "Not enough data available for this service.",
            "NO_ACTIVATIONS": "No active activations found.",
        }
        return messages.get(error_code, "An unexpected error occurred.")


class AuthenticationException(VirtualSMSException):
    pass


class InsufficientBalanceException(VirtualSMSException):
    pass


class NoNumbersException(VirtualSMSException):
    pass


class ValidationException(VirtualSMSException):
    pass


class ActivationException(VirtualSMSException):
    pass


class RateLimitException(VirtualSMSException):
    def __init__(
        self,
        message: str,
        error_code: str,
        http_status: int,
        retry_after: int = 0,
        rate_limit_limit: Optional[int] = None,
        rate_limit_remaining: Optional[int] = None,
    ):
        super().__init__(message, error_code, http_status, retry_after=retry_after)
        self.rate_limit_limit = rate_limit_limit
        self.rate_limit_remaining = rate_limit_remaining


class ServerException(VirtualSMSException):
    pass
