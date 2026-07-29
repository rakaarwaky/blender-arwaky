<!-- File: .agents/issues/issue-security-business-analyst-2026-07-30-120000.md -->

# Issue: security — Business Logic & Requirements Review

## Summary

The `security` feature has a clear FRD and a mostly well-structured AES implementation, but several core business requirements are not fully enforced in code. The most serious gaps are: audit events are not automatically emitted for security violations, archive extraction does not enforce allowed-directory policy, symlink escape prevention is not active by default, path validation does not enforce access-mode-specific directory rules, and multiple security policy configuration fields are defined but never wired into capabilities. These gaps create real security and traceability risk because the module can return “denied” or “failed” results without producing the auditable events promised by FR-SEC-005, and callers can bypass important safety checks simply by invoking capabilities with default wiring. This issue should be resolved before the security module is treated as the central authority for path, archive, code, redaction, and audit policy.

## Findings by Category

### Requirements Clarity


| # | Severity    | Issue                                                                                                                                                                                                                                                                                                                               | Location (File:Line)                                                                                                                                                              | Recommendation                                                                                                                                                                                                                                                                     |
| --- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1 | 🔴 CRITICAL | FR-SEC-001 requires validation against access mode and mentions read-allowed/write-allowed directories, but the policy VO only defines a single`allowed_directories` tuple. There is no way to express read/write/create/delete/extract-specific directory permissions.                                                             | `modules/security/FRD.md:FR-SEC-001`; `modules/shared/src/security/taxonomy_security_vo.py:SecurityPolicyVO`; `modules/security/src/capabilities_path_validator.py:validate_path` | Extend`SecurityPolicyVO` with mode-specific directory allowances, e.g. `read_allowed_directories`, `write_allowed_directories`, `extract_allowed_directories`, or an access-rule VO. Update `PathValidator` to check the requested `AccessMode` against the correct directory set. |
| 2 | 🔴 CRITICAL | FR-SEC-005 says every security violation produces an audit event, but the FRD does not explicitly state whether capabilities must emit audits directly or whether the agent orchestrator must emit them after delegation. The current implementation does neither automatically.                                                    | `modules/security/FRD.md:FR-SEC-005`; `modules/security/src/agent_security_orchestrator.py:validate_path`                                                                         | Clarify in the FRD that the Agent layer is responsible for audit orchestration. Then implement post-delegation audit emission in`SecurityOrchestrator` for denied/failed results and policy overrides.                                                                             |
| 3 | 🟡 WARNING  | FR-SEC-002 says “Security may provide guarded validation hooks; actual archive reading may remain in asset feature.” This creates ambiguity about whether Security must enforce destination-directory policy or whether callers must pre-validate it. The current`ArchiveGuard` assumes callers pre-validate allowed directories. | `modules/security/FRD.md:FR-SEC-002`; `modules/security/src/capabilities_archive_guard.py:validate_extraction`                                                                    | Make Security the owner of destination-directory enforcement. Inject`SecurityPolicyVO` into `ArchiveGuard` and reject destinations outside allowed directories. Document that asset feature only performs physical extraction after Security approval.                             |
| 4 | 🟡 WARNING  | FR-SEC-003 mentions “blocked constructs” as configurable categories, but the implementation treats`blocked_code_constructs` as a flat list of module/function names. The FRD does not define the allowed construct taxonomy or mapping from category to AST check.                                                                | `modules/security/FRD.md:FR-SEC-003`; `modules/security/src/capabilities_code_validator.py:_build_blocked_set`                                                                    | Define a blocked-construct taxonomy in`taxonomy_security_constant.py` or `taxonomy_security_vo.py`, e.g. `dynamic_execution`, `subprocess_execution`, `network_access`, `unsafe_import`, `reflection`, `unsafe_file_access`. Map each category to explicit AST checks.             |
| 5 | 🟡 WARNING  | FR-SEC-004 says input can be “text/structured data”, but`RedactionVO` only supports a single `text: str` field. Structured redaction is only partially implemented inside `AuditEmitter._redact_sensitive`, not in the redaction capability contract.                                                                             | `modules/security/FRD.md:FR-SEC-004`; `modules/shared/src/security/taxonomy_security_vo.py:RedactionVO`; `modules/security/src/capabilities_sensitive_redactor.py:redact`         | Either narrow the FRD to text-only redaction or add structured redaction support to the contract and capability, e.g. `structured_payload: dict                                                                                                                                    |
| 6 | 🟡 WARNING  | FR-SEC-005 defines audit categories and events, but the supplied shared security`__init__.py` references `taxonomy_security_error` and `taxonomy_security_event`, while the visible snapshot does not include their contents. This makes error/event traceability unclear.                                                          | `modules/shared/src/security/__init__.py`; `modules/security/FRD.md:Error Categories`; `modules/security/FRD.md:Events`                                                           | Include or verify`taxonomy_security_error.py` and `taxonomy_security_event.py`. Map each FRD error category and event type to explicit taxonomy types.                                                                                                                             |

### Business Flow


| # | Severity    | Issue                                                                                                                                                                                                                                                           | Location (File:Line)                                                                                                                                                                                                                                                                                                                                      | Recommendation                                                                                                                                                                                                    |
| --- | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | 🔴 CRITICAL | Security violations do not automatically produce audit events.`PathValidator`, `ArchiveGuard`, `CodeValidator`, and `SensitiveRedactor` return denial/failure metadata, but `SecurityOrchestrator` simply returns the result without calling `emit_audit`.      | `modules/security/src/agent_security_orchestrator.py:validate_path`; `modules/security/src/capabilities_path_validator.py:validate_path`; `modules/security/src/capabilities_archive_guard.py:validate_extraction`; `modules/security/src/capabilities_code_validator.py:validate_code`; `modules/security/src/capabilities_sensitive_redactor.py:redact` | Update`SecurityOrchestrator` to inspect results and emit audit events for `allowed=False`, `failed=True`, and policy-override cases. Emission failure must not suppress the original result.                      |
| 2 | 🔴 CRITICAL | Symlink escape prevention is not active in the default composition.`PathValidator` only performs symlink checks when a `_PathResolver` is injected, but `SecurityContainer` does not inject one.                                                                | `modules/security/src/capabilities_path_validator.py:validate_path`; `modules/security/src/root_security_container.py:wire`                                                                                                                                                                                                                               | Either inject a safe resolver in`SecurityContainer` or implement canonicalization directly inside `PathValidator` using `os.path.realpath` with safe allowed-directory checks.                                    |
| 3 | 🔴 CRITICAL | Archive destination allowed-directory enforcement is effectively disabled.`ArchiveGuard` calls `is_within_allowed_dirs(dest, [])`, and an empty allowed-directory list returns `True`. No policy is injected into `ArchiveGuard`.                               | `modules/security/src/capabilities_archive_guard.py:validate_extraction`; `modules/security/src/root_security_container.py:wire`                                                                                                                                                                                                                          | Inject`SecurityPolicyVO` into `ArchiveGuard`. Reject extraction when the normalized destination is not inside configured allowed directories.                                                                     |
| 4 | 🔴 CRITICAL | Missing or empty archive destination is not reliably rejected.`ArchiveGuard` normalizes `request.destination_directory` before checking emptiness. An empty string is normalized to the current working directory, so the `if not dest` guard does not trigger. | `modules/security/src/capabilities_archive_guard.py:validate_extraction`                                                                                                                                                                                                                                                                                  | Check`request.destination_directory` for emptiness before normalization. Reject with `missing_destination` when blank.                                                                                            |
| 5 | 🟡 WARNING  | Path traversal detection is weakened by normalization order.`PathValidator` checks for `..` after `normalize_path()`, but `os.path.normpath(os.path.abspath(...))` usually collapses `..` segments before the check. The check may therefore be ineffective.    | `modules/security/src/capabilities_path_validator.py:validate_path`                                                                                                                                                                                                                                                                                       | Detect traversal segments before normalization, or rely primarily on canonicalization plus strict allowed-directory containment. Add tests for`/allowed/../outside`, relative traversal, and symlinked traversal. |
| 6 | 🟡 WARNING  | Archive total-size enforcement happens after iterating through all entries. The capability accumulates total size and only returns a failure at the end. It does not stop early or mark subsequent entries as rejected.                                         | `modules/security/src/capabilities_archive_guard.py:validate_extraction`                                                                                                                                                                                                                                                                                  | Stop processing once`total_size > max_total_size`, or reject remaining entries and add a clear warning. Ensure the final result is `allowed=False`.                                                               |
| 7 | 🟡 WARNING  | Redaction failure does not produce an audit event.`SensitiveRedactor.redact` returns `failed=True`, but no audit emission occurs for the `redaction_failure` category required by FR-SEC-005.                                                                   | `modules/security/src/capabilities_sensitive_redactor.py:redact`; `modules/security/src/agent_security_orchestrator.py:redact`                                                                                                                                                                                                                            | Have`SecurityOrchestrator.redact` emit a `REDACTION_FAILURE` audit event when `result.failed` is true. Ensure failure reason is itself redacted.                                                                  |

### Logic Implementation


| # | Severity    | Issue                                                                                                                                                                                                                                 | Location (File:Line)                                                                                                                            | Recommendation                                                                                                                                                    |
| --- | ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | 🔴 CRITICAL | Several`SecurityPolicyVO` fields are defined but never used: archive limits, redaction patterns, redaction key names, redaction debug mode, max code size, and policy mode are not consistently wired into the relevant capabilities. | `modules/shared/src/security/taxonomy_security_vo.py:SecurityPolicyVO`; `modules/security/src/root_security_container.py:wire`                  | Wire policy into all capabilities. Use policy values as defaults or hard limits for archive validation, code validation, redaction, and audit behavior.           |
| 2 | 🔴 CRITICAL | `AuditEmitter` creates a fallback event when sink delivery fails, but the fallback event is discarded. FR-SEC-005 requires a local fallback record when the sink is unavailable.                                                      | `modules/security/src/capabilities_audit_emitter.py:emit_audit`                                                                                 | Persist or forward the fallback event to a local buffer, fallback sink, or structured redacted log. Do not construct and discard it.                              |
| 3 | 🟡 WARNING  | `CodeValidator` ignores `SecurityPolicyVO.max_code_size`. It validates only against `request.max_code_size`, so a caller can bypass the configured maximum by supplying a larger request value.                                       | `modules/security/src/capabilities_code_validator.py:validate_code`                                                                             | Use an effective limit such as`min(request.max_code_size, policy.max_code_size)` when a policy is present. Reject values above the policy maximum.                |
| 4 | 🟡 WARNING  | `CodeValidator._build_blocked_set` misclassifies unknown policy constructs as function names. If a policy adds a module name not present in the hardcoded module set, it will not block imports of that module.                       | `modules/security/src/capabilities_code_validator.py:_build_blocked_set`                                                                        | Replace the flat list with explicit blocked-module and blocked-function configuration, or use a construct-category taxonomy with deterministic mapping.           |
| 5 | 🟡 WARNING  | `SensitiveRedactor` key-based redaction replaces the entire `key=value` or `"key": "value"` match with `[REDACTED]`, losing the non-sensitive key name. FR-SEC-004 says non-sensitive diagnostic context should be preserved.         | `modules/security/src/capabilities_sensitive_redactor.py:redact`                                                                                | Preserve the key and redact only the value, e.g. replace with`password=[REDACTED]` or `"password": "[REDACTED]"`.                                                 |
| 6 | 🟡 WARNING  | `PathValidator` may leak path details in denial reasons when path resolution fails: `denial_reason=f"Path resolution failed: {exc}"`. The exception message can include filesystem paths.                                             | `modules/security/src/capabilities_path_validator.py:validate_path`                                                                             | Return a generic denial reason and place detailed diagnostics only in redacted audit metadata.                                                                    |
| 7 | 🟡 WARNING  | `ArchiveGuard` reports rejected entries using raw `entry_path`. FR-SEC-002 says rejected entries should be reported without exposing unsafe raw paths.                                                                                | `modules/security/src/capabilities_archive_guard.py:validate_extraction`; `modules/shared/src/security/taxonomy_security_vo.py:RejectedEntryVO` | Redact or normalize unsafe entry paths before returning them, or add a separate`redacted_entry_ref` field.                                                        |
| 8 | 🟢 INFO     | Redaction logic is duplicated:`SensitiveRedactor` redacts text, while `AuditEmitter._redact_sensitive` recursively redacts nested metadata. Both use the same sensitive patterns but implement separate behavior.                     | `modules/security/src/capabilities_sensitive_redactor.py:redact`; `modules/security/src/capabilities_audit_emitter.py:_redact_sensitive`        | Extract shared redaction mechanics into a stateless utility, or have`AuditEmitter` use a common redaction helper. Keep domain policy ownership in the capability. |

### Testability & Acceptance Criteria


| # | Severity    | Issue                                                                                                                                                                                                 | Location (File:Line)                                              | Recommendation                                                                                                                                                                                                                                                                                                                                                   |
| --- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1 | 🔴 CRITICAL | No security test suite is visible in the module snapshot. FR-SEC-001 through FR-SEC-005 have detailed QA checklist items, but there are no traceable contract/unit/integration/acceptance tests.      | `modules/security/`                                               | Create tests using the project test convention:`tests/contract_security.py`, `tests/unit_security_path_validator.py`, `tests/unit_security_archive_guard.py`, `tests/unit_security_code_validator.py`, `tests/unit_security_sensitive_redactor.py`, `tests/unit_security_audit_emitter.py`, `tests/integration_security.py`, and `tests/acceptance_FR_SEC_*.py`. |
| 2 | 🟡 WARNING  | FRD QA checklist items are not mapped to FR IDs or test names. This makes acceptance verification manual and brittle.                                                                                 | `modules/security/FRD.md:QA Checklist`                            | Add a traceability matrix: each QA item should reference one or more FR IDs and expected test cases.                                                                                                                                                                                                                                                             |
| 3 | 🟡 WARNING  | Audit sink behavior is hard to test because`_AuditSink` is a private protocol inside `capabilities_audit_emitter.py`. Callers cannot easily inject a test double through the public contract surface. | `modules/security/src/capabilities_audit_emitter.py:_AuditSink`   | Expose an audit sink contract or a root-level wiring interface. At minimum, document the expected sink protocol and provide a test fake.                                                                                                                                                                                                                         |
| 4 | 🟡 WARNING  | Structured redaction is not testable through the public redaction contract because`RedactionVO` only carries text.                                                                                    | `modules/shared/src/security/taxonomy_security_vo.py:RedactionVO` | Add structured payload fields or a separate structured-redaction VO. Add tests for nested dictionaries, lists, encoded secrets, and oversized payloads.                                                                                                                                                                                                          |

### Traceability (FRD → Code)

| # | Severity | Issue | Location (File:Line) | Recommendation |
|

<!-- File: .agents/issues/issue-security-business-analyst-2026-07-30-120000.md -->

# Issue: security — Business Logic & Requirements Review

## Summary

The `security` feature has a clear FRD and a mostly well-structured AES implementation, but several core business requirements are not fully enforced in code. The most serious gaps are: audit events are not automatically emitted for security violations, archive extraction does not enforce allowed-directory policy, symlink escape prevention is not active by default, path validation does not enforce access-mode-specific directory rules, and multiple security policy configuration fields are defined but never wired into capabilities. These gaps create real security and traceability risk because the module can return “denied” or “failed” results without producing the auditable events promised by FR-SEC-005, and callers can bypass important safety checks simply by invoking capabilities with default wiring. This issue should be resolved before the security module is treated as the central authority for path, archive, code, redaction, and audit policy.

## Findings by Category

### Requirements Clarity


| # | Severity    | Issue                                                                                                                                                                                                                                                                                                                               | Location (File:Line)                                                                                                                                                              | Recommendation                                                                                                                                                                                                                                                                     |
| --- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1 | 🔴 CRITICAL | FR-SEC-001 requires validation against access mode and mentions read-allowed/write-allowed directories, but the policy VO only defines a single`allowed_directories` tuple. There is no way to express read/write/create/delete/extract-specific directory permissions.                                                             | `modules/security/FRD.md:FR-SEC-001`; `modules/shared/src/security/taxonomy_security_vo.py:SecurityPolicyVO`; `modules/security/src/capabilities_path_validator.py:validate_path` | Extend`SecurityPolicyVO` with mode-specific directory allowances, e.g. `read_allowed_directories`, `write_allowed_directories`, `extract_allowed_directories`, or an access-rule VO. Update `PathValidator` to check the requested `AccessMode` against the correct directory set. |
| 2 | 🔴 CRITICAL | FR-SEC-005 says every security violation produces an audit event, but the FRD does not explicitly state whether capabilities must emit audits directly or whether the agent orchestrator must emit them after delegation. The current implementation does neither automatically.                                                    | `modules/security/FRD.md:FR-SEC-005`; `modules/security/src/agent_security_orchestrator.py:validate_path`                                                                         | Clarify in the FRD that the Agent layer is responsible for audit orchestration. Then implement post-delegation audit emission in`SecurityOrchestrator` for denied/failed results and policy overrides.                                                                             |
| 3 | 🟡 WARNING  | FR-SEC-002 says “Security may provide guarded validation hooks; actual archive reading may remain in asset feature.” This creates ambiguity about whether Security must enforce destination-directory policy or whether callers must pre-validate it. The current`ArchiveGuard` assumes callers pre-validate allowed directories. | `modules/security/FRD.md:FR-SEC-002`; `modules/security/src/capabilities_archive_guard.py:validate_extraction`                                                                    | Make Security the owner of destination-directory enforcement. Inject`SecurityPolicyVO` into `ArchiveGuard` and reject destinations outside allowed directories. Document that asset feature only performs physical extraction after Security approval.                             |
| 4 | 🟡 WARNING  | FR-SEC-003 mentions “blocked constructs” as configurable categories, but the implementation treats`blocked_code_constructs` as a flat list of module/function names. The FRD does not define the allowed construct taxonomy or mapping from category to AST check.                                                                | `modules/security/FRD.md:FR-SEC-003`; `modules/security/src/capabilities_code_validator.py:_build_blocked_set`                                                                    | Define a blocked-construct taxonomy in`taxonomy_security_constant.py` or `taxonomy_security_vo.py`, e.g. `dynamic_execution`, `subprocess_execution`, `network_access`, `unsafe_import`, `reflection`, `unsafe_file_access`. Map each category to explicit AST checks.             |
| 5 | 🟡 WARNING  | FR-SEC-004 says input can be “text/structured data”, but`RedactionVO` only supports a single `text: str` field. Structured redaction is only partially implemented inside `AuditEmitter._redact_sensitive`, not in the redaction capability contract.                                                                             | `modules/security/FRD.md:FR-SEC-004`; `modules/shared/src/security/taxonomy_security_vo.py:RedactionVO`; `modules/security/src/capabilities_sensitive_redactor.py:redact`         | Either narrow the FRD to text-only redaction or add structured redaction support to the contract and capability, e.g. `structured_payload: dict                                                                                                                                    |
| 6 | 🟡 WARNING  | FR-SEC-005 defines audit categories and events, but the supplied shared security`__init__.py` references `taxonomy_security_error` and `taxonomy_security_event`, while the visible snapshot does not include their contents. This makes error/event traceability unclear.                                                          | `modules/shared/src/security/__init__.py`; `modules/security/FRD.md:Error Categories`; `modules/security/FRD.md:Events`                                                           | Include or verify`taxonomy_security_error.py` and `taxonomy_security_event.py`. Map each FRD error category and event type to explicit taxonomy types.                                                                                                                             |

