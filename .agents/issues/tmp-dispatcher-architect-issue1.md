# CRITICAL: Dispatcher sync dispatch returns fake success when no executor is wired

## Summary

`SyncDispatchExecutor.dispatch_sync()` can return a successful envelope even when `self._execute is None`. Instead of executing the owning feature, it synthesizes a fake `"dispatched"` status. This violates FR-DSP-004 routing integrity and misleads CLI/MCP consumers into believing an action ran when it actually did nothing.

## Violations

- **FR-DSP-004**: Routing integrity — dispatcher must route to owning feature, not synthesize success
- **AES305**: Duplicate/fake return paths that bypass actual execution

## Current Code Issue

```python
# modules/dispatcher/src/capabilities_sync_dispatch.py:dispatch_sync()
if self._execute is None:
    return UnifiedResultEnvelopeVO.success_envelope(
        message="Action dispatched",
        tracking_id=tracking_id,
        data={"status": "dispatched"},  # FAKE SUCCESS
    )
```

## Proposed Fix

```python
class SyncDispatchExecutor(SyncDispatchProtocol):
    def __init__(self, execute_action: ActionExecutorProtocol) -> None:
        if execute_action is None:
            raise ValueError("SyncDispatchExecutor requires a non-null action executor")
        self._execute = execute_action

    def dispatch_sync(self, request: ActionCommandVO) -> UnifiedResultEnvelopeVO:
        tracking_id = request.validated_tracking_id or request.tracking_id or ""

        try:
            result = self._execute.execute_action(
                request.action_name,
                dict(request.parameters),
            )
            return UnifiedResultEnvelopeVO.success_envelope(
                message=f"Action {request.action_name} dispatched successfully",
                tracking_id=tracking_id,
                data=result if isinstance(result, dict) else {"result": "completed"},
            )
        except Exception as e:
            logger.exception("Dispatch failed")
            return UnifiedResultEnvelopeVO.error_envelope(
                message="Action execution failed",
                tracking_id=tracking_id,
                error_category=DispatchErrorCategory.EXECUTION,
            )
```

## Labels

security, critical, bug
