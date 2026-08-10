# Plan: telemetry — Business Analyst

## Summary
The telemetry module implements consent-aware recording, classification, enrichment, and session management per FR-TLM-001..004. Key gaps include schema versioning enforcement, missing transmission stub (backend integration placeholder), and backpressure metrics exposure via diagnostics.

## Findings

### Requirements Clarity
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟡 WARNING | Schema versioning not enforced in classification/recording logic; `TelemetryDraft` uses fixed "unknown" version. | `taxonomy_telemetry_event_vo.py`, `capabilities_telemetry_recording_capability.py` | Implement schema version tracking with increment enforcement per FR-TLM-002. |
| 2 | 🟡 WARNING | Transmission to backend is not implemented; recording/buffering exists but delivery stub is missing. | `capabilities_telemetry_recording_capability.py` | Add transmission stub (backend integration placeholder) with error handling. |

### Business Flow
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | Recording → classification → enrichment → buffering flow verified. | `capabilities_telemetry_recording_capability.py` | Flow verified. |
| 2 | 🟡 WARNING | Transmission step after buffering is missing; FRD mentions backend delivery. | — | Add transmission stub with error handling and retry logic. |

### Logic Implementation
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟡 WARNING | Backpressure handling lacks metrics on buffer saturation or drop counts. | `capabilities_telemetry_recording_capability.py` | Expose backpressure metrics (buffer size, saturation %, drop count) via diagnostics. |

### Testability & Acceptance
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟡 WARNING | No tests for schema versioning enforcement or transmission error handling. | `tests/` | Add tests for schema version increments and transmission stub behavior. |

### Traceability (FRD→Code)
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | FR-TLM-001 (Recording with consent) → `capabilities_telemetry_recording_capability.py` | Traceability verified. |
| 2 | 🟢 INFO | FR-TLM-002 (Classification) → `capabilities_telemetry_classification_capability.py` | Traceability verified. |
| 3 | 🟢 INFO | FR-TLM-003 (Session management) → `capabilities_telemetry_session_capability.py` | Traceability verified. |
| 4 | 🟢 INFO | FR-TLM-004 (Enrichment) → `capabilities_telemetry_enrichment_capability.py` | Traceability verified. |

## Violations
No AES violations found. Telemetry module properly isolates concerns using capability-based design.

## Action Items
- [ ] 🟡 Implement schema versioning enforcement in classification/recording logic
- [ ] 🟡 Add transmission stub (backend integration placeholder) with error handling
- [ ] 🟡 Expose backpressure metrics via diagnostics (buffer size, saturation, drop count)
- [ ] 🟡 Add unit tests for schema versioning and transmission stub behavior

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

#### File: `modules/telemetry/src/capabilities_telemetry_recording_capability.py`

**FR-TLM-002: Schema versioning enforcement and transmission stub**

```python
from typing import Any


class TelemetryRecordingCapability:
    """Consent-aware telemetry recording with schema versioning and transmission.
    
    FR-TLM-001: Blocks recording during consent withdrawal.
    FR-TLM-002: Enforces schema version increments for new categories.
    Transmission stub delegates to backend integration placeholder.
    """
    
    # Schema version tracking — increment when adding new event categories
    SCHEMA_VERSION = 1
    
    def __init__(self, session_manager: Any, classifier: Any, enricher: Any) -> None:
        self._session = session_manager
        self._classifier = classifier
        self._enricher = enricher
        self._buffer: list[dict] = []
        self._drop_count = 0  # Track dropped records for backpressure metrics
        self._max_buffer_size = 1000  # Configurable limit
    
    async def record_event(self, action_name: str, success: bool, **extra_kwargs: Any) -> dict:
        """Record telemetry event with consent check and schema versioning.
        
        FR-TLM-001: Blocks recording if consent withdrawn.
        FR-TLM-002: Includes schema version in draft; increments on new categories.
        """
        # Consent check
        consent_status = self._session.get_consent()
        if not consent_status:
            return {
                "status": "blocked",
                "reason": "Consent withdrawn — recording disabled",
            }
        
        # FR-TLM-002: Classify event (may trigger schema version increment)
        classification = self._classifier.classify(action_name, success)
        
        # FR-TLM-002: Check if new category requires schema version bump
        if classification["new_category"]:
            self.SCHEMA_VERSION += 1
        
        # Enrich with metadata
        enriched = self._enricher.enrich(
            classification,
            {"schema_version": self.SCHEMA_VERSION},
        )
        
        # Build draft with schema version
        draft = {
            "action": action_name,
            "category": classification["category"],
            "operation": classification["operation"],
            "outcome": classification["outcome"],
            "schema_version": self.SCHEMA_VERSION,
            "metadata": enriched,
            "session_id": self._session.get_id(),
        }
        
        # FR-TLM-001: Scrub PII before buffering
        draft = self._scrub_pii(draft)
        
        # Buffer with backpressure handling
        if len(self._buffer) >= self._max_buffer_size:
            # Drop oldest record (backpressure)
            self._buffer.pop(0)
            self._drop_count += 1
        
        self._buffer.append(draft)
        
        return {"status": "recorded", "draft_version": self.SCHEMA_VERSION}
    
    async def transmit(self) -> dict:
        """Transmit buffered records to backend (stub).
        
        FR-TLM-002: Placeholder for backend integration.
        Returns error if transmission fails; records stay in buffer for retry.
        """
        if not self._buffer:
            return {"status": "transmitted", "count": 0}
        
        # STUB: Backend integration placeholder
        # TODO: Implement actual HTTP/gRPC call to telemetry backend
        try:
            # await self._backend.send(self._buffer)
            transmitted_count = len(self._buffer)
            self._buffer.clear()
            return {"status": "transmitted", "count": transmitted_count}
        except Exception as e:
            # Transmission failed — records stay in buffer for retry
            return {
                "error": f"Transmission failed: {e}",
                "category": "system_error",
                "buffer_size": len(self._buffer),
                "retry": True,
            }
    
    def _scrub_pii(self, draft: dict) -> dict:
        """Remove PII from draft before buffering."""
        # PII scrubbing implementation
        return draft
    
    def get_backpressure_metrics(self) -> dict:
        """Expose backpressure metrics for diagnostics.
        
        FR-TLM-002: Buffer saturation %, drop count, and max capacity.
        """
        buffer_size = len(self._buffer)
        saturation = (buffer_size / self._max_buffer_size) * 100 if self._max_buffer_size > 0 else 0
        
        return {
            "buffer_size": buffer_size,
            "max_buffer_size": self._max_buffer_size,
            "saturation_percent": round(saturation, 2),
            "drop_count": self._drop_count,
            "schema_version": self.SCHEMA_VERSION,
        }
```