### Business Flow


| # | Severity    | Issue                                                                                                                                                                                                                                                           | Location (File:Line)                                                                                                                                                                                                                                                                                                                                      | Recommendation                                                                                                                                                                                                    |
| --- | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | 🔴 CRITICAL | Security violations do not automatically produce audit events.`PathValidator`, `ArchiveGuard`, `CodeValidator`, and `SensitiveRedactor` return denial/failure metadata, but `SecurityOrchestrator` simply returns the result without calling `emit_audit`.      | `modules/security/src/agent_security_orchestrator.py:validate_path`; `modules/security/src/capabilities_path_validator.py:validate_path`; `modules/security/src/capabilities_archive_guard.py:validate_extraction`; `modules/security/src/capabilities_code_validator.py:validate_code`; `modules/security/src/capabilities_sensitive_redactor.py:redact` | Update`SecurityOrchestrator` to inspect results and emit audit events for `allowed=False`, `failed=True`, and policy-override cases. Emission failure must not suppress the original result.                      |
| 2 | 🔴 CRITICAL | Symlink escape prevention is not active in the default composition.`PathValidator` only performs symlink checks when a `_PathResolver` is injected, but `SecurityContainer` does not inject one.                                                                | `modules/security/src/capabilities_path_validator.py:validate_path`; `modules/security/src/root_security_container.py:wire`                                                                                                                                                                                                                               | Either inject a safe resolver in`SecurityContainer` or implement canonicalization directly inside `PathValidator` using `os.path.realpath` with safe allowed-directory checks.                                    |
| 3 | 🔴 CRITICAL | Archive destination allowed-directory enforcement is effectively disabled.`ArchiveGuard` calls `is_within_allowed_dirs(dest, [])`, and an empty allowed-directory list returns `True`. No policy is injected into `ArchiveGuard`.                               | `modules/security/src/capabilities_archive_guard.py:validate_extraction`; `modules/security/src/root_security_container.py:wire`                                                                                                                                                                                                                          | Inject`SecurityPolicyVO` into `ArchiveGuard`. Reject extraction when the normalized destination is not inside configured allowed directories.                                                                     |
| 4 | 🔴 CRITICAL | Missing or empty archive destination is not reliably rejected.`ArchiveGuard` normalizes `request.destination_directory` before checking emptiness. An empty string is normalized to the current working directory, so the `if not dest` guard does not trigger. | `modules/security/src/capabilities_archive_guard.py:validate_extraction`                                                                                                                                                                                                                                                                                  | Check`request.destination_directory` for emptiness before normalization. Reject with `missing_destination` when blank.                                                                                            |
| 5 | 🟡 WARNING  | Path traversal detection is weakened by normalization order.`PathValidator` checks for `..` after `normalize_path()`, but `os.path.normpath(os.path.abspath(...))` usually collapses `..` segments before the check. The check may therefore be ineffective.    | `modules/security/src/capabilities_path_validator.py:validate_path`                                                                                                                                                                                                                                                                                       | Detect traversal segments before normalization, or rely primarily on canonicalization plus strict allowed-directory containment. Add tests for`/allowed/../outside`, relative traversal, and symlinked traversal. |
| 6 | 🟡 WARNING  | Archive total-size enforcement happens after iterating through all entries. The capability accumulates total size and only returns a failure at the end. It does not stop early or mark subsequent entries as rejected.                                         | `modules/security/src/capabilities_archive_guard.py:validate_extraction`                                                                                                                                                                                                                                                                                  | Stop processing once`total_size > max_total_size`, or reject remaining entries and add a clear warning. Ensure the final result is `allowed=False`.                                                               |
| 7 | 🟡 WARNING  | Redaction failure does not produce an audit event.`SensitiveRedactor.redact` returns `failed=True`, but no audit emission occurs for the `redaction_failure` category required by FR-SEC-005.                                                                   | `modules/security/src/capabilities_sensitive_redactor.py:redact`; `modules/security/src/agent_security_orchestrator.py:redact`                                                                                                                                                                                                                            | Have`SecurityOrchestrator.redact` emit a `REDACTION_FAILURE` audit event when `result.failed` is true. Ensure failure reason is itself redacted.                                                                  |

