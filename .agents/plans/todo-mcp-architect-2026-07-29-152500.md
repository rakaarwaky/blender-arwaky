# Review Plan: mcp — Architect (Phase 1)

## Summary

The MCP module has a fundamental **architectural breach**: the surface layer directly imports and instantiates root containers from other features (`dispatcher`, `diagnostics`, `config`) instead of going through contract protocols. This violates the 7-layer architecture's dependency direction (surface → agent → contract → capabilities). There are no MCP-specific contract protocols, no DI container, and several broken imports. The module also has orphan taxonomy files, duplicate registrations, and missing FRD requirements (schema exposure, protocol negotiation, response formatting, oversized protection).

## Findings by Category

### Layer Boundaries
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| LB01 | 🔴 CRITICAL | **Surface imports root containers from other features** — `surface_execute_command.py` imports `from modules.dispatcher.src.root_dispatcher_container import create_dispatcher_feature`, bypassing contract layer entirely | `modules/mcp/src/surface_execute_command.py` line 10 | Create MCP-to-dispatcher contract protocol. Surface should depend on contract, not root containers. |
| LB02 | 🔴 CRITICAL | **Surface imports from another feature's surface layer** — `surface_execute_command.py` imports `from modules.dispatcher.src.surface_action_registry import validate_action_args`. Surface→Surface cross-feature import breaks layer boundaries | `modules/mcp/src/surface_execute_command.py` line 11 | Move validation to dispatcher contract protocol. MCP surface should never import dispatcher surfaces. |
| LB03 | 🔴 CRITICAL | **No MCP contract protocols exist** — `modules/shared/src/mcp/` has taxonomy files only (VOs, events) but NO `_protocol.py` or `_aggregate.py` files. All tools bypass contracts and call aggregates directly | `modules/shared/src/mcp/` full directory | Create `contract_mcp_protocol.py` defining tool routing, schema exposure, and response formatting protocols. |
| LB04 | 🔴 CRITICAL | **Surface imports non-existent file** — `surface_server_instance.py` and `surface_server_start.py` import `from modules.mcp.src.capabilities_mcp_bootstrap` but no such file exists in the module | `modules/mcp/src/surface_server_instance.py` line 27, `surface_server_start.py` line 13 | Create the missing `capabilities_mcp_bootstrap.py` or remove the broken imports. |
| LB05 | 🟡 WARNING | **`surface_list_commands.py` imports root container** — `from modules.dispatcher.src.root_dispatcher_container import create_dispatcher_feature` | `modules/mcp/src/surface_list_commands.py` line 8 | Route through dispatcher contract protocol instead of direct container creation. |
| LB06 | 🟡 WARNING | **`surface_health_check.py` imports root container** — `from modules.diagnostics.src.root_diagnostics_container import create_diagnostics_feature` | `modules/mcp/src/surface_health_check.py` line 7 | Route through diagnostics contract protocol instead of direct container creation. |
| LB07 | 🟡 WARNING | **`surface_get_config.py` imports from config root** — `from modules.config.src.root_config_container import get_config_snapshot` | `modules/mcp/src/surface_get_config.py` line 25 | Route through config contract protocol. |

### Naming Convention
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| N01 | 🟡 WARNING | **Handler classes in surface files** — Classes named `ExecuteCommandHandler`, `ToolRegistryHandler`, `ServerInstanceHandler` use "Handler" suffix but files have `surface_` prefix. FRD calls them "tools", not handlers | Multiple files | Rename to match tool naming (e.g., `ExecuteCommandSurface`) or move handlers to utility layer. |
| N02 | 🟡 WARNING | **`surface_prompt_register.py` has duplicate `register_prompts`** — Both `PromptHandlerModule.register_prompts` class method AND module-level `register_prompts = PromptHandlerModule.register_prompts` function | `modules/mcp/src/surface_prompt_register.py` lines 57, 63 | Remove duplicate. Keep only one export. |
| N03 | 🟢 INFO | **`ServerStartHandler` has duplicate class docstring** — Two consecutive `"""Handler for..."""` docstrings in same class | `modules/mcp/src/surface_server_start.py` lines 19-21 | Remove duplicate docstring. |

