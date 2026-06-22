from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


_ERROR_CODES: List[str] = [
    "BAD_KEY",
    "BANNED",
    "NO_BALANCE",
    "NO_NUMBERS",
    "WRONG_SERVICE",
    "WRONG_COUNTRY",
    "NO_ACTIVATION",
    "BAD_ACTION",
    "BAD_STATUS",
    "EARLY_CANCEL_DENIED",
    "WRONG_ACTIVATION_ID",
    "RENEW_ACTIVATION_NOT_AVAILABLE",
    "PURCHASE_RESTRICTED",
    "SERVICE_RESTRICTED",
    "CONCURRENT_LIMIT",
    "NO_PRICES",
    "INVALID_PROVIDER",
    "ERROR_SQL",
    "NO_METRICS",
    "NO_ACTIVATIONS",
    "NEW_ACTIVATION_IMPOSSIBLE",
    "SIM_OFFLINE",
    "WRONG_EXCEPTION_PHONE",
    "WRONG_SECURITY",
]

_STATUS_TYPES = ["STATUS_WAIT_CODE", "STATUS_WAIT_RETRY", "STATUS_CANCEL"]
_SET_STATUS_TYPES = ["ACCESS_READY", "ACCESS_RETRY_GET", "ACCESS_ACTIVATION", "ACCESS_CANCEL"]


@dataclass
class ParsedResponse:
    is_success: bool = False
    type: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class TextResponseParser:
    def parse(self, body: str) -> ParsedResponse:
        body = body.strip()

        if body == "":
            return ParsedResponse(
                is_success=False,
                error_code="UNKNOWN",
                error_message="Empty response body.",
            )

        try:
            decoded = json.loads(body)
            if isinstance(decoded, (dict, list)):
                return self._parse_json(decoded, body)
        except (json.JSONDecodeError, ValueError):
            pass

        if body.startswith("ACCESS_BALANCE:"):
            balance = float(body[len("ACCESS_BALANCE:") :])
            return ParsedResponse(
                is_success=True,
                type="balance",
                data={"balance": balance},
            )

        if body.startswith("ACCESS_NUMBER:"):
            parts = body.split(":", 2)
            if len(parts) == 3:
                return ParsedResponse(
                    is_success=True,
                    type="number",
                    data={
                        "activation_id": int(parts[1]),
                        "phone_number": parts[2],
                    },
                )

        if body.startswith("STATUS_OK:"):
            code = body[len("STATUS_OK:") :]
            return ParsedResponse(
                is_success=True,
                type="status",
                data={
                    "status": "STATUS_OK",
                    "code": code if code != "" else None,
                    "sms_text": None,
                },
            )

        if body == "STATUS_OK":
            return ParsedResponse(
                is_success=True,
                type="status",
                data={"status": "STATUS_OK", "code": None, "sms_text": None},
            )

        if body.startswith("FULL_SMS:"):
            sms_text = body[len("FULL_SMS:") :]
            return ParsedResponse(
                is_success=True,
                type="status",
                data={"status": "FULL_SMS", "code": None, "sms_text": sms_text},
            )

        for status in _STATUS_TYPES:
            if body == status:
                return ParsedResponse(
                    is_success=True,
                    type="status",
                    data={"status": status, "code": None, "sms_text": None},
                )

        for status in _SET_STATUS_TYPES:
            if body == status:
                return ParsedResponse(
                    is_success=True,
                    type="set_status",
                    data={"status": status},
                )

        error_code = self._detect_error_code(body)
        if error_code is not None:
            return ParsedResponse(is_success=False, error_code=error_code)

        return ParsedResponse(
            is_success=False,
            error_code="UNKNOWN",
            error_message=body,
        )

    def _parse_json(self, decoded: Any, raw: str) -> ParsedResponse:
        if isinstance(decoded, dict):
            if decoded.get("status") == "error":
                error_code = decoded.get("errorCode", "UNKNOWN")
                error_message = decoded.get("error", "Unknown error.")
                return ParsedResponse(
                    is_success=False,
                    error_code=error_code,
                    error_message=error_message,
                )

        return ParsedResponse(
            is_success=True,
            type="json",
            data={"raw": raw, "decoded": decoded},
        )

    def _detect_error_code(self, body: str) -> Optional[str]:
        for code in _ERROR_CODES:
            if body == code:
                return code
        return None
