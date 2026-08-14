# Plan: security — Revalidated Business Analyst Plan (2026-08-14)

## Summary

This is the revalidated successor to `todo-security-business-analyst-20260808.md`. Every finding from the 2026-08-08 plan was reviewed against the current branch, the module FRD, the AES architecture rules, and the current source/test inventory. The classification policy is conservative: a finding is not marked resolved merely because it is old; only explicit verification statements are resolved, while implementation gaps remain open and uncertainty remains needs-clarification.

## Revalidation Result

The plan contains 19 unique findings after deduplication: 6 open, 1 needs clarification, 12 resolved, and 0 obsolete. Current source evidence closes the speculative validation-order, AST-analysis, and configurable-policy questions; missing edge-case tests remain open.

## Findings

| # | Previous severity | Status | Finding | Location | Decision |
|---:|---|---|---|---|---|
| 1 | 🔴 CRITICAL | **resolved** | FR-SEC-003 "Validate Untrusted Code" — security policy validation must happen before gateway transport | `capabilities_code_validator.py` | Current gateway execution calls code validation before transport and raises on denial; retain as a security regression criterion. |
| 2 | 🔴 CRITICAL | **open** | FR-SEC-001 "Path Traversal Validation" — need explicit test for path traversal attempts | `tests/test_security_path_validator.py` | The current plan identifies missing acceptance evidence; add focused traversal tests before claiming the requirement is complete. |
| 3 | 🟡 WARNING | **open** | FR-SEC-001 "Symlink Escape Prevention" — symlink handling not explicitly tested | `capabilities_path_validator.py` | Add explicit symlink escape acceptance tests; implementation behavior alone is not enough evidence. |
| 4 | 🟢 INFO | **resolved** | File access flow: caller → path validator → allowed directory check → security policy | `agent_security_orchestrator.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 5 | 🟢 INFO | **resolved** | Archive extraction flow: extraction request → destination validation → entry validation → extraction | `capabilities_archive_guard.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 6 | 🟢 INFO | **resolved** | Code validation flow: raw code → syntax tree analysis → blocked construct check → allow/block | `capabilities_code_validator.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 7 | 🟢 INFO | **resolved** | Redaction flow: payload → sensitive key detection → pattern match → replace with placeholder | `capabilities_sensitive_redactor.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 8 | 🔴 CRITICAL | **resolved** | Code validation uses "syntax-tree-based static analysis (not just text matching)" — verify implementation does not use simple text patterns | `capabilities_code_validator.py` | Current implementation parses with `ast.parse` and walks AST nodes; retain AST behavior as a regression criterion. |
| 9 | 🟡 WARNING | **resolved** | "Blocked constructs (configurable): dynamic execution/compilation/import, system/subprocess execution, unsafe file access" — verify blocked construct list is configurable | `capabilities_code_validator.py` | Current `_build_blocked_set` derives module/function sets from `SecurityPolicyVO.blocked_code_constructs`; retain as a regression criterion. |
| 10 | 🟡 WARNING | **needs-clarification** | Redaction "substring-based, case-insensitive" — verify false positive rate acceptable | `capabilities_sensitive_redactor.py` | The finding is an uncertainty or documentation gap; confirm behavior with a focused source/test check before implementation. |
| 11 | 🟡 WARNING | **open** | No test for path traversal with encoded paths (e.g., `%2e%2e%2f`) | `tests/test_security_path_validator.py` | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 12 | 🟡 WARNING | **open** | No test for archive bomb (excessive count/size) detection | `tests/test_security_archive_guard.py` | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 13 | 🟡 WARNING | **open** | No test for nested archive extraction safety | `tests/test_security_archive_guard.py` | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 14 | 🟡 WARNING | **open** | No test for redaction of multiline secrets | `tests/test_security_redactor.py` | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 15 | 🟢 INFO | **resolved** | FR-SEC-001 (Path Traversal Validation) → `capabilities_path_validator.py`, `capabilities_archive_guard.py` | `agent_security_orchestrator.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 16 | 🟢 INFO | **resolved** | FR-SEC-002 (Archive Safety) → `capabilities_archive_guard.py` | `capabilities_archive_guard.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 17 | 🟢 INFO | **resolved** | FR-SEC-003 (Code Validation) → `capabilities_code_validator.py` | `capabilities_code_validator.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 18 | 🟢 INFO | **resolved** | FR-SEC-004 (Sensitive Value Detection + Redaction) → `capabilities_sensitive_redactor.py` | `capabilities_sensitive_redactor.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 19 | 🟢 INFO | **resolved** | FR-SEC-005 (Security Audit Event) → `capabilities_audit_emitter.py` | `capabilities_audit_emitter.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |

## Validated Execution Backlog

Only findings marked **open** should be considered implementation candidates. Findings marked **needs-clarification** require a focused source/test check first. Findings marked **resolved** become regression acceptance criteria and must not be reimplemented without evidence of regression.

| Priority | Status | Action |
|---|---|---|
| 🔴 CRITICAL | resolved | Keep validation-before-transport as a security regression criterion |
| 🔴 CRITICAL | open | Add test suite for path validation edge cases |
| 🟡 WARNING | open | Add symlink escape test cases |
| 🔴 CRITICAL | resolved | Keep AST-based analysis as a security regression criterion |
| 🟡 WARNING | resolved | Keep blocked-construct policy mapping as a regression criterion |
| 🟡 WARNING | needs-clarification | Add test for false positive scenarios |
| 🟡 WARNING | open | Add test for URL-encoded traversal attempts |
| 🟡 WARNING | open | Add test for archive bomb scenarios |
| 🟡 WARNING | open | Add test for nested archive handling |
| 🟡 WARNING | open | Add test for multiline secret redaction |

## Violations

No new violation is asserted by this revalidation without a current source/test proof. Suspected AES violations remain needs-clarification when the old path or architecture context changed.

## Traceability

The module FRD remains the authoritative requirement source. The previous plan is preserved as historical evidence, while this plan is the current status ledger.

## Execution Guardrails

Before implementing any row, confirm the exact current file path, the FRD acceptance criterion, and an executable test. Do not implement recommendations that only say “verify,” “consider,” or “document” until the verification result is recorded. Do not duplicate findings already present in another module plan.

## References

- [`FRD.md`](../../modules/security/FRD.md)
- [`ARCHITECTURE.md`](../../ARCHITECTURE.md)
- [`AES rules`](../../.agents/rules/RULES_AES.md)
- [`Previous plan`](./todo-security-business-analyst-20260808.md)
