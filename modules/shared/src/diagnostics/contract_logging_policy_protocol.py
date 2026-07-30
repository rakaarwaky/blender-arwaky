"""Diagnostics domain contract: logging policy protocol."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_diagnostics_vo import LogRecordRequestVO, LogResultVO


class LoggingPolicyProtocol(ABC):
    """Contract protocol for diagnostic logging policy.

    FR-DIA-004: Diagnostic logging policy enforcing level filtering,
    structured output formatting, secret redaction, and log rotation.
    """

    @abstractmethod
    async def log_record(
        self,
        request: LogRecordRequestVO,
    ) -> LogResultVO:
        """Process and output a structured log record."""
        ...

    @abstractmethod
    async def set_min_level(self, level: str) -> None:
        """Set the minimum logging severity level threshold."""
        ...