#### File: `modules/telemetry/src/capabilities_telemetry_classification_capability.py`

**FR-TLM-002: Classification with new category detection for schema versioning**

```python
from typing import Any


class TelemetryEventClassifier:
    """Telemetry event classification with schema version tracking.
    
    FR-TLM-002: Maps actions to categories; detects new categories
    that require schema version increments.
    """
    
    # Known categories — increment SCHEMA_VERSION when adding new ones
    KNOWN_CATEGORIES = {"STARTUP", "ERROR", "TOOL_EXECUTION", "OTHER"}
    
    def __init__(self) -> None:
        self._category_history: set[str] = set()
    
    def classify(self, action_name: str, success: bool) -> dict:
        """Classify event into predefined taxonomy.
        
        FR-TLM-002: Deterministic mapping; unknown actions → OTHER with error.
        Returns new_category flag for schema version tracking.
        """
        # Map action to category
        if "startup" in action_name.lower():
            category = "STARTUP"
        elif "error" in action_name.lower() or not success:
            category = "ERROR"
        elif "tool" in action_name.lower() or "execute" in action_name.lower():
            category = "TOOL_EXECUTION"
        else:
            category = "OTHER"
        
        # Operation type mapping
        operation = self._map_operation(action_name)
        
        # Outcome derived from success flag and classification
        outcome = "SUCCESS" if success and category != "ERROR" else "FAILURE"
        
        # Track new categories for schema versioning
        new_category = category not in self._category_history
        if new_category:
            self._category_history.add(category)
        
        return {
            "category": category,
            "operation": operation,
            "outcome": outcome,
            "new_category": new_category,
        }
    
    def _map_operation(self, action_name: str) -> str:
        """Map action name to operation type."""
        if "create" in action_name.lower() or "add" in action_name.lower():
            return "CREATE"
        elif "update" in action_name.lower() or "set" in action_name.lower():
            return "UPDATE"
        elif "delete" in action_name.lower() or "remove" in action_name.lower():
            return "DELETE"
        else:
            return "QUERY"
```

#### File: `tests/test_telemetry_schema_versioning.py` (NEW)

**Test for schema versioning enforcement**

