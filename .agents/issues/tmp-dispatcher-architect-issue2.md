# CRITICAL: Dispatcher background submit creates synthetic job IDs bypassing Job feature

## Summary

`BackgroundSubmitExecutor.submit_background()` creates a fake job ID using `uuid.uuid4()` when no `job_tracker` is wired. This bypasses the Job feature and violates FR-DSP-005 atomic submission through the job feature. Production code should never create fake task references.

## Violations
- **FR-DSP-005**: Atomic submission — background jobs must go through Job feature, not synthetic UUIDs
- **AES402**: Contract uses primitive types instead of taxonomy VOs

## Current Code Issue
```python
# modules/dispatcher/src/capabilities_background_submit.py:submit_background()
try:
    job_id = str(uuid.uuid4())  # FAKE JOB ID
    status = {"job_id": job_id, "status": "submitted"}
    return UnifiedResultEnvelopeVO.success_envelope(...)
```

## Proposed Fix
```python
class BackgroundSubmitExecutor(BackgroundSubmitProtocol):
    def __init__(self, job_tracker: JobTrackerProtocol) -> None:
        if job_tracker is None:
            raise ValueError("BackgroundSubmitExecutor requires a real job tracker")
        self._job_tracker = job_tracker

    def submit_background(self, request: ActionCommandVO) -> UnifiedResultEnvelopeVO:
        tracking_id = request.validated_tracking_id or request.tracking_id or ""

        try:
            job_id, status = self._job_tracker.track_new_task(
                operation_type=request.action_name,
                metadata={"tracking_id": tracking_id},
            )
            return UnifiedResultEnvelopeVO.success_envelope(
                message="Background task submitted successfully",
                tracking_id=tracking_id,
                data={"job_id": job_id, "status": status},
            )
        except Exception as e:
            logger.exception("Background submission failed")
            return UnifiedResultEnvelopeVO.error_envelope(
                message="Background submission failed",
                tracking_id=tracking_id,
                error_category=DispatchErrorCategory.EXECUTION,
            )
```

## Labels
critical, bug
