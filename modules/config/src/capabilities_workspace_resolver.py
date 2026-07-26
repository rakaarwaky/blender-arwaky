"""Capability: Workspace resolver (FR-CFG-003).

Implements IWorkspaceResolverProtocol — resolves project workspace
directory using deterministic strategies.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from modules.shared.src.config.contract_workspace_resolver_protocol import IWorkspaceResolverProtocol
from modules.shared.src.config.taxonomy_config_constant import PROJECT_MARKERS
from modules.shared.src.config.taxonomy_config_error import ConfigRootResolutionError
from modules.shared.src.config.taxonomy_config_event import WorkspaceResolvedEvent
from modules.shared.src.config.taxonomy_config_vo import WorkspacePath


class WorkspaceResolverCapability(IWorkspaceResolverProtocol):
    """FR-CFG-003: Resolve project workspace directory.

    Resolution order: explicit override > env signal > settings file location
    > upward marker search > platform config > CWD.
    """

    def __init__(self, explicit_override: str | None = None) -> None:
        self._explicit_override = explicit_override

    def resolve(self) -> WorkspacePath:
        """Resolve workspace using deterministic strategy order."""
        # 1. Explicit override
        if self._explicit_override:
            candidate = Path(self._explicit_override).resolve()
            if candidate.is_dir():
                return WorkspacePath(path=str(candidate), strategy="explicit_override")

        # 2. Product-specific env signal
        env_root = os.environ.get("BLENDER_MCP_ROOT") or os.environ.get("BLENDERMCP_ROOT")
        if env_root:
            try:
                candidate = Path(env_root).resolve()
                if candidate.is_dir():
                    return WorkspacePath(path=str(candidate), strategy="env_signal")
            except (OSError, ValueError):
                pass

        # 3. Upward proximity search for project markers
        marker_path = self._search_upward()
        if marker_path:
            return WorkspacePath(path=str(marker_path), strategy="marker_search")

        # 4. Platform-standard user config location
        xdg_config = os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
        prod_path = Path(xdg_config) / "blender-arwaky"
        if prod_path.is_dir():
            return WorkspacePath(path=str(prod_path), strategy="platform_config")

        # 5. Fallback to CWD
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

    # ─── Block 3: Internal Helpers ─────────────────────────────

    @staticmethod
    def _search_upward() -> Path | None:
        """Search upward from cwd for recognized project markers."""
        current = Path.cwd().resolve()
        for parent in [current, *current.parents]:
            for marker in PROJECT_MARKERS:
                candidate = parent / marker
                try:
                    if candidate.exists():
                        return parent
                except OSError:
                    continue
        return None
