from dataclasses import dataclass
from typing import Any


@dataclass
class ExternalServiceResponse:
    status_code: int
    body: dict[str, Any]
    elapsed_ms: int
