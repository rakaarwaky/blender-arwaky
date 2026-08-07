"""Capability: Workspace resolver (FR-CFG-003).

Implements IWorkspaceResolverProtocol — resolves project workspace
directory using deterministic strategies with result caching.
"""

from __future__ import annotations

import logging
import os
import threading
import time
from pathlib import Path

from modules.shared.src.common.taxonomy_core_vo import ConfigPath, Timestamp
from modules.shared.src.config.contract_workspace_resolver_protocol import IWorkspaceResolverProtocol
from modules.shared.src.config.taxonomy_config_constant import (
    PROJECT_MARKERS,
    WORKSPACE_ROOT_ENV,
)
from modules.shared.src.config.taxonomy_config_error import ConfigRootResolutionError
from modules.shared.src.config.taxonomy_config_event import WorkspaceResolvedEvent
from modules.shared.src.config.taxonomy_config_vo import WorkspacePath
from modules.shared.src.config.utility_config_helpers import search_project_root

logger = logging.getLogger(__name__)


# ─── Block 1: Class Definition & Constructor ───────────────
class WorkspaceResolverCapability(IWorkspaceResolverProtocol):
    """FR-CFG-003: Resolve project workspace directory.

    Resolution order (per FRD minus legacy per Q8):
      explicit override > env BLENDERMCP_ROOT > settings-file parent >
      marker search > platform config > cwd fallback.
    Result is cached for process lifetime.
    """

    def __init__(
        self,
        explicit_override: str | None = None,
        config_path: ConfigPath | None = None,
    ) -> None:
        self._explicit_override = explicit_override
        self._config_path = config_path
        self._lock = threading.Lock()
        self._cached: WorkspacePath | None = None

    # ─── Block 2: Protocol Method Implementation ──────────────

    def resolve(self) -> WorkspacePath:
        """Resolve workspace using deterministic strategy order (cached)."""
        with self._lock:
            if self._cached is not None:
                return self._cached
            self._cached = self._resolve_uncached()
            return self._cached

    def emit_resolved_event(self, workspace: WorkspacePath) -> WorkspaceResolvedEvent:
        """Build a workspace-resolved event payload."""
        return WorkspaceResolvedEvent(
            source_summary=workspace.strategy,
            override_count=0,
            warning_count=0,
            timestamp=Timestamp(time.time()),
        )

    # ─── Block 3: Resolution Strategy ─────────────────────────

    def _resolve_uncached(self) -> WorkspacePath:
        # 1. Explicit override
        if self._explicit_override:
            candidate = Path(self._explicit_override).resolve()
            if candidate.is_dir():
                return WorkspacePath(path=str(candidate), strategy="explicit_override")
            logger.warning(
                "Explicit workspace override is not a directory: %s",
                self._explicit_override,
            )

        # 2. Environment signal (BLENDERMCP_ROOT only — legacy removed, Q8)
        env_root = os.environ.get(WORKSPACE_ROOT_ENV)
        if env_root:
            try:
                candidate = Path(env_root).resolve()
                if candidate.is_dir():
                    return WorkspacePath(path=str(candidate), strategy="env_signal")
                # FR-CFG-003: "Invalid env path logs warning, falls through"
                logger.warning(
                    "BLENDERMCP_ROOT path is not a directory: %s", env_root
                )
            except (OSError, ValueError) as exc:
                logger.warning("Invalid BLENDERMCP_ROOT path '%s': %s", env_root, exc)

        # 3. Settings file parent (NEW)
        if self._config_path:
            candidate = Path(str(self._config_path)).resolve().parent
            if candidate.is_dir():
                return WorkspacePath(path=str(candidate), strategy="settings_file_location")
            logger.warning(
                "Settings file parent is not a directory: %s",
                str(Path(str(self._config_path)).resolve().parent),
            )

        # 4. Marker search
        marker_path = search_project_root(PROJECT_MARKERS)
        if marker_path:
            return WorkspacePath(path=str(marker_path), strategy="marker_search")

        # 5. Platform config
        try:
            home_dir = Path.home()
        except RuntimeError:
            home_dir = None
        if home_dir is not None:
            xdg_config = os.environ.get("XDG_CONFIG_HOME", str(home_dir / ".config"))
        else:
            xdg_config = os.environ.get("XDG_CONFIG_HOME", "")
        prod_path = Path(xdg_config) / "blender-arwaky"
        if prod_path.is_dir():
            return WorkspacePath(path=str(prod_path), strategy="platform_config")

        # 6. CWD fallback
        try:
            cwd = Path.cwd().resolve()
            if cwd.is_dir():
                return WorkspacePath(path=str(cwd), strategy="cwd_fallback")
        except OSError as exc:
            raise ConfigRootResolutionError("All workspace resolution strategies failed") from exc

        raise ConfigRootResolutionError("All workspace resolution strategies failed")

    def __repr__(self) -> str:
        return "WorkspaceResolverCapability()"
