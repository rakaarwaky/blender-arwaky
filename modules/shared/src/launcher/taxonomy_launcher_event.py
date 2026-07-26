"""Launcher domain — Lifecycle events (immutable, observability-safe).

Event payloads avoid secrets, bridge secrets, and full process environment.
"""

from __future__ import annotations

from dataclasses import dataclass, field as dc_field

from .taxonomy_launcher_vo import RuntimeState


@dataclass(frozen=True)
class LauncherLifecycleEvent:
    """Emitted for launcher lifecycle transitions.

    Carries category, before/after state classification, process reference
    summary, termination/launch method, duration metadata, and a redacted
    reason summary. Never includes authentication material or bridge secrets.
    """

    event_category: str = ""
    state_before: RuntimeState = RuntimeState.NOT_RUNNING
    state_after: RuntimeState = RuntimeState.NOT_RUNNING
    process_reference: str = ""  # redacted process summary, not full env
    method: str = ""  # launch or termination method when applicable
    duration_ms: float = 0.0
    reason_summary: str = ""  # already redacted