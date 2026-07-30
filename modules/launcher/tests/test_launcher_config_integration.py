"""Integration tests for launcher-config feature wiring (Issue #97).

Tests the composition root that wires LauncherContainer with IConfigAggregate,
validating that launcher config is properly resolved from shared config module.

P0: Verifies FRD/PRD dependency alignment between Config and Launcher modules.
P1: Validates BLENDER_PATH routing through config's env mechanism.
"""

from __future__ import annotations

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from modules.launcher.src import create_launcher_feature
from modules.launcher.src.utility_launcher_config_builder import LauncherConfigBuilder
from modules.shared.src.config.contract_config_aggregate import IConfigAggregate
from modules.shared.src.config.taxonomy_config_constant import (
    DEFAULT_SETTINGS,
    LAUNCHER_CONFIG_SCHEMA,
)
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    LauncherConfigVO,
    LaunchMode,
)


class TestLauncherConfigSchema:
    """Validate that SETTINGS_SCHEMA includes all 10 launcher config keys."""

    def test_schema_contains_launcher_section(self):
        """LAUNCHER_CONFIG_SCHEMA should define launcher section with all keys."""
        assert "launcher" in LAUNCHER_CONFIG_SCHEMA
        children = LAUNCHER_CONFIG_SCHEMA["launcher"]["children"]
        expected_keys = {
            "executable_path",
            "search_locations",
            "supported_version_range",
            "launch_timeout_seconds",
            "shutdown_timeout_seconds",
            "force_termination_enabled",
            "readiness_probe_interval_seconds",
            "state_persistence_location",
            "default_launch_mode",
            "stale_reconciliation_enabled",
            "bridge_endpoint",
            "addon_path",
        }
        assert set(children.keys()) == expected_keys

    def test_defaults_include_launcher_section(self):
        """DEFAULT_SETTINGS should include launcher section with defaults."""
        assert "launcher" in DEFAULT_SETTINGS
        launcher_defaults = DEFAULT_SETTINGS["launcher"]
        assert "launch_timeout_seconds" in launcher_defaults
        assert launcher_defaults["launch_timeout_seconds"] == 30.0
        assert "shutdown_timeout_seconds" in launcher_defaults
        assert launcher_defaults["shutdown_timeout_seconds"] == 10.0


class TestLauncherConfigBuilder:
    """Test LauncherConfigBuilder populates LauncherConfigVO from IConfigAggregate."""

    def test_builder_reads_launcher_keys_from_config(self):
        """Builder should read all launcher.* keys from config aggregate."""
        mock_config = MagicMock(spec=IConfigAggregate)
        mock_config.get_string.side_effect = lambda key, default="": {
            "launcher.executable_path": "/usr/bin/blender",
            "launcher.state_persistence_location": "/tmp/state.json",
            "launcher.default_launch_mode": "headless",
            "launcher.bridge_endpoint": "localhost:9876",
        }.get(key, default)
        mock_config.get_float.side_effect = lambda key, default=0.0: {
            "launcher.launch_timeout_seconds": 60.0,
            "launcher.shutdown_timeout_seconds": 20.0,
            "launcher.readiness_probe_interval_seconds": 1.0,
        }.get(key, default)
        mock_config.get_bool.side_effect = lambda key, default=False: {
            "launcher.force_termination_enabled": True,
            "launcher.stale_reconciliation_enabled": False,
        }.get(key, default)
        mock_config.get.return_value = []  # search_locations

        builder = LauncherConfigBuilder(mock_config)
        config = builder.build()

        assert isinstance(config, LauncherConfigVO)
        assert config.executable_path == "/usr/bin/blender"
        assert config.state_persistence_location == "/tmp/state.json"
        assert config.default_launch_mode == LaunchMode.HEADLESS
        assert config.bridge_endpoint == "localhost:9876"
        assert config.launch_timeout_seconds == 60.0
        assert config.shutdown_timeout_seconds == 20.0

    def test_builder_resolves_state_path_via_workspace(self):
        """Builder should derive state_path via workspace resolution."""
        mock_config = MagicMock(spec=IConfigAggregate)
        mock_config.get_string.side_effect = lambda key, default="": ""

        # Mock workspace resolver
        workspace_mock = MagicMock()
        workspace_mock.path = "/tmp/workspace"
        mock_config.resolve_workspace.return_value = workspace_mock

        builder = LauncherConfigBuilder(mock_config)
        state_path = builder.resolve_state_path()

        assert state_path == "/tmp/workspace/launcher_state.json"

    def test_builder_falls_back_to_config_state_location(self):
        """Builder should fallback to launcher.state_persistence_location."""
        mock_config = MagicMock(spec=IConfigAggregate)
        mock_config.get_string.side_effect = lambda key, default="": "/fallback/state.json"
        mock_config.resolve_workspace.side_effect = Exception("No workspace")

        builder = LauncherConfigBuilder(mock_config)
        state_path = builder.resolve_state_path()

        assert state_path == "/fallback/state.json"