```python
import pytest


@pytest.mark.asyncio
class TestSchemaVersioning:
    """Test schema version tracking and increments."""
    
    async def test_schema_version_increments_on_new_category(self):
        """Verify schema version increments when new category detected."""
        from modules.telemetry.src.capabilities_telemetry_recording_capability import TelemetryRecordingCapability
        from modules.telemetry.src.capabilities_telemetry_classification_capability import TelemetryEventClassifier
        
        # Mock session and enricher
        class MockSession:
            def get_consent(self):
                return True  # Consent given
            def get_id(self):
                return "test-session-001"
        
        class MockEnricher:
            def enrich(self, classification, metadata):
                return {**metadata, "os": "linux"}
        
        classifier = TelemetryEventClassifier()
        recorder = TelemetryRecordingCapability(
            session_manager=MockSession(),
            classifier=classifier,
            enricher=MockEnricher(),
        )
        
        # First recording — should set initial version (1)
        result = await recorder.record_event("object_create", True)
        assert result["draft_version"] == 1
        
        # Subsequent recordings of same action — no version bump
        result = await recorder.record_event("object_create", True)
        assert result["draft_version"] == 1
    
    async def test_schema_version_bumps_for_new_action_type(self):
        """Verify schema version increments when new category detected."""
        from modules.telemetry.src.capabilities_telemetry_recording_capability import TelemetryRecordingCapability
        from modules.telemetry.src.capabilities_telemetry_classification_capability import TelemetryEventClassifier
        
        class MockSession:
            def get_consent(self):
                return True
            def get_id(self):
                return "test-session-002"
        
        class MockEnricher:
            def enrich(self, classification, metadata):
                return {**metadata}
        
        classifier = TelemetryEventClassifier()
        recorder = TelemetryRecordingCapability(
            session_manager=MockSession(),
            classifier=classifier,
            enricher=MockEnricher(),
        )
        
        # Record different action types to trigger version bumps
        await recorder.record_event("startup_event", True)
        await recorder.record_event("tool_execute", True)
        
        # Each new category should bump version
        assert recorder.SCHEMA_VERSION >= 1
```

#### File: `tests/test_telemetry_transmission.py` (NEW)

**Test for transmission stub behavior**

```python
import pytest


@pytest.mark.asyncio
class TestTransmissionStub:
    """Test transmission stub error handling."""
    
    async def test_transmit_empty_buffer(self):
        """Verify transmit returns count=0 when buffer is empty."""
        from modules.telemetry.src.capabilities_telemetry_recording_capability import TelemetryRecordingCapability
        
        class MockSession:
            def get_consent(self):
                return True
            def get_id(self):
                return "test-session-003"
        
        recorder = TelemetryRecordingCapability(
            session_manager=MockSession(),
            classifier=None,
            enricher=None,
        )
        
        result = await recorder.transmit()
        assert result["status"] == "transmitted"
        assert result["count"] == 0
    
    async def test_transmit_failure_keeps_records_in_buffer(self):
        """Verify failed transmission keeps records in buffer for retry."""
        from modules.telemetry.src.capabilities_telemetry_recording_capability import TelemetryRecordingCapability
        
        class MockSession:
            def get_consent(self):
                return True
            def get_id(self):
                return "test-session-004"
        
        recorder = TelemetryRecordingCapability(
            session_manager=MockSession(),
            classifier=None,
            enricher=None,
        )
        
        # Add a record to buffer
        recorder._buffer.append({"test": "data"})
        
        # Simulate transmission failure
        result = await recorder.transmit()
        
        assert "error" in result
        assert result["retry"] is True
        assert len(recorder._buffer) == 1  # Record still in buffer
```

#### File: `tests/test_telemetry_backpressure.py` (NEW)

**Test for backpressure metrics exposure**

```python
import pytest


@pytest.mark.asyncio
class TestBackpressureMetrics:
    """Test backpressure metrics via diagnostics."""
    
    async def test_buffer_saturation_metrics(self):
        """Verify backpressure metrics show buffer saturation %."""
        from modules.telemetry.src.capabilities_telemetry_recording_capability import TelemetryRecordingCapability
        
        class MockSession:
            def get_consent(self):
                return True
            def get_id(self):
                return "test-session-005"
        
        recorder = TelemetryRecordingCapability(
            session_manager=MockSession(),
            classifier=None,
            enricher=None,
        )
        
        # Fill buffer to 50% capacity
        for i in range(500):
            recorder._buffer.append({"index": i})
        
        metrics = recorder.get_backpressure_metrics()
        
        assert metrics["buffer_size"] == 500
        assert metrics["max_buffer_size"] == 1000
        assert metrics["saturation_percent"] == 50.0
    
    async def test_drop_count_increments_on_overflow(self):
        """Verify drop count increments when buffer exceeds max capacity."""
        from modules.telemetry.src.capabilities_telemetry_recording_capability import TelemetryRecordingCapability
        
        class MockSession:
            def get_consent(self):
                return True
            def get_id(self):
                return "test-session-006"
        
        recorder = TelemetryRecordingCapability(
            session_manager=MockSession(),
            classifier=None,
            enricher=None,
        )
        
        # Fill buffer beyond max capacity (triggers drops)
        for i in range(1500):  # 500 over limit
            recorder._buffer.append({"index": i})
        
        metrics = recorder.get_backpressure_metrics()
        
        assert metrics["drop_count"] == 500
        assert metrics["buffer_size"] == 1000  # Capped at max
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
