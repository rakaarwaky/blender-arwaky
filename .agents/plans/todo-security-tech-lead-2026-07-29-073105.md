# Review Plan: security — Tech Lead (Phase 3)

## Summary

The `modules/security/` feature implements FR-SEC-001 through FR-SEC-005 (path validation, archive guarding, code validation, sensitive redaction, audit emission). The codebase is well-structured with clear layer separation and protocol-based capability interfaces. However, two **critical runtime bugs** will crash the system on execution (undefined `logger` in audit emitter fallback, and a `debug_mode` kwarg passed to a constructor that doesn't accept it), an insecure fallback in the audit emitter fails to redact `redacted_reason`, the archive guard silently ignores its `policy` parameter and omits `allowed_directories` enforcement, and the code validator blocks the async event loop with a synchronous `ast.parse()` call.

## Findings by Category

### Security

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | `logger.warning()` called in `AuditEmitter.emit_audit()` fallback path but `logging` was never imported and `logger` was never defined — will raise `NameError` at runtime whenever audit sink delivery fails | `capabilities_audit_emitter.py:87` | Add `import logging` at the top of the file and `logger = logging.getLogger(__name__)` alongside the other imports (lines 13). This restores the fallback path so audit events are not silently swallowed when the sink is unavailable (FR-SEC-005 mandate). |
| 2 | 🔴 CRITICAL | `SensitiveRedactor(debug_mode=self._policy.redaction_debug_mode)` in `SecurityContainer.wire()` passes a keyword argument that does not exist on `SensitiveRedactor.__init__`, which only accepts `extra_patterns` and `extra_key_names` — will raise `TypeError` at every `wire()` call | `root_security_container.py:65` | Either add `debug_mode` as an accepted parameter to `SensitiveRedactor.__init__` (and store it for use in the redaction logic or diagnostics), or remove the `debug_mode` argument from the `SecurityContainer.wire()` call and wire it through a separate setter or policy pass-through. The constructor signature and the call site must agree. |

### Performance

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 3 | 🟡 WARNING | `ast.parse(request.code_text)` is a synchronous call inside the `async def validate_code()` method — blocks the event loop for the duration of AST parse, which grows linearly with code payload size | `capabilities_code_validator.py:68` | Wrap with `loop.run_in_executor(None, ast.parse, request.code_text)` to offload CPU-bound parsing to a thread pool, keeping the async event loop responsive. Alternatively use `asyncio.get_event_loop().run_in_executor()`. |

### Error Handling

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 4 | 🟡 WARNING | Fallback `SecurityAuditEventVO` on line 95 passes `redacted_reason=event.redacted_reason` directly without applying `_redact_sensitive()`, while the primary path on line 75 redacts the same field — inconsistent defense-in-depth, allowing secrets to leak through the fallback audit channel when the sink fails | `capabilities_audit_emitter.py:95` | Pass `_redact_sensitive(event.redacted_reason)` in the fallback constructor on line 95 (matching line 75), or use the same `_redact_sensitive` call on both paths. FR-SEC-004 mandates that raw secrets must not appear in audit events under any circumstance. |

### SOLID Principles

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 5 | 🟡 WARNING | `ArchiveGuard.__init__` stores `self._policy = policy` but the constructor parameter is never read — all policy decisions use `request.options` (from the VO). This is a dead attribute that misleads maintainers into thinking the capability enforces policy independently. | `capabilities_archive_guard.py:24` | Remove the `policy` parameter from `ArchiveGuard.__init__` and the `self._policy = policy` assignment. The class should be documented as requiring callers (e.g., `SecurityContainer.wire()`) to validate `allowed_directories` separately, OR add enforcement inside the capability (preferred — closes the FR-SEC-002 enforcement gap). |
| 6 | 🟡 WARNING | `SecurityOrchestrator` has 5 `async` delegate methods, each with near-identical boilerplate (`getattr` for correlation_id, `logger.info`, then delegation). The orchestrator's role is coordination, but the uniform pattern suggests a shared helper method `_delegate` could eliminate duplication. | `agent_security_orchestrator.py:56-84` | Extract a private `_delegate` helper that accepts the capability method, request, and correlation_id source, then call it from each public method. This keeps the orchestrator thin and each delegate method readable. |

### Code Quality & AES Violations

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 7 | 🔴 CRITICAL | `capabilities_archive_guard.py:46-48` contains a comment acknowledging the capability does NOT enforce `allowed_directories`, leaving enforcement to callers. FR-SEC-002 requires destination directory validation inside the capability. | `capabilities_archive_guard.py:46-48` | Add `allowed_directories` validation to `ArchiveGuard.validate_extraction`. The destination directory (`dest`) should be checked against policy-configured allowed directories before any entry-level validation runs. This closes the gap where an archive extraction to an unauthorized path could pass the archive guard. |
| 8 | 🟡 WARNING | `capabilities_archive_guard.py` line 24 `self._policy = policy` stores a reference that is never used (dead code). The constructor accepts a `policy` parameter with `None` default, but the stored value is never read. | `capabilities_archive_guard.py:24` | Remove the unused `policy` parameter and `self._policy` assignment (see Finding #5 in SOLID Principles). |
| 9 | 🟢 INFO | Private `_KV_VALUE` imported from `taxonomy_security_constant` in `capabilities_sensitive_redactor.py:12` — `_KV_VALUE` is a private implementation detail of the taxonomy constant file, not part of its public API. | `capabilities_sensitive_redactor.py:12` | Add `_KV_VALUE` to the public exports of `taxonomy_security_constant` (e.g., via `KV_VALUE` without underscore prefix) or move the pattern definition into a shared shared contract protocol so the dependency is explicit rather than reliant on a private name. |

### Maintainability

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 10 | 🟢 INFO | `agent_security_orchestrator.py:33` uses hardcoded `logging.getLogger("BlenderMCPServer")` instead of `__name__`, making it difficult to correlate log output with the security module specifically in multi-module logging configurations. | `agent_security_orchestrator.py:33` | Change to `logging.getLogger(__name__)` for module-scoped logging that matches Python logging conventions. |
| 11 | 🟢 INFO | `capabilities_audit_emitter.py` lines 68-79 (primary path) and lines 88-99 (fallback path) construct `SecurityAuditEventVO` with near-identical field sets, duplicating 8 of 11 fields per AES305 rule. The only differences are the `target_metadata` redaction inconsistency (Finding #4) and the `policy_mode` value. | `capabilities_audit_emitter.py:68-79,88-99` | Extract a helper `_build_audit_event(event, policy_mode, redact_reason=True)` that constructs the common fields and lets each call site override the divergences. Fixes both the duplication (AES305) and the fallback redaction inconsistency (Finding #4). |

## Action Items

- [ ] 🔴 CRITICAL Add `import logging` + `logger = logging.getLogger(__name__)` to `capabilities_audit_emitter.py` to fix the NameError at runtime (Finding #1)
- [ ] 🔴 CRITICAL Fix `SensitiveRedactor` constructor call in `root_security_container.py:65` — either match the signature or add `debug_mode` parameter (Finding #2)
- [ ] 🔴 CRITICAL Add `allowed_directories` enforcement inside `ArchiveGuard.validate_extraction` instead of relying on caller-side validation (Finding #7)
- [ ] 🟡 WARNING Offload `ast.parse()` to executor to avoid blocking the async event loop in `capabilities_code_validator.py` (Finding #3)
- [ ] 🟡 WARNING Pass `_redact_sensitive()` over `redacted_reason` in the `AuditEmitter` fallback path (Finding #4)
- [ ] 🟡 WARNING Remove unused `policy` parameter and `self._policy` from `ArchiveGuard` (Finding #5)
- [ ] 🟡 WARNING Extract `_delegate` helper in `SecurityOrchestrator` to eliminate boilerplate duplication (Finding #6)
- [ ] 🟢 INFO Export `KV_VALUE` publicly from taxonomy constants or use a public accessor (Finding #9)
- [ ] 🟢 INFO Change hardcoded logger name to `__name__` in `agent_security_orchestrator.py` (Finding #10)
- [ ] 🟢 INFO Extract shared `_build_audit_event` helper in `AuditEmitter` to fix AES305 duplication and fallback inconsistency (Finding #11)

## Fixed Code

### Fix #1 — `capabilities_audit_emitter.py`: Add missing logging import and logger

**File:** `modules/security/src/capabilities_audit_emitter.py` (lines 13)

```python
# Before (missing import):
import re
import time
import uuid
from typing import Any, Protocol

# After:
import logging
import re
import time
import uuid
from typing import Any, Protocol

logger = logging.getLogger(__name__)
```

### Fix #2 — `root_security_container.py`: Remove mismatched `debug_mode` kwarg OR extend `SensitiveRedactor`

**File:** `modules/security/src/root_security_container.py` (line 65)

Option A — Remove the argument (if debug mode does not yet need to be passed through):

```python
# Before:
redact_cap = SensitiveRedactor(debug_mode=self._policy.redaction_debug_mode)

# After:
redact_cap = SensitiveRedactor()
```

Option B — Add `debug_mode` to `SensitiveRedactor.__init__` in `capabilities_sensitive_redactor.py`:

```python
# In __init__:
def __init__(
    self,
    extra_patterns: tuple[str, ...] = (),
    extra_key_names: tuple[str, ...] = (),
    debug_mode: bool = False,
) -> None:
    self._patterns = _DEFAULT_PATTERNS + extra_patterns
    self._key_names = extra_key_names
    self._debug_mode = debug_mode
    if debug_mode:
        logger.info("SensitiveRedactor: debug mode enabled, redaction failures will include diagnostic context")
```

### Fix #4 — `capabilities_audit_emitter.py`: Redact `redacted_reason` in fallback path

**File:** `modules/security/src/capabilities_audit_emitter.py` (line 95)

```python
# Before:
redacted_reason=event.redacted_reason,

# After:
redacted_reason=_redact_sensitive(event.redacted_reason) if event.redacted_reason else None,
```

### Fix #5/8 — `capabilities_archive_guard.py`: Remove unused `policy` parameter

**File:** `modules/security/src/capabilities_archive_guard.py` (lines 19, 24)

```python
# Before:
def __init__(self, policy: SecurityPolicyVO | None = None) -> None:
    self._policy = policy

# After:
def __init__(self) -> None:
    pass
```

### Fix #10 — `agent_security_orchestrator.py`: Use module-scoped logger name

**File:** `modules/security/src/agent_security_orchestrator.py` (line 33)

```python
# Before:
logger = logging.getLogger("BlenderMCPServer")

# After:
logger = logging.getLogger(__name__)
```
