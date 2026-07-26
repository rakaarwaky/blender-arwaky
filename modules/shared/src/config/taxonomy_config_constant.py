"""Config domain constants.

Compile-time literal values for configuration management.
No classes, no functions — only ALL_CAPS declarations.
"""

from __future__ import annotations

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

# ─── Project Markers (FR-CFG-003) ─────────────────────────────

PROJECT_MARKERS: tuple[str, ...] = (
    "config.yaml",
    "config.yml",
    ".git",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "requirements.txt",
)

# ─── Limits (FR-CFG-001) ──────────────────────────────────────

MAX_CONFIG_SIZE_BYTES: int = 1024 * 1024  # 1 MB

# ─── Environment Prefixes (FR-CFG-001) ────────────────────────

ENV_PREFIX_PRODUCT: str = "BLENDERMCP_"
ENV_PREFIX_LEGACY: str = "BLENDER_MCP_"

# ─── Redaction Placeholder (FR-CFG-005) ──────────────────────

REDACTION_PLACEHOLDER: str = "***REDACTED***"

# ─── Policy Modes (FR-CFG-001) ────────────────────────────────

POLICY_MODE_STRICT: str = "strict"
POLICY_MODE_PERMISSIVE: str = "permissive"

DEFAULT_POLICY_MODE: str = "strict"