### Logic Implementation


| # | Severity    | Issue                                                                                                                                                                                                                                 | Location (File:Line)                                                                                                                            | Recommendation                                                                                                                                                    |
| --- | ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | 🔴 CRITICAL | Several`SecurityPolicyVO` fields are defined but never used: archive limits, redaction patterns, redaction key names, redaction debug mode, max code size, and policy mode are not consistently wired into the relevant capabilities. | `modules/shared/src/security/taxonomy_security_vo.py:SecurityPolicyVO`; `modules/security/src/root_security_container.py:wire`                  | Wire policy into all capabilities. Use policy values as defaults or hard limits for archive validation, code validation, redaction, and audit behavior.           |
| 2 | 🔴 CRITICAL | `AuditEmitter` creates a fallback event when sink delivery fails, but the fallback event is discarded. FR-SEC-005 requires a local fallback record when the sink is unavailable.                                                      | `modules/security/src/capabilities_audit_emitter.py:emit_audit`                                                                                 | Persist or forward the fallback event to a local buffer, fallback sink, or structured redacted log. Do not construct and discard it.                              |
| 3 | 🟡 WARNING  | `CodeValidator` ignores `SecurityPolicyVO.max_code_size`. It validates only against `request.max_code_size`, so a caller can bypass the configured maximum by supplying a larger request value.                                       | `modules/security/src/capabilities_code_validator.py:validate_code`                                                                             | Use an effective limit such as`min(request.max_code_size, policy.max_code_size)` when a policy is present. Reject values above the policy maximum.                |
| 4 | 🟡 WARNING  | `CodeValidator._build_blocked_set` misclassifies unknown policy constructs as function names. If a policy adds a module name not present in the hardcoded module set, it will not block imports of that module.                       | `modules/security/src/capabilities_code_validator.py:_build_blocked_set`                                                                        | Replace the flat list with explicit blocked-module and blocked-function configuration, or use a construct-category taxonomy with deterministic mapping.           |
| 5 | 🟡 WARNING  | `SensitiveRedactor` key-based redaction replaces the entire `key=value` or `"key": "value"` match with `[REDACTED]`, losing the non-sensitive key name. FR-SEC-004 says non-sensitive diagnostic context should be preserved.         | `modules/security/src/capabilities_sensitive_redactor.py:redact`                                                                                | Preserve the key and redact only the value, e.g. replace with`password=[REDACTED]` or `"password": "[REDACTED]"`.                                                 |
| 6 | 🟡 WARNING  | `PathValidator` may leak path details in denial reasons when path resolution fails: `denial_reason=f"Path resolution failed: {exc}"`. The exception message can include filesystem paths.                                             | `modules/security/src/capabilities_path_validator.py:validate_path`                                                                             | Return a generic denial reason and place detailed diagnostics only in redacted audit metadata.                                                                    |
| 7 | 🟡 WARNING  | `ArchiveGuard` reports rejected entries using raw `entry_path`. FR-SEC-002 says rejected entries should be reported without exposing unsafe raw paths.                                                                                | `modules/security/src/capabilities_archive_guard.py:validate_extraction`; `modules/shared/src/security/taxonomy_security_vo.py:RejectedEntryVO` | Redact or normalize unsafe entry paths before returning them, or add a separate`redacted_entry_ref` field.                                                        |
| 8 | 🟢 INFO     | Redaction logic is duplicated:`SensitiveRedactor` redacts text, while `AuditEmitter._redact_sensitive` recursively redacts nested metadata. Both use the same sensitive patterns but implement separate behavior.                     | `modules/security/src/capabilities_sensitive_redactor.py:redact`; `modules/security/src/capabilities_audit_emitter.py:_redact_sensitive`        | Extract shared redaction mechanics into a stateless utility, or have`AuditEmitter` use a common redaction helper. Keep domain policy ownership in the capability. |

