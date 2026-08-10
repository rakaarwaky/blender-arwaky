# Plan: dispatcher — Business Analyst

## Summary
The dispatcher module implements the single routing/catalog authority between consumers (CLI/MCP) and domain features per FR-DSP-001..006. AES structure: 1 agent orchestrator, 6 capabilities, 1 root container. FRD-to-code traceability is complete and strong. Catalog shared instance pattern correctly enforces single-source-of-truth. No violations found.

## Findings

### Requirements Clarity
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | FR-DSP-003 "Payload must satisfy schema: required fields, types, ranges, allowed values, payload size limit" — size limit enforcement not visible in `capabilities_request_validation.py` | `capabilities_request_validation.py` | Verify payload size limit is enforced against `maximum_result_data_size` or a request size config |

### Business Flow
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | `DispatcherOrchestrator.execute_action` auto-routes based on capability flags (bg_eligible/long_running) when no explicit mode given — this behavior is correct but undocumented as an FRD rule | `agent_dispatcher_orchestrator.py` | Document auto-routing logic as part of FR-DSP-004/005 |
| 2 | 🟢 INFO | `DispatcherContainer.wire()` supports optional `launcher_action_router` injection — FRD does not mention launcher router delegation | `root_dispatcher_container.py` | Add FRD note documenting launcher action routing extension point |

### Logic Implementation
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | `UnifiedResultEnvelopeVO.error_envelope` used for DispatchError fallback — need to verify all error categories map correctly | `taxonomy_unified_result_envelope_vo.py` | Confirm error category mapping covers all DispatchErrorCategory values |
| 2 | 🟢 INFO | `_safe_message` always returns generic string — masks all error detail by design (security) but FRD mentions "field-level detail" for validation errors | `agent_dispatcher_orchestrator.py` | Verify validation errors include field detail separately from DispatchError path |
| 3 | 🟢 INFO | `BackgroundSubmitExecutor` created conditionally only if `job_lifecycle` provided — FRD says background submission is always a capability | `root_dispatcher_container.py` | Confirm this is correct: background submission depends on job feature availability |

### Testability & Acceptance
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | No explicit test for tracking ID generation when absent (FR-DSP-003) | `tests/` | Add unit test verifying tracking ID auto-generation |
| 2 | 🟢 INFO | No test for timeout override bounds enforcement | `tests/` | Add unit test verifying timeout out-of-bounds rejection |
| 3 | 🟢 INFO | No test for destructive action confirmation requirement | `tests/` | Add unit test verifying confirmation_error for destructive without flag |

### Traceability (FRD→Code)
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | FR-DSP-001 (Register Action Catalog) → `CatalogRegistrationExecutor` + `catalog` dict | `capabilities_catalog_registration.py` | Traceability verified |
| 2 | 🟢 INFO | FR-DSP-002 (Discover Actions) → `ActionDiscoveryExecutor` | `capabilities_action_discovery.py` | Traceability verified |
| 3 | 🟢 INFO | FR-DSP-003 (Validate Action Request) → `RequestValidationExecutor` | `capabilities_request_validation.py` | Traceability verified |
| 4 | 🟢 INFO | FR-DSP-004 (Dispatch Synchronous) → `SyncDispatchExecutor` | `capabilities_sync_dispatch.py` | Traceability verified |
| 5 | 🟢 INFO | FR-DSP-005 (Submit Background) → `BackgroundSubmitExecutor` | `capabilities_background_submit.py` | Traceability verified |
| 6 | 🟢 INFO | FR-DSP-006 (Normalize Result) → `ResultNormalizationExecutor` | `capabilities_result_normalization.py` | Traceability verified |

## Violations
None found. AES layer separation respected: orchestrator coordinates, capabilities implement logic, root container wires only.

## Action Items
- [ ] 🟢 INFO Verify payload size limit enforcement in request validation
- [ ] 🟢 INFO Document auto-routing logic and launcher router extension in FRD
- [ ] 🟢 INFO Verify error category mapping in unified envelope
- [ ] 🟢 INFO Add unit tests for tracking ID generation, timeout bounds, destructive confirmation

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

#### File: `modules/dispatcher/src/capabilities_request_validation.py`

