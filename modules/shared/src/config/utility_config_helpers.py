"""Utility: Config helper functions.

Stateless, domain-agnostic standalone functions extracted from capabilities.
No class, no protocol impl, pure functions only.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any


def parse_env_value(value: str) -> Any:
    """Parse environment value as typed scalar.

    boolean-like → bool, integer-like → int, float-like → float,
    null-like → None, otherwise → str.
    """
    if value.lower() in ("true", "yes", "on"):
        return True
    if value.lower() in ("false", "no", "off"):
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    if value.lower() in ("null", "none", ""):
        return None
    return value


def search_project_root(markers: tuple[str, ...]) -> Path | None:
    """Search upward from cwd for recognized project markers.

    Returns first parent containing any marker, or None.
    """
    current = Path.cwd().resolve()
    for parent in [current, *current.parents]:
        for marker in markers:
            candidate = parent / marker
            try:
                if candidate.exists():
                    return parent
            except OSError:
                continue
    return None