### Testability & Acceptance Criteria


| # | Severity    | Issue                                                                                                                                                                                                 | Location (File:Line)                                              | Recommendation                                                                                                                                                                                                                                                                                                                                                   |
| --- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1 | 🔴 CRITICAL | No security test suite is visible in the module snapshot. FR-SEC-001 through FR-SEC-005 have detailed QA checklist items, but there are no traceable contract/unit/integration/acceptance tests.      | `modules/security/`                                               | Create tests using the project test convention:`tests/contract_security.py`, `tests/unit_security_path_validator.py`, `tests/unit_security_archive_guard.py`, `tests/unit_security_code_validator.py`, `tests/unit_security_sensitive_redactor.py`, `tests/unit_security_audit_emitter.py`, `tests/integration_security.py`, and `tests/acceptance_FR_SEC_*.py`. |
| 2 | 🟡 WARNING  | FRD QA checklist items are not mapped to FR IDs or test names. This makes acceptance verification manual and brittle.                                                                                 | `modules/security/FRD.md:QA Checklist`                            | Add a traceability matrix: each QA item should reference one or more FR IDs and expected test cases.                                                                                                                                                                                                                                                             |
| 3 | 🟡 WARNING  | Audit sink behavior is hard to test because`_AuditSink` is a private protocol inside `capabilities_audit_emitter.py`. Callers cannot easily inject a test double through the public contract surface. | `modules/security/src/capabilities_audit_emitter.py:_AuditSink`   | Expose an audit sink contract or a root-level wiring interface. At minimum, document the expected sink protocol and provide a test fake.                                                                                                                                                                                                                         |
| 4 | 🟡 WARNING  | Structured redaction is not testable through the public redaction contract because`RedactionVO` only carries text.                                                                                    | `modules/shared/src/security/taxonomy_security_vo.py:RedactionVO` | Add structured payload fields or a separate structured-redaction VO. Add tests for nested dictionaries, lists, encoded secrets, and oversized payloads.                                                                                                                                                                                                          |

