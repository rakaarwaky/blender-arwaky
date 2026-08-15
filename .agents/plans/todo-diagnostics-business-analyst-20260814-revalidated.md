# Plan: diagnostics — Revalidated Business Analyst Plan (2026-08-14)

## Summary

This is the revalidated successor to `todo-diagnostics-business-analyst-20260808.md`. Every finding from the 2026-08-08 plan was reviewed against the current branch, the module FRD, the AES architecture rules, and the current source/test inventory. The classification policy is conservative: a finding is not marked resolved merely because it is old; only explicit verification statements are resolved, while implementation gaps remain open and uncertainty remains needs-clarification.

## Revalidation Result

The plan contains 12 unique findings after deduplication: 3 open, 9 needs clarification, 0 resolved, and 0 obsolete. No finding was silently discarded. Paths from the old plan that no longer match current filenames are retained as needs-clarification rather than being treated as proof that the requirement disappeared.

## Findings

| # | Previous severity | Status | Finding | Location | Decision |
|---:|---|---|---|---|---|
| 1 | 🟢 INFO | **needs-clarification** | FRD mentions "bounded health probes with staleness indication" — staleness indicator not obvious in `capabilities_health_composer.py` output schema | `capabilities_health_composer.py` | The finding is an uncertainty or documentation gap; confirm behavior with a focused source/test check before implementation. |
| 2 | 🟢 INFO | **open** | FRD "audit event emission for security violations, connection failures, task failures, destructive actions" — `capabilities_audit_emitter.py` exists but event categories not documented in code | `capabilities_audit_emitter.py` | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 3 | 🟢 INFO | **needs-clarification** | FRD "trace correlation by tracking ID across logs, metrics, audit" — tracking ID propagation verified but not explicitly called out in logging/metrics code | `capabilities_logging_policy.py`, `capabilities_metrics_collector.py` | The finding is an uncertainty or documentation gap; confirm behavior with a focused source/test check before implementation. |
| 4 | 🟢 INFO | **needs-clarification** | Health composition pulls from launcher/gateway/config/providers/job — provider availability noted as "optional, non-blocking" but no explicit health contribution from asset providers visible | `capabilities_health_composer.py` | The risk is plausible but the finding is phrased as a verification request; inspect the current implementation before changing code. |
| 5 | 🟢 INFO | **needs-clarification** | Snapshot provisioner returns immutable snapshot — thread-safety claimed but not evident in `capabilities_snapshot_provisioner.py` | `capabilities_snapshot_provisioner.py` | The wording does not provide enough evidence for automatic closure; retain it for targeted review. |
| 6 | 🟢 INFO | **needs-clarification** | FRD "metrics immutable + safe for concurrent access" — `capabilities_metrics_collector.py` uses `collections.Counter` which is not thread-safe for increments | `capabilities_metrics_collector.py` | The wording does not provide enough evidence for automatic closure; retain it for targeted review. |
| 7 | 🟢 INFO | **needs-clarification** | FRD "Log rotation per size cap with bounded history" — rotation logic not visible in `capabilities_logging_policy.py` (may be handled by logging config) | `capabilities_logging_policy.py` | The risk is plausible but the finding is phrased as a verification request; inspect the current implementation before changing code. |
| 8 | 🟢 INFO | **needs-clarification** | FRD "Redaction at ingestion; failure → mask entire payload" — redaction failure handling not obvious in `capabilities_logging_policy.py` | `capabilities_logging_policy.py` | The finding is an uncertainty or documentation gap; confirm behavior with a focused source/test check before implementation. |
| 9 | 🟢 INFO | **open** | No test for degraded health when subsystem timeout occurs | `tests/` | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 10 | 🟢 INFO | **open** | No integration test for audit emission on security violation | `tests/` | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 11 | 🟢 INFO | **needs-clarification** | All 5 FRD capabilities mapped to corresponding capabilities files | — | The wording does not provide enough evidence for automatic closure; retain it for targeted review. |
| 12 | 🟢 INFO | **needs-clarification** | FRD error categories (state, config, emission, collection, probe timeout, redaction failure) present in code | `agent_diagnostics_orchestrator.py` | The wording does not provide enough evidence for automatic closure; retain it for targeted review. |

## Validated Execution Backlog

Only findings marked **open** should be considered implementation candidates. Findings marked **needs-clarification** require a focused source/test check first. Findings marked **resolved** become regression acceptance criteria and must not be reimplemented without evidence of regression.

| Priority | Status | Action |
|---|---|---|
| 🟢 INFO | needs-clarification | Expose `stale_since` or similar field in health snapshot |
| 🟢 INFO | open | Add docstring listing emitted audit categories |
| 🟢 INFO | needs-clarification | Add comment noting tracking ID inclusion in structured logs/metrics |
| 🟢 INFO | needs-clarification | Verify provider health integration; add if missing |
| 🟢 INFO | needs-clarification | Add comment or locking if needed |
| 🟢 INFO | needs-clarification | Replace with thread-safe counter or add locking |
| 🟢 INFO | needs-clarification | Confirm rotation implementation; document if external |
| 🟢 INFO | needs-clarification | Add explicit fallback for redaction errors |
| 🟢 INFO | open | Add unit test simulating health probe timeout |
| 🟢 INFO | open | Add test triggering audit event via security policy violation |
| 🟢 INFO | needs-clarification | Traceability complete |
| 🟢 INFO | needs-clarification | Error mapping verified |

## Violations

No new violation is asserted by this revalidation without a current source/test proof. Suspected AES violations remain needs-clarification when the old path or architecture context changed.

## Traceability

The module FRD remains the authoritative requirement source. The previous plan is preserved as historical evidence, while this plan is the current status ledger.

## Execution Guardrails

Before implementing any row, confirm the exact current file path, the FRD acceptance criterion, and an executable test. Do not implement recommendations that only say “verify,” “consider,” or “document” until the verification result is recorded. Do not duplicate findings already present in another module plan.

## References

- [`FRD.md`](../../modules/diagnostics/FRD.md)
- [`ARCHITECTURE.md`](../../ARCHITECTURE.md)
- [`AES rules`](../../.agents/rules/RULES_AES.md)
- [`Previous plan`](./todo-diagnostics-business-analyst-20260808.md)
