# Execution Report: Dispatcher Background Submit — Developer

## Issue Executed
GitHub Issue #35: CRITICAL: Dispatcher background submit creates synthetic job IDs bypassing Job feature

## Branch Created
`fix/35-dispatcher-fake-job-ids`

## Worktree
`.worktree/35-dispatcher-fake-job-ids`

## Execution Summary

### Problem
`BackgroundSubmitExecutor.submit_background()` created a fake job ID via `uuid.uuid4()` when `self._job_tracker` was None, bypassing the Job feature entirely. This violated FR-DSP-005 atomic submission integrity.

### Changes Made

1. **`capabilities_background_submit.py`**:
   - Added `JobTrackerProtocol` (a `typing.Protocol`) defining the `track_new_task()` interface
   - Changed constructor to require a non-null `job_tracker` — raises `ValueError` if `None`
   - Removed the `if self._job_tracker` / `else: uuid.uuid4()` fake-id branch
   - Now always delegates to `self._job_tracker.track_new_task()`, guaranteed non-null at construction
   - Removed unused `uuid` import
   - Updated `_get_active_job_count()` to remove the `if tracker is None: return 0` guard (tracker now guaranteed non-null)

2. **`root_dispatcher_container.py`**:
   - Removed `background_submit = BackgroundSubmitExecutor()` instantiation (no job tracker available)
   - Removed `BackgroundSubmitExecutor` import
   - Removed `background_submit` from `DispatcherOrchestrator` constructor call
   - Added comment explaining the orchestrator will raise `"BackgroundSubmitProtocol not configured"` instead of creating synthetic job IDs

## Verification Results
- **Ruff linter**: All checks passed ✅
- **Pytest (59 tests)**: All 59 passed in 0.27s ✅
- **Issue resolved**: `BackgroundSubmitExecutor` no longer creates synthetic job IDs; `ValueError` raised at construction if `job_tracker` is None

## Deviations & Notes
- Follows the same pattern established in Issue #34 fix (required Protocol at construction, remove fake-success fallback, update container)
- `JobTrackerProtocol` defined locally in capabilities file rather than shared contract layer, consistent with the `ActionExecutorProtocol` approach from #34
