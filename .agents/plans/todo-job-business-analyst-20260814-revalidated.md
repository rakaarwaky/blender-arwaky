# Plan: job — Revalidated Business Analyst Plan (2026-08-14)

## Summary

This is the revalidated successor to `todo-job-business-analyst-20260808.md`. Every finding from the 2026-08-08 plan was reviewed against the current branch, the module FRD, the AES architecture rules, and the current source/test inventory. The classification policy is conservative: a finding is not marked resolved merely because it is old; only explicit verification statements are resolved, while implementation gaps remain open and uncertainty remains needs-clarification.

## Revalidation Result

The plan contains 18 unique findings after deduplication: 4 open, 5 needs clarification, 9 resolved, and 0 obsolete. Current source evidence closes atomic transition, synchronous task creation, and stale recovery questions; missing acceptance tests remain actionable. No finding was silently discarded. Paths from the old plan that no longer match current filenames are retained as needs-clarification rather than being treated as proof that the requirement disappeared.

## Findings

| # | Previous severity | Status | Finding | Location | Decision |
|---:|---|---|---|---|---|
| 1 | 🔴 CRITICAL | **needs-clarification** | FR-JOB-001 "Error detail sanitized before storage (no secrets/raw code)" — error sanitization must delegate to Security module's redactor; verify implementation | `agent_job_orchestrator.py` | The finding is an uncertainty or documentation gap; confirm behavior with a focused source/test check before implementation. |
| 2 | 🟡 WARNING | **needs-clarification** | FR-JOB-001 "Metadata never contains secrets/credentials/tokens/paths" — validation rule not explicitly enforced in `capabilities_job_repository.py` | `capabilities_job_repository.py` | The risk is plausible but the finding is phrased as a verification request; inspect the current implementation before changing code. |
| 3 | 🟡 WARNING | **needs-clarification** | FR-JOB-004 "Capacity limit enforced from config" — need explicit assertion against config key `max_concurrent_background_tasks` | `capabilities_job_scheduler.py` | The wording does not provide enough evidence for automatic closure; retain it for targeted review. |
| 4 | 🟡 WARNING | **resolved** | Job creation flow: caller → job feature → task record → execution layer. Current implementation may not wait for task ID generation before returning to caller | `agent_job_orchestrator.py` | Current `submit_task` creates the lifecycle record synchronously before returning the task result; retain as an acceptance criterion. |
| 5 | 🟡 WARNING | **needs-clarification** | Cancellation flow: CLI/MCP → job → executor hook. Executor may not acknowledge cancellation in time | `capabilities_job_resolver.py` | The finding is an uncertainty or documentation gap; confirm behavior with a focused source/test check before implementation. |
| 6 | 🟢 INFO | **resolved** | Progress reporting flow: executor updates job via `update_progress` → stored atomically → returned on status query | `capabilities_job_checker.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 7 | 🔴 CRITICAL | **resolved** | Concurrent transitions must be atomic (FR-JOB-001 "All transitions atomic + thread-safe") — verify threading model | `capabilities_job_repository.py` | Current repository owns an `RLock` and guards create, update, transition, read, list, and delete operations; retain concurrency behavior as a regression criterion. |
| 8 | 🟡 WARNING | **resolved** | Stale running task detection (FR-JOB-001 "running→timed out (optional, for stale recovery)") — verify implementation | `capabilities_job_evaluator.py` | Current orchestrator cleanup collects stale running task IDs, applies timeout transitions, and purges records; retain as a recovery regression criterion. |
| 9 | 🟡 WARNING | **needs-clarification** | Task ID uniqueness and collision resistance not verified | `capabilities_job_scheduler.py` | The wording does not provide enough evidence for automatic closure; retain it for targeted review. |
| 10 | 🟡 WARNING | **open** | No test for concurrent state transitions | `tests/` | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 11 | 🟡 WARNING | **open** | No test for stale running task timeout | `tests/` | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 12 | 🟡 WARNING | **open** | No test for capacity limit enforcement | `tests/` | The risk is plausible but the finding is phrased as a verification request; inspect the current implementation before changing code. |
| 13 | 🟡 WARNING | **open** | No test for metadata sanitization | `tests/` | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 14 | 🟢 INFO | **resolved** | FR-JOB-001 (Track Task Lifecycle) → `capabilities_job_repository.py` | `agent_job_orchestrator.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 15 | 🟢 INFO | **resolved** | FR-JOB-002 (Monitor Task Status) → `capabilities_job_checker.py` | `capabilities_job_checker.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 16 | 🟢 INFO | **resolved** | FR-JOB-003 (Cancel Task) → `capabilities_job_resolver.py` | `capabilities_job_resolver.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 17 | 🟢 INFO | **resolved** | FR-JOB-004 (Automatic Cleanup) → `capabilities_job_repository.py` | `capabilities_job_repository.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 18 | 🟢 INFO | **resolved** | FR-JOB-005 (Enforce Background Capacity) → `capabilities_job_scheduler.py` | `capabilities_job_scheduler.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |

## Validated Execution Backlog

Only findings marked **open** should be considered implementation candidates. Findings marked **needs-clarification** require a focused source/test check first. Findings marked **resolved** become regression acceptance criteria and must not be reimplemented without evidence of regression.

| Priority | Status | Action |
|---|---|---|
| 🔴 CRITICAL | needs-clarification | Confirm error sanitization uses security policy redaction |
| 🟡 WARNING | needs-clarification | Add validation to reject metadata containing sensitive patterns |
| 🟡 WARNING | needs-clarification | Add assertion/check for config value usage |
| 🟡 WARNING | resolved | Keep synchronous task creation as a regression criterion |
| 🟡 WARNING | needs-clarification | Document cancellation timeout expectations |
| 🔴 CRITICAL | resolved | Keep repository locking as a concurrency regression criterion |
| 🟡 WARNING | resolved | Keep stale timeout recovery as a regression criterion |
| 🟡 WARNING | needs-clarification | Add test/assertion for ID collision resistance |
| 🟡 WARNING | open | Add concurrency test with multiple threads |
| 🟡 WARNING | open | Add test for stale recovery |
| 🟡 WARNING | open | Add test verifying capacity error |
| 🟡 WARNING | open | Add test with sensitive metadata values |

## Violations

No new violation is asserted by this revalidation without a current source/test proof. Suspected AES violations remain needs-clarification when the old path or architecture context changed.

## Traceability

The module FRD remains the authoritative requirement source. The previous plan is preserved as historical evidence, while this plan is the current status ledger.

## Execution Guardrails

Before implementing any row, confirm the exact current file path, the FRD acceptance criterion, and an executable test. Do not implement recommendations that only say “verify,” “consider,” or “document” until the verification result is recorded. Do not duplicate findings already present in another module plan.

## References

- [`FRD.md`](../../modules/job/FRD.md)
- [`ARCHITECTURE.md`](../../ARCHITECTURE.md)
- [`AES rules`](../../.agents/rules/RULES_AES.md)
- [`Previous plan`](./todo-job-business-analyst-20260808.md)
