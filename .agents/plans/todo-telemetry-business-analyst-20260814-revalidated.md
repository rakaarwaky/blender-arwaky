# Plan: telemetry — Revalidated Business Analyst Plan (2026-08-14)

## Summary

This is the revalidated successor to `todo-telemetry-business-analyst-20260808.md`. Every finding from the 2026-08-08 plan was reviewed against the current branch, the module FRD, the AES architecture rules, and the current source/test inventory. The classification policy is conservative: a finding is not marked resolved merely because it is old; only explicit verification statements are resolved, while implementation gaps remain open and uncertainty remains needs-clarification.

## Revalidation Result

The plan contains 6 unique findings after deduplication: 5 open, 0 needs clarification, 1 resolved, and 0 obsolete. No finding was silently discarded. Paths from the old plan that no longer match current filenames are retained as needs-clarification rather than being treated as proof that the requirement disappeared.

## Findings

| # | Previous severity | Status | Finding | Location | Decision |
|---:|---|---|---|---|---|
| 1 | 🟡 WARNING | **open** | Schema versioning not enforced in classification/recording logic; `TelemetryDraft` uses fixed "unknown" version. | `taxonomy_telemetry_event_vo.py`, `capabilities_telemetry_recording_capability.py` | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 2 | 🟡 WARNING | **open** | Transmission to backend is not implemented; recording/buffering exists but delivery stub is missing. | `capabilities_telemetry_recording_capability.py` | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 3 | 🟢 INFO | **resolved** | Recording → classification → enrichment → buffering flow verified. | `capabilities_telemetry_recording_capability.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 4 | 🟡 WARNING | **open** | Transmission step after buffering is missing; FRD mentions backend delivery. | — | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 5 | 🟡 WARNING | **open** | Backpressure handling lacks metrics on buffer saturation or drop counts. | `capabilities_telemetry_recording_capability.py` | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 6 | 🟡 WARNING | **open** | No tests for schema versioning enforcement or transmission error handling. | `tests/` | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |

## Validated Execution Backlog

Only findings marked **open** should be considered implementation candidates. Findings marked **needs-clarification** require a focused source/test check first. Findings marked **resolved** become regression acceptance criteria and must not be reimplemented without evidence of regression.

| Priority | Status | Action |
|---|---|---|
| 🟡 WARNING | open | Implement schema version tracking with increment enforcement per FR-TLM-002. |
| 🟡 WARNING | open | Add transmission stub (backend integration placeholder) with error handling. |
| 🟡 WARNING | open | Add transmission stub with error handling and retry logic. |
| 🟡 WARNING | open | Expose backpressure metrics (buffer size, saturation %, drop count) via diagnostics. |
| 🟡 WARNING | open | Add tests for schema version increments and transmission stub behavior. |

## Violations

No new violation is asserted by this revalidation without a current source/test proof. Suspected AES violations remain needs-clarification when the old path or architecture context changed.

## Traceability

The module FRD remains the authoritative requirement source. The previous plan is preserved as historical evidence, while this plan is the current status ledger.

## Execution Guardrails

Before implementing any row, confirm the exact current file path, the FRD acceptance criterion, and an executable test. Do not implement recommendations that only say “verify,” “consider,” or “document” until the verification result is recorded. Do not duplicate findings already present in another module plan.

## References

- [`FRD.md`](../../modules/telemetry/FRD.md)
- [`ARCHITECTURE.md`](../../ARCHITECTURE.md)
- [`AES rules`](../../.agents/rules/RULES_AES.md)
- [`Previous plan`](./todo-telemetry-business-analyst-20260808.md)
