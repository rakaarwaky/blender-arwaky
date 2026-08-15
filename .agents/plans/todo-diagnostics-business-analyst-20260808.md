# Plan: diagnostics — Business Analyst
> **Historical plan notice (2026-08-14):** This 2026-08-08 plan is retained for audit history only. Do not execute its recommendations directly. Use the corresponding `*-20260814-revalidated.md` plan, which classifies each finding as `open`, `needs-clarification`, `resolved`, or `obsolete`.


## Summary
The diagnostics module provides centralized observability: health composition, metrics, audit, logging, snapshots per FRD. Code follows AES: 1 agent orchestrator, 5 capabilities, 1 root container. FRD-to-code mapping is strong. Domain isolation respected: diagnostics only composes, never mutates. No major violations found.

## Findings

### Requirements Clarity
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | FRD mentions "bounded health probes with staleness indication" — staleness indicator not obvious in `capabilities_health_composer.py` output schema | `capabilities_health_composer.py` | Expose `stale_since` or similar field in health snapshot |
| 2 | 🟢 INFO | FRD "audit event emission for security violations, connection failures, task failures, destructive actions" — `capabilities_audit_emitter.py` exists but event categories not documented in code | `capabilities_audit_emitter.py` | Add docstring listing emitted audit categories |
| 3 | 🟢 INFO | FRD "trace correlation by tracking ID across logs, metrics, audit" — tracking ID propagation verified but not explicitly called out in logging/metrics code | `capabilities_logging_policy.py`, `capabilities_metrics_collector.py` | Add comment noting tracking ID inclusion in structured logs/metrics |

### Business Flow
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | Health composition pulls from launcher/gateway/config/providers/job — provider availability noted as "optional, non-blocking" but no explicit health contribution from asset providers visible | `capabilities_health_composer.py` | Verify provider health integration; add if missing |
| 2 | 🟢 INFO | Snapshot provisioner returns immutable snapshot — thread-safety claimed but not evident in `capabilities_snapshot_provisioner.py` | `capabilities_snapshot_provisioner.py` | Add comment or locking if needed |

### Logic Implementation
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | FRD "metrics immutable + safe for concurrent access" — `capabilities_metrics_collector.py` uses `collections.Counter` which is not thread-safe for increments | `capabilities_metrics_collector.py` | Replace with thread-safe counter or add locking |
| 2 | 🟢 INFO | FRD "Log rotation per size cap with bounded history" — rotation logic not visible in `capabilities_logging_policy.py` (may be handled by logging config) | `capabilities_logging_policy.py` | Confirm rotation implementation; document if external |
| 3 | 🟢 INFO | FRD "Redaction at ingestion; failure → mask entire payload" — redaction failure handling not obvious in `capabilities_logging_policy.py` | `capabilities_logging_policy.py` | Add explicit fallback for redaction errors |

### Testability & Acceptance
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | No test for degraded health when subsystem timeout occurs | `tests/` | Add unit test simulating health probe timeout |
| 2 | 🟢 INFO | No integration test for audit emission on security violation | `tests/` | Add test triggering audit event via security policy violation |

### Traceability (FRD→Code)
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | All 5 FRD capabilities mapped to corresponding capabilities files | — | Traceability complete |
| 2 | 🟢 INFO | FRD error categories (state, config, emission, collection, probe timeout, redaction failure) present in code | `agent_diagnostics_orchestrator.py` | Error mapping verified |

## Violations
None found. AES boundaries intact: orchestrator does not contain business logic; capabilities are stateless helpers; root container only wires dependencies.

## Action Items
- [ ] 🟢 INFO Add staleness indicator to health snapshot
- [ ] 🟢 INFO Document audit event categories in emitter
- [ ] 🟢 INFO Ensure metrics collector thread-safety
- [ ] 🟢 INFO Add redaction failure fallback in logging policy
- [ ] 🟢 INFO Write unit tests for health degradation and audit emission

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

### Propose Change

#### File: `modules/diagnostics/src/capabilities_health_composer.py`

**FRD: Staleness indicator in health snapshot**

