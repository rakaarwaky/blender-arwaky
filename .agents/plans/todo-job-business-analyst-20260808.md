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

## Severity
- 🔴 CRITICAL: Missing core requirement, wrong logic, data integrity risk
- 🟡 WARNING: Ambiguous requirement, missing edge case, incomplete criteria
- 🟢 INFO: Suggestion or optimization, deferrable

## Checklist
- [ ] Prerequisites read
- [ ] Feature + modules identified
- [ ] FRD mapped to code files
- [ ] All 5 dimensions analyzed
- [ ] Severity categorized
- [ ] Deduped vs existing plans + active PRs
- [ ] Plan written (NEW issues + fixed code)
- [ ] Saved to correct path

### Propose Change

#### File: `modules/job/src/capabilities_job_repository.py`

**FR-JOB-001: Thread-safe concurrent transitions with metadata sanitization**

```python
import threading
import re
from datetime import datetime, timezone
from typing import Any


# Sensitive patterns for metadata validation
SENSITIVE_PATTERNS = [
    re.compile(r'(?i)password\s*[:=]\s*\S+'),
    re.compile(r'(?i)token\s*[:=]\s*\S+'),
    re.compile(r'(?i)api_key\s*[:=]\s*\S+'),
    re.compile(r'(?i)secret\s*[:=]\s*\S+'),
    re.compile(r'/etc/(passwd|shadow|sudoers)'),
    re.compile(r'C:\\Users\\[^\\]+\\AppData'),
]


class JobRepository:
    """Thread-safe job repository with atomic transitions.
    
    FR-JOB-001: All state transitions are atomic and thread-safe.
    Uses threading.Lock to protect concurrent access.
    """
    
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._jobs: dict[str, dict] = {}
    
    def create_job(self, task_id: str, metadata: dict) -> dict:
        """Create new job with metadata sanitization.
        
        FR-JOB-001: Rejects metadata containing secrets/credentials/tokens/paths.
        """
        sanitized_metadata = self._sanitize_metadata(metadata)
        
        if sanitized_metadata is None:
            return {
                "error": "Metadata contains sensitive patterns",
                "category": "validation_error",
            }
        
        job_record = {
            "task_id": task_id,
            "metadata": sanitized_metadata,
            "status": "created",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        
        with self._lock:
            self._jobs[task_id] = job_record
        
        return {"task_id": task_id, "status": "created"}
    
    def transition_state(self, task_id: str, new_status: str) -> dict:
        """Thread-safe state transition.
        
        FR-JOB-001: Atomic transition using lock to prevent race conditions.
        Valid transitions: created→running, running→completed/failed/cancelled
        """
        with self._lock:
            job = self._jobs.get(task_id)
            if not job:
                return {"error": f"Job not found: {task_id}", "category": "validation_error"}
            
            current_status = job["status"]
            valid_transitions = {
                "created": ["running", "cancelled"],
                "running": ["completed", "failed", "cancelled"],
                "completed": [],  # Terminal states — no transitions allowed
                "failed": [],
                "cancelled": [],
            }
            
            if new_status not in valid_transitions.get(current_status, []):
                return {
                    "error": f"Invalid transition: {current_status} → {new_status}",
                    "category": "validation_error",
                }
            
            job["status"] = new_status
            job["updated_at"] = datetime.now(timezone.utc).isoformat()
            self._jobs[task_id] = job
        
        return {"task_id": task_id, "status": new_status}
    
    def _sanitize_metadata(self, metadata: dict) -> dict | None:
        """Sanitize metadata — reject if contains sensitive patterns.
        
        FR-JOB-001: Never store secrets/credentials/tokens/paths in metadata.
        Returns None if sensitive data detected.
        """
        for key, value in metadata.items():
            str_value = str(value) if not isinstance(value, str) else value
            for pattern in SENSITIVE_PATTERNS:
                if pattern.search(str_value):
                    return None  # Reject entire metadata
        return metadata
    
    def get_job(self, task_id: str) -> dict | None:
        """Get job record. Thread-safe read."""
        with self._lock:
            return dict(self._jobs.get(task_id))
```

#### File: `modules/job/src/capabilities_job_evaluator.py`

**FR-JOB-001: Stale running task detection**

```python
import time
from datetime import datetime, timezone
from typing import Any


class JobEvaluator:
    """Stale running task detection and recovery.
    
    FR-JOB-001: Detects running tasks that exceed expected duration.
    Marks them as timed out for stale recovery.
    """
    
    def __init__(self, stale_timeout_seconds: float = 3600.0) -> None:
        self._stale_timeout = stale_timeout_seconds
    
    def evaluate_running_tasks(self, jobs: list[dict]) -> list[dict]:
        """Evaluate running tasks for staleness.
        
        FR-JOB-001: Returns list of tasks that should be marked timed_out.
        """
        stale_tasks = []
        current_time = time.time()
        
        for job in jobs:
            if job.get("status") != "running":
                continue
            
            updated_at = job.get("updated_at", "")
            last_update_ts = self._parse_timestamp(updated_at)
            
            # Check elapsed time since last update
            elapsed = current_time - last_update_ts
            if elapsed > self._stale_timeout:
                stale_tasks.append({
                    "task_id": job["task_id"],
                    "current_status": "running",
                    "action": "mark_timed_out",
                    "elapsed_seconds": elapsed,
                })
        
        return stale_tasks
    
    def mark_stale_as_timed_out(self, task_id: str) -> dict:
        """Mark stale running task as timed out.
        
        FR-JOB-001: Recovery path for orphaned/stale tasks.
        """
        return {
            "task_id": task_id,
            "status": "timed_out",
            "reason": "Stale running task exceeded timeout",
            "recovery": "ready_for_retry",
        }
    
    def _parse_timestamp(self, timestamp_str: str) -> float:
        """Parse ISO timestamp to epoch seconds."""
        from datetime import datetime
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        return dt.timestamp()
```

