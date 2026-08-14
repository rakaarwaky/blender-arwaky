"""Capability: Redaction rules provider (FR-CFG-005).

Implements IRedactionRulesProtocol — provides sensitive key patterns
and redaction rules used by consuming features for masking.
"""

from __future__ import annotations

from modules.shared.src.config.contract_redaction_rules_protocol import IRedactionRulesProtocol
from modules.shared.src.config.taxonomy_config_constant import (
    REDACTION_PLACEHOLDER,
    SENSITIVE_KEY_PATTERNS,
)
from modules.shared.src.config.taxonomy_config_vo import RedactionRule, SettingsData, SettingsValue


# ─── Block 1: Class Definition & Constructor ───────────────
class RedactionRulesCapability(IRedactionRulesProtocol):
    """FR-CFG-005: Provide redaction rules.

    Rules contain key patterns only, never secret values.

    Substring matching semantics are intentional (PM Q14): a pattern such as
    ``auth`` also matches ``author`` — an accepted false positive. Matching is
    case-insensitive substring, so broad patterns catch variants.

    Redaction is full-only (PM Q15): ``full_redact`` is always True; partial
    masking of values is not supported. The placeholder is constant.

    Extension is via composition-root injection only (PM Q16): additional
    patterns are supplied through ``extra_patterns`` at construction time,
    never read from settings at runtime.
    """

    def __init__(self, extra_patterns: tuple[str, ...] = ()) -> None:
        self._rule = RedactionRule(
            key_patterns=SENSITIVE_KEY_PATTERNS + tuple(extra_patterns),
            placeholder=REDACTION_PLACEHOLDER,
            full_redact=True,
        )

    # ─── Block 2: Protocol Method Implementation ──────────────

    def get_redaction_rule(self) -> RedactionRule:
        """Return the authoritative redaction rule."""
        return self._rule

    def redact_value(self, key: str, value: SettingsValue) -> SettingsValue:
        """Redact a value if its key matches a sensitive pattern."""
        if self._rule.matches_key(key):
            return self._rule.placeholder
        return value

    def redact_dict(self, data: SettingsData) -> SettingsData:
        """Recursively redact all sensitive values in a dictionary."""
        result: SettingsData = {}
        for key, value in data.items():
            if self._rule.matches_key(key):
                result[key] = self._rule.placeholder
            elif isinstance(value, dict):
                result[key] = self.redact_dict(value)
            elif isinstance(value, list):
                result[key] = [self.redact_dict(item) if isinstance(item, dict) else item for item in value]
            else:
                result[key] = value
        return result

    # ─── Block 3: Dunder Methods, Factories, Helpers ──────────

    def __repr__(self) -> str:
        return "RedactionRulesCapability()"