### Traceability (FRD → Code)


| # | Severity    | Issue                                                                                                                                                                                                                                                  | Location (File:Line)                                                                                                                                                                                                                                                                                                                       | Recommendation                                                                                                                                                                                                                 |
| --- | ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | 🔴 CRITICAL | FR-SEC-001 access-mode-specific directory enforcement is not traceable to code.`PathValidator` receives `access_mode`, but only uses it for metadata.                                                                                                  | `modules/security/FRD.md:FR-SEC-001`; `modules/security/src/capabilities_path_validator.py:validate_path`                                                                                                                                                                                                                                  | Implement mode-specific checks and add tests named after FR-SEC-001 access modes.                                                                                                                                              |
| 2 | 🔴 CRITICAL | FR-SEC-002 allowed-destination enforcement is not traceable.`ArchiveGuard` has no policy input and uses an empty allowed-directory list.                                                                                                               | `modules/security/FRD.md:FR-SEC-002`; `modules/security/src/capabilities_archive_guard.py:validate_extraction`                                                                                                                                                                                                                             | Inject`SecurityPolicyVO` and enforce `allowed_directories` or `extract_allowed_directories`.                                                                                                                                   |
| 3 | 🔴 CRITICAL | FR-SEC-005 “every security violation produces audit event” is not traceable. There is no code path that automatically emits audits for denied path access, rejected archive entries, blocked code, or redaction failures.                            | `modules/security/FRD.md:FR-SEC-005`; `modules/security/src/agent_security_orchestrator.py`                                                                                                                                                                                                                                                | Add orchestrator audit emission. Add acceptance tests asserting that each denied operation emits an audit event.                                                                                                               |
| 4 | 🟡 WARNING  | FRD configuration keys are not fully traced to implementation. Keys such as`audit_retention_behavior`, `redaction_debug_mode`, and `security_policy_mode` have no visible behavior. Archive limits exist in policy but are not used by `ArchiveGuard`. | `modules/security/FRD.md:Configuration Keys`; `modules/shared/src/security/taxonomy_security_vo.py:SecurityPolicyVO`; `modules/security/src/root_security_container.py:wire`                                                                                                                                                               | Add a config-to-code traceability table in the FRD. Implement or explicitly mark each key as deferred. Wire all active keys into capabilities.                                                                                 |
| 5 | 🟡 WARNING  | FRD error categories are not clearly traced to error taxonomy or result envelopes. The visible VOs contain denial reasons and metadata, but no explicit domain error types are shown in the snapshot.                                                  | `modules/security/FRD.md:Error Categories`; `modules/shared/src/security/taxonomy_security_vo.py`                                                                                                                                                                                                                                          | Define error/category VOs or exception types in`taxonomy_security_error.py`. Map each FRD error category to a concrete type.                                                                                                   |
| 6 | 🟢 INFO     | Contract class naming is inconsistent with the documented convention`I<Name>Protocol`. The aggregate uses `ISecurityOperateAggregate`, but protocols are named `ValidatePathProtocol`, `ExtractArchiveProtocol`, etc.                                  | `modules/shared/src/security/contract_validate_path_protocol.py`; `modules/shared/src/security/contract_extract_archive_protocol.py`; `modules/shared/src/security/contract_validate_code_protocol.py`; `modules/shared/src/security/contract_redact_sensitive_protocol.py`; `modules/shared/src/security/contract_emit_audit_protocol.py` | Rename protocol classes to`IValidatePathProtocol`, `IExtractArchiveProtocol`, `IValidateCodeProtocol`, `IRedactSensitiveProtocol`, and `IEmitAuditProtocol`, or update the convention if the `I` prefix is no longer required. |

