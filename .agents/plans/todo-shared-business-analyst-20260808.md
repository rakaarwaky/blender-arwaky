# Plan: shared — Business Analyst
> **Historical plan notice (2026-08-14):** This 2026-08-08 plan is retained for audit history only. Do not execute its recommendations directly. Use the corresponding `*-20260814-revalidated.md` plan, which classifies each finding as `open`, `needs-clarification`, `resolved`, or `obsolete`.


## Summary
Foundation layer (shared) contains taxonomy, contracts, and utilities but includes incomplete protocol stubs (`pass`) and potential import boundary concerns that affect clarity, testability, and compliance.

## Findings

### Requirements Clarity
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟡 WARNING | Abstract methods in `WorkflowProtocol` use `pass` without implementation, causing ambiguous requirements. | `/home/raka/mcp-arwaky/blender-arwaky/modules/shared/src/common/contract_workflow_protocol.py` | Implement minimal logic or add TODO with target release. |
| 2 | 🟡 WARNING | Import statements reference sibling modules without explicit layer justification, risking Group 2 import rule violations. | `/home/raka/mcp-arwaky/blender-arwaky/modules/shared/src/common/contract_command_catalog_protocol.py` | Review against AES import rules; adjust if forbidden. |

### Business Flow
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | No business-flow anomalies detected; layer adheres to defined taxonomy. | — | Continue monitoring. |

### Logic Implementation
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟡 WARNING | Several protocol methods are left as `pass`, indicating missing logic and risking incomplete contract fulfillment. | Multiple files (`contract_workflow_protocol.py`, `contract_command_catalog_protocol.py`, `contract_execute_action_protocol.py`) | Add minimal stub implementations or deprecation notices. |

### Testability & Acceptance
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟡 WARNING | No test files found alongside protocol modules; unit-test coverage unknown. | All `*.py` under `/src/common` & related dirs | Add minimal test scaffolding to verify signatures and contract compliance. |

### Traceability (FRD→Code)
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | FRD scope directly maps to taxonomy VO/event/constant modules; mapping is clear. | FRD.md ↔ `src/*/taxonomy_*.py` | Keep comment-based registry linking FRD items to code. |

## Violations
🔴 CRITICAL: No critical requirement violations detected; only warnings around incomplete stubs and import patterns.

## Action Items
- [ ] 🟡 Implement concrete bodies for abstract methods marked with `pass` in protocol files.
- [ ] Add unit tests for all protocol classes in `src/common` and related directories.
- [ ] Review and adjust import statements to ensure compliance with Group 2 import rules.
- [ ] Document any pass-based methods with a TODO and target release timestamp.
- [ ] Verify no forbidden dummy imports exist via AES import checks.

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

#### File: `modules/shared/src/common/contract_workflow_protocol.py`

**FRD: Implement concrete stub for WorkflowProtocol**

```python
from abc import ABC, abstractmethod
from typing import Any


class WorkflowProtocol(ABC):
    """Workflow protocol with minimal stub implementations.
    
    FRD: All methods must have concrete bodies (not pass).
    Stub implementations return default values or raise NotImplementedError
    with TODO markers for target release versions.
    """
    
    @abstractmethod
    async def execute(self, workflow_id: str, inputs: dict) -> dict:
        """Execute workflow with given inputs.
        
        FRD: Returns execution result dict.
        TODO: Implement in v0.2.0 release.
        """
        raise NotImplementedError(
            "WorkflowProtocol.execute not implemented — target: v0.2.0"
        )
    
    @abstractmethod
    async def cancel(self, workflow_id: str) -> dict:
        """Cancel running workflow.
        
        FRD: Returns cancellation result.
        TODO: Implement in v0.2.0 release.
        """
        raise NotImplementedError(
            "WorkflowProtocol.cancel not implemented — target: v0.2.0"
        )
    
    @abstractmethod
    async def status(self, workflow_id: str) -> dict:
        """Get workflow execution status.
        
        FRD: Returns status dict with current state.
        TODO: Implement in v0.2.0 release.
        """
        raise NotImplementedError(
            "WorkflowProtocol.status not implemented — target: v0.2.0"
        )


class WorkflowStub(WorkflowProtocol):
    """Concrete stub implementation for shared layer compliance.
    
    Provides minimal working implementations that satisfy protocol
    signatures without implementing full business logic.
    """
    
    async def execute(self, workflow_id: str, inputs: dict) -> dict:
        """Stub: returns placeholder result."""
        return {
            "workflow_id": workflow_id,
            "status": "pending",
            "inputs": inputs,
            "result": None,
            "_stub": True,
        }
    
    async def cancel(self, workflow_id: str) -> dict:
        """Stub: returns cancellation confirmation."""
        return {"workflow_id": workflow_id, "status": "cancelled", "_stub": True}
    
    async def status(self, workflow_id: str) -> dict:
        """Stub: returns placeholder status."""
        return {
            "workflow_id": workflow_id,
            "status": "unknown",
            "_stub": True,
        }
```

