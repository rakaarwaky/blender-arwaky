"""Capabilities: Sensitive redactor — FR-SEC-004.

Detects and redacts sensitive values from text and structured data.
Implements RedactSensitiveProtocol.
"""

from __future__ import annotations

import re

from modules.shared.src.security.contract_redact_sensitive_protocol import RedactSensitiveProtocol
from modules.shared.src.security.taxonomy_security_vo import RedactionVO

_DEFAULT_PATTERNS: tuple[str, ...] = (
    r"(?i)(password|passwd|secret|token|api[_-]?key|access[_-]?key|private[_-]?key)\s*[=:]\s*\S+",
    r"(?i)(bearer|basic)\s+[A-Za-z0-9\-._~+/]+=*",
    r"(?i)sk-[A-Za-z0-9]{20,}",
    r"(?i)ghp_[A-Za-z0-9]{36}",
    r"(?i)AKIA[0-9A-Z]{16}",
)


class SensitiveRedactor(RedactSensitiveProtocol):
    """Detects and redacts sensitive values from text using pattern and key-based detection."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(
        self,
        extra_patterns: tuple[str, ...] = (),
        extra_key_names: tuple[str, ...] = (),
        debug_mode: bool = False,
    ) -> None:
        self._patterns = _DEFAULT_PATTERNS + extra_patterns
        self._key_names = extra_key_names
        self._debug_mode = debug_mode

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
                pattern = rf"(?i)({re.escape(key)})\s*[=:]\s*\S+"
                text, count = re.subn(pattern, r"\1=[REDACTED]", text)
                redacted_count += count

            if len(text) > 10_000:
                text = text[:10_000] + "\n[TRUNCATED]"

            return RedactionVO(
                text=request.text,
                sensitivity_level=request.sensitivity_level,
                patterns=request.patterns,
                key_names=request.key_names,
                redacted_text=text,
                redacted_count=redacted_count,
            )
        except Exception as exc:
            return RedactionVO(
                text=request.text,
                sensitivity_level=request.sensitivity_level,
                redacted_text="[REDACTION_FAILED]",
                failed=True,
                failure_reason=str(exc),
            )

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────
    def __repr__(self) -> str:
        return "SensitiveRedactor()"
