"""
MCP Tool 3: read_skill_context — Read SKILL.md documentation for any skill.

This provides in-context documentation without leaving the chat.
Surface delegates directly to Agent container aggregate (AES compliant).
"""

from modules.mcp.src.container import get_container
from modules.shared.src.common.taxonomy_core_vo import Prompt, SectionRef, SkillName


class SkillReadHandler:
    """Handler for reading skill documentation."""


    @staticmethod
    def register_read_skill_context(mcp):
        """Register the read_skill_context tool (MCP Tool #3)."""

        @mcp.tool()
        def read_skill_context(skill_name: SkillName, section: SectionRef | None = None) -> Prompt:
            """
            Read the SKILL.md documentation for a given skill.

            Args:
                skill_name: Name of the skill (e.g., 'auto-linter', 'blender-mcp')
                section: Optional section to extract (directives, mcp-tools, cli_entry_point-commands, workflows, architecture)

            Returns:
                Markdown content of the SKILL.md (or empty string if not found)
            """
            # Keep section as None if not provided (orchestrator handles None vs empty)

            orchestrator = get_container().core_agent_orchestrator
            return orchestrator.read_skill_context(skill_name, section)


