from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class BalanceResponse:
    balance: float


@dataclass
class NumberResponse:
    activation_id: int
    phone_number: str


@dataclass
class StatusResponse:
    status: str
    code: Optional[str] = None
    sms_text: Optional[str] = None


@dataclass
class RateLimitInfo:
    limit: int
    remaining: int
