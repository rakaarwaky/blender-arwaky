"""Utility: Security path helpers — FR-SEC-001, FR-SEC-002.

Stateless functions for path normalization and allowed-directory
boundary checks. Used by capability layers to keep path logic
DRY and centrally maintained.
"""

from __future__ import annotations

import os


def normalize_path(path: str) -> str:
    """Return the absolute, normalized canonical form of *path*.

    Replaces the repeated ``os.path.normpath(os.path.abspath(...))``
    pattern across capability files with a single source of truth.
    """
    return os.path.normpath(os.path.abspath(path))


def resolve_path(path: str) -> str:
    """Return the canonical resolved path, following symlinks safely."""
    return os.path.realpath(os.path.abspath(path))


def redact_path(path: str) -> str:
    """Return a redacted filesystem path, keeping only the last two components."""
    parts = path.replace("\\", "/").split("/")
    if len(parts) <= 2:
        return "***"
    return "/" + "/".join(["***"] + list(parts[-2:]))


def is_within_allowed_dirs(
    target: str,
    allowed_dirs: list[str] | tuple[str, ...],
    *,
    allow_empty: bool = False,
) -> bool:
    """Return ``True`` when *target* resolves inside one of *allowed_dirs*.

    For security enforcement, allow_empty defaults to False: an empty
    allow-list means no directory is allowed (deny by default).
    """
    if not allowed_dirs:
        return allow_empty

    norm_target = normalize_path(target)

    for allowed_dir in allowed_dirs:
        norm_allowed = normalize_path(allowed_dir)
        if norm_target == norm_allowed:
            return True
        if norm_target.startswith(norm_allowed + os.sep):
            return True

    return False
