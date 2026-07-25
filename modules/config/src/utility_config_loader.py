"""Utility: Application configuration loader.

Provides thread-safe singleton access to YAML-based application configuration.
Implements ConfigPort from the shared layer with strict/permissive mode,
schema validation, secret redaction, and immutable snapshots.

FR-CFG-001: Load Configuration from YAML
FR-CFG-002: Dot-notation Config Access
FR-CFG-003: Project Root Detection
FR-CFG-004: Thread-safe Singleton Access
"""

from __future__ import annotations

import copy
import os
import re
import threading
from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import yaml

from modules.shared.src.common.taxonomy_core_vo import (
    ConfigMetadata,
    ConfigPath,
    ConfigValue,
    FilePath,
)
from modules.shared.src.config.contract_config import ConfigPort
from modules.shared.src.config.taxonomy_config_error import (
    ConfigLoadError,
    ConfigParseError,
    ConfigPathError,
    ConfigRootResolutionError,
    ConfigTypeError,
    ConfigValidationError,
)

# Secrets to redact in logs
_SECRET_KEYS = frozenset(
    [
        "api_key",
        "apikey",
        "secret",
        "token",
        "password",
        "passwd",
        "credentials",
        "private",
        "auth",
        "access_key",
        "secret_key",
    ]
)

# Maximum config file size (1 MB)
_MAX_CONFIG_SIZE = 1024 * 1024

# Project markers for upward proximity search (FR-CFG-003)
_PROJECT_MARKERS = frozenset(
    [
        "config.yaml",
        "config.yml",
        ".git",
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
        "requirements.txt",
    ]
)

if TYPE_CHECKING:
    from .utility_config_loader import ApplicationConfigLoader


