"""Dispatcher taxonomy — Domain constants for action metadata fields.

Centralises string constants used across dispatcher contracts, capabilities,
and surfaces. Replaces raw string literals with named constants.
"""

from __future__ import annotations


class RiskLevel:
    """Risk level constants for action execution."""

    LOW: str = "low"
    MEDIUM: str = "medium"
    HIGH: str = "high"


class TimeoutClass:
    """Timeout classification constants for action execution."""

    SHORT: str = "short"
    DEFAULT: str = "default"
    LONG: str = "long"
    EXTENDED: str = "extended"


class ExecutionMode:
    """Execution mode constants for action dispatch."""

    SYNC: str = "sync"
    BACKGROUND: str = "background"
