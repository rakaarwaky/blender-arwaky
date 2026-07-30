"""Diagnostics domain contract: snapshot provision protocol (ABC based).

Defines the protocol for serving one canonical point-in-time snapshot
combining health, metrics, recent audit summary, and config metadata.

FR-DIA-005: Provide Diagnostics Snapshot
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_diagnostics_vo import DiagnosticsSnapshotVO, SnapshotRequestVO


class SnapshotProvisionProtocol(ABC):
    """Protocol for providing diagnostics snapshots to CLI/MCP consumers."""

    @abstractmethod
    async def get_snapshot(
        self,
        request: SnapshotRequestVO,
    ) -> DiagnosticsSnapshotVO:
        """Serve one canonical point-in-time diagnostics snapshot.

        FR-DIA-005: CLI/MCP consume snapshots — never probe subsystems or compute health themselves.
        """
        ...
