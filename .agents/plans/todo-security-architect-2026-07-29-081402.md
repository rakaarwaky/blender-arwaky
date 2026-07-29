# Review Plan: security — Architect (Phase 1)

## Summary

The `modules/security/` feature implements FR-SEC-001 through FR-SEC-005 across 8 source files and follows the AES 7-layer structure correctly. Taxonomy and contracts live in `shared`, capabilities implement 5 protocols, the agent orchestrator delegates via contracts, and the root container wires everything. However, 1 CRITICAL defect (path traversal check uses original un-normalized path instead of canonical form), 2 WARNING-grade findings (dead import in archive guard; capability files ignore the utility layer's `normalize_path` and `is_within_allowed_dirs` functions), and 2 INFO-grade findings (private `_redact_path` function duplicated from utility pattern, redundant `SecurityPolicyVO` import). The CRITICAL issue must be fixed immediately; the WARNING items belong in this cycle.

## Findings by Category

### Layer Boundaries
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | `capabilities_archive_guard.py` line 10 imports `SecurityPolicyVO` from taxonomy but never uses it anywhere in the file. The `policy` parameter was removed from `__init__` in a prior fix, making this import dead (AES203). | `capabilities_archive_guard.py:10` | Remove the unused `SecurityPolicyVO` import. |

### Naming Convention
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 2 | 🟢 INFO | All 8 source files comply with AES101/AES102 naming. No naming violations found. | — | None needed — naming is clean. |

### Dead Code / Orphan
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 3 | 🟢 INFO | `capabilities_path_validator.py` lines 124-133 defines `_redact_path()` as a module-level function. The same pattern exists in `utility_security_path.py` conceptually (path redaction for audit metadata). While not strictly duplicated since the utility doesn't export this function, having it in both places creates confusion about where the canonical implementation lives. | `capabilities_path_validator.py:124-133` | Consider moving `_redact_path` to `utility_security_path.py` as a public helper, or document why it stays private to the path validator capability. |

### Scalability & Coupling
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 4 | 🟡 WARNING | `capabilities_path_validator.py` lines 65, 128-129 and `capabilities_archive_guard.py` line 30 independently compute `os.path.normpath(os.path.abspath(...))` for path normalization. A utility layer function `normalize_path()` already exists in `modules/shared/src/security/utility_security_path.py` but is never imported by any capability. Three copies of identical technical logic across capability files violates DRY and creates silent drift risk. | `capabilities_path_validator.py:65,129; capabilities_archive_guard.py:30` | Import and use `normalize_path()` from `utility_security_path.py` in both capability files. Remove local normalization calls. |
| 5 | 🟡 WARNING | `capabilities_path_validator.py` lines 108-117 defines `_is_within_allowed_dirs()` which duplicates the logic of `is_within_allowed_dirs()` from `modules/shared/src/security/utility_security_path.py`. The utility function takes a `list[str]` while the capability uses `self._policy.allowed_directories` (tuple), but both serve the same purpose. | `capabilities_path_validator.py:108-117` | Import and use `is_within_allowed_dirs()` from `utility_security_path.py`. Convert tuple to list or update the utility signature to accept `Sequence[str]`. |

### Data Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 6 | 🔴 CRITICAL | `capabilities_path_validator.py` line 73 checks `".." in target.split(os.sep)` on the ORIGINAL `target` string BEFORE it is normalized with `os.path.normpath(os.path.abspath(target))` on line 81. This means a path like `./../etc/passwd` or `foo/../bar` may pass the traversal check because the raw string contains `".."` but after normalization the traversal is resolved and the check on line 73 would miss it (the check runs before normalization, so relative paths with `".."` segments that normalize away still get through). The traversal check should run AFTER normalization, or the normalized path should be checked instead. | `capabilities_path_validator.py:73` | Move the traversal check to after line 81 (after `normalized = os.path.normpath(os.path.abspath(target))`) and change the split to check `normalized.split(os.sep)` instead of `target`. This ensures the canonical form is validated, not the raw input. |

## Violations

- **AES201** — No forbidden cross-layer imports detected. All layers import only from allowed upstream layers. ✓
- **AES205** — No circular imports. Dependencies flow unidirectional bottom-up (taxonomy → contract → capabilities → agent → root). ✓
- **AES101/AES102** — All files comply with naming and suffix conventions. ✓
- **AES301** — No file exceeds 1000 lines. ✓
- **AES303** — All files have class definitions. ✓
- **AES304** — No bypass comments detected. ✓
- **AES403** — No capability exceeds 3 type declarations; all implement their protocol. ✓
- **AES405** — Agent has 1 type declaration (under 3); implements aggregate; no `Any` annotations; depends on contracts not concrete capabilities; coordinates ≥2 subsystems. ✓
- **AES406** — No surface files in security module (intentional, documented in `__init__.py`). ✓
- **AES201 rule #7 (Capabilities Mandatory Imports)** — All 5 capability files import both taxonomy AND contract(protocol). ✓
- **AES203** — `capabilities_archive_guard.py:10` imports `SecurityPolicyVO` but never uses it. ✗
- **AES504** — `utility_security_path.py` exists but is NOT imported by any capability file (only utility files import it). The utility layer is orphaned from its consumers. ✗

## Action Items

- [ ] 🔴 [P0] Fix path traversal check order in `capabilities_path_validator.py` — move `".."` check after normalization (CRITICAL — data flow vulnerability)
- [ ] 🟡 [P1] Remove unused `SecurityPolicyVO` import from `capabilities_archive_guard.py` (AES203 dead import)
- [ ] 🟡 [P1] Refactor `capabilities_path_validator.py` to use `utility_security_path.normalize_path()` and `is_within_allowed_dirs()` — eliminate duplication (DRY violation)
- [ ] 🟡 [P1] Refactor `capabilities_archive_guard.py` to use `utility_security_path.normalize_path()` — eliminate duplication (DRY violation)
- [ ] 🟢 [P2] Move `_redact_path()` from `capabilities_path_validator.py` to `utility_security_path.py` as public helper (optional, low priority)

## Fixed Code

### Fix 1 — `capabilities_path_validator.py`: Move traversal check after normalization

**File:** `modules/security/src/capabilities_path_validator.py`

```python
# Before (lines 73-82):
        if ".." in target.split(os.sep):
            return PathValidationVO(
                target_path=request.target_path,
                access_mode=request.access_mode,
                allowed=False,
                denial_reason="Path traversal detected",
                audit_metadata={"rule": "path_traversal"},
            )

        # ... later ...
            normalized = os.path.normpath(os.path.abspath(target))

# After:
            normalized = os.path.normpath(os.path.abspath(target))

        if ".." in normalized.split(os.sep):
            return PathValidationVO(
                target_path=request.target_path,
                access_mode=request.access_mode,
                allowed=False,
                denial_reason="Path traversal detected",
                audit_metadata={"rule": "path_traversal"},
            )
```

### Fix 2 — `capabilities_archive_guard.py`: Remove unused import

**File:** `modules/security/src/capabilities_archive_guard.py`

```python
# Before:
from modules.shared.src.security.taxonomy_security_vo import (
    ArchiveExtractionVO,
    RejectedEntryVO,
    SecurityPolicyVO,
)

# After:
from modules.shared.src.security.taxonomy_security_vo import (
    ArchiveExtractionVO,
    RejectedEntryVO,
)
```

### Fix 3 — `capabilities_path_validator.py`: Use utility functions

**File:** `modules/security/src/capabilities_path_validator.py`

```python
# Add import:
from modules.shared.src.security.utility_security_path import (
    is_within_allowed_dirs,
    normalize_path,
)

# Replace line 65:
-            normalized = os.path.normpath(os.path.abspath(target))
+            normalized = normalize_path(target)

# Replace lines 108-117:
-        if not self._is_within_allowed_dirs(normalized):
+        allowed_dirs = list(self._policy.allowed_directories) if self._policy.allowed_directories else []
+        if not is_within_allowed_dirs(normalized, allowed_dirs):

# Remove method _is_within_allowed_dirs (lines 108-117)
```

### Fix 4 — `capabilities_archive_guard.py`: Use utility function

**File:** `modules/security/src/capabilities_archive_guard.py`

```python
# Add import:
from modules.shared.src.security.utility_security_path import normalize_path

# Replace line 30:
-        dest = os.path.normpath(os.path.abspath(request.destination_directory))
+        dest = normalize_path(request.destination_directory)
```
