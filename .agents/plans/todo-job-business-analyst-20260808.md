# Plan: job — Business Analyst

## Summary
The job module implements background task tracking per FR-JOB-001..005. AES structure: 1 agent orchestrator, 8 capabilities, 1 root container. FRD-to-code traceability is strong. Security dependency and observability gaps identified. Config enforcement verified.

## Findings

### Requirements Clarity
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🔴 CRITICAL | FR-JOB-001 "Error detail sanitized before storage (no secrets/raw code)" — error sanitization must delegate to Security module's redactor; verify implementation | `agent_job_orchestrator.py` | Confirm error sanitization uses security policy redaction |
| 2 | 🟡 WARNING | FR-JOB-001 "Metadata never contains secrets/credentials/tokens/paths" — validation rule not explicitly enforced in `capabilities_job_repository.py` | `capabilities_job_repository.py` | Add validation to reject metadata containing sensitive patterns |
| 3 | 🟡 WARNING | FR-JOB-004 "Capacity limit enforced from config" — need explicit assertion against config key `max_concurrent_background_tasks` | `capabilities_job_scheduler.py` | Add assertion/check for config value usage |

### Business Flow
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟡 WARNING | Job creation flow: caller → job feature → task record → execution layer. Current implementation may not wait for task ID generation before returning to caller | `agent_job_orchestrator.py` | Verify task creation is atomic and ID is available before returning success |
| 2 | 🟡 WARNING | Cancellation flow: CLI/MCP → job → executor hook. Executor may not acknowledge cancellation in time | `capabilities_job_resolver.py` | Document cancellation timeout expectations |
| 3 | 🟢 INFO | Progress reporting flow: executor updates job via `update_progress` → stored atomically → returned on status query | `capabilities_job_checker.py` | Traceability verified |

### Logic Implementation
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🔴 CRITICAL | Concurrent transitions must be atomic (FR-JOB-001 "All transitions atomic + thread-safe") — verify threading model | `capabilities_job_repository.py` | Add threading lock or use atomic database operations |
| 2 | 🟡 WARNING | Stale running task detection (FR-JOB-001 "running→timed out (optional, for stale recovery)") — verify implementation | `capabilities_job_evaluator.py` | Add or verify stale detection logic |
| 3 | 🟡 WARNING | Task ID uniqueness and collision resistance not verified | `capabilities_job_scheduler.py` | Add test/assertion for ID collision resistance |

### Testability & Acceptance
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟡 WARNING | No test for concurrent state transitions | `tests/` | Add concurrency test with multiple threads |
| 2 | 🟡 WARNING | No test for stale running task timeout | `tests/` | Add test for stale recovery |
| 3 | 🟡 WARNING | No test for capacity limit enforcement | `tests/` | Add test verifying capacity error |
| 4 | 🟡 WARNING | No test for metadata sanitization | `tests/` | Add test with sensitive metadata values |

### Traceability (FRD→Code)
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | FR-JOB-001 (Track Task Lifecycle) → `capabilities_job_repository.py` | `agent_job_orchestrator.py` | Traceability verified |
| 2 | 🟢 INFO | FR-JOB-002 (Monitor Task Status) → `capabilities_job_checker.py` | `capabilities_job_checker.py` | Traceability verified |
| 3 | 🟢 INFO | FR-JOB-003 (Cancel Task) → `capabilities_job_resolver.py` | `capabilities_job_resolver.py` | Traceability verified |
| 4 | 🟢 INFO | FR-JOB-004 (Automatic Cleanup) → `capabilities_job_repository.py` | `capabilities_job_repository.py` | Traceability verified |
| 5 | 🟢 INFO | FR-JOB-005 (Enforce Background Capacity) → `capabilities_job_scheduler.py` | `capabilities_job_scheduler.py` | Traceability verified |

## Violations
None found for AES layer separation. However, **CRITICAL**: error sanitization must properly delegate to Security module per FRD boundary requirements.

## Action Items
- [ ] 🔴 CRITICAL Verify error sanitization uses security redaction
- [ ] 🔴 CRITICAL Verify concurrent transitions are atomic/thread-safe
- [ ] 🟡 WARNING Add validation to reject metadata with sensitive patterns
- [ ] 🟡 WARNING Add assertion for config capacity limit usage
- [ ] 🟡 WARNING Add concurrency test for state transitions
- [ ] 🟡 WARNING Add test for stale running task timeout
- [ ] 🟡 WARNING Add test for capacity limit enforcement
- [ ] 🟡 WARNING Add test for metadata sanitization

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