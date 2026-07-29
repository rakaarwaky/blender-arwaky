"""MCP Tool: Scene operations — inspect and cleanup via SceneCommand.

FR-MCP-001: Expose MCP Tools — scene tools registered with MCP server
FR-MCP-002: Route Tool Calls — delegates to ISceneAggregate through SceneCommand
FR-MCP-003: Format MCP Responses — returns structured result from aggregate
"""

import json
import logging
from typing import Any, Callable

from modules.shared.src.scene.contract_scene_aggregate import ISceneAggregate
from modules.shared.src.scene.taxonomy_scene_vo import SceneCleanupVO, SceneInspectionVO

logger = logging.getLogger("BlenderMCPServer")


class SceneToolsSurface:
    """MCP surface for scene inspection and cleanup tools."""

    @staticmethod
    def register_scene_tools(mcp, aggregate_factory: Callable[[], ISceneAggregate | None] | None = None):
        """Register scene inspection and cleanup tools with MCP server.

        Args:
            mcp: MCP server instance
            aggregate_factory: Optional factory that returns ISceneAggregate.
                When None, attempts lazy import from scene container.
        """
        aggregate: ISceneAggregate | None = None
        if aggregate_factory is not None:
            aggregate = aggregate_factory()

        # Lazy load — only works when config and code executor are available
        if aggregate is None:
            try:
                from modules.scene.src.root_scene_container import create_scene_container

                # This requires a code_executor to be passed, which we can't do here
                # without importing the actual implementation
                raise ImportError("Scene container requires code_executor")
            except ImportError:
                pass

        if aggregate is None:
            return

        from modules.scene.src.surface_scene_command import SceneCommand

        command = SceneCommand(aggregate)

        @mcp.tool()
        async def inspect_scene(request_json: str) -> str:
            """Inspect the current Blender scene state.

            Args:
                request_json: JSON string with SceneInspectionVO fields
                    - detail_level: 'standard' or 'detailed' (default: 'standard')
                    - filter_hidden: boolean to include hidden objects (default: false)

            Returns:
                JSON string with scene state summary including object counts,
                cameras, lights, render settings, and collections.
            """
            try:
                request_data = json.loads(request_json) if request_json else {}
                vo = SceneInspectionVO(**request_data)
                result = await command.inspect(vo)
                return json.dumps(result.__dict__ if hasattr(result, '__dict__') else result, default=str)
            except Exception as e:
                logger.error("inspect_scene failed: %s", e, exc_info=True)
                return json.dumps({"error": str(e), "success": False})

        @mcp.tool()
        async def cleanup_scene(request_json: str) -> str:
            """Clean up scene objects according to policy.

            Args:
                request_json: JSON string with SceneCleanupVO fields
                    - mode: 'all', 'unused', or 'orphan' (default: 'all')
                    - preservation_list: list of object types to preserve
                      (default: ['camera', 'light'])
                    - dry_run: boolean for preview mode (default: true)
                    - confirmation: boolean for destructive operations (default: false)
                    - child_handling_policy: 'delete', 'detach', or 'reject'
                    - dependent_handling_policy: 'ignore', 'reject', or 'remove_safe'

            Returns:
                JSON string with cleanup metrics including removed/preserved/skipped counts.
            """
            try:
                request_data = json.loads(request_json) if request_json else {}
                vo = SceneCleanupVO(**request_data)
                result = await command.cleanup(vo)
                return json.dumps(result.__dict__ if hasattr(result, '__dict__') else result, default=str)
            except Exception as e:
                logger.error("cleanup_scene failed: %s", e, exc_info=True)
                return json.dumps({"error": str(e), "success": False})