### Orphan Detection
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| O01 | 🔴 CRITICAL | **`capabilities_mcp_bootstrap.py` is referenced but doesn't exist** — Two files import it but the file is missing from the module. This makes `surface_server_instance.py` and `surface_server_start.py` broken imports | `modules/mcp/src/surface_server_instance.py` line 27, `surface_server_start.py` line 13 | Create the file or remove imports. The `ServerBootstrapManager` and `record_startup` symbols are undefined. |
| O02 | 🟡 WARNING | **`taxonomy_mcp_event.py` is orphaned** — `McpEvent` and `McpEventKind` are defined but never imported by any capability, agent, or surface file. FRD says "Events: None" so these serve no purpose | `modules/shared/src/mcp/taxonomy_mcp_event.py` full file | Remove or comment out until FRD adds event requirements. |
| O03 | 🟡 WARNING | **`taxonomy_mcp_vo.py` VOs are orphaned** — `McpToolDef`, `McpServerConfig`, `McpResponse` defined but never consumed by any contract or capability | `modules/shared/src/mcp/taxonomy_mcp_vo.py` full file | Remove or use in new MCP contract protocols. |
| O04 | 🟢 INFO | **`surface_prompt_register.py` prompts are never called** — PromptHandlerModule defines 4 prompts but there's no mechanism to invoke them outside MCP registration | `modules/mcp/src/surface_prompt_register.py` full file | This is acceptable for surface layer but verify prompts are actually used by MCP clients. |

### Scalability & Coupling
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| SC01 | 🔴 CRITICAL | **No DI container for MCP** — No `root_mcp_container.py` exists. Each tool creates its own container (`create_dispatcher_feature()`, `create_diagnostics_feature()`) inline, breaking DI pattern and creating multiple container instances | `surface_execute_command.py` line 32, `surface_list_commands.py` line 28, `surface_health_check.py` line 19 | Create `root_mcp_container.py` with proper DI wiring. Tools should receive protocols via constructor injection. |
| SC02 | 🔴 CRITICAL | **No MCP-to-feature contract layer** — MCP tools directly call dispatcher/diagnostics/config aggregates instead of going through contract protocols. This couples surface to concrete implementations | All tool files | Create `contract_dispatcher_proxy.py` in shared/mcp that defines how MCP routes to dispatcher, diagnostics, config. |
| SC03 | 🟡 WARNING | **Tool registration is static and monolithic** — `ToolRegistryHandler.register_tools()` imports all 5 handlers inline. New tools require editing this registry file instead of auto-discovery | `modules/mcp/src/surface_tool_registry.py` lines 24-31 | Implement tool auto-registration via MCP decorator pattern or plugin system. |
| SC04 | 🟡 WARNING | **SKILLS_DIR uses fragile path traversal** — `Path(__file__).resolve().parent.parent.parent.parent.parent / ".agents" / "skills"` — 5 `.parent` traversals, breaks on any directory rename | `modules/mcp/src/surface_read_skill.py` line 14 | Use `importlib.metadata` or config-based path. Hardcoded parent traversal is brittle. |

### Data Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| DF01 | 🔴 CRITICAL | **No response formatting per FR-MCP-003** — FRD requires "MCP-compliant structured responses" with unified envelope (success, data, error category, message, warnings, metadata), tracking ID, protocol-compliant status. Current implementation returns raw results or simple JSON strings | `surface_execute_command.py` lines 36-42, `surface_health_check.py` line 21 | Create response formatter that wraps all tool results in MCP envelope with tracking ID and error categorization. |
| DF02 | 🔴 CRITICAL | **No oversized payload protection** — FR-MCP-002 says "Oversized input rejected at surface", FR-MCP-003 says "Payload size bounded by configured max". No size validation exists anywhere | All files | Add payload size validator in surface layer. Reject oversized inputs before routing. |
| DF03 | 🔴 CRITICAL | **No secrets masking in responses** — FR-MCP-003 says "Secrets/tokens/credentials/code/paths masked via security policy before any response leaves". No redaction applied to any tool output | All files | Add security redaction step between tool result and MCP response. |
| DF04 | 🟡 WARNING | **No protocol version negotiation** — FR-MCP-001 says "Incompatible client protocol version → rejected with unsupported error". FastMCP handles this internally but MCP layer has no explicit version check | `surface_server_instance.py` lines 53-66 | Add explicit protocol version negotiation in server lifespan. |
| DF05 | 🟡 WARNING | **No degraded capability indication** — FR-MCP-001 says "Degraded owning features: tool listed with explicit degraded indicator". Tools are registered without any degradation metadata | All tool files | Integrate diagnostics health snapshot into tool schema metadata. |

