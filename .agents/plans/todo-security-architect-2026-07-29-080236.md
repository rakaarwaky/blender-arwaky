# Review Plan: security — Architect (Phase 1)

## Summary

Architect analysis of the `modules/security/` feature (14 FRD files, 8 source modules). The security feature follows AES 7-layer structure correctly overall — taxonomy and contract live in `shared`, capabilities implement 5 protocols, the agent orchestrator delegates via contracts, and the root container wires everything. However, 1 CRITICAL defect (undefined `logger` causing `NameError` on audit sink failure), 2 WARNING-grade structural gaps (unused `self._policy` in ArchiveGuard; missing allowed_directories enforcement; disabled-validation skips audit emission), and 3 INFO-grade findings (duplicate path normalization, private-coupling import, missing utility layer). The CRITICAL issue must be fixed immediately; the WARNING items and actionable INFO items belong in this cycle.

## Findings by Category

### Layer Boundaries
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | `capabilities_audit_emitter.py` calls `logger.warning()` (line 87) but never imports `logging` or defines `logger`. When `self._sink.deliver()` raises, a `NameError` crashes the fallback logic, potentially suppressing the original security violation (violating FR-SEC-005 error handling rules). | `capabilities_audit_emitter.py:87` | Add `import logging` and `logger = logging.getLogger(__name__)` at module top. This ensures the fallback audit record path is always reachable. |
| 2 | 🟡 WARNING | `capabilities_archive_guard.py` stores `self._policy = policy` (line 24) but never reads `self._policy` anywhere else in the file. The policy parameter is dead weight — the constructor accepts it but the guard ignores it entirely for its own allowed_directories validation. | `capabilities_archive_guard.py:24,38-83` | Either (a) use `self._policy` to validate `request.destination_directory` against `allowed_directories`, fulfilling FR-SEC-002 end-to-end; or (b) remove the unused `policy` parameter and make the guard's role purely structural (path traversal / symlink / depth/size/count checks only) — then update the FRD and container wiring accordingly. |
| 3 | 🟡 WARNING | `capabilities_code_validator.py` returns `allowed=True` with audit metadata when code validation is disabled (lines 56-65) but never emits an audit event. FR-SEC-003 requires a warning audit event when validation is bypassed. The silent allow creates a gap in the audit trail. | `capabilities_code_validator.py:56-65` | Emit an audit event via `EmitAuditProtocol` when `code_validation_enabled=False`. If no sink is available, log a warning and attach a `validation_disabled_override` category to the return value's `audit_metadata`. |

### Naming Convention
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 4 | 🟢 INFO | All 8 source files comply with AES101/AES102 naming. `agent_*_orchestrator`, `capabilities_*_*`, `root_*_container` all follow prefix_concept_suffix with correct allowed suffixes per layer. No naming violations found. | — | None needed — naming is clean. |

