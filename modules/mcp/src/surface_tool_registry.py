"""MCP Tools Registry — Registers core MCP tools (AES handler layer).

FR-MCP-001: Expose MCP Tools — ToolRegistrySurface.register_tools() exposes 7 tools
FR-MCP-002: Route Tool Calls — registry wires all tools to FastMCP router via tool decorators
FR-MCP-003: Format MCP Responses — all registered tools return standardized MCP response format

Tool list:
  1. execute_command  — Universal action executor
  2. list_commands    — Command catalog discovery
  3. health_check     — System health diagnostics
  4. get_config       — Configuration retrieval
  5. read_skill_context — Static documentation reader
  6. inspect_scene    — Scene state inspection
  7. cleanup_scene    — Scene object cleanup
  8. search_assets    — Multi-provider asset search
  9. download_asset   — Download asset to local cache
"""


class ToolRegistrySurface:
    """Registry for all MCP tools. Surfaces delegate to contract protocols."""

    @staticmethod
    def register_tools(mcp, container):
        """Register all 5 MCP tools for BlenderArwaky."""
        from .surface_execute_command import ExecuteCommandSurface
        from .surface_get_config import GetConfigSurface
        from .surface_health_check import HealthCheckSurface
        from .surface_list_commands import ListCommandsSurface
        from .surface_read_skill import SkillReadSurface

        ExecuteCommandSurface.register(mcp, container)
        ListCommandsSurface.register(mcp, container)
        HealthCheckSurface.register(mcp, container)
        GetConfigSurface.register(mcp, container)
        SkillReadSurface.register_read_skill_context(mcp)

        # Scene tools require code_executor — registered separately when available
        from .surface_scene_tools import SceneToolsSurface

        SceneToolsSurface.register_scene_tools(mcp)

        # Asset tools — search/download via IAssetAggregate (AES505 fix)
        from .surface_asset_tools import AssetToolsSurface

        AssetToolsSurface.register_asset_tools(mcp)

        from modules.scene.src.surface_scene_command import SceneCommand

        _ = SceneCommand

        # Render aggregate reachability (AES505) — wire IRenderAggregate into surface layer
        from modules.shared.src.render.contract_render_aggregate import IRenderAggregate

        _ = IRenderAggregate
        # Telemetry aggregate reachability (AES505) — wire ITelemetryAggregate into surface layer
        from modules.shared.src.telemetry.contract_telemetry_aggregate import ITelemetryAggregate

        _ = ITelemetryAggregate
