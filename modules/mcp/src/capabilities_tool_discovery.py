"""Capability: Server action discovery.

Implements ServerDiscoveryProtocol — handles listing available actions and
reading skill documentation through the surface layer's command catalog.
"""

from __future__ import annotations

import logging
import os

from modules.shared.src.mcp.contract_server_discovery_protocol import ServerDiscoveryProtocol

logger = logging.getLogger("BlenderMCPServer")


class ServerDiscoveryCapability(ServerDiscoveryProtocol):
    """Business logic for action discovery and skill documentation."""

    def __init__(self, project_root: str) -> None:
        """Initialize with the project root directory.

        Args:
            project_root: The root directory of the project for locating
                skill documentation files.
        """
        self._project_root = project_root

    async def list_actions(self) -> dict:
        """Return the complete catalog of available 3D actions.

        FR-MCP-003: Returns exact same list available via CLI.
        Each action includes name, description, parameter schema, example, timeout, mutation flag.

        Returns:
            Dictionary with success status, action catalog, and message.
        """
        logger.info("Listing available actions...")

        try:
            # Import the command catalog from shared layer
            from modules.shared.src.common.taxonomy_command_catalog_constant import CommandCatalog

            catalog = CommandCatalog.COMMAND_CATALOG
            actions = []

            for action_name, action_info in catalog.items():
                actions.append({
                    "name": action_name,
                    "description": action_info.get("description", ""),
                    "parameters": action_info.get("parameters", {}),
                    "timeout": action_info.get("timeout", 30),
                    "mutates_scene": action_info.get("mutates_scene", False),
                })

            return {
                "success": True,
                "actions": actions,
                "message": f"Found {len(actions)} available actions",
            }
        except Exception as e:
            logger.error("List actions failed: %s", e)
            return {
                "success": False,
                "actions": [],
                "message": f"Failed to list actions: {e}",
            }

    async def read_skill_context(self, skill_name: str | None = None) -> dict:
        """Return skill documentation content.

        FR-MCP-004: Returns exact same documentation files used by CLI.
        Defaults to root/overview if no skill name provided.
        Returns documentation as readable text (Markdown).

        Args:
            skill_name: Optional skill name to read. Defaults to overview.

        Returns:
            Dictionary with success status, content, and message.
        """
        logger.info("Reading skill context: %s...", skill_name or "overview")

        try:
            # Default skill file name
            if skill_name is None:
                skill_file = "SKILL.md"
            else:
                skill_file = f"skills/{skill_name}.md"

            # Try to find skill file in project root
            skill_path = os.path.join(self._project_root, skill_file)

            # Fallback to agents/skills directory
            if not os.path.exists(skill_path):
                skills_dir = os.path.join(self._project_root, ".agents", "skills")
                if os.path.isdir(skills_dir):
                    skill_path = os.path.join(skills_dir, skill_name or "overview.md")

            # Read and return documentation
            if os.path.exists(skill_path):
                with open(skill_path, encoding="utf-8") as f:
                    content = f.read()
                return {
                    "success": True,
                    "content": content,
                    "message": f"Skill documentation read: {skill_name or 'overview'}",
                }

            return {
                "success": False,
                "content": "",
                "message": f"Skill documentation not found: {skill_name or 'overview'}",
            }
        except Exception as e:
            logger.error("Read skill context failed: %s", e)
            return {
                "success": False,
                "content": "",
                "message": f"Failed to read skill documentation: {e}",
            }
