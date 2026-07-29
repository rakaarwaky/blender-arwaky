"""MCP Tool 5: read_skill_context — Read SKILL.md documentation for any skill.

FR-MCP-001: Expose MCP Tools — register_read_skill registers tool with MCP
FR-MCP-002: Route Tool Calls — SkillDocumentationReader reads SKILL.md from static files
FR-MCP-003: Format MCP Responses — Prompt type wraps skill context result
"""

from pathlib import Path

from modules.shared.src.common.taxonomy_core_vo import Prompt, SectionRef, SkillName


def _resolve_skills_dir() -> Path:
    """Resolve .agents/skills directory by walking up from this file.

    Replaces fragile parent-parent-grandparent chain (SC04) with a
    robust search that is resilient to directory renames and restructurings.
    """
    current = Path(__file__).resolve().parent
    for _ in range(10):
        candidate = current / ".agents" / "skills"
        if candidate.is_dir():
            return candidate
        current = current.parent
    raise RuntimeError("Could not locate .agents/skills directory relative to this file")


class SkillDocumentationReader:
    """Static SKILL.md reader for the read_skill_context MCP tool."""

    SKILLS_DIR = _resolve_skills_dir()

    def read_skill(self, skill_name: str, section: str | None = None) -> str:
        """Read the SKILL.md for a given skill, optionally extracting a section.

        Args:
            skill_name: Skill directory name under .agents/skills/
            section: Optional section header (### ...) to extract

        Returns:
            Markdown content of the SKILL.md (or empty string if not found)
        """
        skill_dir = self.SKILLS_DIR / skill_name
        skill_file = skill_dir / "SKILL.md"

        if not skill_file.is_file():
            return ""

        return self._read(skill_file, section)

    @staticmethod
    def _read(skill_file: Path, section: str | None = None) -> str:
        content = skill_file.read_text(encoding="utf-8")
        if section is None:
            return content
        return SkillDocumentationReader._extract_section(content, section)

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


class SkillReadSurface:
    """Surface for the read_skill_context MCP tool."""

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
