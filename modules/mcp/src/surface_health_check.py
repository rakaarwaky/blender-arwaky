"""Health Check for BlenderArwaky — delegates directly to Agent container aggregate (AES compliant).

FR-MCP-001: Expose MCP Tools — register_health_check registers tool with MCP
FR-MCP-002: Route Tool Calls — get_container().core_agent_orchestrator.execute_action routes health check
FR-MCP-003: Format MCP Responses — Prompt type wraps health check result
"""

from modules.mcp.src.container import get_container
from modules.shared.src.common.taxonomy_core_vo import Prompt


class HealthCheckHandler:
    """Handler for health check operations."""

    @staticmethod
    def register_health_check(mcp):
        @mcp.tool()
        async def health_check() -> Prompt:
            """Check the health and connectivity of BlenderArwaky via Agent aggregate."""

            orchestrator = get_container().core_agent_orchestrator
            return orchestrator.health_check()
