from __future__ import annotations

import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class Response:
    status_code: int
    body: str
    headers: Dict[str, str] = field(default_factory=dict)


class Transport(ABC):
    @abstractmethod
    def send(self, url: str, headers: dict) -> Response:
        ...


class UrllibTransport(Transport):
    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def send(self, url: str, headers: dict) -> Response:
        request = urllib.request.Request(url, method="GET")
        for key, value in headers.items():
            request.add_header(key, value)

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8")
                status_code = resp.getcode()
                response_headers = {k: v for k, v in resp.getheaders()}
                return Response(status_code, body, response_headers)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8") if e.fp else ""
            response_headers = {k: v for k, v in e.headers.items()} if e.headers else {}
            return Response(e.code, body, response_headers)
