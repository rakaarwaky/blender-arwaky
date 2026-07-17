"""Unit tests for telemetry configuration (TelemetryConfig)."""
import os
import pytest
from unittest.mock import patch

from infrastructure.telemetry_signal_recorder import TelemetryConfig


@pytest.mark.unit
class TestTelemetryConfigLoader:
    """Tests for TelemetryConfig loader and overrides."""

    def test_telemetry_config_env_disable(self):
        # 1. DISABLE_TELEMETRY = true
        with patch.dict(os.environ, {"DISABLE_TELEMETRY": "true"}):
            config = TelemetryConfig()
            assert config.is_enabled() is False

        # 2. BLENDER_MCP_DISABLE_TELEMETRY = true
        with patch.dict(os.environ, {"BLENDER_MCP_DISABLE_TELEMETRY": "TRUE"}):
            config = TelemetryConfig()
            assert config.is_enabled() is False

    def test_telemetry_config_yaml(self):
        # telemetry.enabled = True in yaml
        with patch.dict(os.environ, {}, clear=True):
            with patch("infrastructure.config_file_loader.ApplicationConfigLoader.get_config", return_value=True):
                config = TelemetryConfig()
                assert config.is_enabled() is True

            # telemetry.enabled = False in yaml
            with patch("infrastructure.config_file_loader.ApplicationConfigLoader.get_config", return_value=False):
                config = TelemetryConfig()
                assert config.is_enabled() is False

            # telemetry.enabled is None (not set)
            with patch("infrastructure.config_file_loader.ApplicationConfigLoader.get_config", return_value=None):
                config = TelemetryConfig()
                assert config.is_enabled() is False

    def test_telemetry_config_get_methods(self):
        config = TelemetryConfig()
        assert config.get("enabled") == config.enabled
        assert config.get("max_prompt_length") == 500
        assert config.get("nonexistent_path", "default_val") == "default_val"
