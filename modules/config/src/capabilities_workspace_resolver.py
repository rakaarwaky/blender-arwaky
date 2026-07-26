"""Capability: Workspace resolver (FR-CFG-003).

Implements IWorkspaceResolverProtocol — resolves project workspace
directory using deterministic strategies.
"""

from __future__ import annotations

import os
from pathlib import Path

from modules.shared.src.config.contract_workspace_resolver_protocol import IWorkspaceResolverProtocol
from modules.shared.src.config.taxonomy_config_constant import PROJECT_MARKERS
from modules.shared.src.config.taxonomy_config_error import ConfigRootResolutionError
from modules.shared.src.config.taxonomy_config_event import WorkspaceResolvedEvent
from modules.shared.src.config.taxonomy_config_vo import WorkspacePath

from modules.shared.src.config.utility_config_helpers import search_project_root


# ─── Block 1: Class Definition & Constructor ───────────────
class WorkspaceResolverCapability(IWorkspaceResolverProtocol):
    """FR-CFG-003: Resolve project workspace directory.

    Resolution order: explicit override > env signal > marker search
    > platform config > CWD.
    """

    def __init__(self, explicit_override: str | None = None) -> None:
        self._explicit_override = explicit_override

# ─── Block 2: Protocol Method Implementation ──────────────

    def resolve(self) -> WorkspacePath:
        """Resolve workspace using deterministic strategy order."""
        if self._explicit_override:
            candidate = Path(self._explicit_override).resolve()
            if candidate.is_dir():
                return WorkspacePath(path=str(candidate), strategy="explicit_override")

        env_root = os.environ.get("BLENDER_MCP_ROOT") or os.environ.get("BLENDERMCP_ROOT")
        if env_root:
            try:
                candidate = Path(env_root).resolve()
                if candidate.is_dir():
                    return WorkspacePath(path=str(candidate), strategy="env_signal")
            except (OSError, ValueError):
                pass

        marker_path = search_project_root(PROJECT_MARKERS)
        if marker_path:
            return WorkspacePath(path=str(marker_path), strategy="marker_search")

        xdg_config = os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
        prod_path = Path(xdg_config) / "blender-arwaky"
        if prod_path.is_dir():
            return WorkspacePath(path=str(prod_path), strategy="platform_config")

        try:
            cwd = Path.cwd().resolve()
            if cwd.is_dir():
                return WorkspacePath(path=str(cwd), strategy="cwd_fallback")
        except OSError as exc:
            raise ConfigRootResolutionError("All workspace resolution strategies failed") from exc

        raise ConfigRootResolutionError("All workspace resolution strategies failed")

    def emit_resolved_event(self, workspace: WorkspacePath) -> WorkspaceResolvedEvent:
        """Build workspace-resolved event payload."""
        return WorkspaceResolvedEvent(
            source_summary=workspace.strategy,
            override_count=0,
            warning_count=0,
        )

# ─── Block 3: Dunder Methods, Factories, Helpers ──────────

    def __repr__(self) -> str:
        return "WorkspaceResolverCapability()"
