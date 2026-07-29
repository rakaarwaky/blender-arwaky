"""MCP Tool 5: read_skill_context — Read SKILL.md documentation for any skill.

FR-MCP-001: Expose MCP Tools — register_read_skill registers tool with MCP
FR-MCP-002: Route Tool Calls — SkillDocumentationReader reads SKILL.md from static files
FR-MCP-003: Format MCP Responses — Prompt type wraps skill context result
"""

from pathlib import Path

from modules.shared.src.common.taxonomy_core_vo import Prompt, SectionRef, SkillName


class SkillDocumentationReader:
    """Static SKILL.md reader for the read_skill_context MCP tool."""

    SKILLS_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / ".agents" / "skills"

    def read_skill(self, skill_name: str, section: str | None = None) -> str:
        """Read the SKILL.md for a given skill, optionally extracting a section."""
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
        """Extract a ### section from markdown content."""
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
    """Handler for the read_skill_context MCP tool."""

    @staticmethod
    def register_read_skill_context(mcp):
        """Register the read_skill_context tool (MCP Tool #5)."""

        @mcp.tool()
        def read_skill_context(skill_name: SkillName, section: SectionRef | None = None) -> Prompt:
            """Read the SKILL.md documentation for a given skill.

            Args:
                skill_name: Skill name (e.g., 'blender-mcp', 'auto-linter')
                section: Optional section to extract (tools, commands, workflows, addon, troubleshooting)

            Returns:
                Markdown content of the SKILL.md (or empty string if not found)
            """
            content = SkillDocumentationReader().read_skill(str(skill_name), section=section)
            return Prompt(content)
