"""Launcher domain — Lifecycle events (immutable, observability-safe).

Event payloads avoid secrets, bridge secrets, and full process environment.
"""

from __future__ import annotations

from dataclasses import dataclass

from modules.shared.src.common.taxonomy_core_vo import DurationMs

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
    process_reference: str = ""
    method: str = ""
    duration_ms: DurationMs = DurationMs(0.0)
    reason_summary: str = ""
