# Review Plan: security — Business Analyst (Phase 2)

## Summary

The **security** feature is the oldest unprocessed module (FRD.md mtime 1785067353) and serves as the centralized security policy layer for blender-arwaky, implementing all 5 FR-SEC requirements (path validation, archive safety, code validation, redaction, audit emission). The module follows a clean layered architecture with 5 capability protocols, shared taxonomy VOs, an orchestrator agent, and a DI container. However, several gaps exist: two configuration fields in `SecurityPolicyVO` (`blocked_code_constructs`, `redaction_patterns`) are defined but never consumed by capabilities; the audit emitter silently drops delivery failures instead of creating fallback records as mandated by FR-SEC-005; and the archive guard does not validate that the extraction destination itself is within allowed directories. Duplicate redaction regex patterns across `SensitiveRedactor` and `AuditEmitter` also violate DRY and AES305.

## Findings by Category

### Requirements Clarity

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | `SecurityPolicyVO.blocked_code_constructs` is a configurable field (FRD Config Keys table) but `CodeValidator` uses a hardcoded blocklist instead of reading from the policy object — the configurable interface exists but is unimplemented | `modules/shared/src/security/taxonomy_security_vo.py:245` (field exists); `modules/security/src/capabilities_code_validator.py:100-101` (hardcoded) | Wire `policy.blocked_code_constructs` into the blocked set at construction or validation time; fall back to hardcoded defaults when the policy field is empty |
| 2 | 🟡 WARNING | `SecurityPolicyVO.redaction_patterns` is a configurable field (FRD Config Keys table) but `SensitiveRedactor` only reads `request.patterns`, never `self._policy.redaction_patterns` — the policy is injected but unused for redaction patterns | `modules/shared/src/security/taxonomy_security_vo.py:247` (field exists); `modules/security/src/capabilities_sensitive_redactor.py:54` (uses only request patterns) | Read `self._policy.redaction_patterns` in `__init__` or `redact()` and merge with request patterns before applying |
| 3 | 🟡 WARNING | `canonical_path` is returned in `PathValidationVO` even on denial responses (lines 101-103), which FR-SEC-001 explicitly says should not expose sensitive path details beyond redacted diagnostic information | `modules/security/src/capabilities_path_validator.py:101` | Remove `canonical_path` from denial responses, or redact it to only the last path segment |
| 4 | 🟡 WARNING | FR-SEC-003 states "Validation may support allowed exception list for trusted operations when explicitly configured" but `CodeValidator` has no support for an allowlist — it is always deny-by-default | `modules/security/src/capabilities_code_validator.py:38-130` | Add optional `allowed_constructs` field to policy/request that bypasses blocked-module/function checks when a trusted context is provided |
| 5 | 🔴 CRITICAL | FR-SEC-002 states archive extraction should validate that the destination directory is inside allowed directories — `ArchiveGuard` validates entries don't escape the destination but never checks if the destination itself is within allowed directories, meaning an arbitrary path could be used as the extraction target | `modules/security/src/capabilities_archive_guard.py:29` (only normalizes destination, no allowed-dir check) | Add destination directory validation against `SecurityPolicyVO.allowed_directories` before processing entries |
| 6 | 🟡 WARNING | FR-SEC-002 explicitly calls out "archive bomb patterns" as an edge case to defend against, but `ArchiveGuard` only enforces depth/size/count limits — no detection of nested archives attempting bomb behavior | `modules/security/src/capabilities_archive_guard.py:26-103` | Add a check for nested archive entries (e.g., `.zip` inside `.zip`) and flag or reject them when the policy prohibits recursive extraction |

### Business Flow

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | `AuditEmitter.emit_audit()` uses `contextlib.suppress(Exception)` to silently swallow all sink delivery failures. FR-SEC-005 mandates: "If audit sink is unavailable, violation must still be returned to caller and local fallback audit record should be created." The current code drops the audit event entirely on sink failure — no fallback record is created | `modules/security/src/capabilities_audit_emitter.py:91-92` | On sink failure, create and store a local fallback audit record (e.g., append to a local queue or file) before returning; never suppress without a fallback |
| 2 | 🟡 WARNING | No composed multi-step security flow exists — capabilities are independent and a caller must manually chain validate_path → validate_code → emit_audit. The FRD specifies that security decisions should be delegated consistently, but there is no orchestrated "secure execution" flow that validates, executes, and audits as one transaction | `modules/security/src/agent_security_orchestrator.py:55-79` | Add a composed method (e.g., `secure_execute`) that validates the operation context, runs the action, and emits an audit event atomically |
| 3 | 🟡 WARNING | `_AuditSink.deliver()` is a sync protocol (`def deliver`, not `async def deliver`) while all other capability methods are async. This blocks the event loop when the observability sink is slow or unresponsive | `modules/security/src/capabilities_audit_emitter.py:59` | Make `_AuditSink.deliver()` async (`async def deliver`) to be consistent with the async architecture |
| 4 | 🟡 WARNING | `ArchiveGuard` does not check `ArchiveEntryVO.is_directory` — directory entries in archives can be used for traversal attacks (e.g., a directory symlink or a directory with `..` in its path) | `modules/security/src/capabilities_archive_guard.py:65-77` (entry loop ignores `is_directory`) | Validate directory entries against the same traversal rules as file entries; reject directory entries that could enable escape |

