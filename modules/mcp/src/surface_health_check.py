"""Health Check for BlenderArwaky — delegates to diagnostics capability (AES compliant).

FR-MCP-001: Expose MCP Tools — register_health_check registers tool with MCP
FR-MCP-002: Route Tool Calls — get_container().diagnostics.get_snapshot provides health status
FR-MCP-003: Format MCP Responses — Prompt type wraps health check result

Routes health check queries to the diagnostics capability for subsystem
health snapshots. The surface delegates via the DI container to the
diagnostics aggregate, not the dispatcher orchestrator.
"""

from modules.mcp.src.agent_mcp_orchestrator import get_container
from modules.shared.src.common.taxonomy_core_vo import Prompt


class HealthCheckHandler:
    """Handler for health check operations."""

    @staticmethod
    def register_health_check(mcp):
        @mcp.tool()
        async def health_check() -> Prompt:
            """Check the health and connectivity of BlenderArwaky via diagnostics snapshot."""

            diagnostics = get_container().diagnostics
            snapshot = await diagnostics.get_snapshot()
            return Prompt(str(snapshot))
