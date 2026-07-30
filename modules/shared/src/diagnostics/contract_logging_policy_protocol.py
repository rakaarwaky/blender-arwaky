"""Diagnostics domain contract: logging policy protocol (ABC based).

Defines the protocol for enforcing one structured logging policy for
the whole system, with redaction applied at ingestion.

FR-DIA-004: Structured Logging Policy
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_diagnostics_vo import LogRecordRequestVO, LogResultVO


class LoggingPolicyProtocol(ABC):
    """Protocol for enforcing structured logging policy with redaction."""

    @abstractmethod
    async def log_record(
        self,
        request: LogRecordRequestVO,
    ) -> LogResultVO:
        """Write sanitized structured log entry.

        FR-DIA-004: All features log through diagnostics policy.
        Redaction applied at ingestion before any destination write.
        Logging must not block callers; records buffer under backpressure.
        No raw code/tokens/credentials/passwords/paths at any level.
        """
        ...