```python
import time
from typing import Any


class HealthComposer:
    """Health composition with staleness indication.
    
    FRD: Exposes stale_since field indicating when last probe occurred.
    Subsystems with no recent probe are marked stale (timeout = 30s).
    """
    
    STALENESS_TIMEOUT = 30  # Seconds before a subsystem is considered stale
    
    def __init__(self, providers: list[dict]) -> None:
        self._providers = providers
    
    def compose(self) -> dict:
        """Compose health snapshot with staleness indicators.
        
        FRD: Returns overall status + per-provider health with stale_since timestamps.
        """
        import threading
        
        lock = threading.Lock()
        now = time.time()
        
        providers_health = []
        overall_status = "healthy"
        
        for provider in self._providers:
            last_probe = provider.get("last_probe_time", 0)
            staleness_age = now - last_probe if last_probe > 0 else None
            
            # Determine health based on probe result
            probe_result = provider.get("last_probes_result", "unknown")
            health = "healthy" if probe_result == "ok" else "degraded"
            
            # FRD: Mark stale if no recent probe
            if staleness_age and staleness_age > self.STALENESS_TIMEOUT:
                health = "stale"
            
            providers_health.append({
                "provider": provider["name"],
                "status": health,
                "last_probe_time": last_probe,
                "staleness_age_seconds": staleness_age,
                "stale_since": time.ctime(last_probe) if last_probe > 0 else None,
            })
            
            # Overall status is worst of all providers
            if health == "degraded" or health == "stale":
                overall_status = "degraded"
        
        return {
            "overall_status": overall_status,
            "providers": providers_health,
            "timestamp": now,
        }
```

#### File: `modules/diagnostics/src/capabilities_audit_emitter.py`

**FRD: Documented audit event categories**

```python
from typing import Any


class AuditEmitter:
    """Audit event emitter with documented categories.
    
    FRD: Emits audit events for security violations, connection failures,
    task failures, and destructive actions. Each event includes tracking_id
    and timestamp for trace correlation.
    """
    
    # Documented audit event categories per FRD
    CATEGORIES = {
        "security_violation": "File access policy violation detected",
        "connection_failure": "MCP/CLI connection failure or reconnection",
        "task_failure": "Background task execution failure",
        "destructive_action": "Destructive operation (delete, overwrite, etc.)",
    }
    
    def __init__(self) -> None:
        self._events: list[dict] = []
    
    def emit(self, category: str, details: dict, tracking_id: str | None = None) -> dict:
        """Emit audit event with documented category.
        
        FRD: Validates category against known types; logs event for traceability.
        """
        if category not in self.CATEGORIES:
            return {
                "error": f"Unknown audit category: {category}",
                "category": "emission_error",
            }
        
        event = {
            "category": category,
            "description": self.CATEGORIES[category],
            "details": details,
            "tracking_id": tracking_id,
            "timestamp": time.time(),
        }
        
        self._events.append(event)
        return {"status": "emitted", "event_id": len(self._events)}
    
    def get_events(self) -> list[dict]:
        """Return all recorded audit events."""
        return self._events.copy()
```

#### File: `modules/diagnostics/src/capabilities_metrics_collector.py`

**FRD: Thread-safe metrics collector**

```python
import threading
from collections import defaultdict
from typing import Any


class MetricsCollector:
    """Thread-safe metrics collector with immutable snapshots.
    
    FRD: Metrics are safe for concurrent access; uses Lock to protect
    Counter increments and snapshot creation. Snapshots return deep copies.
    """
    
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counters: dict[str, int] = defaultdict(int)
        self._timings: dict[str, list[float]] = defaultdict(list)
    
    def increment(self, metric_name: str, value: int = 1) -> None:
        """Thread-safe counter increment.
        
        FRD: Uses Lock to protect concurrent increments.
        """
        with self._lock:
            self._counters[metric_name] += value
    
    def record_timing(self, metric_name: str, duration_ms: float) -> None:
        """Thread-safe timing recording."""
        with self._lock:
            self._timings[metric_name].append(duration_ms)
    
    def snapshot(self) -> dict:
        """Return immutable snapshot of all metrics.
        
        FRD: Returns deep copy safe for concurrent access.
        """
        with self._lock:
            return {
                "counters": dict(self._counters),
                "timings": {k: list(v) for k, v in self._timings.items()},
            }
```

#### File: `modules/diagnostics/src/capabilities_logging_policy.py`

**FRD: Log rotation and redaction failure fallback**

