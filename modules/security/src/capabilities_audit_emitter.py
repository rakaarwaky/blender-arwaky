"""Capabilities: Audit emitter — FR-SEC-005.

Emits structured security audit events for violations, suspicious activity, and policy overrides.
Implements EmitAuditProtocol.

FR-SEC-004: tokens/credentials/passwords must not appear in logs. Audit events are
observability output, so any sensitive value nested in `target_metadata` (or
`redacted_reason`) is redacted at the sink before emission — defense-in-depth that
complements SensitiveRedactor and protects against callers passing raw secrets.
"""

from __future__ import annotations

import contextlib
import re
import time
import uuid
from typing import Any, Protocol

from modules.shared.src.security.contract_emit_audit_protocol import EmitAuditProtocol
from modules.shared.src.security.taxonomy_security_vo import SecurityAuditEventVO

# Matches the canonical SensitiveRedactor detection set (FR-SEC-004). Kept local to
# the emit sink so the capability stays independently usable (no capability→capability
# dependency) while still masking the same secret shapes at the audit boundary.
# Value half mirrors SensitiveRedactor._KV_VALUE (spaced quoted secrets consumed whole).
_KV_VALUE = r'(?:(["\'])(?:\\.|[^"\'])*\2|[^"\'\s,]+)'

_SENSITIVE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r'(?i)(["\']?)(password|passwd|secret|token|api[_-]?key|access[_-]?key|private[_-]?key)\1\s*[:=]\s*' + _KV_VALUE),
    re.compile(r"(?i)(bearer|basic)\s+[A-Za-z0-9\-._~+/]+=*"),
    re.compile(r"(?i)sk-[A-Za-z0-9]{20,}"),
    re.compile(r"(?i)ghp_[A-Za-z0-9]{36}"),
    re.compile(r"(?i)AKIA[0-9A-Z]{16}"),
)


def _redact_sensitive(value: object) -> Any:
    """Recursively mask obvious secret shapes in nested audit metadata.

    Strings are pattern-redacted; dict/list/tuple are walked without mutating the
    caller's input object. Non-text scalars pass through untouched.
    """
    if isinstance(value, str):
        text = value
        for pattern in _SENSITIVE_PATTERNS:
            text = pattern.sub("[REDACTED]", text)
        return text
    if isinstance(value, dict):
        return {key: _redact_sensitive(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return type(value)(_redact_sensitive(item) for item in value)
    return value


class _AuditSink(Protocol):
    """Protocol for delivering audit events to observability (DI boundary)."""

    def deliver(self, event: SecurityAuditEventVO) -> None: ...


class AuditEmitter(EmitAuditProtocol):
    """Emits structured security audit events with fallback on sink failure."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self, sink: _AuditSink | None = None) -> None:
        self._sink = sink

    # ─── Block 2: Public Contract  ────────────────────────
    async def emit_audit(self, event: SecurityAuditEventVO) -> SecurityAuditEventVO:
        """Emit a structured security audit event for violations and policy activity.

        FR-SEC-004: redact sensitive values from `target_metadata` / `redacted_reason`
        before emission so secrets never reach the observability sink, regardless of
        whether the caller pre-redacted. The caller's input event is never mutated.
        """
        emitted = SecurityAuditEventVO(
            violation_category=event.violation_category,
            operation_type=event.operation_type,
            source_feature=event.source_feature,
            target_metadata=_redact_sensitive(event.target_metadata),  # FR-SEC-004
            severity=event.severity,
            correlation_id=event.correlation_id,
            redacted_reason=_redact_sensitive(event.redacted_reason) if event.redacted_reason else None,
            event_id=uuid.uuid4().hex[:16],
            timestamp=time.time(),
            policy_mode=event.policy_mode,
        )

        if self._sink:
            with contextlib.suppress(Exception):
                self._sink.deliver(emitted)

        return emitted

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────
    def __repr__(self) -> str:
        return "AuditEmitter()"
