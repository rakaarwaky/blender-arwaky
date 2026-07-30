"""Launcher config builder — populates LauncherConfigVO from IConfigAggregate.

Resolves launcher configuration values from the shared config feature,
providing a composition root that aligns with FRD/PRD dependency declarations.

Usage:
    config_aggregate = ConfigContainer().build()
    launcher_config = LauncherConfigBuilder(config_aggregate).build()

This replaces hardcoded defaults and raw string parameters with
config-driven resolution via workspace resolver and settings retriever.
"""

from __future__ import annotations

import os

from modules.shared.src.config.contract_config_aggregate import IConfigAggregate
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    LauncherConfigVO,
    LaunchMode,
)


class LauncherConfigBuilder:
    """Build LauncherConfigVO from IConfigAggregate and environment.

    P0: Replaces raw LauncherConfigVO construction with config-driven
    resolution. Reads all 10 launcher config keys from settings snapshot
    and applies environment overrides via config's env mechanism.
    """

    def __init__(self, config_aggregate: IConfigAggregate) -> None:
        self._config = config_aggregate

    def build(self) -> LauncherConfigVO:
        """Populate LauncherConfigVO from config aggregate.

        Reads launcher.* keys from settings snapshot, applies environment
        overrides, and returns immutable LauncherConfigVO.
        """
        # Read launcher section from config
        snapshot = self._config.get_snapshot()

        executable_path = self._config.get_string("launcher.executable_path", "") or None
        launch_timeout = self._config.get_float("launcher.launch_timeout_seconds", 30.0)
        shutdown_timeout = self._config.get_float("launcher.shutdown_timeout_seconds", 10.0)
        force_termination = self._config.get_bool("launcher.force_termination_enabled", True)
        probe_interval = self._config.get_float("launcher.readiness_probe_interval_seconds", 0.5)
        state_location = self._config.get_string("launcher.state_persistence_location", "") or None
        default_mode_str = self._config.get_string("launcher.default_launch_mode", "interface")
        stale_reconciliation = self._config.get_bool("launcher.stale_reconciliation_enabled", True)
        bridge_endpoint = self._config.get_string("launcher.bridge_endpoint", "") or None
        addon_path = self._config.get_string("launcher.addon_path", "") or None

        # Parse search_locations (list → tuple)
        search_locs = snapshot.get("launcher.search_locations", [])
        search_locations = tuple(str(loc) for loc in search_locs) if isinstance(search_locs, list) else ()

        # Parse default_launch_mode enum
        try:
            default_mode = LaunchMode(default_mode_str)
        except ValueError:
            default_mode = LaunchMode.INTERFACE

        return LauncherConfigVO(
            executable_path=executable_path or None,
            search_locations=search_locations,
            supported_version_range="",  # FR-LAU-001: version check is stub, P1 task
            launch_timeout_seconds=launch_timeout,
            shutdown_timeout_seconds=shutdown_timeout,
            force_termination_enabled=force_termination,
            readiness_probe_interval_seconds=probe_interval,
            state_persistence_location=state_location,
            default_launch_mode=default_mode,
            stale_reconciliation_enabled=stale_reconciliation,
            bridge_endpoint=bridge_endpoint,
            addon_path=addon_path,
        )

    def resolve_state_path(self) -> str | None:
        """Derive state persistence path via workspace resolution.

        P0: Replaces raw state_path parameter with workspace-derived path.
        Falls back to launcher.state_persistence_location if workspace
        resolver doesn't provide a path.
        """
        # Try workspace resolver first
        try:
            workspace = self._config.resolve_workspace()
            if workspace.path:
                return os.path.join(workspace.path, "launcher_state.json")
        except Exception:
            pass

        # Fallback to config-derived state_persistence_location
        state_loc = self._config.get_string("launcher.state_persistence_location", "")
        return state_loc or None
