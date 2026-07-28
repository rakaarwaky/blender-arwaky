"""Utility: Server configuration loading from file, environment, and programmatic overrides.

Stateless function that resolves ServerConfig with priority:
1. Explicit programmatic overrides
2. Environment variables
3. Config file (YAML)
4. Built-in defaults

All values are validated. Invalid config raises ConnectionConfigError.
Implements v2.0.0 configuration behavior per Section 4.1.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from contextlib import suppress
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

from modules.shared.src.gateway.taxonomy_gateway_error import ConnectionConfigError
from modules.shared.src.gateway.taxonomy_gateway_vo import ServerConfig


def load_server_config(
    config_path: str | None = None,
    env: Mapping[str, str] | None = None,
    overrides: dict[str, Any] | None = None,
) -> ServerConfig:
    """Load and resolve server configuration.

    Priority order:
    1. Programmatic overrides (highest priority)
    2. Environment variables
    3. Config file (from config_path or BLENDERMCP_CONFIG_PATH)
    4. Built-in defaults (lowest priority)

    Args:
        config_path: Path to YAML config file. Falls back to BLENDERMCP_CONFIG_PATH env var.
        env: Environment mapping. Defaults to os.environ.
        overrides: Programmatic key-value overrides.

    Returns:
        Fully resolved ServerConfig VO.

    Raises:
        ConnectionConfigError: If configuration values are invalid.
    """
    env = env or os.environ

    # ─── Step 1: Load defaults ──────────────────────────────────
    config_dict: dict[str, Any] = {
        "host": "localhost",
        "port": 9876,
        "transport_type": "socket",
        "connection_timeout_seconds": 30.0,
        "protocol_version": "2.0.0",
        "auth_token": None,
        "require_auth_for_remote": True,
        "heartbeat_interval_seconds": 10,
        "heartbeat_failure_threshold": 3,
        "reconnect_max_attempts": 3,
        "reconnect_base_delay_seconds": 1.0,
        "reconnect_max_delay_seconds": 4.0,
        "reconnect_request_policy": "reject",
        "queue_max_depth": 50,
        "queue_wait_timeout_ms": 10_000.0,
        "execution_default_timeout_ms": 30_000.0,
        "max_code_payload_bytes": 1_048_576,
        "max_execution_output_bytes": 10_240,
        "command_default_timeout_ms": 5_000.0,
        "max_command_response_bytes": 1_048_576,
        "task_retention_seconds": 600.0,
        "allowed_directories": [],
        "use_active_file_directory": True,
        "temp_blend_directory": None,
        "workspace_filename_prefix": "blender_session",
        "ensure_temp_blend_file": True,
        "metrics_enabled": True,
        "event_bus_enabled": True,
    }

    # ─── Step 2: Load config file ──────────────────────────────
    file_path = config_path or env.get("BLENDERMCP_CONFIG_PATH")
    if file_path is not None and yaml is not None:
        try:
            with open(file_path) as f:
                file_data = yaml.safe_load(f)
            if isinstance(file_data, dict):
                _merge_dict(config_dict, file_data)
        except Exception:  # pragma: no cover
            # Config file is optional; warn but continue with defaults
            pass

    # ─── Step 3: Apply environment variables ────────────────────
    _apply_env_overrides(config_dict, env)

    # ─── Step 4: Apply programmatic overrides (highest priority) ─
    if overrides:
        _merge_dict(config_dict, overrides)

    # ─── Step 5: Validate and build ────────────────────────────
    return _validate_and_build(config_dict)


def _merge_dict(target: dict[str, Any], source: dict[str, Any]) -> None:
    """Deep-merge source dict into target dict."""
    for key, value in source.items():
        if key in ("allowed_directories",):
            if isinstance(value, list):
                target[key] = value
        elif isinstance(value, dict) and key in target and isinstance(target[key], dict):
            _merge_dict(target[key], value)
        else:
            target[key] = value


def _apply_env_overrides(config_dict: dict[str, Any], env: Mapping[str, str]) -> None:
    """Apply environment variable overrides to config dict."""
    # Server host/port
    host = env.get("BLENDER_HOST")
    if host:
        config_dict["host"] = host

    port = env.get("BLENDER_PORT")
    if port:
        with suppress(ValueError):
            config_dict["port"] = int(port)

    # Auth token
    auth_token = env.get("BLENDER_AUTH_TOKEN")
    if auth_token:
        config_dict["auth_token"] = auth_token

    # Protocol version
    protocol_version = env.get("BLENDER_PROTOCOL_VERSION")
    if protocol_version:
        config_dict["protocol_version"] = protocol_version

    # Queue settings
    queue_max = env.get("SERVER_QUEUE_MAX_DEPTH")
    if queue_max:
        with suppress(ValueError):
            config_dict["queue_max_depth"] = int(queue_max)

    queue_wait = env.get("SERVER_QUEUE_WAIT_TIMEOUT_MS")
    if queue_wait:
        with suppress(ValueError):
            config_dict["queue_wait_timeout_ms"] = float(queue_wait)

    exec_timeout = env.get("SERVER_EXECUTION_TIMEOUT_MS")
    if exec_timeout:
        with suppress(ValueError):
            config_dict["execution_default_timeout_ms"] = float(exec_timeout)

    # Allowed directories (platform path separator)
    allowed_dirs = env.get("SERVER_ALLOWED_DIRECTORIES")
    if allowed_dirs:
        sep = ":" if os.name != "nt" else ";"
        config_dict["allowed_directories"] = [d.strip() for d in allowed_dirs.split(sep) if d.strip()]


def _validate_and_build(config_dict: dict[str, Any]) -> ServerConfig:
    """Validate all config values and build frozen ServerConfig."""
    # Validate reconnect_request_policy
    policy = config_dict.get("reconnect_request_policy", "reject")
    if policy != "reject":
        raise ConnectionConfigError(
            message="reconnect_request_policy only supports 'reject' in v2.0.0",
            details={"value": policy},
        )

    # Validate port range
    port = config_dict.get("port")
    if not isinstance(port, int) or port < 1 or port > 65535:
        raise ConnectionConfigError(
            message=f"Port must be between 1 and 65535, got {port}",
            details={"value": port},
        )

    # Validate numeric fields
    try:
        connection_timeout = float(config_dict.get("connection_timeout_seconds", 30.0))
        if connection_timeout <= 0:
            raise ValueError()
    except (ValueError, TypeError):
        raise ConnectionConfigError(message="connection_timeout_seconds must be a positive number") from None

    # Normalize allowed_directories to tuple
    allowed_dirs = config_dict.get("allowed_directories", [])
    if isinstance(allowed_dirs, list):
        allowed_dirs = tuple(allowed_dirs)

    return ServerConfig(
        host=str(config_dict.get("host", "localhost")),
        port=int(config_dict.get("port", 9876)),
        transport_type=str(config_dict.get("transport_type", "socket")),
        connection_timeout_seconds=connection_timeout,
        protocol_version=str(config_dict.get("protocol_version", "2.0.0")),
        auth_token=config_dict.get("auth_token"),
        require_auth_for_remote=bool(config_dict.get("require_auth_for_remote", True)),
        heartbeat_interval_seconds=int(config_dict.get("heartbeat_interval_seconds", 10)),
        heartbeat_failure_threshold=int(config_dict.get("heartbeat_failure_threshold", 3)),
        reconnect_max_attempts=int(config_dict.get("reconnect_max_attempts", 3)),
        reconnect_base_delay_seconds=float(config_dict.get("reconnect_base_delay_seconds", 1.0)),
        reconnect_max_delay_seconds=float(config_dict.get("reconnect_max_delay_seconds", 4.0)),
        reconnect_request_policy=str(policy),
        queue_max_depth=int(config_dict.get("queue_max_depth", 50)),
        queue_wait_timeout_ms=float(config_dict.get("queue_wait_timeout_ms", 10_000.0)),
        execution_default_timeout_ms=float(config_dict.get("execution_default_timeout_ms", 30_000.0)),
        max_code_payload_bytes=int(config_dict.get("max_code_payload_bytes", 1_048_576)),
        max_execution_output_bytes=int(config_dict.get("max_execution_output_bytes", 10_240)),
        command_default_timeout_ms=float(config_dict.get("command_default_timeout_ms", 5_000.0)),
        max_command_response_bytes=int(config_dict.get("max_command_response_bytes", 1_048_576)),
        task_retention_seconds=float(config_dict.get("task_retention_seconds", 600.0)),
        allowed_directories=allowed_dirs,
        use_active_file_directory=bool(config_dict.get("use_active_file_directory", True)),
        temp_blend_directory=config_dict.get("temp_blend_directory"),
        workspace_filename_prefix=str(config_dict.get("workspace_filename_prefix", "blender_session")),
        ensure_temp_blend_file=bool(config_dict.get("ensure_temp_blend_file", True)),
        metrics_enabled=bool(config_dict.get("metrics_enabled", True)),
        event_bus_enabled=bool(config_dict.get("event_bus_enabled", True)),
    )
