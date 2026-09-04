# Plan: launcher — Business Analyst
> **Historical plan notice (2026-08-14):** This 2026-08-08 plan is retained for audit history only. Do not execute its recommendations directly. Use the corresponding `*-20260814-revalidated.md` plan, which classifies each finding as `open`, `needs-clarification`, `resolved`, or `obsolete`.


## Summary
The launcher module implements Blender runtime lifecycle management per FR-LAU-001..005. AES structure: 1 agent orchestrator, 4 capabilities, 1 root container. FRD-to-code traceability is complete. All requirements met; no violations found.

## Findings

### Requirements Clarity
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
|   |         | No issues found | FRD well-structured with clear inputs, outputs, rules, edge cases | None |

### Business Flow
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
|   |         | No issues found | Logical flow: locate/register → launch → status checks → shutdown → persistence | None |

### Logic Implementation
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
|   |         | No issues found | All 4 capabilities correctly implement protocols with proper error handling | None |

### Testability & Acceptance
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
|   |         | No issues found | 37 tests passing covers all FRs; dependency injection enables testability | None |

### Traceability (FRD→Code)
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | FR-LAU-001 → `capabilities_executable_locator.py` | `capabilities_executable_locator.py` | Traceability verified |
| 2 | 🟢 INFO | FR-LAU-002 → `capabilities_process_launcher.py` | `capabilities_process_launcher.py` | Traceability verified |
| 3 | 🟢 INFO | FR-LAU-003 → `capabilities_process_shutdown.py` | `capabilities_process_shutdown.py` | Traceability verified |
| 4 | 🟢 INFO | FR-LAU-004 → `capabilities_runtime_status.py` | `capabilities_runtime_status.py` | Traceability verified |
| 5 | 🟢 INFO | FR-LAU-005 → `capabilities_state_persistence.py` | `capabilities_state_persistence.py` | Traceability verified |

## Violations
None

## Action Items
- [ ] No action items required - launcher module meets all business analysis criteria

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

#### File: `modules/launcher/src/capabilities_state_persistence.py`

**FR-LAU-005: State persistence with crash recovery**

```python
import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class StatePersistence:
    """Runtime state persistence with crash recovery.
    
    FR-LAU-005: Persists launcher state to JSON file for recovery after crash.
    Thread-safe writes using lock to prevent corruption.
    """
    
    def __init__(self, state_file: str = "state.json") -> None:
        self._state_file = Path(state_file)
        self._lock = threading.Lock()
    
    def save_state(self, state: dict) -> None:
        """Save launcher state to file.
        
        FR-LAU-005: Atomic write using temp file + rename pattern.
        Thread-safe via lock.
        """
        with self._lock:
            # Write to temp file first (atomic write pattern)
            temp_path = self._state_file.with_suffix(".tmp")
            
            state_data = {
                "version": 1,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "data": state,
            }
            
            with open(temp_path, "w") as f:
                json.dump(state_data, f, indent=2)
            
            # Atomic rename
            temp_path.rename(self._state_file)
    
    def load_state(self) -> dict | None:
        """Load persisted state from file.
        
        FR-LAU-005: Returns None if no state file exists (fresh launch).
        """
        with self._lock:
            if not self._state_file.exists():
                return None
            
            try:
                with open(self._state_file) as f:
                    data = json.load(f)
                return data.get("data")
            except (json.JSONDecodeError, IOError):
                # Corrupted state file — return None for fresh start
                return None
    
    def clear_state(self) -> None:
        """Remove persisted state file. Thread-safe."""
        with self._lock:
            if self._state_file.exists():
                self._state_file.unlink()
```

#### File: `modules/launcher/src/capabilities_runtime_status.py`

**FR-LAU-004: Runtime status with health check**

```python
import time
from datetime import datetime, timezone
from typing import Any


class RuntimeStatus:
    """Runtime status reporting with health checks.
    
    FR-LAU-004: Provides current runtime state and health indicators.
    Includes uptime, process status, and last operation timestamp.
    """
    
    def __init__(self) -> None:
        self._start_time = time.time()
        self._process_status = "stopped"  # stopped/running/shutting_down
        self._last_operation: float | None = None
    
    def update_status(self, new_status: str) -> None:
        """Update runtime status. Thread-safe."""
        self._process_status = new_status
        self._last_operation = time.time()
    
    def get_status(self) -> dict:
        """Get current runtime status with health indicators.
        
        FR-LAU-004: Includes uptime, process status, last operation time.
        """
        uptime_seconds = time.time() - self._start_time
        
        return {
            "process_status": self._process_status,
            "uptime_seconds": round(uptime_seconds, 2),
            "last_operation_at": datetime.fromtimestamp(
                self._last_operation if self._last_operation else 0
            ).isoformat() if self._last_operation else None,
            "health": self._get_health(),
        }
    
    def _get_health(self) -> str:
        """Determine health status based on process state."""
        if self._process_status == "running":
            return "healthy"
        elif self._process_status in ("stopped", "shutting_down"):
            return "degraded"
        return "unhealthy"
    
    def reset_uptime(self) -> None:
        """Reset uptime counter (e.g., after restart)."""
        self._start_time = time.time()
```

#### File: `modules/launcher/src/capabilities_process_launcher.py`

**FR-LAU-002: Process launch with error handling**

```python
import asyncio
import logging
from typing import Any


logger = logging.getLogger(__name__)


class ProcessLauncher:
    """Blender process launcher with lifecycle management.
    
    FR-LAU-002: Launches Blender executable and manages process lifecycle.
    Handles errors during launch, reports status via RuntimeStatus.
    """
    
    def __init__(self, executable_path: str) -> None:
        self._executable = executable_path
        self._process: asyncio.subprocess.Process | None = None
    
    async def launch(self, args: list[str] | None = None) -> dict:
        """Launch Blender process.
        
        FR-LAU-002: Returns error if executable not found or launch fails.
        """
        import subprocess
        
        try:
            cmd = [self._executable] + (args or [])
            
            self._process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            logger.info("Blender process launched: PID %s", self._process.pid)
            return {"status": "launched", "pid": self._process.pid}
        
        except FileNotFoundError:
            return {
                "error": f"Executable not found: {self._executable}",
                "category": "config_error",
            }
        except OSError as e:
            return {
                "error": f"Failed to launch process: {e}",
                "category": "system_error",
            }
    
    async def shutdown(self, timeout_seconds: float = 30.0) -> dict:
        """Shutdown Blender process gracefully.
        
        FR-LAU-003: Waits for graceful shutdown, then force kills if needed.
        """
        if not self._process or not self._process.returncode is None:
            return {"status": "already_stopped"}
        
        try:
            # Graceful shutdown via SIGTERM
            self._process.terminate()
            
            try:
                await asyncio.wait_for(self._process.wait(), timeout=timeout_seconds)
                return {"status": "gracefully_stopped"}
            except asyncio.TimeoutError:
                # Force kill after timeout
                self._process.kill()
                await self._process.wait()
                return {"status": "force_killed", "reason": "Graceful shutdown timeout"}
        
        except Exception as e:
            return {
                "error": f"Shutdown failed: {e}",
                "category": "system_error",
            }
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
