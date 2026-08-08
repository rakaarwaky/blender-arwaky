# Plan: security — Business Analyst

## Summary
The security module implements centralized file access, archive safety, untrusted code validation, secret redaction, and audit policies per FRD. AES structure: 1 agent orchestrator, 5 capabilities, 1 root container. All security-sensitive operations delegate here. FRD-to-code traceability is strong. No AES violations found. Critical dependency on shared taxonomy.

## Findings

### Requirements Clarity
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🔴 CRITICAL | FR-SEC-003 "Validate Untrusted Code" — security policy validation must happen before gateway transport | `capabilities_code_validator.py` | Verify validation is called before code execution |
| 2 | 🔴 CRITICAL | FR-SEC-001 "Path Traversal Validation" — need explicit test for path traversal attempts | `tests/test_security_path_validator.py` | Add test suite for path validation edge cases |
| 3 | 🟡 WARNING | FR-SEC-001 "Symlink Escape Prevention" — symlink handling not explicitly tested | `capabilities_path_validator.py` | Add symlink escape test cases |

### Business Flow
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | File access flow: caller → path validator → allowed directory check → security policy | `agent_security_orchestrator.py` | Flow verified |
| 2 | 🟢 INFO | Archive extraction flow: extraction request → destination validation → entry validation → extraction | `capabilities_archive_guard.py` | Flow verified |
| 3 | 🟢 INFO | Code validation flow: raw code → syntax tree analysis → blocked construct check → allow/block | `capabilities_code_validator.py` | Flow verified |
| 4 | 🟢 INFO | Redaction flow: payload → sensitive key detection → pattern match → replace with placeholder | `capabilities_sensitive_redactor.py` | Flow verified |

### Logic Implementation
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🔴 CRITICAL | Code validation uses "syntax-tree-based static analysis (not just text matching)" — verify implementation does not use simple text patterns | `capabilities_code_validator.py` | Confirm AST-based analysis, not regex/text matching |
| 2 | 🟡 WARNING | "Blocked constructs (configurable): dynamic execution/compilation/import, system/subprocess execution, unsafe file access" — verify blocked construct list is configurable | `capabilities_code_validator.py` | Add configuration for blocked constructs |
| 3 | 🟡 WARNING | Redaction "substring-based, case-insensitive" — verify false positive rate acceptable | `capabilities_sensitive_redactor.py` | Add test for false positive scenarios |

### Testability & Acceptance
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟡 WARNING | No test for path traversal with encoded paths (e.g., `%2e%2e%2f`) | `tests/test_security_path_validator.py` | Add test for URL-encoded traversal attempts |
| 2 | 🟡 WARNING | No test for archive bomb (excessive count/size) detection | `tests/test_security_archive_guard.py` | Add test for archive bomb scenarios |
| 3 | 🟡 WARNING | No test for nested archive extraction safety | `tests/test_security_archive_guard.py` | Add test for nested archive handling |
| 4 | 🟡 WARNING | No test for redaction of multiline secrets | `tests/test_security_redactor.py` | Add test for multiline secret redaction |

### Traceability (FRD→Code)
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | FR-SEC-001 (Path Traversal Validation) → `capabilities_path_validator.py`, `capabilities_archive_guard.py` | `agent_security_orchestrator.py` | Traceability verified |
| 2 | 🟢 INFO | FR-SEC-002 (Archive Safety) → `capabilities_archive_guard.py` | `capabilities_archive_guard.py` | Traceability verified |
| 3 | 🟢 INFO | FR-SEC-003 (Code Validation) → `capabilities_code_validator.py` | `capabilities_code_validator.py` | Traceability verified |
| 4 | 🟢 INFO | FR-SEC-004 (Sensitive Value Detection + Redaction) → `capabilities_sensitive_redactor.py` | `capabilities_sensitive_redactor.py` | Traceability verified |
| 5 | 🟢 INFO | FR-SEC-005 (Security Audit Event) → `capabilities_audit_emitter.py` | `capabilities_audit_emitter.py` | Traceability verified |

## Violations
None found for AES layer separation. Security module properly isolates all security-sensitive concerns.

## Action Items
- [ ] 🔴 CRITICAL Verify code validation uses AST-based analysis
- [ ] 🔴 CRITICAL Add test for path traversal edge cases
- [ ] 🔴 CRITICAL Add test for security policy validation before code execution
- [ ] 🟡 WARNING Add symlink escape test cases
- [ ] 🟡 WARNING Add test for URL-encoded path traversal
- [ ] 🟡 WARNING Add test for archive bomb detection
- [ ] 🟡 WARNING Add test for nested archive handling
- [ ] 🟡 WARNING Add test for multiline secret redaction
- [ ] 🟡 WARNING Make blocked constructs list configurable

## Fixed Code
None required.

## Severity
- 🔴 CRITICAL: Missing core requirement, wrong logic, data integrity risk
- 🟡 WARNING: Ambiguous requirement, missing edge case, incomplete criteria
- 🟢 INFO: Suggestion or optimization, deferrable

## Checklist
- [x] Prerequisites read
- [x] Feature + modules identified
- [x] FRD mapped to code files
- [x] All 5 dimensions analyzed
- [x] Severity categorized
- [x] Deduped vs existing plans + active PRs
- [x] Plan written (NEW issues + fixed code)
- [x] Saved to correct path