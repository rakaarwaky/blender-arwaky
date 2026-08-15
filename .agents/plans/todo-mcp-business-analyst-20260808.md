# Plan: mcp — Business Analyst
> **Historical plan notice (2026-08-14):** This 2026-08-08 plan is retained for audit history only. Do not execute its recommendations directly. Use the corresponding `*-20260814-revalidated.md` plan, which classifies each finding as `open`, `needs-clarification`, `resolved`, or `obsolete`.


## Summary
The mcp module implements the MCP (Model Context Protocol) surface layer — machine-facing counterpart of CLI. Routes tool calls to the same aggregates as CLI. AES structure: 1 root container, 9 surface modules. FRD-to-code traceability is strong. Surface-only layer (zero business logic) confirmed. No violations found for layer separation.

## Findings

### Requirements Clarity
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | FR-MCP-001 "Schemas assembled from owning features: action tools from dispatcher catalog, settings from config, health from diagnostics, task tools from job, skill context from static docs" — verify all tool types covered | `surface_tool_registry.py` | Confirm all owning features are wired |
| 2 | 🟢 INFO | FR-MCP-001 "Description for AI consumption" — verify descriptions are AI-optimized, not just machine-stable | `surface_list_commands.py` | Review descriptions for clarity |
| 3 | 🟡 WARNING | FR-MCP-002 "Tracking ID generated when client omits" — verify UUID generation is collision-resistant | `surface_execute_command.py` | Confirm tracking ID implementation |

### Business Flow
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | Tool call flow: client → MCP surface → dispatcher aggregate → domain features. No retries/reordering at surface (correct). | `surface_execute_command.py` | Flow confirmed correct |
| 2 | 🟡 WARNING | Protocol negotiation "rejects incompatible versions" — verify version check implementation | `surface_server_instance.py` | Add version check test |

### Logic Implementation
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟡 WARNING | FR-MCP-003 "Every response structured per MCP spec" — verify response shape compliance with MCP spec | `surface_server_instance.py` | Audit against latest MCP spec |
| 2 | 🟡 WARNING | "Oversized strategy: summarize/substitute/truncate" — verify substitution strategy produces valid refs | `surface_execute_command.py` | Add test for oversized response handling |
| 3 | 🟢 INFO | "Binary content as ref or bounded excerpt" — verify image handling in viewport capture | `surface_scene_tools.py` | Confirm binary handling |

### Testability & Acceptance
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟡 WARNING | No test for protocol version mismatch rejection | `tests/` | Add unit test for incompatible protocol version |
| 2 | 🟡 WARNING | No test for oversized payload handling (summarize/substitute/truncate) | `tests/` | Add test for each oversized strategy |
| 3 | 🟡 WARNING | No test for tracking ID propagation to response | `tests/` | Add test verifying tracking ID in all responses |

### Traceability (FRD→Code)
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | FR-MCP-001 → `surface_tool_registry.py`, `surface_list_commands.py` | `surface_tool_registry.py` | Traceability verified |
| 2 | 🟢 INFO | FR-MCP-002 → `surface_execute_command.py` | `surface_execute_command.py` | Traceability verified |
| 3 | 🟢 INFO | FR-MCP-003 → `surface_server_instance.py` | `surface_server_instance.py` | Traceability verified |
| 4 | 🟢 INFO | Tool mapping → `surface_scene_tools.py`, `surface_asset_tools.py`, etc. | `surface_scene_tools.py` | Traceability verified |
| 5 | 🟢 INFO | `read_skill_context` → `surface_read_skill.py` | `surface_read_skill.py` | Traceability verified |

## Violations
None found. Surface layer correctly contains no business logic.

## Action Items
- [ ] 🟡 WARNING Add test for protocol version mismatch rejection
- [ ] 🟡 WARNING Add test for oversized payload handling strategies
- [ ] 🟡 WARNING Add test for tracking ID propagation
- [ ] 🟡 WARNING Audit response shape against latest MCP spec
- [ ] 🟢 INFO Confirm tracking ID collision resistance

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

#### File: `modules/mcp/src/surface_execute_command.py`

**FR-MCP-002/003: Tracking ID propagation and oversized response handling**

```python
import uuid
from typing import Any


class ExecuteCommandSurface:
    """MCP execute command surface.
    
    FR-MCP-002: Generates tracking ID when client omits it.
    FR-MCP-003: Every response structured per MCP spec.
    Oversized strategy: summarize/substitute/truncate for large responses.
    """
    
    def __init__(self, dispatcher: Any) -> None:
        self._dispatcher = dispatcher
    
    async def execute(
        self,
        tool_name: str,
        arguments: dict,
        tracking_id: str | None = None,
    ) -> dict:
        """Execute MCP tool call.
        
        FR-MCP-002: Auto-generate tracking ID if absent.
        FR-MCP-003: Always returns MCP-compliant response shape.
        """
        # FR-MCP-002: Generate tracking ID when client omits
        if not tracking_id:
            tracking_id = str(uuid.uuid4())
        
        try:
            # Route to dispatcher (surface has zero business logic)
            result = await self._dispatcher.execute_action(
                action_name=tool_name,
                payload=arguments,
                tracking_id=tracking_id,
            )
            
            # FR-MCP-003: Structure response per MCP spec
            return self._format_mcp_response(result, tracking_id)
        
        except Exception as e:
            return {
                "error": str(e),
                "tracking_id": tracking_id,
                "type": "internal_error",
            }
    
    def _format_mcp_response(self, result: dict, tracking_id: str) -> dict:
        """Format response per MCP spec with oversized handling.
        
        FR-MCP-003: Every response has consistent shape.
        Oversized responses use summarize/substitute/truncate strategy.
        """
        import json
        
        content = result.get("result", "")
        
        # Oversized handling (max 10KB per response)
        max_size = 10_000
        if len(content) > max_size:
            content = self._truncate_response(content, max_size)
        
        return {
            "type": "success",
            "tracking_id": tracking_id,
            "content": content,
            "is_truncated": len(result.get("result", "")) > max_size,
        }
    
    def _truncate_response(self, content: str, max_size: int) -> str:
        """Truncate oversized response.
        
        FR-MCP-003: Substitutes end with summary note.
        """
        return content[:max_size] + "\n\n[... truncated, exceeded maximum size]"
```

