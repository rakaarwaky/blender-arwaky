"""CLI init command — Initialize workspace structure, configuration, and agent skills."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from . import surface_launch_command

logger = logging.getLogger(__name__)


def _mask_error(category: str, ref: str, message: str = "Operation failed") -> dict[str, object]:
    return {"success": False, "error": message, "category": category, "ref": ref}


def _find_repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists() and (parent / "modules").exists():
            return parent
    return current.parent.parent.parent


def handle(args: object, _dispatcher: object | None = None) -> dict[str, object]:
    """Handle init command: initialize workspace or redirect to launch if --filepath is provided."""
    # Backward compatibility: if --filepath was passed, delegate to surface_launch_command
    if getattr(args, "filepath", None):
        logger.warning(
            "Using 'blender-arwaky init --filepath ...' is deprecated. Use 'blender-arwaky launch --filepath ...' instead."
        )
        return surface_launch_command.handle(args, _dispatcher)

    raw_target_dir = getattr(args, "target_dir", None)
    target_path = Path(str(raw_target_dir)).resolve() if raw_target_dir else Path.cwd().resolve()
    force = bool(getattr(args, "force", False))

    repo_root = _find_repo_root()
    created_dirs: list[str] = []

    try:
        target_path.mkdir(parents=True, exist_ok=True)

        # 1. Ensure standard workspace directories exist
        subdirs = [
            target_path / ".agents" / "skills" / "blender-arwaky",
            target_path / "renders",
            target_path / "assets",
        ]
        for sdir in subdirs:
            if not sdir.exists():
                sdir.mkdir(parents=True, exist_ok=True)
                created_dirs.append(str(sdir.relative_to(target_path)))

        # 2. Provision SKILL.md for AI agents
        skills_dir = target_path / ".agents" / "skills" / "blender-arwaky"
        skill_dest = skills_dir / "SKILL.md"
        source_skill = repo_root / "SKILL.md"

        skill_installed = False
        if source_skill.exists() and (not skill_dest.exists() or force):
            try:
                # Prefer symlink if inside the same tree or relative, fallback to copy
                if skill_dest.is_symlink() or skill_dest.exists():
                    skill_dest.unlink(missing_ok=True)
                shutil.copy2(source_skill, skill_dest)
                skill_installed = True
            except OSError:
                shutil.copy2(source_skill, skill_dest)
                skill_installed = True

        # 3. Provision config.yaml from config.example.yaml if missing
        config_dest = target_path / "config.yaml"
        config_source = repo_root / "config.example.yaml"
        if not config_source.exists():
            config_source = repo_root / "config.yaml"

        config_created = False
        if config_source.exists() and (not config_dest.exists() or force):
            shutil.copy2(config_source, config_dest)
            config_created = True

        return {
            "success": True,
            "message": f"BlenderArwaky workspace initialized at {target_path}",
            "data": {
                "workspace_dir": str(target_path),
                "skills_dir": str(skills_dir),
                "skill_installed": skill_installed,
                "config_created": config_created,
                "created_dirs": created_dirs,
            },
        }
    except Exception as e:
        logger.exception("Failed to initialize workspace")
        return _mask_error("unexpected", "cli-500", f"Workspace initialization failed: {e}")