#### File: `modules/shared/src/common/contract_command_catalog_protocol.py`

**FRD: Fix import compliance and implement stub**

```python
from abc import ABC, abstractmethod
from typing import Any


class CommandCatalogProtocol(ABC):
    """Command catalog protocol with concrete implementations.
    
    FRD: All methods have bodies (not pass).
    No sibling module imports — only standard library and typing.
    """
    
    @abstractmethod
    async def register(self, command_name: str, schema: dict) -> None:
        """Register command with schema."""
        raise NotImplementedError(
            "CommandCatalogProtocol.register not implemented — target: v0.2.0"
        )
    
    @abstractmethod
    async def get_schema(self, command_name: str) -> dict | None:
        """Get registered schema for command."""
        raise NotImplementedError(
            "CommandCatalogProtocol.get_schema not implemented — target: v0.2.0"
        )
    
    @abstractmethod
    async def list_commands(self) -> list[str]:
        """List all registered commands."""
        raise NotImplementedError(
            "CommandCatalogProtocol.list_commands not implemented — target: v0.2.0"
        )


class CommandCatalogStub(CommandCatalogProtocol):
    """Concrete stub for shared layer compliance."""
    
    def __init__(self) -> None:
        self._catalog: dict[str, dict] = {}
    
    async def register(self, command_name: str, schema: dict) -> None:
        """Stub: registers command in local dict."""
        self._catalog[command_name] = schema
    
    async def get_schema(self, command_name: str) -> dict | None:
        """Stub: returns registered schema or None."""
        return self._catalog.get(command_name)
    
    async def list_commands(self) -> list[str]:
        """Stub: returns list of registered commands."""
        return list(self._catalog.keys())
```

#### File: `modules/shared/src/common/contract_execute_action_protocol.py`

**FRD: Implement execute action protocol stubs**

```python
from abc import ABC, abstractmethod
from typing import Any


class ExecuteActionProtocol(ABC):
    """Execute action protocol with concrete stubs.
    
    FRD: All methods have bodies (not pass).
    """
    
    @abstractmethod
    async def execute(self, action_name: str, payload: dict) -> dict:
        """Execute action with payload."""
        raise NotImplementedError(
            "ExecuteActionProtocol.execute not implemented — target: v0.2.0"
        )
    
    @abstractmethod
    async def validate(self, action_name: str, payload: dict) -> dict | None:
        """Validate action request."""
        raise NotImplementedError(
            "ExecuteActionProtocol.validate not implemented — target: v0.2.0"
        )


class ExecuteActionStub(ExecuteActionProtocol):
    """Concrete stub for shared layer compliance."""
    
    async def execute(self, action_name: str, payload: dict) -> dict:
        """Stub: returns placeholder result."""
        return {
            "action": action_name,
            "payload": payload,
            "result": None,
            "_stub": True,
        }
    
    async def validate(self, action_name: str, payload: dict) -> dict | None:
        """Stub: always passes validation."""
        return None  # No errors
```

#### File: `tests/test_shared_protocols.py` (NEW)

**Unit tests for protocol signatures and compliance**

```python
import pytest


@pytest.mark.asyncio
class TestSharedProtocols:
    """Test protocol signatures and stub implementations."""
    
    async def test_workflow_protocol_stubs(self):
        """Verify WorkflowProtocol stub methods return valid dicts."""
        from modules.shared.src.common.contract_workflow_protocol import WorkflowStub
        
        stub = WorkflowStub()
        
        result = await stub.execute("wf-001", {"input": "test"})
        assert result["workflow_id"] == "wf-001"
        assert result["_stub"] is True
        
        result = await stub.cancel("wf-001")
        assert result["status"] == "cancelled"
        
        result = await stub.status("wf-001")
        assert result["workflow_id"] == "wf-001"
    
    async def test_command_catalog_protocol(self):
        """Verify CommandCatalogProtocol register/get/list."""
        from modules.shared.src.common.contract_command_catalog_protocol import CommandCatalogStub
        
        catalog = CommandCatalogStub()
        
        await catalog.register("test_cmd", {"type": "object", "required": ["name"]})
        
        schema = await catalog.get_schema("test_cmd")
        assert schema is not None
        assert schema["type"] == "object"
        
        commands = await catalog.list_commands()
        assert "test_cmd" in commands
    
    async def test_execute_action_protocol(self):
        """Verify ExecuteActionProtocol stub methods."""
        from modules.shared.src.common.contract_execute_action_protocol import ExecuteActionStub
        
        stub = ExecuteActionStub()
        
        result = await stub.execute("object_list", {})
        assert result["action"] == "object_list"
        
        validation_result = await stub.validate("object_list", {})
        assert validation_result is None  # No errors
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