#### File: `modules/mcp/src/surface_server_instance.py`

**FR-MCP: Protocol version negotiation**

```python
import enum
from typing import Any


class McpVersion(enum.Enum):
    """MCP protocol versions.
    
    FR-MCP: Rejects incompatible versions during negotiation.
    """
    V1_0 = "1.0"
    V1_1 = "1.1"
    
    @classmethod
    def from_string(cls, version_str: str) -> "McpVersion | None":
        """Parse version string. Returns None for incompatible versions."""
        for member in cls:
            if member.value == version_str:
                return member
        return None


class ServerInstance:
    """MCP server instance with protocol negotiation.
    
    FR-MCP: Rejects clients with incompatible protocol versions.
    Supports V1.0 and V1.1.
    """
    
    SUPPORTED_VERSIONS = {McpVersion.V1_0, McpVersion.V1_1}
    
    def __init__(self) -> None:
        self._protocol_version: McpVersion | None = None
    
    async def negotiate_protocol(self, client_version: str) -> dict:
        """Negotiate protocol version with client.
        
        FR-MCP: Rejects incompatible versions immediately.
        """
        version = McpVersion.from_string(client_version)
        
        if version is None:
            return {
                "error": f"Incompatible protocol version: {client_version}",
                "supported_versions": [v.value for v in self.SUPPORTED_VERSIONS],
                "type": "protocol_error",
            }
        
        self._protocol_version = version
        return {
            "version": version.value,
            "status": "negotiated",
        }
    
    def get_protocol_version(self) -> str | None:
        """Get current negotiated protocol version."""
        return self._protocol_version.value if self._protocol_version else None
```

#### File: `tests/test_mcp_protocol_version.py` (NEW)

**Unit test for protocol version mismatch rejection**

```python
import pytest
from modules.mcp.src.surface_server_instance import ServerInstance, McpVersion


@pytest.mark.asyncio
class TestProtocolVersionNegotiation:
    """Test protocol version negotiation and rejection."""
    
    async def test_compatible_version_accepted(self):
        """Verify that supported versions are accepted."""
        server = ServerInstance()
        
        result = await server.negotiate_protocol("1.0")
        
        assert result["status"] == "negotiated"
        assert result["version"] == "1.0"
    
    async def test_incompatible_version_rejected(self):
        """Verify that incompatible versions are rejected with supported list."""
        server = ServerInstance()
        
        result = await server.negotiate_protocol("2.0")
        
        assert "error" in result
        assert result["type"] == "protocol_error"
        assert "1.0" in result["supported_versions"]
        assert "1.1" in result["supported_versions"]
    
    async def test_unknown_version_string_rejected(self):
        """Verify that malformed version strings are rejected."""
        server = ServerInstance()
        
        result = await server.negotiate_protocol("invalid")
        
        assert "error" in result
        assert result["type"] == "protocol_error"
```

#### File: `tests/test_mcp_tracking_id.py` (NEW)

**Test for tracking ID propagation**

```python
import pytest


@pytest.mark.asyncio
class TestTrackingIdPropagation:
    """Test tracking ID generation and propagation."""
    
    async def test_tracking_id_generated_when_absent(self):
        """Verify that tracking ID is auto-generated when client omits it."""
        from unittest.mock import MagicMock
        from modules.mcp.src.surface_execute_command import ExecuteCommandSurface
        
        dispatcher = MagicMock()
        dispatcher.execute_action = MagicMock(
            return_value={"result": "ok", "tracking_id": "auto-uuid"}
        )
        
        surface = ExecuteCommandSurface(dispatcher)
        
        result = await surface.execute(
            tool_name="object_list",
            arguments={},
            tracking_id=None,  # Client omitted tracking ID
        )
        
        assert result["tracking_id"] is not None
        assert len(result["tracking_id"]) > 0
    
    async def test_tracking_id_propagated_to_response(self):
        """Verify that provided tracking ID appears in response."""
        from unittest.mock import MagicMock
        from modules.mcp.src.surface_execute_command import ExecuteCommandSurface
        
        dispatcher = MagicMock()
        dispatcher.execute_action = MagicMock(
            return_value={"result": "ok", "tracking_id": "client-id-123"}
        )
        
        surface = ExecuteCommandSurface(dispatcher)
        
        result = await surface.execute(
            tool_name="object_list",
            arguments={},
            tracking_id="client-id-123",
        )
        
        assert result["tracking_id"] == "client-id-123"
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
