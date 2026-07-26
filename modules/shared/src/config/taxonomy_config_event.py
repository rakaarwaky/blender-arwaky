"""Config domain events.

Domain events emitted by the configuration feature.
All payloads exclude raw settings content and secret values.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..common.taxonomy_core_vo import Timestamp


@dataclass(frozen=True)
class SettingsLoadedEvent:
    """Emitted after settings snapshot is successfully loaded."""

    category: str = "settings"
    source_summary: str = ""
    override_count: int = 0
    warning_count: int = 0
    policy_mode: str = "strict"
    timestamp: Timestamp = field(default_factory=lambda: Timestamp(0.0))


@dataclass(frozen=True)
class SettingsReloadEvent:
    """Emitted after settings snapshot is successfully replaced."""

    category: str = "settings"
    source_summary: str = ""
    override_count: int = 0
    warning_count: int = 0
    policy_mode: str = "strict"
    timestamp: Timestamp = field(default_factory=lambda: Timestamp(0.0))


@dataclass(frozen=True)
class WorkspaceResolvedEvent:
    """Emitted after project workspace directory is resolved."""

    category: str = "workspace"
    source_summary: str = ""
    override_count: int = 0
    warning_count: int = 0
    policy_mode: str = "strict"
    timestamp: Timestamp = field(default_factory=lambda: Timestamp(0.0))


@dataclass(frozen=True)
class SettingsValidationWarningEvent:
    """Emitted when schema or parse warnings occur in permissive mode."""

    category: str = "validation"
    source_summary: str = ""
    override_count: int = 0
    warning_count: int = 0
    policy_mode: str = "permissive"
    timestamp: Timestamp = field(default_factory=lambda: Timestamp(0.0))