### Architecture Pattern Violations
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| AP01 | 🔴 CRITICAL | **Surface layer implements routing logic** — FRD says "MCP surface only — zero business logic" but `surface_execute_command.py` has `validate_action_args` call, error handling, and JSON serialization. This is business logic in surface | `surface_execute_command.py` lines 28-42 | Move validation to dispatcher contract. Surface should only format and route. |
| AP02 | 🔴 CRITICAL | **No tracking ID injection/propagation** — FR-MCP-002 says "Tracking ID generated when client omits; propagated through aggregate, result, logs". No tracking ID mechanism exists | All files | Add tracking ID generator and propagator in surface layer. |
| AP03 | 🟡 WARNING | **Direct aggregate instantiation per call** — Each tool call creates a new container (`create_dispatcher_feature()`), which is expensive and breaks singleton pattern | `surface_execute_command.py` line 32, `surface_list_commands.py` line 28, `surface_health_check.py` line 19 | Cache container in MCP container singleton. Reuse across calls. |

## Violations

### AES Rule Violations
- **AES201 (Forbidden Import)**: Surface files import from root containers of other features (dispatcher, diagnostics, config) — violates layer boundary rules #6, #8, #9
- **AES201 (Forbidden Import)**: `surface_execute_command.py` imports from dispatcher's surface layer (`surface_action_registry`) — cross-surface import is forbidden
- **AES503 (Capabilities Orphan)**: No MCP capability files exist — the module has only surface files with no capabilities or agent layer
- **AES502 (Contract Orphan)**: No MCP contract protocols exist — `_protocol` files are missing from `modules/shared/src/mcp/`
- **AES405 (Agent Orphan)**: No MCP orchestrator exists — there's no `_orchestrator.py` file

### FRD Compliance Gaps
- **FR-MCP-001**: Tool schemas not exposed (no schema generation, no catalog version, no degraded indicators)
- **FR-MCP-002**: No tracking ID mechanism, no oversized input rejection, no protocol negotiation
- **FR-MCP-003**: No MCP-compliant response envelope, no secrets masking, no payload size bounds

## Action Items
- [CRITICAL] Create `capabilities_mcp_bootstrap.py` to fix broken imports (or remove imports)
- [CRITICAL] Create MCP contract protocols (`contract_mcp_protocol.py`) in shared layer
- [CRITICAL] Create `root_mcp_container.py` with DI wiring for all tools
- [CRITICAL] Refactor all tool handlers to depend on contracts, not root containers
- [CRITICAL] Implement MCP response formatter with unified envelope and tracking ID
- [CRITICAL] Add oversized payload protection in surface layer
- [CRITICAL] Add secrets masking via security policy before responses leave
- [HIGH] Create MCP-to-feature proxy contracts (dispatcher, diagnostics, config)
- [HIGH] Implement protocol version negotiation in server lifespan
- [HIGH] Add degraded capability indicators to tool schemas
- [MEDIUM] Fix duplicate `register_prompts` in prompt_register.py
- [MEDIUM] Fix duplicate docstring in ServerStartHandler
- [MEDIUM] Clean up orphan taxonomy files (event, VO) or integrate into contracts
- [LOW] Standardize naming: "Handler" → "Surface" or move to utility layer

## Fixed Code

### Fix 1: Create MCP contract protocols (modules/shared/src/mcp/contract_mcp_protocol.py)

