"""Security domain — Constants.

All magic strings, defaults, and limits for security policy.
"""

from __future__ import annotations

# ─── Default Limits ─────────────────────────────────────────────

SECURITY_DEFAULT_MAX_CODE_SIZE: int = 1_048_576  # 1 MB
SECURITY_DEFAULT_ARCHIVE_MAX_DEPTH: int = 5
SECURITY_DEFAULT_ARCHIVE_MAX_TOTAL_SIZE: int = 104_857_600  # 100 MB
SECURITY_DEFAULT_ARCHIVE_MAX_ENTRY_SIZE: int = 10_485_760  # 10 MB
SECURITY_DEFAULT_ARCHIVE_MAX_ENTRY_COUNT: int = 1_000

# ─── Policy Modes ───────────────────────────────────────────────

SECURITY_POLICY_STRICT: str = "strict"
SECURITY_POLICY_PERMISSIVE: str = "permissive"

# ─── Event Categories ───────────────────────────────────────────

AUDIT_EVENT_VIOLATION: str = "security_violation"
AUDIT_EVENT_AUDIT: str = "security_audit"
AUDIT_EVENT_REDACTION_FAILURE: str = "redaction_failure"
AUDIT_EVENT_POLICY_OVERRIDE: str = "policy_override"

# ─── Source Feature Name ────────────────────────────────────────

SECURITY_SOURCE_FEATURE: str = "security"

# ============================================================
# Shared Redaction Patterns (AES305 — single source of truth)
# ============================================================

# Quoted-key aware value half — matches shell (cred=secret), YAML
# (cred: secret), and JSON ("cred": "secret") forms.
KV_VALUE: str = r'(?:(["\'])(?:\\.|[^"\'])*\2|[^"\'\s,]+)'

REDACTION_SENSITIVE_PATTERNS: tuple[str, ...] = (
    r'(?i)(["\']?)(?:password|passwd|secret|token|api[_-]?key|access[_-]?key|private[_-]?key)\1\s*[:=]\s*' + KV_VALUE,
    r"(?i)(bearer|basic)\s+[A-Za-z0-9\-._~+/]+=*",
    r"(?i)sk-[A-Za-z0-9]{20,}",
    r"(?i)ghp_[A-Za-z0-9]{36}",
    r"(?i)AKIA[0-9A-Z]{16}",
)
