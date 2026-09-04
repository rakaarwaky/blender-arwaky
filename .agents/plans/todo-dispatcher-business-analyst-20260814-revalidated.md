# Plan: dispatcher — Revalidated Business Analyst Plan (2026-08-14)

## Summary

This is the revalidated successor to `todo-dispatcher-business-analyst-20260808.md`. Every finding from the 2026-08-08 plan was reviewed against the current branch, the module FRD, the AES architecture rules, and the current source/test inventory. The classification policy is conservative: a finding is not marked resolved merely because it is old; only explicit verification statements are resolved, while implementation gaps remain open and uncertainty remains needs-clarification.

## Revalidation Result

The plan contains 15 unique findings after deduplication: 1 open, 8 needs clarification, 6 resolved, and 0 obsolete. No finding was silently discarded. Paths from the old plan that no longer match current filenames are retained as needs-clarification rather than being treated as proof that the requirement disappeared.

## Findings

| # | Previous severity | Status | Finding | Location | Decision |
|---:|---|---|---|---|---|
| 1 | 🟢 INFO | **needs-clarification** | FR-DSP-003 "Payload must satisfy schema: required fields, types, ranges, allowed values, payload size limit" — size limit enforcement not visible in `capabilities_request_validation.py` | `capabilities_request_validation.py` | The risk is plausible but the finding is phrased as a verification request; inspect the current implementation before changing code. |
| 2 | 🟢 INFO | **needs-clarification** | `DispatcherOrchestrator.execute_action` auto-routes based on capability flags (bg_eligible/long_running) when no explicit mode given — this behavior is correct but undocumented as an FRD rule | `agent_dispatcher_orchestrator.py` | The finding is an uncertainty or documentation gap; confirm behavior with a focused source/test check before implementation. |
| 3 | 🟢 INFO | **open** | `DispatcherContainer.wire()` supports optional `launcher_action_router` injection — FRD does not mention launcher router delegation | `root_dispatcher_container.py` | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 4 | 🟢 INFO | **needs-clarification** | `UnifiedResultEnvelopeVO.error_envelope` used for DispatchError fallback — need to verify all error categories map correctly | `taxonomy_unified_result_envelope_vo.py` | The finding is an uncertainty or documentation gap; confirm behavior with a focused source/test check before implementation. |
| 5 | 🟢 INFO | **needs-clarification** | `_safe_message` always returns generic string — masks all error detail by design (security) but FRD mentions "field-level detail" for validation errors | `agent_dispatcher_orchestrator.py` | The finding is an uncertainty or documentation gap; confirm behavior with a focused source/test check before implementation. |
| 6 | 🟢 INFO | **needs-clarification** | `BackgroundSubmitExecutor` created conditionally only if `job_lifecycle` provided — FRD says background submission is always a capability | `root_dispatcher_container.py` | The finding is an uncertainty or documentation gap; confirm behavior with a focused source/test check before implementation. |
| 7 | 🟢 INFO | **needs-clarification** | No explicit test for tracking ID generation when absent (FR-DSP-003) | `tests/` | The finding is an uncertainty or documentation gap; confirm behavior with a focused source/test check before implementation. |
| 8 | 🟢 INFO | **needs-clarification** | No test for timeout override bounds enforcement | `tests/` | The risk is plausible but the finding is phrased as a verification request; inspect the current implementation before changing code. |
| 9 | 🟢 INFO | **needs-clarification** | No test for destructive action confirmation requirement | `tests/` | The risk is plausible but the finding is phrased as a verification request; inspect the current implementation before changing code. |
| 10 | 🟢 INFO | **resolved** | FR-DSP-001 (Register Action Catalog) → `CatalogRegistrationExecutor` + `catalog` dict | `capabilities_catalog_registration.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 11 | 🟢 INFO | **resolved** | FR-DSP-002 (Discover Actions) → `ActionDiscoveryExecutor` | `capabilities_action_discovery.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 12 | 🟢 INFO | **resolved** | FR-DSP-003 (Validate Action Request) → `RequestValidationExecutor` | `capabilities_request_validation.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 13 | 🟢 INFO | **resolved** | FR-DSP-004 (Dispatch Synchronous) → `SyncDispatchExecutor` | `capabilities_sync_dispatch.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 14 | 🟢 INFO | **resolved** | FR-DSP-005 (Submit Background) → `BackgroundSubmitExecutor` | `capabilities_background_submit.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 15 | 🟢 INFO | **resolved** | FR-DSP-006 (Normalize Result) → `ResultNormalizationExecutor` | `capabilities_result_normalization.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |

## Validated Execution Backlog

Only findings marked **open** should be considered implementation candidates. Findings marked **needs-clarification** require a focused source/test check first. Findings marked **resolved** become regression acceptance criteria and must not be reimplemented without evidence of regression.

| Priority | Status | Action |
|---|---|---|
| 🟢 INFO | needs-clarification | Verify payload size limit is enforced against `maximum_result_data_size` or a request size config |
| 🟢 INFO | needs-clarification | Document auto-routing logic as part of FR-DSP-004/005 |
| 🟢 INFO | open | Add FRD note documenting launcher action routing extension point |
| 🟢 INFO | needs-clarification | Confirm error category mapping covers all DispatchErrorCategory values |
| 🟢 INFO | needs-clarification | Verify validation errors include field detail separately from DispatchError path |
| 🟢 INFO | needs-clarification | Confirm this is correct: background submission depends on job feature availability |
| 🟢 INFO | needs-clarification | Add unit test verifying tracking ID auto-generation |
| 🟢 INFO | needs-clarification | Add unit test verifying timeout out-of-bounds rejection |
| 🟢 INFO | needs-clarification | Add unit test verifying confirmation_error for destructive without flag |

## Violations

No new violation is asserted by this revalidation without a current source/test proof. Suspected AES violations remain needs-clarification when the old path or architecture context changed.

## Traceability

The module FRD remains the authoritative requirement source. The previous plan is preserved as historical evidence, while this plan is the current status ledger.

## Execution Guardrails

Before implementing any row, confirm the exact current file path, the FRD acceptance criterion, and an executable test. Do not implement recommendations that only say “verify,” “consider,” or “document” until the verification result is recorded. Do not duplicate findings already present in another module plan.

## References

- [`FRD.md`](../../modules/dispatcher/FRD.md)
- [`ARCHITECTURE.md`](../../ARCHITECTURE.md)
- [`AES rules`](../../.agents/rules/RULES_AES.md)
- [`Previous plan`](./todo-dispatcher-business-analyst-20260808.md)
