"""Health Check for BlenderArwaky — delegates directly to Agent container aggregate (AES compliant)."""

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


# Module-level alias for backward compatibility
register_health_check = HealthCheckHandler.register_health_check