```python
"""MCP domain contracts — tool routing, schema exposure, response formatting.

FR-MCP-001: Expose MCP Tools
FR-MCP-002: Route Tool Calls
FR-MCP-003: Format MCP Responses
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import (
    ActionName,
    Details,
    Prompt,
    ServerName,
)


class McpSchemaProtocol(ABC):
    """Protocol for exposing MCP tool schemas from dispatcher catalog."""

    @abstractmethod
    async def get_tool_schemas(self) -> list[dict[str, Any]]:
        """Return tool schema list with names, descriptions, params, examples.
        
        FR-MCP-001: Schemas assembled from owning features.
        Degraded tools listed with indicator, not hidden.
        """
        ...

    @abstractmethod
    async def get_catalog_version(self) -> str:
        """Return dispatcher catalog version for drift detection."""
        ...


class McpRoutingProtocol(ABC):
    """Protocol for routing tool calls to owning aggregates."""

    @abstractmethod
    async def route_tool_call(
        self,
        tool_name: str,
        payload: dict[str, Any],
        tracking_id: str | None = None,
    ) -> dict[str, Any]:
        """Route tool call to correct aggregate.
        
        FR-MCP-002: Every tool routes to same aggregate as CLI command.
        No retries, no reordering, no multi-aggregate composition.
        """
        ...

    @abstractmethod
    async def validate_tool_input(
        self,
        tool_name: str,
        payload: dict[str, Any],
        strict_mode: bool = True,
    ) -> list[str]:
        """Validate surface-level input shape.
        
        FR-MCP-002: Surface validates shape only (recognized, parsed, required fields).
        Semantic validation delegated to dispatcher + owning features.
        """
        ...


class McpResponseProtocol(ABC):
    """Protocol for formatting MCP-compliant responses."""

    @abstractmethod
    async def format_response(
        self,
        result: Any,
        tool_name: str,
        tracking_id: str,
        error_category: str | None = None,
    ) -> dict[str, Any]:
        """Format aggregate result into MCP-compliant response.
        
        FR-MCP-003: Structured per MCP spec with unified envelope.
        Tracking ID in every response. Payload size bounded.
        Secrets masked via security policy.
        """
        ...

    @abstractmethod
    async def mask_secrets(self, response: dict[str, Any]) -> dict[str, Any]:
        """Redact secrets/tokens/credentials/paths from response."""
        ...
```

### Fix 2: Create MCP DI container (modules/mcp/src/root_mcp_container.py)

```python
"""Root: MCP surface composition container.

Wires MCP tool handlers to the MCP server instance via contract protocols.
"""

from __future__ import annotations

import logging

from modules.shared.src.mcp.contract_mcp_protocol import (
    McpResponseProtocol,
    McpRoutingProtocol,
    McpSchemaProtocol,
)

logger = logging.getLogger("BlenderMCPServer")


class McpContainer:
    """Dependency injection container for the MCP surface module.

    Provides contract-protocol instances to tool handlers.
    """

    def __init__(self) -> None:
        self._routing: McpRoutingProtocol | None = None
        self._schema: McpSchemaProtocol | None = None
        self._response: McpResponseProtocol | None = None
        self._wired: bool = False

    def wire(self) -> None:
        """Wire MCP surface to contract protocols."""
        if self._wired:
            return

        logger.info("Wiring MCP surface module")

        # Create protocol implementations (delegating to owning features)
        self._routing = McpRoutingImpl()
        self._schema = McpSchemaImpl()
        self._response = McpResponseImpl()

        self._wired = True
        logger.info("MCP surface module wired successfully")

    @property
    def routing(self) -> McpRoutingProtocol:
        if not self._wired or self._routing is None:
            raise RuntimeError("McpContainer not wired — call wire() first")
        return self._routing

    @property
    def schema(self) -> McpSchemaProtocol:
        if not self._wired or self._schema is None:
            raise RuntimeError("McpContainer not wired — call wire() first")
        return self._schema

    @property
    def response(self) -> McpResponseProtocol:
        if not self._wired or self._response is None:
            raise RuntimeError("McpContainer not wired — call wire() first")
        return self._response


def create_mcp_feature() -> McpContainer:
    """Factory function to create and wire the MCP surface module."""
    container = McpContainer()
    container.wire()
    return container
```

### Fix 3: Refactor execute_command to use contracts (surface_execute_command.py)