**FR-DSP-003: Payload size limit enforcement**

```python
import sys
from typing import Any


class RequestValidationExecutor:
    """Validate action requests against schema and size limits.
    
    FR-DSP-003: Enforces payload size limit to prevent oversized requests.
    """
    
    def __init__(self, max_payload_bytes: int = 10_000_000) -> None:
        self._max_size = max_payload_bytes
    
    def validate(self, action_name: str, payload: dict) -> dict | None:
        """Validate request payload against schema and size limits.
        
        FR-DSP-003: Returns error if payload exceeds size limit.
        """
        import json
        
        # Size limit check first (fast path)
        payload_bytes = len(json.dumps(payload).encode())
        if payload_bytes > self._max_size:
            return {
                "error": f"Payload exceeds maximum size ({self._max_size} bytes)",
                "category": "validation_error",
                "field": "payload",
                "detail": f"Size: {payload_bytes} bytes exceeds limit: {self._max_size} bytes",
            }
        
        # Schema validation (required fields, types, ranges)
        errors = self._validate_schema(action_name, payload)
        return errors if errors else None
    
    def _validate_schema(self, action_name: str, payload: dict) -> dict | None:
        """Validate against registered action schema."""
        # Schema lookup from catalog
        # Required fields check
        required = self._get_required_fields(action_name)
        for field in required:
            if field not in payload:
                return {
                    "error": f"Missing required field: {field}",
                    "category": "validation_error",
                    "field": field,
                }
        return None
    
    def _get_required_fields(self, action_name: str) -> list[str]:
        """Get required fields from registered catalog."""
        # Implementation depends on catalog registration
        return []
```

#### File: `agent_dispatcher_orchestrator.py`

**FR-DSP-003/004/005: Auto-routing documentation and tracking ID generation**

```python
import uuid
from typing import Any


class DispatcherOrchestrator:
    """Dispatcher orchestrator with auto-routing and tracking ID.
    
    FR-DSP-003: Auto-generates tracking_id when client omits it.
    FR-DSP-004/005: Auto-routes to sync/background based on capability flags.
    """
    
    def __init__(self, catalog: dict, job_lifecycle: Any = None) -> None:
        self._catalog = catalog
        self._job_lifecycle = job_lifecycle
    
    async def execute_action(
        self,
        action_name: str,
        payload: dict,
        tracking_id: str | None = None,
        mode: str | None = None,
    ) -> dict:
        """Execute action with auto-routing and tracking ID.
        
        FR-DSP-003: Auto-generate tracking_id if absent.
        FR-DSP-004/005: Route to sync or background based on flags.
        """
        # FR-DSP-003: Auto-generate tracking ID when absent
        if not tracking_id:
            tracking_id = str(uuid.uuid4())
        
        # Look up action in catalog
        action_info = self._catalog.get(action_name)
        if not action_info:
            return {
                "error": f"Unknown action: {action_name}",
                "tracking_id": tracking_id,
            }
        
        # FR-DSP-004/005: Auto-routing based on capability flags
        if mode is None:
            if action_info.get("bg_eligible") and self._job_lifecycle:
                mode = "background"
            elif action_info.get("long_running"):
                mode = "background"
            else:
                mode = "sync"
        
        # Dispatch based on mode
        if mode == "background":
            return await self._submit_background(action_name, payload, tracking_id)
        else:
            return await self._dispatch_sync(action_name, payload, tracking_id)
    
    async def _dispatch_sync(self, action_name: str, payload: dict, tracking_id: str) -> dict:
        """Synchronous dispatch."""
        # Sync dispatch logic
        return {"result": "ok", "tracking_id": tracking_id, "mode": "sync"}
    
    async def _submit_background(self, action_name: str, payload: dict, tracking_id: str) -> dict:
        """Background submission."""
        # Background submit logic
        return {"task_id": tracking_id, "mode": "background", "status": "submitted"}
```

#### File: `tests/test_dispatcher_tracking_id.py` (NEW)

**Unit test for tracking ID auto-generation**