## Violations

- **AES405 — Agent Role**: `SecurityOrchestrator._delegate` is an untyped private helper placed before/within the aggregate implementation block. Agent helpers should be typed and placed in Block 3, while Block 2 should contain only aggregate method implementations.
- **AES405 — Agent Role**: The agent currently delegates calls but does not perform the audit orchestration implied by the FRD. While this is primarily a business-flow gap, it also weakens the agent’s intended coordination responsibility.
- **AES305 — Duplication Code**: Sensitive-redaction pattern logic is duplicated between `capabilities_sensitive_redactor.py` and `capabilities_audit_emitter.py`. Shared redaction mechanics should be centralized.
- **AES404 — Utility Role**: Stateless helpers such as path redaction and recursive metadata redaction live inside capability files. If reused across capabilities or root composition, they should be extracted to a utility file, e.g. `utility_security_redactor.py`.
- **Potential AES201 / Contract Boundary Concern**: `PathValidator` defines a private `_PathResolver` protocol inside the capability file. If this resolver is a public dependency boundary, it should be defined in the contract layer; if it is purely internal, the capability should implement safe resolution directly or receive it through explicit root wiring.

## Action Items (For Developer)

- [ ]  P0 Make `SecurityOrchestrator` emit audit events for every denied or failed security operation.
- [ ]  P0 Emit audit events for policy overrides, especially disabled code validation.
- [ ]  P0 Inject `SecurityPolicyVO` into `ArchiveGuard` and enforce allowed extraction directories.
- [ ]  P0 Reject empty or missing archive destination before normalization.
- [ ]  P0 Enable symlink escape prevention by default in `PathValidator` or wire a safe resolver in `SecurityContainer`.
- [ ]  P0 Implement access-mode-specific path validation for read/write/create/delete/extract operations.
- [ ]  P0 Wire unused `SecurityPolicyVO` fields into the relevant capabilities or remove them from the FRD/VO.
- [ ]  P1 Make `AuditEmitter` create a real fallback record when the sink is unavailable.
- [ ]  P1 Use policy maximum code size in `CodeValidator`, not only request-provided size.
- [ ]  P1 Replace flat blocked-code construct list with explicit category-to-check mapping.
- [ ]  P1 Preserve non-sensitive key names during key-based redaction.
- [ ]  P1 Redact unsafe archive entry paths before returning rejected-entry metadata.
- [ ]  P1 Add structured redaction support or narrow FR-SEC-004 to text-only redaction.
- [ ]  P2 Create full security test suite: contract, unit, integration, acceptance, and smoke tests.
- [ ]  P2 Add FRD traceability matrix mapping each QA checklist item to FR ID and test name.
- [ ]  P2 Rename protocol contracts to follow the `I<Name>Protocol` convention or update the convention.