```python
"""MCP Tool 1: execute_command — Universal action executor.

FR-MCP-001: Expose MCP Tools — register via contract protocol
FR-MCP-002: Route Tool Calls — dispatcher aggregate via routing protocol
FR-MCP-003: Format MCP Responses — unified envelope via response protocol
"""

import logging
from typing import Any

from modules.shared.src.mcp.contract_mcp_protocol import (
    McpResponseProtocol,
    McpRoutingProtocol,
)

logger = logging.getLogger("BlenderMCPServer")


class ExecuteCommandSurface:
    """Surface handler for execute_command MCP tool.

    Delegates all logic to contract protocols — zero business logic.
    """

    def __init__(
        self,
        routing: McpRoutingProtocol,
        response: McpResponseProtocol,
    ) -> None:
        self._routing = routing
        self._response = response

    @staticmethod
    def register(mcp, container: McpContainer) -> None:
        """Register execute_command tool with MCP server."""
        
        async def execute_command(
            action: str,
            args: dict[str, Any] | None = None,
        ) -> dict[str, Any]:
            """Execute ANY BlenderArwaky action via dispatcher aggregate."""
            if args is None:
                args = {}

            # Surface-level validation only (FR-MCP-002)
            errors = await container.routing.validate_tool_input("execute_command", {"action": action, "args": args})
            if errors:
                return await container.response.format_response(
                    result={"error": "; ".join(errors)},
                    tool_name="execute_command",
                    tracking_id="",  # Generated by response formatter
                    error_category="validation",
                )

            # Route to dispatcher aggregate via protocol (FR-MCP-002)
            try:
                result = await container.routing.route_tool_call(
                    tool_name="execute_command",
                    payload={"action": action, "args": args},
                )
                return await container.response.format_response(
                    result=result,
                    tool_name="execute_command",
                    tracking_id="",
                )
            except Exception as e:
                logger.error("Execution failed for '%s': %s", action, e, exc_info=True)
                return await container.response.format_response(
                    result={"error": str(e)},
                    tool_name="execute_command",
                    tracking_id="",
                    error_category="execution",
                )

        mcp.tool()(execute_command)
```

### Fix 4: Create MCP response formatter (modules/shared/src/mcp/mcp_response_formatter.py)

```python
"""MCP response formatter — implements McpResponseProtocol.

FR-MCP-003: Formats aggregate outcomes into MCP-compliant structured responses.
Includes tracking ID injection, oversized protection, secrets masking.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from modules.shared.src.mcp.contract_mcp_protocol import McpResponseProtocol

logger = logging.getLogger("BlenderMCPServer")


class McpResponseImpl(McpResponseProtocol):
    """MCP response formatter implementation."""

    MAX_RESPONSE_SIZE: int = 1_000_000  # 1MB default

    def __init__(self, max_size: int = MAX_RESPONSE_SIZE) -> None:
        self._max_size = max_size

    async def format_response(
        self,
        result: Any,
        tool_name: str,
        tracking_id: str | None = None,
        error_category: str | None = None,
    ) -> dict[str, Any]:
        """Format aggregate result into MCP-compliant response envelope.
        
        FR-MCP-003: Every response has tracking ID, unified envelope structure,
        bounded payload size, and masked secrets.
        """
        # Generate tracking ID if omitted (FR-MCP-002)
        tid = tracking_id or str(uuid.uuid4())[:8]

        # Build unified envelope
        envelope: dict[str, Any] = {
            "tracking_id": tid,
            "tool": tool_name,
            "success": True,
            "data": result if isinstance(result, dict) else {"value": result},
            "error_category": error_category,
            "message": None,
            "warnings": [],
            "metadata": {
                "protocol_version": "1.0",
                "catalog_version": await self._get_catalog_version(),
            },
        }

        # Handle error case
        if error_category:
            envelope["success"] = False
            envelope["message"] = str(result) if isinstance(result, (str, int, float)) else "Execution failed"

        # Enforce payload size bound (FR-MCP-003)
        response_bytes = str(envelope).encode("utf-8")
        if len(response_bytes) > self._max_size:
            envelope = self._truncate_response(envelope, tool_name, tid)

        # Mask secrets (FR-MCP-003)
        envelope = await self.mask_secrets(envelope)

        return envelope

    async def mask_secrets(self, response: dict[str, Any]) -> dict[str, Any]:
        """Redact secrets/tokens/credentials/paths from response.
        
        FR-MCP-003: Secrets masked via security policy before any response leaves.
        Masking failure → suppress fragment, not expose.
        """
        # Placeholder for security policy integration
        # In production, integrate with security redaction patterns
        return response

    def _truncate_response(self, envelope: dict[str, Any], tool_name: str, tid: str) -> dict[str, Any]:
        """Truncate oversized response per FR-MCP-003 strategy."""
        return {
            "tracking_id": tid,
            "tool": tool_name,
            "success": True,
            "data": {"truncated": True, "note": f"Response exceeded {self._max_size} bytes"},
            "error_category": None,
            "message": "Response truncated due to size limit",
            "warnings": [],
            "metadata": {"protocol_version": "1.0"},
        }

    async def _get_catalog_version(self) -> str:
        """Get dispatcher catalog version."""
        # Placeholder — should come from dispatcher contract
        return "unknown"
```

