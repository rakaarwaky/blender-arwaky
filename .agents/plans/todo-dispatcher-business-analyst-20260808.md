# Plan: dispatcher — Business Analyst

## Summary
The dispatcher module implements the single routing/catalog authority between consumers (CLI/MCP) and domain features per FR-DSP-001..006. AES structure: 1 agent orchestrator, 6 capabilities, 1 root container. FRD-to-code traceability is complete and strong. Catalog shared instance pattern correctly enforces single-source-of-truth. No violations found.

## Findings

### Requirements Clarity
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | �� 🟢 INFO | FR-DSP-003 "Payload must satisfy schema: required fields, types, ranges, allowed values, payload size limit" — size limit enforcement not visible in `capabilities_request_validation.py` | `capabilities_request_validation.py` | Verify payload size limit is enforced against `maximum_result_data_size` or a request size config |

### Business Flow
| # | Severity | Issue | Location | Recommendation |
|---|---|---|---|---|
| 1 | �� 🟢 INFO | `DispatcherOrchestrator.execute_action` auto-routes based on capability flags (bg_eligible/long_running) when no explicit mode given — this behavior is correct but undocumented as an FRD rule | `agent_dispatcher_orchestrator.py` | Document auto-routing logic as part of FR-DSP-004/005 |
| 2 | �� 🟢 INFO | `DispatcherContainer.wire()` supports optional `launcher_action_router` injection — FRD does not mention launcher router delegation | `root_dispatcher_container.py` | Add FRD note documenting launcher action routing extension point |

### Logic Implementation
| # | Severity | Issue | Location | Recommendation |
|---|---|---|---|---|
| 1 | �� 🟢 INFO | `UnifiedResultEnvelopeVO.error_envelope` used for DispatchError fallback — need to verify all error categories map correctly | `taxonomy_unified_result_envelope_vo.py` | Confirm error category mapping covers all DispatchErrorCategory values |
| 2 | �� 🟢 INFO | `_safe_message` always returns generic string — masks all error detail by design (security) but FRD mentions "field-level detail" for validation errors | `agent_dispatcher_orchestrator.py` | Verify validation errors include field detail separately from DispatchError path |
| 3 | �� 🟢 INFO | `BackgroundSubmitExecutor` created conditionally only if `job_lifecycle` provided — FRD says background submission is always a capability | `root_dispatcher_container.py` | Confirm this is correct: background submission depends on job feature availability |

### Testability & Acceptance
| # | Severity | Issue | Location | Recommendation |
|---|---|---|---|---|
| 1 | �� 🟢 INFO | No explicit test for tracking ID generation when absent (FR-DSP-003) | `tests/` | Add unit test verifying tracking ID auto-generation |
| 2 | �� 🟢 INFO | No test for timeout override bounds enforcement | `tests/` | Add unit test verifying timeout out-of-bounds rejection |
| 3 | �� 🟢 INFO | No test for destructive action confirmation requirement | `tests/` | Add unit test verifying confirmation_error for destructive without flag |

### Traceability (FRD→Code)
| # | Severity | Issue | Location | Recommendation |
|---|---|---|---|---|
| 1 | �� 🟢 INFO | FR-DSP-001 (Register Action Catalog) → `CatalogRegistrationExecutor` + `catalog` dict | `capabilities_catalog_registration.py` | Traceability verified |
| 2 | �� 🟢 INFO | FR-DSP-002 (Discover Actions) → `ActionDiscoveryExecutor` | `capabilities_action_discovery.py` | Traceability verified |
| 3 | �� 🟢 INFO | FR-DSP-003 (Validate Action Request) → `RequestValidationExecutor` | `capabilities_request_validation.py` | Traceability verified |
| 4 | �� 🟢 INFO | FR-DSP-004 (Dispatch Synchronous) → `SyncDispatchExecutor` | `capabilities_sync_dispatch.py` | Traceability verified |
| 5 | �� 🟢 INFO | FR-DSP-005 (Submit Background) → `BackgroundSubmitExecutor` | `capabilities_background_submit.py` | Traceability verified |
| 6 | �� 🟢 INFO | FR-DSP-006 (Normalize Result) → `ResultNormalizationExecutor` | `capabilities_result_normalization.py` | Traceability verified |

## Violations
None found. AES layer separation respected: orchestrator coordinates, capabilities implement logic, root container wires only.

## Action Items
- [ ] �� 🟢 INFO Verify payload size limit enforcement in request validation
- [ ] �� 🟢 INFO Document auto-routing logic and launcher router extension in FRD
- [ ] �� 🟢 INFO Verify error category mapping in unified envelope
- [ ] �� 🟢 INFO Add unit tests for tracking ID generation, timeout bounds, destructive confirmation

## Fixed Code
None required.

## Severity
- �� 🔴 CRITICAL: Missing core requirement, wrong logic, data integrity risk
- �� 🟡 WARNING: Ambiguous requirement, missing edge case, incomplete criteria
- �� 🟢 INFO: Suggestion or optimization, deferrable

## Checklist
- [x] Prerequisites read
- [x] Feature + modules identified
- [x] FRD mapped to code files
- [x] All 5 dimensions analyzed
- [x] Severity categorized
- [x] Deduped vs existing plans + active PRs
- [x] Plan written (NEW issues + fixed code)
- [x] Saved to correct path