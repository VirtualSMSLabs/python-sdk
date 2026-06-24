from __future__ import annotations

import hashlib
import platform
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Type
from urllib.parse import urlencode

from virtualsms.constants import PoolProvider
from virtualsms.exceptions import VirtualSMSException
from virtualsms.parser import TextResponseParser
from virtualsms.response import BalanceResponse, NumberResponse, RateLimitInfo, StatusResponse
from virtualsms.transport import Response, Transport, UrllibTransport


class VirtualSMSClient:
    VERSION = "1.1.0"
    SDK_LANGUAGE = "python"

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.virtualsms.de",
        transport: Optional[Transport] = None,
    ):
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._transport = transport if transport is not None else UrllibTransport()
        self._parser = TextResponseParser()
        self._machine_id = hashlib.sha256(
            (platform.platform() + sys.implementation.name).encode("utf-8")
        ).hexdigest()[:32]
        self._rate_limit_info: Optional[RateLimitInfo] = None

    def get_rate_limit_info(self) -> Optional[RateLimitInfo]:
        return self._rate_limit_info

    def get_balance(self) -> BalanceResponse:
        response = self._call_api("getBalance")
        parsed = self._parser.parse(response.body)
        self._ensure_success(parsed, response)
        return BalanceResponse(balance=parsed.data["balance"])

    def get_countries(self, pool_provider: Optional[str] = None) -> Dict[str, Any]:
        response = self._call_api("getCountries", {"poolProvider": pool_provider})
        parsed = self._parser.parse(response.body)
        self._ensure_success(parsed, response)
        return parsed.data["decoded"]

    def get_services_list(
        self,
        country: Optional[int] = None,
        lang: Optional[str] = None,
    ) -> Dict[str, Any]:
        response = self._call_api(
            "getServicesList",
            {"country": country, "lang": lang},
        )
        parsed = self._parser.parse(response.body)
        self._ensure_success(parsed, response)
        return parsed.data["decoded"]

    def get_operators(
        self,
        country: int,
        pool_provider: Optional[str] = None,
    ) -> List[str]:
        response = self._call_api(
            "getOperators",
            {"country": country, "poolProvider": pool_provider},
        )
        parsed = self._parser.parse(response.body)
        self._ensure_success(parsed, response)
        decoded = parsed.data["decoded"]
        return decoded.get("countryOperators", decoded)

    def get_prices(
        self,
        service: Optional[str] = None,
        country: Optional[int] = None,
        pool_provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        response = self._call_api(
            "getPrices",
            {"service": service, "country": country, "poolProvider": pool_provider},
        )
        parsed = self._parser.parse(response.body)
        self._ensure_success(parsed, response)
        return parsed.data["decoded"]

    def get_prices_extended(
        self,
        service: Optional[str] = None,
        country: Optional[int] = None,
        free_price: Optional[bool] = None,
        pool_provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        response = self._call_api(
            "getPricesExtended",
            {
                "service": service,
                "country": country,
                "freePrice": "true" if free_price is True else ("false" if free_price is False else None),
                "poolProvider": pool_provider,
            },
        )
        parsed = self._parser.parse(response.body)
        self._ensure_success(parsed, response)
        return parsed.data["decoded"]

    def get_prices_verification(
        self,
        service: Optional[str] = None,
        pool_provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        response = self._call_api(
            "getPricesVerification",
            {"service": service, "poolProvider": pool_provider},
        )
        parsed = self._parser.parse(response.body)
        self._ensure_success(parsed, response)
        return parsed.data["decoded"]

    def get_numbers_status(
        self,
        country: int,
        operator: Optional[str] = None,
        pool_provider: Optional[str] = None,
    ) -> Dict[str, int]:
        response = self._call_api(
            "getNumbersStatus",
            {"country": country, "operator": operator, "poolProvider": pool_provider},
        )
        parsed = self._parser.parse(response.body)
        self._ensure_success(parsed, response)
        return parsed.data["decoded"]

    def get_number(
        self,
        service: str,
        country: int,
        max_price: Optional[float] = None,
        operator: Optional[str] = None,
        phone_exception: Optional[str] = None,
        forward: Optional[bool] = None,
        activation_type: Optional[int] = None,
        language: Optional[str] = None,
        use_cashback: Optional[bool] = None,
        user_id: Optional[str] = None,
        ref: Optional[str] = None,
        pool_provider: Optional[str] = None,
    ) -> NumberResponse:
        response = self._call_api(
            "getNumber",
            {
                "service": service,
                "country": country,
                "maxPrice": max_price,
                "operator": operator,
                "phoneException": phone_exception,
                "forward": "1" if forward is True else ("0" if forward is False else None),
                "activationType": activation_type,
                "language": language,
                "useCashBack": "true" if use_cashback is True else ("false" if use_cashback is False else None),
                "userId": user_id,
                "ref": ref,
                "poolProvider": pool_provider,
            },
        )
        parsed = self._parser.parse(response.body)
        self._ensure_success(parsed, response)
        return NumberResponse(
            activation_id=parsed.data["activation_id"],
            phone_number=parsed.data["phone_number"],
        )

    def get_number_v2(
        self,
        service: str,
        country: int,
        max_price: Optional[float] = None,
        operator: Optional[str] = None,
        phone_exception: Optional[str] = None,
        forward: Optional[bool] = None,
        activation_type: Optional[int] = None,
        language: Optional[str] = None,
        use_cashback: Optional[bool] = None,
        user_id: Optional[str] = None,
        ref: Optional[str] = None,
        order_id: Optional[str] = None,
        pool_provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        response = self._call_api(
            "getNumberV2",
            {
                "service": service,
                "country": country,
                "maxPrice": max_price,
                "operator": operator,
                "phoneException": phone_exception,
                "forward": "1" if forward is True else ("0" if forward is False else None),
                "activationType": activation_type,
                "language": language,
                "useCashBack": "true" if use_cashback is True else ("false" if use_cashback is False else None),
                "userId": user_id,
                "ref": ref,
                "orderId": order_id,
                "poolProvider": pool_provider,
            },
        )
        parsed = self._parser.parse(response.body)
        self._ensure_success(parsed, response)
        return parsed.data["decoded"]

    def set_status(self, id: int, status: int) -> str:
        response = self._call_api("setStatus", {"id": id, "status": status})
        parsed = self._parser.parse(response.body)
        self._ensure_success(parsed, response)
        return parsed.data["status"]

    def get_status(self, id: int) -> StatusResponse:
        response = self._call_api("getStatus", {"id": id})
        parsed = self._parser.parse(response.body)
        self._ensure_success(parsed, response)
        return StatusResponse(
            status=parsed.data["status"],
            code=parsed.data.get("code"),
            sms_text=parsed.data.get("sms_text"),
        )

    def get_status_v2(self, id: int) -> Dict[str, Any]:
        response = self._call_api("getStatusV2", {"id": id})
        parsed = self._parser.parse(response.body)
        self._ensure_success(parsed, response)
        return parsed.data["decoded"]

    def get_active_activations(self) -> List[Dict[str, Any]]:
        response = self._call_api("getActiveActivations")
        parsed = self._parser.parse(response.body)
        self._ensure_success(parsed, response)
        decoded = parsed.data["decoded"]
        return decoded.get("activeActivations", [])

    def check_extra_activation(self, id: int) -> Dict[str, Any]:
        response = self._call_api("checkExtraActivation", {"id": id})
        parsed = self._parser.parse(response.body)
        self._ensure_success(parsed, response)
        return parsed.data["decoded"]

    def get_extra_activation(self, id: int) -> NumberResponse:
        response = self._call_api("getExtraActivation", {"id": id})
        parsed = self._parser.parse(response.body)
        self._ensure_success(parsed, response)
        return NumberResponse(
            activation_id=parsed.data["activation_id"],
            phone_number=parsed.data["phone_number"],
        )

    def get_top_countries_by_service(self, service: str) -> List[Dict[str, Any]]:
        response = self._call_api("getListOfTopCountriesByService", {"service": service})
        parsed = self._parser.parse(response.body)
        self._ensure_success(parsed, response)
        return parsed.data["decoded"]

    def get_notifications(self) -> Dict[str, Any]:
        response = self._call_api("getNotifications")
        parsed = self._parser.parse(response.body)
        self._ensure_success(parsed, response)
        return parsed.data["decoded"]

    def _call_api(self, action: str, params: Optional[Dict[str, Any]] = None) -> Response:
        query_params: Dict[str, Any] = {"api_key": self._api_key, "action": action}
        if params:
            for key, value in params.items():
                if value is not None:
                    query_params[key] = value

        url = self._base_url + "/stubs/handler_api?" + urlencode(query_params)
        headers = self._build_headers()
        response = self._transport.send(url, headers)
        self._rate_limit_info = self._extract_rate_limit_info(response.headers)
        return response

    def _extract_rate_limit_info(self, headers: Dict[str, str]) -> Optional[RateLimitInfo]:
        limit = self._parse_int_header(headers, "X-RateLimit-Limit")
        remaining = self._parse_int_header(headers, "X-RateLimit-Remaining")

        if limit is None and remaining is None:
            return None

        return RateLimitInfo(
            limit=limit if limit is not None else 0,
            remaining=remaining if remaining is not None else 0,
        )

    @staticmethod
    def _parse_int_header(headers: Dict[str, str], name: str) -> Optional[int]:
        value = headers.get(name)
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def _build_headers(self) -> Dict[str, str]:
        return {
            "X-SDK-Version": self.VERSION,
            "X-SDK-Language": self.SDK_LANGUAGE,
            "X-SDK-Machine-Id": self._machine_id,
            "X-SDK-Timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _ensure_success(self, parsed, response: Response) -> None:
        if not parsed.is_success:
            retry_after = None
            if response.headers.get("Retry-After"):
                try:
                    retry_after = int(response.headers["Retry-After"])
                except (ValueError, TypeError):
                    retry_after = None
            rate_limit_limit = self._parse_int_header(response.headers, "X-RateLimit-Limit")
            rate_limit_remaining = self._parse_int_header(response.headers, "X-RateLimit-Remaining")
            raise VirtualSMSException.from_error_code(
                error_code=parsed.error_code or "UNKNOWN",
                http_status=response.status_code,
                retry_after=retry_after,
                rate_limit_limit=rate_limit_limit,
                rate_limit_remaining=rate_limit_remaining,
            )