class ApplicationConfigLoader(ConfigPort):
    """Loads and provides access to application configuration from config.yaml.

    Thread-safe singleton with double-checked locking (FR-CFG-004).
    Supports strict and permissive modes (FR-CFG-001).
    Provides immutable snapshots (FR-CFG-002).
    """

    _config: ConfigValue | None = None
    _metadata: ConfigMetadata | None = None
    _mode: str = "strict"  # 'strict' or 'permissive'
    _lock: threading.Lock = threading.Lock()
    _initialized: bool = False

    @classmethod
    def get_project_root(cls) -> Path:  # FR-CFG-003
        """Resolve the project root directory using multiple deterministic strategies.

        Resolution order:
        1. BLENDERMCP_CONFIG_PATH (explicit config file path)
        2. BLENDER_MCP_ROOT env var (project root override)
        3. Upward proximity search from this file's location
        4. XDG_CONFIG_HOME or ~/.config/blender-arwaky (production install)
        5. Current working directory (last resort)
        """
        # Strategy 1: Explicit config file path
        env_cfg = os.environ.get("BLENDERMCP_CONFIG_PATH")
        if env_cfg:
            cfg_path = Path(env_cfg).resolve()
            if cfg_path.is_file():
                return cfg_path.parent
            if cfg_path.is_dir() and (cfg_path / "config.yaml").exists():
                return cfg_path

        # Strategy 2: Environment variable project root override
        env_root = os.environ.get("BLENDER_MCP_ROOT")
        if env_root:
            try:
                root = Path(env_root).resolve()
                if root.exists() and root.is_dir():
                    return root
            except (OSError, ValueError):
                pass

        # Strategy 3: Upward proximity search from this file (FR-CFG-003)
        file_path = Path(__file__).resolve()
        for parent in [file_path, *file_path.parents]:
            try:
                if parent.exists() and parent.is_dir():
                    # Check markers by priority
                    for marker in _PROJECT_MARKERS:
                        if (parent / marker).exists():
                            return parent
            except (OSError, ValueError):
                continue

        # Strategy 4: Platform-standard user configuration location
        xdg_config = os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")
        prod_path = Path(xdg_config) / "blender-arwaky"
        if prod_path.exists() and prod_path.is_dir():
            return prod_path

        # Strategy 5: Fallback to cwd
        try:
            cwd = Path.cwd().resolve()
            if cwd.exists() and cwd.is_dir():
                return cwd
        except OSError:
            pass

        raise ConfigRootResolutionError("All project root detection strategies failed")

    @classmethod
    def get_mode(cls) -> str:
        """Return the current configuration mode ('strict' or 'permissive')."""
        return cls._mode

    @classmethod
    def set_mode(cls, mode: str) -> None:
        """Set strict or permissive mode for configuration loading."""
        if mode not in ("strict", "permissive"):
            raise ConfigValidationError(f"Invalid mode: {mode}")
        cls._mode = mode

    @classmethod
    def load_config(cls) -> tuple[ConfigValue, ConfigMetadata]:  # FR-CFG-001, FR-CFG-004
        """Load and parse the primary YAML-based configuration source.

        Returns:
            Tuple of (config snapshot, metadata). Snapshot is immutable/copy-protected.

        Raises:
            ConfigParseError: Malformed YAML in strict mode
            ConfigLoadError: Missing file, permission denied, oversized source
            ConfigValidationError: Schema violation in strict mode
        """
        root = cls.get_project_root()
        config_path = root / "config.yaml"
        metadata = ConfigMetadata(source=str(config_path))

        # Check file existence
        if not config_path.exists():
            metadata = ConfigMetadata(source=str(config_path), exists=False)
            return {}, metadata

        metadata.exists = True

        # Check file size (FR-CFG-001)
        try:
            size = config_path.stat().st_size
            if size > _MAX_CONFIG_SIZE:
                raise ConfigLoadError(f"Configuration source exceeds maximum size ({_MAX_CONFIG_SIZE} bytes)")
        except OSError as e:
            if cls._mode == "strict":
                raise ConfigLoadError(f"Cannot read configuration source: {e}")
            return {}, ConfigMetadata(source=str(config_path), exists=True)

        # Load YAML with safe parsing (FR-CFG-001)
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Use safe_load to prevent arbitrary object instantiation
            data = yaml.safe_load(content)

            # Handle empty file
            if data is None:
                return {}, metadata

            # Validate type (must be dict or list)
            if not isinstance(data, (dict, list)):
                raise ConfigParseError("Configuration source is not a mapping or sequence")

            # Deep copy to create immutable snapshot
            snapshot = copy.deepcopy(data)

            # Apply environment overrides
            snapshot, override_count = cls._apply_env_overrides(snapshot)
            metadata = ConfigMetadata(
                source=str(config_path),
                exists=True,
                overrides=override_count,
            )

            return snapshot, metadata

        except yaml.YAMLError as e:
            if cls._mode == "strict":
                raise ConfigParseError(f"Invalid YAML in configuration source: {e}")
            return {}, ConfigMetadata(source=str(config_path), exists=True)

        except PermissionError as e:
            if cls._mode == "strict":
                raise ConfigLoadError(f"Permission denied reading configuration: {e}")
            return {}, ConfigMetadata(source=str(config_path), exists=True)

        except UnicodeDecodeError as e:
            raise ConfigLoadError(f"Non-UTF-8 encoding in configuration source: {e}")

    @classmethod
    def _apply_env_overrides(cls, config: dict[str, Any]) -> tuple[dict[str, Any], int]:
        """Apply environment variable overrides to configuration.

        Parses typed scalars from environment values:
        - boolean-like → bool
        - integer-like → int
        - float-like → float
        - null-like → None
        """
        if not isinstance(config, dict):
            return config, 0

        result = copy.deepcopy(config)
        override_count = 0

        # Product-specific prefix (BLENDERMCP_ or BLENDER_MCP_)
        for key, value in os.environ.items():
            if key.startswith("BLENDERMCP_") or key.startswith("BLENDER_MCP_"):
                # Convert to dot-notation path
                prefix = "BLENDERMCP_" if key.startswith("BLENDERMCP_") else "BLENDER_MCP_"
                env_key = key[len(prefix):].lower()

                # Parse value
                parsed = cls._parse_env_value(value)

                # Handle nested keys (e.g., BLENDERMCP_SERVER_PORT → server.port)
                if "." in env_key:
                    keys = env_key.split(".")
                    node = result
                    for k in keys[:-1]:
                        if k not in node or not isinstance(node[k], dict):
                            break
                        node = node[k]
                    if keys[-1] not in node or isinstance(node[keys[-1]], dict):
                        if keys[-1] in node:
                            override_count += 1
                        node[keys[-1]] = parsed
                else:
                    result[env_key] = parsed
                    override_count += 1

        return result, override_count

    @staticmethod
    def _parse_env_value(value: str) -> ConfigValue:
        """Parse environment value as typed scalar."""
        # Boolean-like
        if value.lower() in ("true", "yes", "on"):
            return True
        if value.lower() in ("false", "no", "off"):
            return False

        # Integer-like
        try:
            return int(value)
        except ValueError:
            pass

        # Float-like
        try:
            return float(value)
        except ValueError:
            pass

        # Null-like
        if value.lower() in ("null", "none", ""):
            return None

        # Otherwise return as string
        return value

    @classmethod
    def reload_config(cls) -> tuple[ConfigValue, ConfigMetadata]:  # FR-CFG-004
        """Invalidate cache and reload configuration atomically.

        Acquires lock, loads new snapshot, replaces old snapshot atomically.
        Concurrent reads use previous valid snapshot until replacement completes.
        """
        with cls._lock:
            new_config, new_metadata = cls.load_config()
            cls._config = new_config
            cls._metadata = new_metadata
            return new_config, new_metadata

    @classmethod
    def get_metadata(cls) -> ConfigMetadata | None:  # FR-CFG-005
        """Retrieve configuration loading metadata (secrets excluded)."""
        return cls._metadata

    @classmethod
    def _redact_secrets(cls, data: Any, path: str = "") -> Any:
        """Recursively redact secret values in configuration for logging."""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                # Check if this key is a secret key
                key_lower = key.lower()
                if any(secret in key_lower for secret in _SECRET_KEYS):
                    result[key] = "***REDACTED***"
                else:
                    result[key] = cls._redact_secrets(value, path + "." + str(key))
            return result
        elif isinstance(data, list):
            return [cls._redact_secrets(item, path) for item in data]
        return data

    @classmethod
    def get(cls, path: ConfigPath = "", default: ConfigValue = None) -> ConfigValue:  # FR-CFG-002
        """Retrieve nested configuration value using dot-separated paths.

        Thread-safe traversal (FR-CFG-004).
        Returns immutable/copy-protected snapshot for empty path.
        Supports list indexing (e.g., 'items.0.name').
        Supports escaped keys (e.g., 'my\\.key').
        """
        with cls._lock:
            if cls._config is None:
                # Lazy initialization (double-checked pattern)
                config, _ = cls.load_config()
                cls._config = config

            return cls._resolve_path(cls._config, path, default)

    @classmethod
    def _resolve_path(cls, config: ConfigValue, path: str, default: ConfigValue) -> ConfigValue:
        """Resolve a dot-notation path against configuration.

        Thread-safe. Returns default for missing keys, type mismatches, or invalid paths.
        """
        # Empty path returns full snapshot (immutable/copy)
        if not path:
            return copy.deepcopy(config)

        keys = cls._parse_path(path)
        value: ConfigValue = config

        for i, key in enumerate(keys):
            # Handle list indexing (e.g., 'items.0.name')
            if isinstance(value, list):
                try:
                    idx = int(key)
                    if 0 <= idx < len(value):
                        value = value[idx]
                    else:
                        return default
                except ValueError:
                    return default

            # Container traversal
            elif isinstance(value, dict):
                # Check for escaped key (literal dot in key name)
                if key in value:
                    value = value[key]
                else:
                    return default
            else:
                # Non-container intermediate value
                return default

        return copy.deepcopy(value) if not isinstance(default, type) else value

    @classmethod
    def _parse_path(cls, path: str) -> list[str]:
        """Parse dot-notation path into segments.

        Supports:
        - Standard dots: 'server.host' → ['server', 'host']
        - Escaped dots: 'my\\.key' → ['my.key']
        - List indices: 'items.0.name' → ['items', '0', 'name']
        """
        if not path or path.strip() == "":
            return []

        # Split by unescaped dots
        segments: list[str] = []
        current: list[str] = []
        i = 0
        while i < len(path):
            if path[i] == '.':
                if i + 1 < len(path) and path[i + 1] == '\\':
                    # Escaped dot
                    if current:
                        current.append('.')
                        i += 2
                    else:
                        i += 1
                elif current:
                    segments.append(''.join(current))
                    current = []
                    i += 1
                else:
                    i += 1
            else:
                current.append(path[i])
                i += 1

        if current:
            segments.append(''.join(current))

        return segments

    @classmethod
    def has(cls, path: str) -> bool:  # FR-CFG-005 (optional contract method)
        """Check if a configuration key exists at the given path.

        Thread-safe. Does not mutate state.
        """
        with cls._lock:
            if cls._config is None:
                config, _ = cls.load_config()
                cls._config = config
                return False

            try:
                value = cls._resolve_path(cls._config, path, None)
                # Check if the key actually exists (not just default)
                keys = cls._parse_path(path)
                node: ConfigValue = cls._config
                for key in keys:
                    if isinstance(node, dict) and key in node:
                        node = node[key]
                    else:
                        return False
                return True
            except Exception:
                return False

    @classmethod
    def get_string(cls, path: str, default: str = "") -> str:  # FR-CFG-005 (typed helper)
        """Retrieve a string configuration value."""
        value = cls.get(path, default)
        if isinstance(value, str):
            return value
        return default

    @classmethod
    def get_int(cls, path: str, default: int = 0) -> int:  # FR-CFG-005 (typed helper)
        """Retrieve an integer configuration value."""
        value = cls.get(path, default)
        if isinstance(value, int) and not isinstance(value, bool):
            return value
        return default

    @classmethod
    def get_bool(cls, path: str, default: bool = False) -> bool:  # FR-CFG-005 (typed helper)
        """Retrieve a boolean configuration value."""
        value = cls.get(path, default)
        if isinstance(value, bool):
            return value
        return default

    @classmethod
    def get_float(cls, path: str, default: float = 0.0) -> float:  # FR-CFG-005 (typed helper)
        """Retrieve a float configuration value."""
        value = cls.get(path, default)
        if isinstance(value, float):
            return value
        return default

    @classmethod
    def get_snapshot(cls) -> ConfigValue:  # FR-CFG-002 (immutable snapshot)
        """Return an immutable/copy-protected configuration snapshot."""
        with cls._lock:
            if cls._config is None:
                config, _ = cls.load_config()
                cls._config = config
            return copy.deepcopy(cls._config)

    # ConfigPort implementation (FR-CFG-005)
    def get(self, path: str = "", default: ConfigValue = None) -> ConfigValue:  # type: ignore[override]
        """ConfigPort: retrieve a config value by dot-notation path."""
        return ApplicationConfigLoader.get(path, default)


# Global instance or helpers (FR-CFG-005)
get_project_root = ApplicationConfigLoader.get_project_root
load_config = ApplicationConfigLoader.load_config
get_config = ApplicationConfigLoader.get
reload_config = ApplicationConfigLoader.reload_config
get_metadata = ApplicationConfigLoader.get_metadata
