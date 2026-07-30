"""Diagnostics domain contract: audit state provider protocol."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_diagnostics_vo import AuditRecordVO, AuditSummaryVO


class AuditStateProviderProtocol(ABC):
    """Provides recent audit state for diagnostics snapshots."""

    @abstractmethod
    async def get_audit_summary(self) -> AuditSummaryVO | None: ...
