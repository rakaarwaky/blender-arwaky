"""CLI value objects — result envelope and error structures."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CliErrorVo:
    """CLI error Value Object."""

    category: str
    ref: str
    message: str = "Operation failed"
    detail: str | None = None


@dataclass(frozen=True)
class CliResultVo:
    """CLI result envelope Value Object."""

    success: bool
    message: str | None = None
    error: str | None = None
    category: str | None = None
    ref: str | None = None
    warnings: list[str] | None = None
    data: dict[str, object] | None = None
