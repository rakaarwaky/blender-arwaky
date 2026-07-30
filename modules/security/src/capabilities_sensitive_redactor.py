"""Capabilities: Sensitive redactor — FR-SEC-004.

Detects and redacts sensitive values from text and structured data.
Implements RedactSensitiveProtocol.
"""

from __future__ import annotations

import re

from modules.shared.src.security.contract_redact_sensitive_protocol import RedactSensitiveProtocol

# ─── Taxonomy imports ─────────────────────
from modules.shared.src.security.taxonomy_security_constant import KV_VALUE, REDACTION_SENSITIVE_PATTERNS
from modules.shared.src.security.taxonomy_security_vo import RedactionVO


class SensitiveRedactor(RedactSensitiveProtocol):
    """Detects and redacts sensitive values from text using pattern and key-based detection."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(
        self,
        extra_patterns: tuple[str, ...] = (),
        extra_key_names: tuple[str, ...] = (),
    ) -> None:
        self._patterns = REDACTION_SENSITIVE_PATTERNS + extra_patterns
        self._key_names = extra_key_names

    # ─── Block 2: Public Contract  ────────────────────────
    async def redact(self, request: RedactionVO) -> RedactionVO:
        """Detect and redact sensitive values from text.

        FR-SEC-004: preserves non-sensitive key names during key-based redaction,
        replacing only the value portion with [REDACTED].
        """
        try:
            text = request.text
            redacted_count = 0

            patterns = self._patterns + request.patterns
            for pattern in patterns:
                text, count = re.subn(pattern, "[REDACTED]", text)
                redacted_count += count

            all_keys = self._key_names + request.key_names
            for key in all_keys:
                # Case-insensitive quoted-key aware matching
                pattern = rf'((["\']?)(?i:{re.escape(key)})\2\s*[:=]\s*)' + KV_VALUE
                text, count = re.subn(pattern, r'\1[REDACTED]', text)
                redacted_count += count

            if len(text) > 10_000:
                text = text[:10_000] + "\n[TRUNCATED]"

            return RedactionVO(
                text=text,
                sensitivity_level=request.sensitivity_level,
                patterns=request.patterns,
                key_names=request.key_names,
                redacted_text=text,
                redacted_count=redacted_count,
            )
        except Exception as exc:
            return RedactionVO(
                text="[REDACTION_FAILED]",
                sensitivity_level=request.sensitivity_level,
                redacted_text="[REDACTION_FAILED]",
                failed=True,
                failure_reason=str(exc),
            )

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────
    def __repr__(self) -> str:
        return "SensitiveRedactor()"
