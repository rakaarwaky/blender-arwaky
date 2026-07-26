"""Config domain constants.

Compile-time literal values for configuration management.
No classes, no functions — only ALL_CAPS declarations.
"""

from __future__ import annotations

from typing import Any

# ─── Sensitive Key Patterns (FR-CFG-005) ──────────────────────

SENSITIVE_KEY_PATTERNS: tuple[str, ...] = (
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
    "signing_key",
    "encryption_key",
    "connection_string",
)

# ─── Environment Variable Names (FR-CFG-001 / FR-CFG-003) ────

CONFIG_PATH_ENV: str = "BLENDERMCP_CONFIG_PATH"
WORKSPACE_ROOT_ENV: str = "BLENDERMCP_ROOT"      # replaces both legacy+product root lookup
STRICT_MODE_FLAG_ENV: str = "BLENDERMCP_STRICT"
DEFAULT_CONFIG_FILENAME: str = "config.yaml"

# Environment keys that are control signals, never settings overrides.
RESERVED_ENV_KEYS: tuple[str, ...] = (
    "BLENDERMCP_CONFIG_PATH",
    "BLENDERMCP_ROOT",
    "BLENDERMCP_STRICT",
)

# ─── Event Sink (FR-CFG-001 / T-09) ──────────────────────────

EVENT_RING_BUFFER_SIZE: int = 50

# ─── Project Markers (FR-CFG-003) ────────────────────────────
# Manifest markers precede version-control metadata per FR-CFG-003.

PROJECT_MARKERS: tuple[str, ...] = (
    "config.yaml",
    "config.yml",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "requirements.txt",
    ".git",
)

# ─── Compile-Time Defaults (FR-CFG-001, Q4) ──────────────────

DEFAULT_SETTINGS: dict[str, Any] = {
    "blender": {"executable_path": "blender", "host": "localhost", "port": 9876},
    "server": {"transport": "stdio", "log_dir": "log"},
}

# ─── Settings Schema (FR-CFG-001, Q3) ───────────────────────
# Python-native schema: node = {"type", "required", "children"}.

SETTINGS_SCHEMA: dict[str, Any] = {
    "blender": {
        "type": "dict",
        "required": False,
        "children": {
            "executable_path": {"type": "str", "required": False},
            "host": {"type": "str", "required": False},
            "port": {"type": "int", "required": False},
        },
    },
    "server": {
        "type": "dict",
        "required": False,
        "children": {
            "transport": {"type": "str", "required": False},
            "log_dir": {"type": "str", "required": False},
        },
    },
}

# ─── Limits (FR-CFG-001) ─────────────────────────────────────

MAX_CONFIG_SIZE_BYTES: int = 1024 * 1024  # 1 MiB

# ─── Environment Override Prefix (FR-CFG-001) ───────────────

ENV_PREFIX_PRODUCT: str = "BLENDERMCP_"  # legacy BLENDER_MCP_ prefix removed (v1.7.0 BREAKING)

# ─── Redaction Placeholder (FR-CFG-005) ──────────────────────

REDACTION_PLACEHOLDER: str = "***REDACTED***"

# ─── Policy Modes (FR-CFG-001) ───────────────────────────────

POLICY_MODE_STRICT: str = "strict"
POLICY_MODE_PERMISSIVE: str = "permissive"

DEFAULT_POLICY_MODE: str = "strict"

# ─── Scene Management Defaults (FR-SCN-001, FR-SCN-002) ──────────────

# Default preservation list — categories preserved during cleanup when request does not specify explicit preservation.
DEFAULT_PRESERVATION_LIST: tuple[str, ...] = (
    "camera",
    "light",
    "active_camera",
    "sole_camera",
    "protected",
)

# Default dry-run mode — whether cleanup defaults to preview-only mode.
DEFAULT_DRY_RUN_MODE: bool = False

# Include hidden objects in inspection — whether hidden objects are included by default.
DEFAULT_INCLUDE_HIDDEN_OBJECTS: bool = False

# Maximum inspection detail limit — limit for object detail returned during inspection.
MAX_INSPECTION_DETAIL_LIMIT: int = 1000

# Default cleanup timeout in seconds.
CLEANUP_TIMEOUT_SECONDS: float = 30.0

# Default inspection timeout in seconds.
INSPECTION_TIMEOUT_SECONDS: float = 15.0

# Cleanup confirmation required — whether destructive cleanup requires explicit confirmation when undo is unavailable.
CLEANUP_CONFIRMATION_REQUIRED: bool = True

# Default child handling policy — behavior for children of deleted objects.
DEFAULT_CHILD_HANDLING_POLICY: str = "detach"  # "delete", "detach", "reject"

# Default dependent handling policy — behavior for dependents such as constraints or references.
DEFAULT_DEPENDENT_HANDLING_POLICY: str = "reject"  # "ignore", "reject", "remove_safe"

# Protected object policy defaults.
PROTECTED_OBJECT_POLICY_ACTIVE_CAMERA: bool = True
PROTECTED_OBJECT_POLICY_SOLE_CAMERA: bool = True
PROTECTED_OBJECT_POLICY_LIGHTS: bool = True
PROTECTED_OBJECT_POLICY_PROTECTED: bool = True