### Dead Code / Orphan
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 5 | 🟡 WARNING | `capabilities_archive_guard.py` line 24: `self._policy = policy` is never referenced in any method. Dead instance attribute. | `capabilities_archive_guard.py:24` | Remove the unused attribute or implement actual policy-driven allowed_directories checking (see Finding #2). |
| 6 | 🟢 INFO | `capabilities_sensitive_redactor.py` line 16 re-exports `REDACTION_SENSITIVE_PATTERNS` as module-level `_DEFAULT_PATTERNS` with a leading underscore, adding a redundant indirection. The `_DEFAULT_PATTERNS` alias is never used by external consumers — only `_patterns` instance attribute (line 28) uses it. | `capabilities_sensitive_redactor.py:16` | Remove `_DEFAULT_PATTERNS` alias and reference `REDACTION_SENSITIVE_PATTERNS` directly in `__init__`. Eliminates the unnecessary public-to-private re-export. |

### Scalability & Coupling
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 7 | 🟡 WARNING | `capabilities_path_validator.py` (line 65) and `capabilities_archive_guard.py` (line 30) both independently compute `os.path.normpath(os.path.abspath(...))` for path normalization. The same pattern appears in path validator lines 128-129. Three copies of identical technical logic across capability files. | `capabilities_path_validator.py:65,128; capabilities_archive_guard.py:30` | Extract path normalization into a `utility_security_path` function in a utility layer, then have all callers use the single function. This eliminates silent drift if the normalization logic needs to change (e.g., case-insensitive handling). |
| 8 | 🟢 INFO | No `utility_` layer exists in the security feature. All technical helpers (`_redact_path`, `_redact_sensitive`, `_build_blocked_set`) live inside capability classes. As the feature grows, extracting these into a utility layer keeps capabilities focused on domain logic. | `modules/security/src/` (cross-cutting) | Create a `utility_security_normalizer.py` and `utility_security_sanitizer.py` (or similar) under `modules/shared/src/security/` to hold stateless technical functions. This also satisfies AES404 (utility layer dependency) and prevents future duplication. |

### Data Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 9 | 🟢 INFO | `capabilities_sensitive_redactor.py` line 48 imports `_KV_VALUE` (private name with leading underscore) from `modules.shared.src.security.taxonomy_security_constant`. Private-convention names are implementation details that can break without warning when taxonomy internals change. | `capabilities_sensitive_redactor.py:48` | Use a public constant or protocol method instead of relying on a private regex pattern. Move the `KV_VALUE` pattern to the contract layer as part of `RedactSensitiveProtocol` if callers need access, or export it as a public constant from taxonomy. |

## Violations

- **AES201** — No forbidden cross-layer imports detected. All layers import only from allowed upstream layers. ✓
- **AES205** — No circular imports. Dependencies flow unidirectional bottom-up (taxonomy → contract → capabilities → agent → root). ✓
- **AES101/AES102** — All files comply with naming and suffix conventions. ✓
- **AES301** — No file exceeds 1000 lines. ✓
- **AES303** — All files have class definitions. ✓
- **AES304** — No bypass comments (`noqa`, `unwrap`, `TODO`, `FIXME`, `HACK`, `XXX`, `type: ignore`) found. ✓
- **AES403** — No capability exceeds 3 type declarations; all implement their protocol. ✓
- **AES405** — Agent has 1 type declaration (under 3); implements aggregate; no `Any` annotations; depends on contracts not concrete capabilities; coordinates ≥2 subsystems. ✓
- **AES406** — No surface files in security module (intentional, documented in `__init__.py`). ✓
- **AES201 rule #7 (Capabilities Mandatory Imports)** — All 5 capability files import both taxonomy AND contract(protocol). ✓
- **AES501/Taxonomy Orphan** — Taxonomy files are in shared and imported by all contract and capability layers. ✓

## Action Items

- [ ] 🔴 [P0] Fix undefined `logger` in `capabilities_audit_emitter.py:87` — add `import logging` + `logger = logging.getLogger(__name__)` (CRITICAL — runtime crash on audit sink failure)
- [ ] 🟡 [P1] Implement `allowed_directories` check in `capabilities_archive_guard.py` using `self._policy` — remove dead `self._policy` or make it functional (fulfills FR-SEC-002 end-to-end)
- [ ] 🟡 [P1] Emit audit event when code validation is disabled in `capabilities_code_validator.py:56-65` — add warning-level audit emission for `validation_disabled_override`
- [ ] 🟢 [P2] Remove redundant `_DEFAULT_PATTERNS` alias in `capabilities_sensitive_redactor.py:16` — reference `REDACTION_SENSITIVE_PATTERNS` directly
- [ ] 🟢 [P2] Extract path normalization into utility layer — create `utility_security_path.py` with `normalize_path()` and `is_within_allowed_dirs()` and update callers
- [ ] 🟢 [P3] Replace private `_KV_VALUE` import in `capabilities_sensitive_redactor.py:48` with public contract/taxonomy API

## Fixed Code

### Fix 1 — `capabilities_audit_emitter.py`: Add missing logging import and logger

```python
# Add at top of file, after existing imports:
import logging

# Add after class-level docstring:
logger = logging.getLogger(__name__)

# The logger.warning() call on line 87 now resolves correctly.
```

### Fix 2 — `capabilities_archive_guard.py`: Remove dead `self._policy` or implement allowed_directories check

```python
# Option A: Remove unused policy param (simpler, if policy-driven allowlisting is handled upstream):
class ArchiveGuard(ExtractArchiveProtocol):
    def __init__(self) -> None:   # removed policy param
        pass
# And update root_security_container.py line 63 accordingly.

# Option B: Implement allowed_directories check using self._policy:
# In validate_extraction(), after resolving dest (line 30), add:
if self._policy and self._policy.allowed_directories:
    norm_allowed = [os.path.normpath(os.path.abspath(d)) for d in self._policy.allowed_directories]
    if not any(dest.startswith(na + os.sep) or dest == na for na in norm_allowed):
        return ArchiveExtractionVO(
            destination_directory=request.destination_directory,
            entries=request.entries,
            options=request.options,
            allowed=False,
            rejected_entries=tuple(rejected),
            warnings=tuple(warnings),
            audit_metadata={"rule": "destination_outside_allowed"},
        )
```

### Fix 3 — `capabilities_code_validator.py`: Emit audit event when validation disabled

```python
# In validate_code(), at line 56-65, change:
if self._policy and not self._policy.code_validation_enabled:
    # Emit audit warning before allowing
    # Note: the protocol has no emit_audit method; the caller's orchestrator
    # should be called, OR we raise a Warning-level event through the protocol.
    # Recommended: return audit_metadata with explicit warning category,
    # and rely on the orchestrator or container to emit the audit event.
    return CodeValidationVO(
        code_text=request.code_text,
        max_code_size=request.max_code_size,
        strict_mode=request.strict_mode,
        execution_context=request.execution_context,
        allowed=True,
        redacted_metadata={"warning": "Code validation disabled by policy"},
        audit_metadata={"rule": "validation_disabled_override", "severity": "WARNING"},
    )
```

### Fix 4 — `capabilities_sensitive_redactor.py`: Remove redundant `_DEFAULT_PATTERNS` alias

```python
# Remove line 16 (_DEFAULT_PATTERNS alias), and change line 28:
# Before:
self._patterns = _DEFAULT_PATTERNS + extra_patterns
# After:
self._patterns = REDACTION_SENSITIVE_PATTERNS + extra_patterns
```
