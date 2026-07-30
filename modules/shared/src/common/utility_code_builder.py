"""Stateless helpers for safely building generated Python code.

Extracted from duplicated _safe_str(), _tuple_str(), and _validate_scale()
across all object capability executors (AES305 duplication fix).
Utility must remain stateless and depend only on taxonomy/stdlib.
"""

from __future__ import annotations

import math

from .taxonomy_core_vo import CoordinateList, ScaleVector


def quote_string(value: str) -> str:
    """Safely embed a string into generated Python code using repr()."""
    return repr(value)


def tuple_str(coords: CoordinateList) -> str:
    """Format a 3-element sequence of floats for embedding in generated Python code."""
    return f"({coords[0]}, {coords[1]}, {coords[2]})"


def validate_finite_vector(vector: CoordinateList, field_name: str) -> None:
    """Validate that all vector components are finite numeric values."""
    for index, value in enumerate(vector):
        if not isinstance(value, (int, float)):
            raise ValueError(f"{field_name}[{index}] is not numeric: {value}")
        if not math.isfinite(float(value)):
            raise ValueError(f"{field_name}[{index}] is not finite: {value}")


def validate_scale(scale: ScaleVector) -> None:
    """Validate scale values are finite and non-zero.

    FR-OBJ-003: Scale values must be finite and non-zero.
    """
    for index, value in enumerate(scale):
        if not isinstance(value, (int, float)):
            raise ValueError(f"Scale component {index} is not numeric: {value}")
        if not math.isfinite(float(value)):
            raise ValueError(f"Scale component {index} is not finite: {value}")
        if value == 0:
            raise ValueError(f"Scale component {index} is zero — non-zero scale is required")
