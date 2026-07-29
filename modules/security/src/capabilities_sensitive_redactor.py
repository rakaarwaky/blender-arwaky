"""Capabilities: Sensitive redactor — FR-SEC-004.

Detects and redacts sensitive values from text and structured data.
Implements RedactSensitiveProtocol.
"""

from __future__ import annotations

import re

from modules.shared.src.security.contract_redact_sensitive_protocol import RedactSensitiveProtocol
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
        """Detect and redact sensitive values from text."""
        try:
            text = request.text
            redacted_count = 0

            patterns = self._patterns + request.patterns
            for pattern in patterns:
                text, count = re.subn(pattern, "[REDACTED]", text)
                redacted_count += count

            all_keys = self._key_names + request.key_names
            for key in all_keys:
                # Quoted-key aware so custom key names also match JSON/`"key": "value"` forms
                # — FR-SEC-004 nested/structured. Value half reuses KV_VALUE so spaced
                # quoted values are consumed whole.
                pattern = rf'(?i)(["\']?)(?:{re.escape(key)})\1\s*[:=]\s*' + KV_VALUE
                text, count = re.subn(pattern, "[REDACTED]", text)
                redacted_count += count

            if len(text) > 10_000:
                text = text[:10_000] + "\n[TRUNCATED]"

            # FR-SEC-004: the returned `text` carries the redacted (safe) output,
            # never the raw secret — any consumer reading `.text` stays leak-free.
            return RedactionVO(
                text=text,
                sensitivity_level=request.sensitivity_level,
                patterns=request.patterns,
                key_names=request.key_names,
                redacted_text=text,
                redacted_count=redacted_count,
            )
        except Exception as exc:
            # FR-SEC-004: on failure, prefer masking the entire payload over
            # leaking the original secret — never echo request.text back.
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