### Logic Implementation

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | `CodeValidator` hardcodes `blocked_modules` and `blocked_functions` instead of reading from `SecurityPolicyVO.blocked_code_constructs`. The FRD explicitly requires a configurable block list: "Blocked construct list must be configurable." The `PolicyOverride` event type exists for when validation is disabled by config, but no event type exists when constructs are reconfigured | `modules/security/src/capabilities_code_validator.py:100-101` | Read `policy.blocked_code_constructs` (if non-empty) and use it as the blocklist; only fall back to hardcoded defaults when the policy field is empty |
| 2 | 🔴 CRITICAL | `SensitiveRedactor` does not read `SecurityPolicyVO.redaction_patterns` — custom patterns from the policy configuration are silently ignored. The same is true for `key_names` from the policy. Only the `request`-level patterns are applied | `modules/security/src/capabilities_sensitive_redactor.py:54` | In `redact()`, prepend `self._policy.redaction_patterns` and `self._policy.redaction_key_names` to the effective patterns/keys, just as `extra_patterns` and `extra_key_names` already support |
| 3 | 🟡 WARNING | Duplicate regex patterns for sensitive value detection exist in both `SensitiveRedactor._DEFAULT_PATTERNS` (lines 24-30) and `AuditEmitter._SENSITIVE_PATTERNS` (lines 29-35). These are identical detection logic copied across two files — a violation of AES305 (Duplication Code) | `modules/security/src/capabilities_sensitive_redactor.py:24-30` and `modules/security/src/capabilities_audit_emitter.py:29-35` | Extract the shared pattern set to a shared taxonomy constant or utility module (e.g., `modules/shared/src/security/taxonomy_security_constant.py`) and import from both locations |
| 4 | 🟡 WARNING | `_CodePayloadChecker` protocol is defined at line 20-23 but never used anywhere — dead interface that creates confusion about its purpose | `modules/security/src/capabilities_code_validator.py:20-23` | Either implement the payload check using this protocol or remove the unused protocol definition |
| 5 | 🟡 WARNING | Path traversal check on line 67 of `PathValidator` operates on the raw `target` string (pre-normalization) using `target.split(os.sep)`. Encoded or double-encoded traversal sequences (`%2e%2e`, `..\\/`) may bypass this check on some platforms | `modules/security/src/capabilities_path_validator.py:67` | Normalize the path first, then check the normalized result for `..` components; also add percent-decoding normalization before the check |
| 6 | 🟡 WARNING | Truncation in `SensitiveRedactor` at line 68-69 (`text[:10_000]`) could split a `[REDACTED]` placeholder mid-tag if the cutoff lands within it, potentially exposing that a redaction was attempted and its approximate location | `modules/security/src/capabilities_sensitive_redactor.py:68-69` | Truncate first, then apply redaction patterns to the truncated text; or ensure truncation point does not split across a `[REDACTED]` segment |
| 7 | 🟡 WARNING | The `validate_code` method in `CodeValidator` returns `allowed=False` immediately on syntax error even in non-strict mode (lines 88-98). The FRD states "an unparseable tree cannot be walked" but the intent of non-strict mode is to continue recording violations rather than blocking entirely — the early return stops at the first syntax error without attempting to report it as a violation and continue | `modules/security/src/capabilities_code_validator.py:88-98` | In non-strict mode, record syntax_error as a violation and continue processing (but since AST walk is impossible, the early return is reasonable — however the violation should still be returned to the caller, which it is) |

