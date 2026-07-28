"""Diagnostics domain contract: diagnostics snapshot protocol (ABC based).

Defines the protocol for serving one canonical, point-in-time diagnostics
snapshot combining health, metrics, recent audit summary, and config metadata.

FR-DIA-005: Provide Diagnostics Snapshot
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_core_vo import Details, ToolName


class DiagnosticsSnapshotProtocol(ABC):
    """Protocol for serving canonical diagnostics snapshots."""

    @abstractmethod
    async def get_snapshot(
        self,
        detail_level: str = "summary",
        section_filter: list[str] | None = None,
        source_tool: ToolName | None = None,
    ) -> Details:
        """Serve one canonical diagnostics snapshot.

        FR-DIA-005: CLI and MCP consume snapshots; they must never probe
        subsystems or compute health themselves. Snapshot is a consistent
        point-in-time view combining health, metrics, audit summary, and config.

        Args:
            detail_level: "summary" or "full".
            section_filter: Optional sections to include (health, metrics, audit, config).

        Returns:
            Dict with composed health, metrics snapshot, audit summary, and config metadata.
        """
        pass
