"""Utility: Time conversion and duration formatting helpers.

Stateless standalone functions for millisecond/second conversions,
duration formatting, and deadline calculations. Domain-agnostic —
reusable across modules.
"""

from __future__ import annotations

import time
from typing import Final


# Default time unit mappings (binary notation: 1k = 1024)
_MS_PER_SECOND: Final[float] = 1_000.0
_SECONDS_PER_MINUTE: Final[float] = 60.0
_MS_PER_MINUTE: Final[float] = _MS_PER_SECOND * _SECONDS_PER_MINUTE
_MS_PER_HOUR: Final[float] = _MS_PER_SECOND * _SECONDS_PER_MINUTE * 24


def ms_to_seconds(ms: float) -> float:
    """Convert milliseconds to seconds.

    Args:
        ms: Duration in milliseconds.

    Returns:
        Duration in seconds.
    """
    return ms / _MS_PER_SECOND


def seconds_to_ms(seconds: float) -> float:
    """Convert seconds to milliseconds.

    Args:
        seconds: Duration in seconds.

    Returns:
        Duration in milliseconds.
    """
    return seconds * _MS_PER_SECOND


def format_duration(duration_seconds: float) -> str:
    """Format a duration in seconds to a human-readable string.

    Handles seconds, minutes, and hours. Uses binary notation
    (1k = 1024 bytes for size, but duration uses base-10).

    Args:
        duration_seconds: Duration in seconds.

    Returns:
        Formatted string like '5.2s', '2m 30s', or '1h 30m 15s'.
    """
    if duration_seconds < _MS_PER_SECOND:
        return f"{duration_seconds:.1f}s"

    minutes = int(duration_seconds / _SECONDS_PER_MINUTE)
    remaining_seconds = duration_seconds % _SECONDS_PER_MINUTE

    if minutes < 60:
        return f"{minutes}m {int(remaining_seconds)}s"

    hours = int(minutes / 60)
    remaining_minutes = minutes % 60
    return f"{hours}h {remaining_minutes}m {int(remaining_seconds)}s"


def calculate_deadline(timeout_ms: float) -> float:
    """Calculate an absolute deadline timestamp from a relative timeout.

    Args:
        timeout_ms: Relative timeout in milliseconds.

    Returns:
        Absolute deadline as time.monotonic() timestamp.
    """
    return time.monotonic() + ms_to_seconds(timeout_ms)


def is_past_deadline(deadline: float) -> bool:
    """Check if the current time is past a given deadline.

    Args:
        deadline: Absolute deadline timestamp from calculate_deadline().

    Returns:
        True if current time is past the deadline.
    """
    return time.monotonic() > deadline


def remaining_ms(deadline: float) -> float:
    """Calculate remaining milliseconds until a deadline.

    Args:
        deadline: Absolute deadline timestamp from calculate_deadline().

    Returns:
        Remaining milliseconds (negative if past deadline).
    """
    elapsed = (time.monotonic() - deadline) * _MS_PER_SECOND
    return -elapsed