### Testability & Acceptance Criteria

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | No tests exist for the `SecurityOrchestrator` (agent layer) — all 2266 test lines cover individual capabilities in isolation, but there is no integration test that exercises the orchestrator delegating through all 5 protocols | `modules/security/tests/test_security_feature.py` (only covers `create_security_feature` aggregate, not `SecurityOrchestrator` directly) | Add orchestrator-level tests verifying delegation to each protocol and proper error propagation |
| 2 | 🟡 WARNING | No tests for `SecurityContainer.wire()` or `create_security_feature()` factory — the DI wiring is untested | No test file for container wiring | Add tests verifying that `wire()` correctly connects all 5 capabilities and that `aggregate` raises `RuntimeError` before wiring |
| 3 | 🟡 WARNING | The `conftest.py` comment notes "modules.shared.src is currently broken without it" — import shim issues suggest the test infrastructure is fragile and could mask real failures | `modules/security/tests/conftest.py` | Fix the import shim so tests can run cleanly without the workaround |
| 4 | 🟡 WARNING | No test coverage for cross-FR composition scenarios (e.g., path validation failure should trigger an audit event) | All test files | Add integration tests that exercise the full security flow: validate → act → audit |
| 5 | 🟢 INFO | Acceptance criteria from the FRD QA checklist (29 items) should be mapped to individual test functions with IDs matching the FR-SEC-XXX references | QA checklist in `modules/security/FRD.md` | Each QA checklist item should have a corresponding test function named `test_{fr_id}_{scenario}` |

### Traceability (FRD → Code)

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | `SecurityPolicyVO.blocked_code_constructs` (taxonomy field, FRD Config Keys) is not consumed by any code — traceability gap between configuration and implementation for FR-SEC-003 | `modules/shared/src/security/taxonomy_security_vo.py:245` | Wire the field into `CodeValidator` as described in Findings by Category |
| 2 | 🔴 CRITICAL | `SecurityPolicyVO.redaction_patterns` (taxonomy field, FRD Config Keys) is not consumed by any code — traceability gap for FR-SEC-004 | `modules/shared/src/security/taxonomy_security_vo.py:247` | Wire the field into `SensitiveRedactor` as described in Findings by Category |
| 3 | 🟡 WARNING | `SecurityPolicyVO.redaction_key_names` is not a defined field on `SecurityPolicyVO` but redaction supports key names via request — there is no way to configure default key names at the policy level | `modules/shared/src/security/taxonomy_security_vo.py:236-249` | Add `redaction_key_names: tuple[str, ...]` to `SecurityPolicyVO` |
| 4 | 🟢 INFO | All 5 FR-SEC requirements trace to exactly one capability file each ✓ — good one-to-one mapping | FRD → `capabilities_*.py` | No action needed |
| 5 | 🟢 INFO | All 5 contract protocols exist in `modules/shared/src/security/` and match their FR specifications ✓ | `contract_*_protocol.py` (5 files) | No action needed |

## Violations

- **AES305** (Duplication Code): Redaction regex patterns are duplicated verbatim between `capabilities_sensitive_redactor.py` (`_DEFAULT_PATTERNS`, lines 24-30) and `capabilities_audit_emitter.py` (`_SENSITIVE_PATTERNS`, lines 29-35). Both define identical regexes for password/token/secret/bearer/API key detection.
- **AES404** (Utility Role): No utility-layer files exist in the security module — `_redact_path()` (path_validator.py:130-134) and `_redact_sensitive()` (audit_emitter.py:38-53) are module-level helper functions inside capability files rather than being in a shared utility. These should be extracted to a shared taxonomy or utility module if reused across features.
- **AES303** (Mandatory Definition — MEDIUM sub-check): The `_KV_VALUE` regex constant in `sensitive_redactor.py` (line 17) and `audit_emitter.py` (line 27) serve the same purpose but are defined independently. They are not "empty" definitions, but the duplication is a structural concern.

## Action Items

- [ ] 🔴 CRITICAL Wire `SecurityPolicyVO.blocked_code_constructs` into `CodeValidator` — remove hardcoded blocklist, read from policy at construction
- [ ] 🔴 CRITICAL Wire `SecurityPolicyVO.redaction_patterns` into `SensitiveRedactor` — merge policy patterns with request patterns in `redact()`
- [ ] 🔴 CRITICAL Fix `AuditEmitter` to create a local fallback audit record on sink delivery failure — FR-SEC-005 mandates this explicitly
- [ ] 🔴 CRITICAL Validate that archive extraction destination directory is within allowed directories in `ArchiveGuard`
- [ ] 🟡 WARNING Extract shared redaction detection patterns into `taxonomy_security_constant.py` to fix AES305 duplication between `SensitiveRedactor` and `AuditEmitter`
- [ ] 🟡 WARNING Remove `canonical_path` from denial responses in `PathValidator` to prevent filesystem structure leakage
- [ ] 🟡 WARNING Remove unused `_CodePayloadChecker` protocol from `CodeValidator` or implement it via the policy's `max_code_size` field
- [ ] 🟡 WARNING Add `redaction_key_names` field to `SecurityPolicyVO` for configuring default key names at the policy level
- [ ] 🟡 WARNING Make `_AuditSink.deliver()` async to match the async architecture
- [ ] 🟡 WARNING Add orchestrator-level integration tests covering full security flow (validate → act → audit)
- [ ] 🟢 INFO Add archive bomb detection (nested archive detection) to `ArchiveGuard`
- [ ] 🟢 INFO Add directory entry validation (`is_directory`) to `ArchiveGuard` traversal checks
- [ ] 🟢 INFO Add path normalization before `..` check in `PathValidator` to handle encoded traversal attempts
- [ ] 🟢 INFO Ensure truncation in `SensitiveRedactor` does not split `[REDACTED]` tags mid-segment
- [ ] 🟢 INFO Map all 29 QA checklist items from FRD to individual test functions with FR-SEC-XXX IDs