## Proposed Fixes / Reference Code

### `modules/shared/src/security/taxonomy_security_vo.py`

Add mode-specific directory policy fields and preserve existing generic field for backward compatibility.

```python
@dataclass(frozen=True)
class SecurityPolicyVO:
    """Security policy configuration."""

    allowed_directories: tuple[str, ...] = ()

    # Optional mode-specific directories.
    # If empty, fall back to allowed_directories.
    read_allowed_directories: tuple[str, ...] = ()
    write_allowed_directories: tuple[str, ...] = ()
    extract_allowed_directories: tuple[str, ...] = ()

    archive_max_depth: int = 5
    archive_max_total_size: int = 104_857_600
    archive_max_entry_size: int = 10_485_760
    archive_max_entry_count: int = 1_000
    archive_allow_symbolic_links: bool = False
    archive_allow_hard_links: bool = False

    code_validation_enabled: bool = True
    blocked_code_constructs: tuple[str, ...] = dc_field(default_factory=tuple)
    max_code_size: int = 1_048_576

    redaction_patterns: tuple[str, ...] = dc_field(default_factory=tuple)
    redaction_key_names: tuple[str, ...] = dc_field(default_factory=tuple)
    redaction_debug_mode: bool = False

    security_policy_mode: str = "strict"
```

### `modules/security/src/capabilities_path_validator.py`

Use canonical path resolution by default and enforce access-mode-specific directories.

```python
async def validate_path(self, request: PathValidationVO) -> PathValidationVO:
    target = request.target_path

    if not target:
        return PathValidationVO(
            target_path=request.target_path,
            access_mode=request.access_mode,
            base_directory=request.base_directory,
            operation_context=request.operation_context,
            allowed=False,
            denial_reason="Empty path",
            audit_metadata={"rule": "empty_path"},
        )

    if ".." in target.replace("\\", "/").split("/"):
        return PathValidationVO(
            target_path=request.target_path,
            access_mode=request.access_mode,
            base_directory=request.base_directory,
            operation_context=request.operation_context,
            allowed=False,
            denial_reason="Path traversal detected",
            audit_metadata={"rule": "path_traversal"},
        )

    if not os.path.isabs(target):
        base = request.base_directory
        if base is None and self._policy.allowed_directories:
            base = self._policy.allowed_directories[0]

        if base is None:
            return PathValidationVO(
                target_path=request.target_path,
                access_mode=request.access_mode,
                allowed=False,
                denial_reason="No base directory configured",
                audit_metadata={"rule": "no_base_directory"},
            )

        target = os.path.join(base, target)

    try:
        normalized = normalize_path(target)
        canonical = os.path.realpath(normalized)
    except (OSError, ValueError):
        return PathValidationVO(
            target_path=request.target_path,
            access_mode=request.access_mode,
            allowed=False,
            denial_reason="Path resolution failed",
            audit_metadata={"rule": "path_resolution_failed"},
        )

    allowed_dirs = self._allowed_dirs_for_mode(request.access_mode)

    if not is_within_allowed_dirs(canonical, allowed_dirs):
        rule = "symlink_escape" if canonical != normalized else "unauthorized_access"
        return PathValidationVO(
            target_path=request.target_path,
            access_mode=request.access_mode,
            allowed=False,
            denial_reason="Path outside allowed directories",
            audit_metadata={"rule": rule, "path": _redact_path(canonical)},
        )

    return PathValidationVO(
        target_path=request.target_path,
        access_mode=request.access_mode,
        base_directory=request.base_directory,
        operation_context=request.operation_context,
        allowed=True,
        canonical_path=canonical,
        audit_metadata={"path": _redact_path(canonical), "mode": request.access_mode.value},
    )
```

Add a private helper in Block 3:

```python
def _allowed_dirs_for_mode(self, mode: AccessMode) -> list[str]:
    if mode in (AccessMode.WRITE, AccessMode.CREATE, AccessMode.DELETE):
        mode_dirs = list(self._policy.write_allowed_directories)
    elif mode == AccessMode.EXTRACT:
        mode_dirs = list(self._policy.extract_allowed_directories)
    else:
        mode_dirs = list(self._policy.read_allowed_directories)

    return mode_dirs or list(self._policy.allowed_directories)
```

### `modules/security/src/capabilities_archive_guard.py`

Inject policy, reject missing destination, and enforce allowed extraction directories.

```python
class ArchiveGuard(ExtractArchiveProtocol):
    def __init__(self, policy: SecurityPolicyVO | None = None) -> None:
        self._policy = policy or SecurityPolicyVO()

    async def validate_extraction(self, request: ArchiveExtractionVO) -> ArchiveExtractionVO:
        opts = request.options
        rejected: list[RejectedEntryVO] = []
        warnings: list[str] = []

        if not request.destination_directory.strip():
            return ArchiveExtractionVO(
                destination_directory=request.destination_directory,
                entries=request.entries,
                options=request.options,
                allowed=False,
                rejected_entries=tuple(rejected),
                warnings=tuple(warnings),
                audit_metadata={"rule": "missing_destination"},
            )

        dest = normalize_path(request.destination_directory)

        allowed_dirs = list(self._policy.extract_allowed_directories or self._policy.allowed_directories)

        if allowed_dirs and not is_within_allowed_dirs(dest, allowed_dirs):
            return ArchiveExtractionVO(
                destination_directory=request.destination_directory,
                entries=request.entries,
                options=request.options,
                allowed=False,
                rejected_entries=tuple(rejected),
                warnings=tuple(warnings),
                audit_metadata={"rule": "unauthorized_destination"},
            )

        # Existing entry validation remains here.
```

### `modules/security/src/agent_security_orchestrator.py`

Emit audit events after delegation. Keep helpers in Block 3.