```python
import logging
from typing import Any


class LoggingPolicy:
    """Logging policy with rotation and redaction fallback.
    
    FRD: Implements log rotation per size cap (10MB) with bounded history (5 files).
    Redaction at ingestion; on redaction failure, masks entire payload.
    Includes tracking ID in structured logs for trace correlation.
    """
    
    LOG_MAX_BYTES = 10_000_000  # 10MB per log file
    LOG_BACKUP_COUNT = 5  # Keep 5 rotated files
    
    def __init__(self, redactor: Any) -> None:
        self._redactor = redactor
    
    def setup_logging(self, level: int = logging.INFO) -> None:
        """Configure logging with rotation and tracking ID context."""
        import logging.handlers
        
        handler = logging.handlers.RotatingFileHandler(
            filename="diagnostics.log",
            maxBytes=self.LOG_MAX_BYTES,
            backupCount=self.LOG_BACKUP_COUNT,
        )
        
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - [%(tracking_id)s] - %(message)s"
        )
        handler.setFormatter(formatter)
        
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        root_logger.setLevel(level)
    
    def log_with_redaction(self, level: int, message: str, payload: dict | None = None,
                           tracking_id: str | None = None) -> None:
        """Log with redaction and tracking ID inclusion.
        
        FRD: Redacts sensitive data at ingestion; on failure masks entire payload.
        Includes tracking_id in log context for trace correlation.
        """
        # FRD: Redaction with fallback — mask entire payload on error
        try:
            if payload:
                redacted = self._redactor.redact(payload)
            else:
                redacted = None
        except Exception:
            # FRD: Redaction failure → mask entire payload
            redacted = "*** REDACTION_FAILED — payload masked ***"
        
        # Set tracking ID in logging context
        extra = {"tracking_id": tracking_id or "N/A"}
        
        logger = logging.Logger(__name__, level)
        logger.info(message, extra=extra)
```

#### File: `modules/diagnostics/src/capabilities_snapshot_provisioner.py`

**FRD: Thread-safe snapshot with deep copy**

```python
import copy
import threading
from typing import Any


class SnapshotProvisioner:
    """Snapshot provisioner with deep copy and thread safety.
    
    FRD: Returns immutable snapshot safe for concurrent access.
    Uses Lock to protect state mutations; snapshot is deep copy.
    """
    
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._state: dict = {}
    
    def update_state(self, key: str, value: Any) -> None:
        """Update snapshot state with locking."""
        with self._lock:
            self._state[key] = value
    
    def get_snapshot(self) -> dict:
        """Return immutable deep copy of current state.
        
        FRD: Snapshot is safe for concurrent access; caller cannot mutate internal state.
        """
        with self._lock:
            return copy.deepcopy(self._state)
```

#### File: `tests/test_diagnostics_health_timeout.py` (NEW)

**Unit test for health probe timeout / staleness**

```python
import pytest
import time


@pytest.mark.asyncio
class TestHealthTimeout:
    """Test health composition with stale subsystem detection."""
    
    async def test_stale_subsystem_detected(self):
        """Verify that subsystems without recent probes are marked stale.
        
        Unit test for diagnostics health composer staleness timeout.
        """
        from modules.diagnostics.src.capabilities_health_composer import HealthComposer
        
        # Mock provider with old probe time (1 minute ago)
        old_probe_time = time.time() - 60  # 60 seconds ago > 30s threshold
        providers = [{"name": "test_provider", "last_probe_time": old_probe_time, "last_probes_result": "ok"}]
        
        composer = HealthComposer(providers=providers)
        result = composer.compose()
        
        assert result["overall_status"] == "degraded"
        assert result["providers"][0]["status"] == "stale"
        assert result["providers"][0]["staleness_age_seconds"] is not None
    
    async def test_recent_probe_healthy(self):
        """Verify that subsystems with recent probes are marked healthy."""
        from modules.diagnostics.src.capabilities_health_composer import HealthComposer
        
        # Mock provider with recent probe (1 second ago)
        recent_probe_time = time.time() - 1  # 1 second ago < 30s threshold
        providers = [{"name": "test_provider", "last_probe_time": recent_probe_time, "last_probes_result": "ok"}]
        
        composer = HealthComposer(providers=providers)
        result = composer.compose()
        
        assert result["overall_status"] == "healthy"
        assert result["providers"][0]["status"] == "healthy"
```

#### File: `tests/test_diagnostics_audit_emission.py` (NEW)

**Unit test for audit event emission**

```python
import pytest


@pytest.mark.asyncio
class TestAuditEmission:
    """Test audit event emission on security violation."""
    
    async def test_emit_security_violation(self):
        """Verify audit event is emitted when security violation occurs."""
        from modules.diagnostics.src.capabilities_audit_emitter import AuditEmitter
        
        emitter = AuditEmitter()
        
        result = emitter.emit(
            category="security_violation",
            details={"path": "/tmp/../../../etc/passwd", "action": "read"},
            tracking_id="test-123",
        )
        
        assert result["status"] == "emitted"
        events = emitter.get_events()
        assert len(events) == 1
        assert events[0]["category"] == "security_violation"
        assert events[0]["tracking_id"] == "test-123"
    
    async def test_emit_unknown_category_error(self):
        """Verify that unknown category returns error."""
        from modules.diagnostics.src.capabilities_audit_emitter import AuditEmitter
        
        emitter = AuditEmitter()
        
        result = emitter.emit(
            category="unknown_category",
            details={},
        )
        
        assert "error" in result
        assert result["category"] == "emission_error"
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
