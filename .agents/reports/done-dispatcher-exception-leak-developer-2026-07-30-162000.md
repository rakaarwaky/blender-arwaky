# Execution Report: Dispatcher Exception Leak — Developer

## Issue Executed
GitHub Issue #37: CRITICAL: Dispatcher exception messages leak sensitive information into result envelopes

## Branch Created
`fix/37-dispatcher-exception-leak`

## Worktree
`.worktree/37-dispatcher-exception-leak`

## Execution Summary

### Problem
Exception messages were placed directly into result envelopes without sanitization. Examples included `f"Action '{action_name}' failed: {e}"`, `f"Job creation failed: {e}"`, and `safe_error_envelope(str(e))`. Exception text could contain paths, secrets, stack traces, or provider details, violating FR-DSP-006 security requirements.

### Changes Made

1. **New `taxonomy_dispatch_error.py`** — `DispatchErrorCategory` constants class and `DispatchError` exception with typed error category

2. **`capabilities_sync_dispatch.py`** — Replaced `f"Action '{action_name}' failed: {e}"` with generic `"Action execution failed"`; changed `_map_error_category` to use `DispatchErrorCategory` constants

3. **`agent_dispatcher_orchestrator.py`** — Added `_safe_message()` static method returning generic `"Action request could not be processed"`; replaced `str(e)` leaks with safe messages; replaced `safe_error_envelope(str(e))` with typed error envelope

4. **`capabilities_background_submit.py`** — Replaced `f"Job creation failed: {e}"` with `"Background job submission failed"`; uses `DispatchErrorCategory.EXECUTION`

5. **`dispatcher/__init__.py`** — Exports `DispatchError` and `DispatchErrorCategory`

### Sanitization Guarantee
Exception details remain in logs only — no exception text, paths, secrets, or stack traces escape to result envelopes.

## Verification Results
- **Ruff linter**: All checks passed ✅
- **Pytest (59 tests)**: All 59 passed ✅

## Deviations & Notes
- Followed the issue's proposed fix closely: safe generic messages, DispatchErrorCategory constants, DispatchError exception
- The `_safe_message()` uses `_error: object` prefix with underscore to indicate unused parameter (respects ruff ARG004)
- No test changes needed — tests check envelope structure and success/failure flags, not message content