```python
from modules.shared.src.security.taxonomy_security_vo import (
    AuditSeverity,
    ViolationCategory,
)


async def validate_path(self, request: PathValidationVO) -> PathValidationVO:
    result = await self._delegate(self._validate_path.validate_path, request)

    if not result.allowed:
        await self._emit_security_audit(
            category=ViolationCategory.PATH_TRAVERSAL,
            operation_type="validate_path",
            metadata=result.audit_metadata,
        )

    return result


async def validate_extraction(self, request: ArchiveExtractionVO) -> ArchiveExtractionVO:
    result = await self._delegate(self._validate_archive.validate_extraction, request)

    if not result.allowed:
        await self._emit_security_audit(
            category=ViolationCategory.UNSAFE_ARCHIVE_ENTRY,
            operation_type="validate_extraction",
            metadata=result.audit_metadata,
        )

    return result


async def validate_code(self, request: CodeValidationVO) -> CodeValidationVO:
    result = await self._delegate(self._validate_code.validate_code, request)

    if result.audit_metadata.get("rule") == "validation_disabled_override":
        await self._emit_security_audit(
            category=ViolationCategory.POLICY_OVERRIDE,
            operation_type="validate_code",
            metadata=result.audit_metadata,
            severity=AuditSeverity.WARNING,
        )
    elif not result.allowed:
        await self._emit_security_audit(
            category=ViolationCategory.CODE_VIOLATION,
            operation_type="validate_code",
            metadata=result.audit_metadata,
        )

    return result


async def redact(self, request: RedactionVO) -> RedactionVO:
    result = await self._delegate(self._redact.redact, request)

    if result.failed:
        await self._emit_security_audit(
            category=ViolationCategory.REDACTION_FAILURE,
            operation_type="redact",
            metadata={"failure_reason": result.failure_reason or "unknown"},
            severity=AuditSeverity.ERROR,
        )

    return result
```

Add Block 3 helper:

```python
async def _emit_security_audit(
    self,
    category: ViolationCategory,
    operation_type: str,
    metadata: dict,
    severity: AuditSeverity = AuditSeverity.WARNING,
) -> None:
    event = SecurityAuditEventVO(
        violation_category=category,
        operation_type=operation_type,
        source_feature="security",
        target_metadata=metadata,
        severity=severity,
    )

    try:
        await self._emit_audit.emit_audit(event)
    except Exception:
        # Do not suppress the original security result.
        logger.error("Audit emission failed for %s", operation_type)
```

### `modules/security/src/capabilities_audit_emitter.py`

Create a real fallback record instead of discarding it.

```python
async def emit_audit(self, event: SecurityAuditEventVO) -> SecurityAuditEventVO:
    emitted = SecurityAuditEventVO(
        violation_category=event.violation_category,
        operation_type=event.operation_type,
        source_feature=event.source_feature,
        target_metadata=_redact_sensitive(event.target_metadata),
        severity=event.severity,
        correlation_id=event.correlation_id,
        redacted_reason=(_redact_sensitive(event.redacted_reason) if event.redacted_reason else None),
        event_id=uuid.uuid4().hex[:16],
        timestamp=time.time(),
        policy_mode=event.policy_mode,
    )

    if self._sink is None:
        logger.error(
            "Audit sink not configured; fallback audit event=%s category=%s",
            emitted.event_id,
            emitted.violation_category.value,
        )
        return emitted

    try:
        self._sink.deliver(emitted)
    except Exception:
        fallback = SecurityAuditEventVO(
            violation_category=emitted.violation_category,
            operation_type=emitted.operation_type,
            source_feature=emitted.source_feature,
            target_metadata=emitted.target_metadata,
            severity=AuditSeverity.ERROR,
            correlation_id=emitted.correlation_id,
            redacted_reason=emitted.redacted_reason,
            event_id=uuid.uuid4().hex[:16],
            timestamp=time.time(),
            policy_mode="fallback",
        )

        # Minimum acceptable fallback: structured redacted log.
        # Preferred: deliver to a local buffer or fallback sink.
        logger.error(
            "Audit sink delivery failed; fallback audit event=%s category=%s metadata=%s",
            fallback.event_id,
            fallback.violation_category.value,
            _redact_sensitive(fallback.target_metadata),
        )

    return emitted
```

### `modules/security/src/capabilities_code_validator.py`

Use policy maximum code size.

```python
async def validate_code(self, request: CodeValidationVO) -> CodeValidationVO:
    effective_max_size = request.max_code_size

    if self._policy is not None:
        effective_max_size = min(request.max_code_size, self._policy.max_code_size)

    code_bytes = len(request.code_text.encode("utf-8"))

    if code_bytes > effective_max_size:
        return CodeValidationVO(
            code_text=request.code_text,
            max_code_size=effective_max_size,
            strict_mode=request.strict_mode,
            execution_context=request.execution_context,
            allowed=False,
            violations=(
                CodeViolationVO(
                    category="size_limit",
                    description=f"Code too large: {code_bytes} > {effective_max_size}",
                ),
            ),
            audit_metadata={"rule": "code_oversized", "size": code_bytes},
        )

    # Existing validation logic remains here.
```

### `modules/security/src/capabilities_sensitive_redactor.py`

Preserve key names and redact only values.

```python
for key in all_keys:
    pattern = rf'(?i)(["\']?{re.escape(key)}["\']?\s*[:=]\s*)' + KV_VALUE
    text, count = re.subn(pattern, r"\1[REDACTED]", text)
    redacted_count += count
```

### `modules/security/src/root_security_container.py`

Wire policy into all capabilities.

```python
def wire(self) -> None:
    if self._wired:
        return

    logger.info("Wiring security feature module")

    validate_path_cap = PathValidator(policy=self._policy)
    validate_archive_cap = ArchiveGuard(policy=self._policy)
    validate_code_cap = CodeValidator(policy=self._policy)
    redact_cap = SensitiveRedactor(
        extra_patterns=self._policy.redaction_patterns,
        extra_key_names=self._policy.redaction_key_names,
    )
    emit_audit_cap = AuditEmitter()

    self._orchestrator = SecurityOrchestrator(
        validate_path_cap=validate_path_cap,
        validate_archive_cap=validate_archive_cap,
        validate_code_cap=validate_code_cap,
        redact_cap=redact_cap,
        emit_audit_cap=emit_audit_cap,
    )

    self._wired = True
```
