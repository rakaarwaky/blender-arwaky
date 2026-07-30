"""Contract: Redaction rules protocol (FR-CFG-005).

Defines the inbound behavior interface for providing sensitive key
patterns and redaction rules used by consuming features for masking.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import ConfigPath
from .taxonomy_config_vo import RedactionRule, SettingsData, SettingsValue


class IRedactionRulesProtocol(ABC):
    """Protocol for providing redaction rules (FR-CFG-005)."""

    @abstractmethod
    def get_redaction_rule(self) -> RedactionRule:
        """Return the authoritative redaction rule for sensitive key detection."""
        ...

    @abstractmethod
    def redact_value(self, key: ConfigPath, value: SettingsValue) -> SettingsValue:
        """Redact a value if its key matches a sensitive pattern."""
        ...

    @abstractmethod
    def redact_dict(self, data: SettingsData) -> SettingsData:
        """Recursively redact all sensitive values in a dictionary."""
        ...