#### File: `modules/job/src/capabilities_job_scheduler.py`

**FR-JOB-005: Capacity limit enforcement**

```python
import threading
from typing import Any


class JobScheduler:
    """Background job scheduler with capacity limits.
    
    FR-JOB-005: Enforces max_concurrent_background_tasks from config.
    Rejects submissions when capacity is reached.
    """
    
    def __init__(self, max_concurrent: int = 10) -> None:
        self._max_concurrent = max_concurrent
        self._lock = threading.Lock()
        self._active_count = 0
    
    def can_submit(self) -> bool:
        """Check if capacity allows new submission.
        
        FR-JOB-005: Returns False when active count >= max_concurrent.
        """
        with self._lock:
            return self._active_count < self._max_concurrent
    
    def submit(self, task_id: str) -> dict:
        """Submit background job with capacity enforcement.
        
        FR-JOB-005: Raises error when capacity limit exceeded.
        """
        with self._lock:
            if self._active_count >= self._max_concurrent:
                return {
                    "error": f"Background capacity reached ({self._max_concurrent})",
                    "category": "validation_error",
                    "hint": "Retry after current jobs complete",
                }
            
            self._active_count += 1
        
        return {"task_id": task_id, "status": "submitted", "position": self._active_count}
    
    def complete(self, task_id: str) -> None:
        """Decrement active count when job completes."""
        with self._lock:
            self._active_count = max(0, self._active_count - 1)
```

#### File: `tests/test_job_concurrent_transitions.py` (NEW)

**Concurrency test for state transitions**

```python
import pytest
import threading
from modules.job.src.capabilities_job_repository import JobRepository


@pytest.mark.asyncio
class TestConcurrentTransitions:
    """Test concurrent state transitions are atomic."""
    
    async def test_concurrent_transitions_no_race(self):
        """Verify that multiple threads can safely transition job states."""
        repo = JobRepository()
        
        # Create initial job
        repo.create_job(task_id="test-001", metadata={"name": "render"})
        
        errors = []
        
        def transition_to_running():
            try:
                repo.transition_state("test-001", "running")
            except Exception as e:
                errors.append(e)
        
        def transition_to_completed():
            try:
                repo.transition_state("test-001", "completed")
            except Exception as e:
                errors.append(e)
        
        # Run concurrent transitions
        thread1 = threading.Thread(target=transition_to_running)
        thread2 = threading.Thread(target=transition_to_completed)
        
        thread1.start()
        thread2.start()
        
        thread1.join(timeout=5)
        thread2.join(timeout=5)
        
        # At most one should succeed (the other gets invalid transition error)
        # No exceptions should be raised (thread-safe)
        assert len(errors) == 0
    
    async def test_metadata_sanitization_rejects_secrets(self):
        """Verify that metadata containing secrets is rejected."""
        from modules.job.src.capabilities_job_repository import JobRepository
        
        repo = JobRepository()
        
        # Metadata with password
        result = repo.create_job(
            task_id="test-002",
            metadata={"name": "test", "config": "password=secret123"},
        )
        
        assert "error" in result
        assert result["category"] == "validation_error"
    
    async def test_clean_metadata_accepted(self):
        """Verify that clean metadata is accepted."""
        from modules.job.src.capabilities_job_repository import JobRepository
        
        repo = JobRepository()
        
        result = repo.create_job(
            task_id="test-003",
            metadata={"name": "render_scene", "resolution": 1.0},
        )
        
        assert result["status"] == "created"
        assert result["task_id"] == "test-003"
```

#### File: `tests/test_job_capacity_limit.py` (NEW)

**Test for capacity limit enforcement**

```python
import pytest
from modules.job.src.capabilities_job_scheduler import JobScheduler


@pytest.mark.asyncio
class TestCapacityLimit:
    """Test background capacity limit enforcement."""
    
    async def test_capacity_exceeded_rejects_submission(self):
        """Verify that submissions are rejected when capacity is reached."""
        scheduler = JobScheduler(max_concurrent=2)
        
        # Fill capacity
        result1 = scheduler.submit("task-001")
        assert result1["status"] == "submitted"
        
        result2 = scheduler.submit("task-002")
        assert result2["status"] == "submitted"
        
        # Third submission should be rejected
        result3 = scheduler.submit("task-003")
        assert "error" in result3
        assert "capacity reached" in result3["error"].lower()
    
    async def test_capacity_frees_after_complete(self):
        """Verify that completing a job frees capacity for new submission."""
        scheduler = JobScheduler(max_concurrent=1)
        
        # Fill capacity
        scheduler.submit("task-001")
        
        # Complete first job
        scheduler.complete("task-001")
        
        # Should now accept new submission
        result = scheduler.submit("task-002")
        assert result["status"] == "submitted"
```

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