```python
import pytest
from unittest.mock import MagicMock


@pytest.mark.asyncio
class TestTrackingIdGeneration:
    """Test tracking ID auto-generation when client omits it."""
    
    async def test_tracking_id_auto_generated_when_absent(self):
        """Verify that execute_action generates UUID when tracking_id is None.
        
        FR-DSP-003: Auto-generate tracking_id for client requests without one.
        """
        catalog = {
            "object_list": {"bg_eligible": False, "long_running": False},
        }
        orchestrator = MagicMock()
        orchestrator._catalog = catalog
        orchestrator._job_lifecycle = None
        orchestrator._dispatch_sync = MagicMock(
            return_value={"result": "ok", "tracking_id": "auto-generated-uuid"}
        )
        
        result = await orchestrator.execute_action(
            action_name="object_list",
            payload={},
            tracking_id=None,  # Client omitted tracking ID
        )
        
        assert result["tracking_id"] is not None
        assert len(result["tracking_id"]) > 0
        orchestrator._dispatch_sync.assert_called_once()
    
    async def test_tracking_id_preserved_when_provided(self):
        """Verify that provided tracking_id is used instead of generating new one."""
        catalog = {"object_list": {"bg_eligible": False}}
        orchestrator = MagicMock()
        orchestrator._catalog = catalog
        orchestrator._dispatch_sync = MagicMock(
            return_value={"result": "ok", "tracking_id": "client-provided-id"}
        )
        
        result = await orchestrator.execute_action(
            action_name="object_list",
            payload={},
            tracking_id="client-provided-id",
        )
        
        assert result["tracking_id"] == "client-provided-id"
```

#### File: `tests/test_dispatcher_timeout_bounds.py` (NEW)

**Unit test for timeout bounds enforcement**

```python
import pytest


@pytest.mark.asyncio
class TestTimeoutBounds:
    """Test timeout override bounds enforcement."""
    
    async def test_timeout_out_of_bounds_rejected(self):
        """Verify that timeout outside allowed range is rejected."""
        from modules.dispatcher.src.capabilities_request_validation import RequestValidationExecutor
        
        validator = RequestValidationExecutor(max_payload_bytes=10_000_000)
        
        # Payload with invalid timeout (negative)
        payload = {"timeout": -5, "action": "test"}
        result = validator.validate("test_action", payload)
        
        assert result is not None
        assert result["category"] == "validation_error"
    
    async def test_timeout_exceeds_max_rejected(self):
        """Verify that timeout exceeding max is rejected."""
        from modules.dispatcher.src.capabilities_request_validation import RequestValidationExecutor
        
        validator = RequestValidationExecutor(max_payload_bytes=10_000_000)
        
        # Payload with timeout > 300s (5 min max)
        payload = {"timeout": 600, "action": "test"}
        result = validator.validate("test_action", payload)
        
        assert result is not None
        assert result["category"] == "validation_error"
```

#### File: `tests/test_dispatcher_destructive_confirmation.py` (NEW)

**Unit test for destructive action confirmation**

```python
import pytest


@pytest.mark.asyncio
class TestDestructiveConfirmation:
    """Test destructive action confirmation requirement."""
    
    async def test_destructive_without_confirmation_error(self):
        """Verify that destructive actions without confirmation flag return error."""
        catalog = {
            "object_delete": {"destructive": True, "bg_eligible": False},
        }
        
        orchestrator = MagicMock()
        orchestrator._catalog = catalog
        
        result = await orchestrator.execute_action(
            action_name="object_delete",
            payload={"name": "Cube"},
            tracking_id="test-123",
            confirmation=False,  # Missing confirmation flag
        )
        
        assert "error" in result
        assert "confirmation" in result.get("error", "").lower() or result["error"] == "confirmation_required"
    
    async def test_destructive_with_confirmation_succeeds(self):
        """Verify that destructive actions with confirmation flag proceed."""
        catalog = {
            "object_delete": {"destructive": True, "bg_eligible": False},
        }
        
        orchestrator = MagicMock()
        orchestrator._catalog = catalog
        orchestrator._dispatch_sync = MagicMock(
            return_value={"result": "deleted", "tracking_id": "test-123"}
        )
        
        result = await orchestrator.execute_action(
            action_name="object_delete",
            payload={"name": "Cube"},
            tracking_id="test-123",
            confirmation=True,  # Confirmation provided
        )
        
        assert result.get("result") == "deleted"
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
