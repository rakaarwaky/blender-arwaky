"""Diagnostics domain contract: snapshot provision protocol (ABC based).

Defines the protocol for serving one canonical point-in-time snapshot
combining health, metrics, recent audit summary, and config metadata.

FR-DIA-005: Provide Diagnostics Snapshot
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_diagnostics_vo import DiagnosticsSnapshotVO


class SnapshotProvisionProtocol(ABC):
    """Protocol for providing diagnostics snapshots to CLI/MCP consumers."""

    @abstractmethod
    async def get_snapshot(
        self,
        detail_level: str = "summary",
        section_filter: list[str] | None = None,
    ) -> DiagnosticsSnapshotVO:
        """Serve one canonical point-in-time diagnostics snapshot.

        FR-DIA-005: CLI/MCP consume snapshots — never probe subsystems or compute health themselves.
        Consistent point-in-time view from composed state. Detail: summary (safe for routine)
        or full (per-subsystem/metric depth). Section filter: health/metrics/audit only.
        Identical shape for all consumers; formatting belongs to consumer.
        Read-only, idempotent. Bounded latency — reuse composed state, recompute only when freshness expired.
        Stale sections carry staleness indicators. No secrets/raw code/credentials/sensitive paths;
        audit summary = categories+counts. First run with no history → empty-window indicators.

        Args:
            detail_level: "summary" or "full".
            section_filter: List of sections to include (health, metrics, audit_summary).

        Returns:
            DiagnosticsSnapshotVO with health, metrics, audit summary, config metadata, staleness.
        """
        ...
