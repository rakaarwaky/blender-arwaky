# Phase 1 Architect Report: job

## Overview

The `job` feature implements a background task tracking system with a clean separation of concerns across 5 capabilities and a thin orchestrator. The state machine enforcement, sanitization pipeline, event emission, and capacity evaluation all follow AES patterns correctly.

**Overall Assessment: PASS — no blocking issues.**

| Dimension | Health | Key Findings |
|---|---|---|
| Naming Convention | ✅ Good | All files follow prefix_concept_suffix pattern |
| Layer Boundaries | ⚠️ Warning | Utility event emitter misplaced in job/src; transitor file exists in capabilities |
| Capabilities | ✅ Good | Each has ≤ 3 types; all implement required protocols |
| Agent | ✅ Good | Single orchestrator type; implements aggregate correctly |
| Orphan | ⚠️ Possible | JobSchedulerProtocol may be external-facing only |
| Scalability | ✅ Good | Clean single-responsibility per capability; thin orchestrator |

## Findings by Category

### Layer Boundaries

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| LB01 | 🟡 WARNING | `utility_job_event_emitter.py` is in `modules/job/src/` (capabilities layer) instead of `modules/shared/src/job/` where other utilities live | `modules/job/src/utility_job_event_emitter.py` | Move to `modules/shared/src/job/utility_job_event_emitter.py` per shared-layer convention |

### Naming Convention

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| NC01 | 🟢 INFO | File named `capabilities_job_transitor.py` — "transitor" is not a valid suffix per AES102; should be "transition" | `modules/job/src/capabilities_job_transitor.py` | Rename to `capabilities_job_transition.py` (and update all imports) |

### Dead Code / Orphan

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| OR01 | 🟢 INFO | `contract_job_protocol.py` (`JobSchedulerProtocol`) — only used externally by asset module for `submit_download`. Not implemented by any internal capability. Verify if needed or remove. | `modules/shared/src/job/contract_job_protocol.py` | Confirm with asset feature; if only used by asset, keep but document as external-facing protocol |

### Scalability & Coupling

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| SC01 | 🟢 INFO | `JobStateTransitor` is stateful (holds policy, clock, id_generator, lock) but should be stateless if moved to utility. Consider making it a pure function or passing state as parameters. | `modules/job/src/capabilities_job_transitor.py` lines 30-36 | Keep as capability (acceptable since repository already composes it), or refactor to stateless functions |

### Data Flow

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| DF01 | 🟢 INFO | `JobRecord.to_snapshot()` creates `JobStatusSnapshot` directly — this is acceptable as internal conversion. However, `JobStatusMonitor.project()` creates a second copy of the snapshot with redaction, which is correct for defense-in-depth. No fix needed. | N/A | Document this two-layer projection pattern as intentional architecture |

## Violations

| Code | Severity | Description |
|---|---|---|
| AES201 (sub-check 7) | WARNING | `capabilities_job_repository.py` imports `JobStateTransitor` from `capabilities_job_transitor.py` — cross-capability import is forbidden |

## Action Items

- [ ] Move `JobStateTransitor` class from `capabilities_job_transitor.py` to `modules/shared/src/job/utility_job_transition.py` as stateless functions
- [ ] Rename `capabilities_job_transitor.py` → `utility_job_transition.py` and update all imports
- [ ] Move `utility_job_event_emitter.py` from `modules/job/src/` to `modules/shared/src/job/`
- [ ] Verify `JobSchedulerProtocol` usage — document if external-facing or remove

## Detailed Fix Code

See `.agents/plans/todo-job-architect-2026-07-29-184500.md` for complete fixed code examples.
