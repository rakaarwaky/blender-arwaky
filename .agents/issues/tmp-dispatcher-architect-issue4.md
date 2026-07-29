# CRITICAL: Dispatcher exception messages leak sensitive information into result envelopes

## Summary

Exception messages are placed directly into result envelopes without sanitization. Examples include `f"Action '{action_name}' failed: {e}"`, `f"Job creation failed: {e}"`, and `safe_error_envelope(str(e))`. Exception text may contain paths, secrets, stack-derived strings, or provider details, conflicting with FR-DSP-006 security requirements.

## Violations
- **FR-DSP-006**: Security — exception messages must be sanitized before envelope construction
- **AES305**: Duplicated unsafe error message handling across capabilities

## Current Code Issue
```python
# modules/dispatcher/src/capabilities_sync_dispatch.py:dispatch_sync()
except Exception as e:
    logger.exception("Dispatch failed")
    return UnifiedResultEnvelopeVO.error_envelope(
        message=f"Action '{action_name}' failed: {e}",  # LEAKS EXCEPTION TEXT
        tracking_id=tracking_id,
        error_category="execution_error",
    )

# modules/dispatcher/src/agent_dispatcher_orchestrator.py:execute_action()
except Exception as e:
    logger.exception("Unexpected dispatch failure")
    return UnifiedResultEnvelopeVO.error_envelope(
        message=f"Action execution failed unexpectedly: {e}",  # LEAKS
        tracking_id=request.validated_tracking_id,
        error_category="execution_error",
    )
```

## Proposed Fix
```python
# New shared taxonomy: modules/shared/src/dispatcher/taxonomy_dispatch_error.py
class DispatchErrorCategory:
    VALIDATION = "validation_error"
    NOT_FOUND = "not_found_error"
    EXECUTION = "execution_error"
    CAPACITY = "capacity_error"
    UNSUPPORTED = "unsupported_error"
    TIMEOUT = "timeout_error"
    CONFIRMATION = "confirmation_error"
    REGISTRATION = "registration_error"

class DispatchError(Exception):
    def __init__(self, message: str, error_category: str = DispatchErrorCategory.EXECUTION) -> None:
        super().__init__(message)
        self.error_category = error_category

# Updated orchestrator
class DispatcherOrchestrator(IDispatcherAggregate):
    @staticmethod
    def _safe_message(error: Exception) -> str:
        # Do not return raw exception text to consumers.
        # Keep detailed diagnostics in logs only.
        return "Action request could not be processed"

    def execute_action(self, request: ActionCommandVO) -> UnifiedResultEnvelopeVO:
        try:
            validated = self.validate_request(request)
            if validated.resolved_metadata.get("background_eligibility_flag", False):
                return self.submit_background(validated)
            return self.dispatch_sync(validated)
        except DispatchError as e:
            logger.error("Dispatch rejected: %s", e)
            return UnifiedResultEnvelopeVO.error_envelope(
                message=self._safe_message(e),
                tracking_id=request.validated_tracking_id,
                error_category=e.error_category,
            )
        except Exception as e:
            logger.exception("Unexpected dispatch failure")
            return UnifiedResultEnvelopeVO.error_envelope(
                message="Action execution failed unexpectedly",
                tracking_id=request.validated_tracking_id,
                error_category=DispatchErrorCategory.EXECUTION,
            )

# Updated sync dispatch
class SyncDispatchExecutor(SyncDispatchProtocol):
    def dispatch_sync(self, request: ActionCommandVO) -> UnifiedResultEnvelopeVO:
        tracking_id = request.validated_tracking_id or request.tracking_id or ""
        try:
            result = self._execute.execute_action(request.action_name, dict(request.parameters))
            return UnifiedResultEnvelopeVO.success_envelope(
                message=f"Action {request.action_name} dispatched successfully",
                tracking_id=tracking_id,
                data=result if isinstance(result, dict) else {"result": "completed"},
            )
        except Exception:
            logger.exception("Dispatch failed")
            return UnifiedResultEnvelopeVO.error_envelope(
                message="Action execution failed",
                tracking_id=tracking_id,
                error_category=DispatchErrorCategory.EXECUTION,
            )
```

## Labels
critical, security, bug
