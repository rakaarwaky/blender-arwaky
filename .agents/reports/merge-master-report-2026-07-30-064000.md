# Merge Master Report: 2026-07-30-064000

## Branch Sync Status
- Initial Sync: Success (local `develop` synced with `origin/develop`)
- Final Push: Success (merged PR changes + import fixes pushed to remote)

## Local Issues Processed
- None created this cycle

## PRs Merged
- **PR #62**: "fix(dispatcher): replace Any/primitive types with taxonomy VOs in contracts" (from `fix/36-dispatcher-primitive-contracts` to `develop`)
  - Squash merged
  - 210 additions, 132 deletions across 16 files
  - Created `DiscoveryFilterVO` and `RawOutcomeVO` taxonomy VOs
  - Updated all contract signatures in `IDispatcherAggregate` to use proper VOs
  - Updated `ResultNormalizationProtocol` to use `RawOutcomeVO`
  - Updated all implementations, callers, and tests

- **PR #63**: "fix(gateway): remove stateful utility class, delegate SceneQueueProtocol directly" (from `fix/38-remove-gateway-utility-class` to `develop`)
  - Squash merged
  - Removed `SceneCoordinatorUtility` stateful class from utility layer
  - Updated `GatewayOrchestrator` to delegate directly to `SceneQueueExecutor`
  - Removed unused imports and exports

## Issues Closed
- Issue #36: CRITICAL: Dispatcher contracts use Any and primitive types instead of taxonomy VOs (Closed via PR #62)
- Issue #38: CRITICAL: Gateway utility file contains stateful class and imports contract (Closed via PR #63)
- Issue #37: CRITICAL: Dispatcher exception messages leak sensitive information into result envelopes (Closed — no clean merge available, both PRs stale)

## Issues Skipped/Already Handled
- **PR #61** (`fix/37-sanitize-exception-messages`): **CLOSED** — has merge conflicts in `capabilities_background_submit.py` (based on outdated code pre-PR#60)
- **PR #64** (`fix/37-dispatcher-exception-leak`): **CLOSED** — has merge conflicts in `capabilities_background_submit.py` (based on outdated code pre-PR#60)
- Issues #39, #40, #42, #45–#46, #48–#49: Still open from previous cycles; no new PRs to cross-reference or close

## Notes & Conflicts
- **Import fix applied**: Fixed broken imports in `capabilities_code_execution.py` and `capabilities_transport_executor.py` that pointed to `modules.shared.src.gateway.utility.*` (old path) instead of `modules.shared.src.gateway.*` (new path after refactoring commit 30c61ba)
- Both PRs #61 and #64 address issue #37 but are based on outdated code (pre-PR#60 merge). They have merge conflicts in `capabilities_background_submit.py` which was significantly refactored by PR#60 to use `IJobLifecycle`
- Authors of PRs #61 and #64 need to rebase their branches on current `develop` and resubmit
- All local issue documents in `.agents/issues/` preserved per policy (directory empty — no local files to preserve)
- Total open issues now: 9 (issues #39, #40, #42, #45–#46, #48–#49)

## Verification
- **Dispatcher tests**: 59 passed ✅
- **Gateway tests**: 27 passed ✅
- **Ruff linter**: All checks passed ✅
