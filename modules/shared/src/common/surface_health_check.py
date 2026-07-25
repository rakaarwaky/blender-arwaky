"""Health Check for BlenderArwaky — delegates directly to Agent container aggregate (AES compliant)."""

from ..common.agent_di_aggregate import AgentDiContainerAggregate
from ..common.taxonomy_core_vo import Prompt


class HealthCheckHandler:
    """Handler for health check operations."""

    _contract_ref: AgentDiContainerAggregate

    @staticmethod
    def register_health_check(mcp):
        @mcp.tool()
        async def health_check() -> Prompt:
            """Check the health and connectivity of BlenderArwaky via Agent aggregate."""
            from modules.shared.src.common.agent_di_container import get_container

            container: AgentDiContainerAggregate = get_container()
            orchestrator = container.core_agent_orchestrator
            return orchestrator.health_check()


# Module-level alias for backward compatibility
register_health_check = HealthCheckHandler.register_health_check