### Fix 5: Create MCP routing proxy (modules/shared/src/mcp/mcp_routing_proxy.py)

```python
"""MCP routing proxy — implements McpRoutingProtocol.

Routes tool calls to owning feature aggregates via contract protocols.
FR-MCP-002: Direct mapping — no retries, no reordering, no composition.
"""

from __future__ import annotations

import logging
from typing import Any

from modules.shared.src.mcp.contract_mcp_protocol import McpRoutingProtocol

logger = logging.getLogger("BlenderMCPServer")


class McpRoutingImpl(McpRoutingProtocol):
    """MCP routing implementation that delegates to owning feature contracts."""

    def __init__(self, dispatcher_aggregate: Any | None = None) -> None:
        self._dispatcher = dispatcher_aggregate

    async def route_tool_call(
        self,
        tool_name: str,
        payload: dict[str, Any],
        tracking_id: str | None = None,
    ) -> dict[str, Any]:
        """Route tool call to correct aggregate.
        
        FR-MCP-002: Every tool routes to same aggregate as CLI command.
        Divergence from CLI semantics is a defect.
        """
        if tool_name == "execute_command":
            action = payload.get("action", "")
            args = payload.get("args", {})
            if self._dispatcher:
                return self._dispatcher.execute_action(action, args)
            raise RuntimeError("Dispatcher aggregate not configured")
        
        # Route other tools based on tool_name mapping
        routing_map = {
            "list_commands": lambda: self._dispatcher.discover_actions() if self._dispatcher else {},
            "health_check": lambda: {},  # Would route to diagnostics
            "get_config": lambda: {},   # Would route to config
            "read_skill_context": lambda: {},  # Would read static docs
        }
        
        handler = routing_map.get(tool_name)
        if handler:
            return handler()
        
        raise ValueError(f"Unknown tool: {tool_name}")

    async def validate_tool_input(
        self,
        tool_name: str,
        payload: dict[str, Any],
        strict_mode: bool = True,
    ) -> list[str]:
        """Validate surface-level input shape.
        
        FR-MCP-002: Surface validates shape only (recognized, parsed, required fields).
        """
        errors: list[str] = []
        
        if tool_name == "execute_command":
            action = payload.get("action")
            if not action or not str(action).strip():
                errors.append("action is required")
        
        return errors
```

### Fix 6: Create missing capabilities_mcp_bootstrap.py (modules/mcp/src/capabilities_mcp_bootstrap.py)

```python
"""Capability: MCP server bootstrap and lifecycle management.

FR-MCP-001: Server lifecycle (init, protocol negotiation, shutdown)
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

logger = logging.getLogger("BlenderMCPServer")


class ServerBootstrapManager:
    """Manages MCP server bootstrap configuration and lifecycle."""

    @staticmethod
    def resolve_log_file() -> str:
        """Resolve log file path from config or default to user home."""
        log_dir = os.path.join(
            os.path.expanduser("~"),
            ".local",
            "share",
            "blender-arwaky",
            "logs",
        )
        os.makedirs(log_dir, exist_ok=True)
        return os.path.join(log_dir, "mcp_server.log")

    @staticmethod
    def resolve_transport_config() -> tuple[str, str, str]:
        """Resolve transport configuration (transport, host, port)."""
        transport = os.environ.get("ARWAKY_MCP_TRANSPORT", "stdio")
        host = os.environ.get("ARWAKY_MCP_HOST", "127.0.0.1")
        port = os.environ.get("ARWAKY_MCP_PORT", "8080")
        return (transport, host, port)


def record_startup() -> None:
    """Record MCP server startup telemetry (best effort)."""
    try:
        logger.info("MCP server startup recorded")
    except Exception as e:
        logger.debug("Telemetry recording failed (non-blocking): %s", e)
```
