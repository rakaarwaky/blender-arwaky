"""MCP Tool 3: read_skill_context — Read SKILL.md documentation for any skill.

FR-MCP-001: Expose MCP Tools — register_skill_read registers tool with MCP
FR-MCP-002: Route Tool Calls — SkillDocumentationReader reads SKILL.md from static files
FR-MCP-003: Format MCP Responses — Prompt type wraps skill context result

This provides in-context documentation without leaving the chat.
Surface delegates to the static documentation reader via the DI container.
"""

from pathlib import Path

from modules.shared.src.common.taxonomy_core_vo import Prompt, SectionRef, SkillName


class SkillDocumentationReader:
    """Static SKILL.md reader for the read_skill_context MCP tool.

    Reads versioned SKILL.md files from the project's skills directory
    without requiring a live aggregate or runtime dependency.
    """

    SKILLS_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / ".agents" / "skills"

    def read_skill(self, skill_name: str, section: str | None = None) -> str:
        """Read the SKILL.md for a given skill, optionally extracting a section.

        Args:
            skill_name: Name of the skill (directory name under .agents/skills/)
            section: Optional section header to extract (e.g. "Workflows")

        Returns:
            Markdown content of the SKILL.md (or the requested section),
            or an empty string if the skill or section is not found.
        """
        skill_dir = self.SKILLS_DIR / skill_name
        skill_file = skill_dir / "SKILL.md"

        if not skill_file.is_file():
            return ""

        content = skill_file.read_text(encoding="utf-8")

        if section is None:
            return content

        return self._extract_section(content, section)

    @staticmethod
    def _extract_section(content: str, section: str) -> str:
        """Extract a ### section from markdown content, or return full content."""
        lines = content.splitlines(keepends=True)
        in_section = False
        result_lines: list[str] = []
        section_marker = f"### {section}"

        for line in lines:
            if line.strip() == section_marker:
                in_section = True
                continue
            if in_section and line.startswith("### "):
                break
            if in_section:
                result_lines.append(line)

        return "".join(result_lines).strip() if result_lines else content


class SkillReadHandler:
    """Handler for reading skill documentation."""

    @staticmethod
    def register_read_skill_context(mcp):
        """Register the read_skill_context tool (MCP Tool #3)."""

        @mcp.tool()
        def read_skill_context(skill_name: SkillName, section: SectionRef | None = None) -> Prompt:
            """Read the SKILL.md documentation for a given skill.

            Args:
                skill_name: Name of the skill (e.g., 'auto-linter', 'blender-mcp')
                section: Optional section to extract (directives, mcp-tools, cli_entry_point-commands, workflows, architecture)

            Returns:
                Markdown content of the SKILL.md (or empty string if not found)
            """
            content = SkillDocumentationReader().read_skill(str(skill_name), section=section)
            return Prompt(content)
