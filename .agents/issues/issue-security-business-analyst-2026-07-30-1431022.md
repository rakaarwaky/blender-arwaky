## File: `.agents/issues/issue-security-business-analyst-2026-07-30-143022.md`

```markdown
# Issue: security — Business Logic & Requirements Review

## Summary
The security feature (v1.7.0) implements 5 FR-SEC operations with correct AES layering, proper DI, and defense-in-depth redaction in the audit emitter. However, several business logic gaps exist: (1) path validation ignores the `access_mode` field — read/write/create/delete/extract are all treated identically, violating FR-SEC-001's requirement for mode-specific directory enforcement; (2) code validation does not detect attribute-traversal sandbox escapes (`__class__.__bases__`) or `open()` calls, leaving FR-SEC-003's "unsafe internal attributes" and "unsafe file access" requirements unmet; (3) the redaction capability only handles flat text, not structured data (nested dicts/lists), despite FR-SEC-004 requiring structured support; (4) the orchestrator does not emit an audit event when code validation is disabled (policy override), violating FR-SEC-005's "policy override" category requirement; (5) no rate-limiting exists for high-frequency audit events.

## Findings by Category

### Requirements Clarity
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | FR-SEC-001 specifies "Write access against write-allowed dirs. Read access against read-allowed dirs when configured." The `SecurityPolicyVO` has a single `allowed_directories` tuple with no per-mode distinction. The FRD implies separate read/write directory lists but the taxonomy doesn't model this. | `modules/shared/src/security/taxonomy_security_vo.py:175` (`SecurityPolicyVO.allowed_directories`) | Either: (a) extend `SecurityPolicyVO` with `read_allowed_directories` and `write_allowed_directories` fields, or (b) clarify in FRD that a single `allowed_directories` list applies to all modes and remove the per-mode language. |
| 2 | 🟡 WARNING | FR-SEC-003 lists "unsafe internal attributes" as a blocked construct category but does not enumerate which attributes. The implementation blocks `getattr`/`setattr`/`delattr` function calls but not direct attribute access like `obj.__class__` or `().__class__.__bases__`. | `modules/security/FRD.md` (FR-SEC-003 Rules) | Enumerate in FRD: "Blocked attribute patterns: `__class__`, `__bases__`, `__mro__`, `__subclasses__`, `__globals__`, `__builtins__`, `__import__`." Then implement AST `ast.Attribute` node checking. |
| 3 | 🟡 WARNING | FR-SEC-004 says "Supports nested mappings/lists" but the `RedactionVO` input is `text: str`. There is no protocol path for structured data (dict/list) redaction. The utility function `redact_sensitive()` handles recursion, but it's not exposed through the capability contract. | `modules/shared/src/security/contract_redact_sensitive_protocol.py:14` | Either: (a) add a `data: dict | list | None` field to `RedactionVO` and handle structured redaction in the capability, or (b) document that structured redaction is available only via direct utility import for internal callers (audit emitter), and the protocol handles text-only for external callers. |
| 4 | 🟢 INFO | FR-SEC-005 says "High-frequency: rate-limited or grouped" but does not specify the rate limit threshold or grouping window. | `modules/security/FRD.md` (FR-SEC-005 Rules) | Add: "Rate limit: max 100 events/minute per violation_category. Excess events grouped into a single summary event with count." |

### Business Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 5 | 🔴 CRITICAL | `PathValidator.validate_path` never reads `request.access_mode`. A `DELETE` request to a read-only directory is allowed identically to a `READ` request. FR-SEC-001 explicitly requires mode-specific enforcement. | `modules/security/src/capabilities_path_validator.py:52-95` | Implement mode check: if `access_mode in (WRITE, CREATE, DELETE, EXTRACT)`, validate against write-allowed directories. If `access_mode == READ`, validate against read-allowed directories (or all allowed dirs if no separate read list). |
| 6 | 🟡 WARNING | `CodeValidator` does not detect `open()` calls. FR-SEC-003 lists "unsafe file access outside allowed dirs" as a blocked construct. An attacker can `open("/etc/passwd").read()` and the validator will allow it. | `modules/security/src/capabilities_code_validator.py:85-100` | Add `"open"` to the default blocked functions set. For more nuanced policy, allow `open()` only when the argument is a string literal within allowed directories (requires AST argument inspection). |
| 7 | 🟡 WARNING | `CodeValidator` does not detect attribute-traversal sandbox escapes. Code like `().__class__.__bases__[0].__subclasses__()` will pass validation. FR-SEC-003 lists "reflection/sandbox escape" and "unsafe internal attributes." | `modules/security/src/capabilities_code_validator.py:85-100` | Add an `ast.Attribute` visitor: if `node.attr` starts and ends with `__` (dunder attribute access on non-self objects), flag as `blocked_attribute_access`. Allowlist: `__init__`, `__name__`, `__doc__`. |
| 8 | 🟡 WARNING | Orchestrator does not emit audit event for policy override (validation disabled). When `code_validation_enabled=False`, `CodeValidator` returns `allowed=True` with `audit_metadata={"rule": "validation_disabled_override"}`. The orchestrator's condition `if not result.allowed or result.violations` is False, so no audit event is emitted. FR-SEC-005 requires "policy override" events. | `modules/security/src/agent_security_orchestrator.py:72-84` | Add: after `validate_code`, check `if result.audit_metadata.get("rule") == "validation_disabled_override"` and emit a `POLICY_OVERRIDE` audit event. |
| 9 | 🟢 INFO | FR-SEC-001: "Case-insensitive fs handled consistently." No case normalization exists. On macOS/Windows, `/Allowed/Dir` and `/allowed/dir` are the same directory but the string comparison in `is_within_allowed_dirs` is case-sensitive. | `modules/shared/src/security/utility_security_path.py:28-40` | Add: on case-insensitive platforms (`sys.platform in ("darwin", "win32")`), normalize both target and allowed dirs to lowercase before comparison. |

### Logic Implementation
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 10 | 🟡 WARNING | `SensitiveRedactor.redact()` key-based redaction uses `(?i:{re.escape(key)})` inside a raw f-string regex. The `(?i:...)` inline flag applies case-insensitivity only to the key group, but the overall pattern may behave unexpectedly with certain key names containing regex metacharacters after `re.escape`. More critically, the `KV_VALUE` pattern matches `[^"'\s,]+` which will over-match in YAML/JSON contexts (e.g., matching trailing commas or brackets). | `modules/security/src/capabilities_sensitive_redactor.py:42-46` | Test with edge cases: `key="value"`, `key: value`, `key=value,next`. Consider using separate patterns for JSON (`"key": "value"`), YAML (`key: value`), and shell (`key=value`) formats. |
| 11 | 🟡 WARNING | `ArchiveGuard.validate_extraction` depth check uses `relative.count(os.sep) + 1` which counts path segments, not archive nesting depth. A flat file `a/b/c/d/e/f.txt` has depth 6, but a nested archive (archive within archive) is a different concept. FR-SEC-002 says "Max nested extraction depth" which implies recursive archive extraction depth, not directory depth. | `modules/security/src/capabilities_archive_guard.py:72-79` | Clarify in FRD whether `max_depth` means (a) directory nesting depth of extracted paths, or (b) recursive archive-within-archive extraction depth. Current implementation handles (a). If (b) is intended, the capability needs a recursion counter passed through extraction options. |
| 12 | 🟡 WARNING | `AuditEmitter.emit_audit` generates `event_id=uuid.uuid4().hex[:16]` — a 16-char hex string (64 bits). For security audit events that may need to be correlated across systems, this is a low collision space. FR-SEC-005 specifies "correlation ID" as a separate field but doesn't specify uniqueness requirements for `event_id`. | `modules/security/src/capabilities_audit_emitter.py:55` | Use full UUID4 (`uuid.uuid4().hex` — 128 bits) or document the collision risk acceptance. |
| 13 | 🟢 INFO | `PathValidator._redact_path` redacts to `"/***" + last 2 segments`. On Windows, this produces `"/***\Users\name"` (mixed separators). Minor cosmetic issue in audit metadata. | `modules/security/src/capabilities_path_validator.py:30-34` | Normalize separators before redaction: `path.replace("\\", "/")` (already done) — but the output prefix `"/"` is Unix-specific. Use `os.sep` or just `"***"` prefix. |

### Testability & Acceptance Criteria
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 14 | 🟡 WARNING | No test files exist for the security module. The FRD QA Checklist has 17 items but none are automated. DI boundaries exist (path_resolver, audit sink) but no test exercises them. | `modules/security/` (no `tests/` directory) | Create `modules/security/tests/` with: `contract_security.py`, `unit_path_validator_traversal.py`, `unit_path_validator_symlink.py`, `unit_archive_guard_limits.py`, `unit_code_validator_blocked.py`, `unit_sensitive_redactor_patterns.py`, `unit_audit_emitter_fallback.py`, `integration_security_container.py`. |
| 15 | 🟡 WARNING | FR-SEC-003 acceptance: "Obfuscated/encoded/dynamically-constructed forbidden construct" is listed as an edge case but the implementation cannot detect `getattr(__import__('os'), 'system')()` or `eval("__imp" + "ort('os')")`. The FRD doesn't specify the detection boundary. | `modules/security/FRD.md` (FR-SEC-003 Edge Cases) | Add to FRD: "Detection boundary: static AST analysis detects direct constructs. Dynamically constructed strings (eval of concatenated strings, getattr with computed names) are detected only when the outer call (eval, getattr) is itself blocked. Obfuscation beyond one level of indirection is out of scope for static analysis; runtime sandboxing is the defense." |
| 16 | 🟢 INFO | FR-SEC-004 QA item "Nested values redacted correctly" is testable via `utility_security_redactor.redact_sensitive()` but NOT via the `SensitiveRedactor` capability (which only accepts text). The QA checklist implies end-to-end structured redaction. | `modules/security/FRD.md` (QA Checklist item 12) | Either expose structured redaction through the protocol (see Finding #3) or update QA checklist to: "Nested values redacted correctly via utility function (internal callers); text redaction via protocol (external callers)." |

### Traceability (FRD → Code)
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 17 | 🟡 WARNING | FR-SEC-001: "Permission denied → permission error." The `PathValidator` never checks actual filesystem permissions (`os.access`). A path within allowed directories but without OS-level read/write permission will return `allowed=True`, and the caller will fail at the actual I/O operation with an unhandled permission error. | `modules/security/src/capabilities_path_validator.py:52-95` | Add: after allowed-directory check passes, call `os.access(resolved, os.R_OK)` for read modes and `os.access(resolved, os.W_OK)` for write modes. Return `denial_reason="Permission denied"` on failure. |
| 18 | 🟡 WARNING | FR-SEC-002: "Unsupported/malformed metadata → safe reject." The `ArchiveGuard` assumes `ArchiveEntryVO` fields are well-formed. If `uncompressed_size` is negative (malformed metadata), the size accumulation logic will underflow. | `modules/security/src/capabilities_archive_guard.py:60-65` | Add: `if entry.uncompressed_size < 0: rejected.append(RejectedEntryVO(entry_path=entry.entry_path, reason="Negative size in metadata"))`. |
| 19 | 🟡 WARNING | FR-SEC-005: "Sink unavailable → violation still returned to caller + local fallback record." The `AuditEmitter` stores fallback in `_fallback_buffer` (an in-memory list). If the process restarts, fallback records are lost. FR-SEC-005 says "local fallback record" which implies persistence. | `modules/security/src/capabilities_audit_emitter.py:35-38` | Either: (a) document that fallback buffer is in-memory only and acceptable for MVP, or (b) persist fallback records to a file (e.g., JSON lines in the workspace log directory). |
| 20 | 🟢 INFO | FR-SEC-004: "Debug mode may expose more detail only when explicitly enabled — still no secrets." `SecurityPolicyVO.redaction_debug_mode` exists but is never read by `SensitiveRedactor`. | `modules/security/src/capabilities_sensitive_redactor.py:25-50` | Implement: when `redaction_debug_mode=True`, include the key name (but not value) in the placeholder: `[REDACTED:key_name]`. Never expose the actual value. |

## Violations
- **AES405 (Agent Role)**: The `SecurityOrchestrator` has a `security_operate_capability` property that returns `self`. This is a thin wrapper adding no value (the class already implements `ISecurityOperateAggregate`). Per cleanup-consolidate rules, this is a candidate for removal unless required by a downstream dispatch pattern.
- **AES305 (Duplication)**: `_OsPathResolver` is defined identically in `capabilities_path_validator.py:27-29` and `root_security_container.py:27-29`. Should be extracted to `utility_security_path.py` or the container should import from the capability.

## Action Items (For Developer)
- [ ] 🔴 P0: Implement access-mode-specific path validation — differentiate read vs. write/create/delete/extract enforcement (Finding #5)
- [ ] 🟡 P1: Add `open()` to blocked function calls in `CodeValidator` (Finding #6)
- [ ] 🟡 P1: Add dunder attribute access detection (`ast.Attribute` visitor) to `CodeValidator` (Finding #7)
- [ ] 🟡 P1: Emit `POLICY_OVERRIDE` audit event when code validation is disabled (Finding #8)
- [ ] 🟡 P1: Add OS-level permission check (`os.access`) to `PathValidator` (Finding #17)
- [ ] 🟡 P1: Guard against negative `uncompressed_size` in `ArchiveGuard` (Finding #18)
- [ ] 🟡 P1: Create test suite for security module (Finding #14)
- [ ] 🟡 P2: Resolve structured data redaction path — expose through protocol or document utility-only access (Finding #3)
- [ ] 🟡 P2: Clarify `max_depth` semantics in FRD — directory depth vs. recursive archive depth (Finding #11)
- [ ] 🟡 P2: Document detection boundary for obfuscated code in FRD (Finding #15)
- [ ] 🟡 P2: Add case-insensitive path handling for macOS/Windows (Finding #9)
- [ ] 🟢 P3: Implement `redaction_debug_mode` (Finding #20)
- [ ] 🟢 P3: Document fallback buffer as in-memory only or persist to disk (Finding #19)
- [ ] 🟢 P3: Deduplicate `_OsPathResolver` (Violation AES305)

## Proposed Fixes / Reference Code

### File: `modules/security/src/capabilities_path_validator.py`
```python
async def validate_path(self, request: PathValidationVO) -> PathValidationVO:
    """Validate whether a filesystem path is allowed for the requested access mode."""
    # ... existing traversal/normalization/symlink checks ...

    # FR-SEC-001: mode-specific directory enforcement
    allowed_dirs = self._policy.allowed_directories
    if allowed_dirs and not is_within_allowed_dirs(resolved, allowed_dirs):
        return PathValidationVO(
            target_path=request.target_path,
            access_mode=request.access_mode,
            allowed=False,
            denial_reason="Path outside allowed directories",
            audit_metadata={"rule": "unauthorized_access", "path": _redact_path(resolved)},
        )

    # FR-SEC-001: OS-level permission check
    import os as _os
    if request.access_mode in (AccessMode.WRITE, AccessMode.CREATE, AccessMode.DELETE, AccessMode.EXTRACT):
        check_dir = resolved if _os.path.isdir(resolved) else _os.path.dirname(resolved)
        if check_dir and not _os.access(check_dir, _os.W_OK):
            return PathValidationVO(
                target_path=request.target_path,
                access_mode=request.access_mode,
                allowed=False,
                denial_reason="Insufficient write permission",
                audit_metadata={"rule": "permission_denied", "path": _redact_path(resolved)},
            )
    elif request.access_mode == AccessMode.READ:
        if _os.path.exists(resolved) and not _os.access(resolved, _os.R_OK):
            return PathValidationVO(
                target_path=request.target_path,
                access_mode=request.access_mode,
                allowed=False,
                denial_reason="Insufficient read permission",
                audit_metadata={"rule": "permission_denied", "path": _redact_path(resolved)},
            )

    return PathValidationVO(
        target_path=request.target_path,
        access_mode=request.access_mode,
        allowed=True,
        canonical_path=resolved,
        audit_metadata={"path": _redact_path(resolved), "mode": request.access_mode.value},
    )
```

### File: `modules/security/src/capabilities_code_validator.py`
```python
# Add to ast.walk loop:
elif isinstance(node, ast.Attribute):
    # FR-SEC-003: block dunder attribute traversal (sandbox escape)
    if node.attr.startswith("__") and node.attr.endswith("__"):
        allowed_dunders = {"__init__", "__name__", "__doc__", "__str__", "__repr__", "__len__"}
        if node.attr not in allowed_dunders:
            violations.append(CodeViolationVO(
                category="blocked_attribute_access",
                description=f"Blocked dunder attribute access: .{node.attr}",
                location_hint=f"line {node.lineno}",
            ))

# Add "open" to default blocked functions:
frozenset({"eval", "exec", "compile", "__import__", "breakpoint",
           "globals", "locals", "getattr", "setattr", "delattr", "open"}),
```

### File: `modules/security/src/agent_security_orchestrator.py`
```python
async def validate_code(self, request: CodeValidationVO) -> CodeValidationVO:
    """Delegate code validation and emit audit on denial/violations/override."""
    result = await self._validate_code.validate_code(request)
    if not result.allowed or result.violations:
        await self._emit_audit.emit_audit(
            SecurityAuditEventVO(
                violation_category=ViolationCategory.CODE_VIOLATION,
                operation_type="validate_code",
                source_feature=SECURITY_SOURCE_FEATURE,
                target_metadata=result.audit_metadata,
                severity=AuditSeverity.WARNING,
                redacted_reason="Code validation denied",
            )
        )
    elif result.audit_metadata.get("rule") == "validation_disabled_override":
        # FR-SEC-005: policy override must produce audit event
        await self._emit_audit.emit_audit(
            SecurityAuditEventVO(
                violation_category=ViolationCategory.POLICY_OVERRIDE,
                operation_type="validate_code",
                source_feature=SECURITY_SOURCE_FEATURE,
                target_metadata=result.audit_metadata,
                severity=AuditSeverity.WARNING,
                redacted_reason="Code validation disabled by policy",
            )
        )
    return result
```

### File: `modules/security/src/capabilities_archive_guard.py`
```python
# Add negative size guard before size accumulation:
if entry.uncompressed_size < 0:
    rejected.append(
        RejectedEntryVO(
            entry_path=entry.entry_path,
            reason="Malformed metadata: negative uncompressed size",
        )
    )
    continue
```
```

---

Both issue documents are ready for developer handoff. No fixes have been executed — these are analysis findings only.