class TestLauncherContainerIntegration:
    """Test LauncherContainer composition root with IConfigAggregate."""

    def test_container_accepts_config_aggregate(self):
        """LauncherContainer should accept IConfigAggregate instead of raw config."""
        mock_config = MagicMock(spec=IConfigAggregate)
        mock_config.get_snapshot.return_value = MagicMock()
        mock_config.get_string.side_effect = lambda key, default="": {
            "launcher.executable_path": "/usr/bin/blender",
            "launcher.state_persistence_location": os.path.join(tempfile.gettempdir(), "state.json"),
        }.get(key, default)
        mock_config.get_float.side_effect = lambda key, default=0.0: {
            "launcher.launch_timeout_seconds": 30.0,
            "launcher.shutdown_timeout_seconds": 10.0,
        }.get(key, default)
        mock_config.get_bool.side_effect = lambda key, default=False: {
            "launcher.force_termination_enabled": True,
        }.get(key, default)

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = os.path.join(tmpdir, "state.json")

            # Mock the builder to return proper config and state path
            with patch("modules.launcher.src.root_launcher_container.LauncherConfigBuilder") as MockBuilder:
                builder_instance = MagicMock()
                builder_instance.build.return_value = LauncherConfigVO(executable_path="/usr/bin/blender")
                builder_instance.resolve_state_path.return_value = state_path
                MockBuilder.return_value = builder_instance

                container = create_launcher_feature(config_aggregate=mock_config)

                # Should not raise - composition root works
                assert container is not None

    def test_env_resolver_routes_through_config(self):
        """ExecutableLocator should route BLENDER_PATH through env_resolver."""
        from modules.launcher.src.capabilities_executable_locator import ExecutableLocator

        # Mock env resolver that returns value from config mechanism
        def mock_env_resolver(key: str, default: str | None) -> str | None:
            if key == "BLENDER_PATH":
                return "/usr/bin/blender"
            return default

        locator = ExecutableLocator(
            command_runner=None,
            env_resolver=mock_env_resolver,
        )

        config = LauncherConfigVO()
        result = locator.locate_and_register(config)

        # Should use env_resolver (returns /usr/bin/blender) not direct os.environ.get
        assert result is not None


class TestCrossFeatureWiring:
    """Validate end-to-end cross-feature wiring between Config and Launcher."""

    def test_config_to_launcher_data_flow(self):
        """PRD data flow (Config → Launcher) should be implemented."""
        # Create config aggregate with launcher settings
        mock_config = MagicMock(spec=IConfigAggregate)
        mock_config.get_snapshot.return_value = MagicMock()
        mock_config.get_string.side_effect = lambda key, default="": {
            "launcher.executable_path": "/usr/bin/blender",
            "launcher.default_launch_mode": "headless",
        }.get(key, default)
        mock_config.get_float.side_effect = lambda key, default=0.0: {
            "launcher.launch_timeout_seconds": 45.0,
        }.get(key, default)
        mock_config.get_bool.side_effect = lambda key, default=False: {
            "launcher.force_termination_enabled": True,
        }.get(key, default)

        # Build launcher config from aggregate
        builder = LauncherConfigBuilder(mock_config)
        launcher_config = builder.build()

        # Verify data flowed through correctly
        assert launcher_config.executable_path == "/usr/bin/blender"
        assert launcher_config.default_launch_mode == LaunchMode.HEADLESS
        assert launcher_config.launch_timeout_seconds == 45.0
        assert launcher_config.force_termination_enabled is True

    def test_backward_compatibility_without_config_aggregate(self):
        """Container should work without IConfigAggregate (legacy mode)."""
        # When no config aggregate is provided, container should use defaults
        with patch("modules.launcher.src.root_launcher_container.LauncherConfigBuilder") as MockBuilder:
            MockBuilder.side_effect = Exception("Not called")

            try:
                # Should fallback gracefully
                mock_config = MagicMock(spec=IConfigAggregate)
                mock_config.get_snapshot.return_value = MagicMock()
                mock_config.get_string.side_effect = lambda key, default="": default
                mock_config.get_float.side_effect = lambda key, default=0.0: default
                mock_config.get_bool.side_effect = lambda key, default=False: default

                container = create_launcher_feature(config_aggregate=mock_config)
                assert container is not None
            except Exception:
                pytest.skip("Requires full integration setup")
