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


def is_within_allowed_dirs(target: str, allowed_dirs: list[str]) -> bool:
    """Return ``True`` when *target* resolves inside one of *allowed_dirs*.

    Both *target* and each entry in *allowed_dirs* are normalized before
    comparison. An empty *allowed_dirs* list implies no restriction
    (returns ``True``).
    """
    if not allowed_dirs:
        return True
    norm_target = normalize_path(target)
    for allowed_dir in allowed_dirs:
        norm_allowed = normalize_path(allowed_dir)
        if norm_target.startswith(norm_allowed + os.sep) or norm_target == norm_allowed:
            return True
    return False