## Fixed Code

### Fix 1: Wire `blocked_code_constructs` into `CodeValidator`

```python
# modules/security/src/capabilities_code_validator.py

# Replace line 100-101 (hardcoded) with policy-aware construction:
def _build_blocked_set(self) -> tuple[frozenset[str], frozenset[str]]:
    """Build blocked modules/functions from policy, falling back to defaults."""
    if self._policy and self._policy.blocked_code_constructs:
        # Parse policy string list into module and function sets
        modules = set()
        functions = set()
        for construct in self._policy.blocked_code_constructs:
            if construct in {"os", "subprocess", "shutil", "importlib", "sys",
                             "socket", "ctypes", "multiprocessing", "threading",
                             "signal", "pickle"}:
                modules.add(construct)
            else:
                functions.add(construct)
        return frozenset(modules), frozenset(functions)

    # Defaults (preserved for backward compatibility)
    return (
        frozenset({"os", "subprocess", "shutil", "importlib", "sys",
                    "socket", "ctypes", "multiprocessing", "threading",
                    "signal", "pickle"}),
        frozenset({"eval", "exec", "compile", "__import__", "breakpoint",
                   "globals", "locals", "getattr", "setattr", "delattr"}),
    )
```

### Fix 2: Create fallback audit record on sink failure

```python
# modules/security/src/capabilities_audit_emitter.py

# Replace lines 90-93:

local_fallback = None
if self._sink:
    try:
        self._sink.deliver(emitted)
    except Exception:
        # FR-SEC-005: create local fallback record when sink is unavailable
        local_fallback = SecurityAuditEventVO(
            violation_category=event.violation_category,
            operation_type=event.operation_type,
            source_feature=event.source_feature,
            target_metadata=event.target_metadata,
            severity=AuditSeverity.ERROR,
            correlation_id=event.correlation_id,
            redacted_reason=event.redacted_reason,
            event_id=uuid.uuid4().hex[:16],
            timestamp=time.time(),
            policy_mode="fallback",
        )
        logger.warning("Audit sink unavailable, stored fallback record: %s",
                        local_fallback.violation_category)

return emitted  # original violation is never suppressed
```

### Fix 3: Validate archive destination against allowed directories

```python
# modules/security/src/capabilities_archive_guard.py

# Add at the start of validate_extraction(), after destination normalization (line 29):
if self._policy and self._policy.allowed_directories:
    dest_allowed = any(
        dest.startswith(os.path.normpath(os.path.abspath(d)) + os.sep) or
        dest == os.path.normpath(os.path.abspath(d))
        for d in self._policy.allowed_directories
    )
    if not dest_allowed:
        return ArchiveExtractionVO(
            destination_directory=request.destination_directory,
            entries=request.entries,
            options=request.options,
            allowed=False,
            rejected_entries=tuple(rejected),
            warnings=tuple(warnings),
            audit_metadata={"rule": "destination_outside_allowed_dirs", "path": _redact_path(dest)},
        )
```

### Fix 4: Extract shared redaction patterns to taxonomy constant

```python
# modules/shared/src/security/taxonomy_security_constant.py  (add to existing file)

# Canonical sensitive value detection patterns — single source of truth.
# Shared by SensitiveRedactor and AuditEmitter to eliminate duplication (AES305).

REDACTION_SENSITIVE_PATTERNS: tuple[str, ...] = (
    r'(?i)(["\']?)(?:password|passwd|secret|token|api[_-]?key|access[_-]?key|private[_-]?key)\1\s*[:=]\s*' + _KV_VALUE,
    r"(?i)(bearer|basic)\s+[A-Za-z0-9\-._~+/]+=*",
    r"(?i)sk-[A-Za-z0-9]{20,}",
    r"(?i)ghp_[A-Za-z0-9]{36}",
    r"(?i)AKIA[0-9A-Z]{16}",
)
```

Then replace the duplicated definitions in both `capabilities_sensitive_redactor.py` (lines 24-30) and `capabilities_audit_emitter.py` (lines 29-35) with a single `from modules.shared.src.security.taxonomy_security_constant import REDACTION_SENSITIVE_PATTERNS`.
