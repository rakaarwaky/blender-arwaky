"""MCP Tool 3: health_check — Delegates to diagnostics aggregate for system health.

FR-MCP-001: Expose MCP Tools — register_health_check registers tool with MCP
FR-MCP-002: Route Tool Calls — diagnostics aggregate get_snapshot provides health status
FR-MCP-003: Format MCP Responses — Prompt type wraps health check result
"""

from modules.diagnostics.src.root_diagnostics_container import create_diagnostics_feature
from modules.shared.src.common.taxonomy_core_vo import Prompt


class HealthCheckHandler:
    """Handler for the health_check MCP tool."""

    @staticmethod
    def register_health_check(mcp):
        """Register the health_check tool (MCP Tool #3)."""

        @mcp.tool()
        async def health_check() -> Prompt:
            """Check the health and connectivity of BlenderArwaky."""
            diagnostics = create_diagnostics_feature()
            snapshot = await diagnostics.get_snapshot()
            return Prompt(str(snapshot))
