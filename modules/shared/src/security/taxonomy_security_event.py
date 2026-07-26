"""Security domain — Events for audit, violation, redaction failure, and policy override.

Immutable event payloads for the observability layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field as dc_field

from .taxonomy_security_vo import (
    AuditSeverity,
    ViolationCategory,
)


@dataclass(frozen=True)
class SecurityViolationEvent:
    """Emitted when a security policy violation is detected."""
    event_category: str = "security_violation"
    violation_category: ViolationCategory = ViolationCategory.PATH_TRAVERSAL
    severity: AuditSeverity = AuditSeverity.WARNING
    source_feature: str = ""
    operation_type: str = ""
    target_metadata: dict = dc_field(default_factory=dict)
    correlation_id: str | None = None
    timestamp: float = 0.0
    policy_mode: str = "strict"


@dataclass(frozen=True)
class SecurityAuditEvent:
    """Emitted for auditable security-related activity."""
    event_category: str = "security_audit"
    violation_category: ViolationCategory = ViolationCategory.PATH_TRAVERSAL
    severity: AuditSeverity = AuditSeverity.INFO
    source_feature: str = ""
    operation_type: str = ""
    target_metadata: dict = dc_field(default_factory=dict)
    correlation_id: str | None = None
    timestamp: float = 0.0
    policy_mode: str = "strict"


@dataclass(frozen=True)
class RedactionFailureEvent:
    """Emitted when sensitive value redaction cannot be safely completed."""
    event_category: str = "redaction_failure"
    severity: AuditSeverity = AuditSeverity.ERROR
    source_feature: str = ""
    operation_type: str = ""
    failure_reason: str = ""
    target_metadata: dict = dc_field(default_factory=dict)
    correlation_id: str | None = None
    timestamp: float = 0.0


@dataclass(frozen=True)
class PolicyOverrideEvent:
    """Emitted when a security control is explicitly disabled or bypassed."""
    event_category: str = "policy_override"
    severity: AuditSeverity = AuditSeverity.WARNING
    source_feature: str = ""
    operation_type: str = ""
    override_detail: str = ""
    target_metadata: dict = dc_field(default_factory=dict)
    correlation_id: str | None = None
    timestamp: float = 0.0
