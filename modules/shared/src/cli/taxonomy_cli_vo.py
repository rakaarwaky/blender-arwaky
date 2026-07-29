"""CLI value objects — result envelope and error structures."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CliErrorVo:
    category: str
    ref: str
    message: str = "Operation failed"
    detail: str | None = None


@dataclass(frozen=True)
class CliResultVo:
    success: bool
    message: str | None = None
    error: str | None = None
    category: str | None = None
    ref: str | None = None
    warnings: list[str] | None = None
    data: dict[str, Any] | None = None
