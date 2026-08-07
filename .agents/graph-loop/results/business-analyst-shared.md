# Plan: shared — Business-Analyst

## Summary

The `modules/shared` module contains 190 Python files across 15 sub-domains (common, config, asset, cli, diagnostics, dispatcher, gateway, job, launcher, mcp, object, render, scene, security, telemetry). It defines the taxonomy (VOs, entities, errors, events, constants), contracts (protocols, aggregates), and shared utilities that all feature modules depend on. The module is well-structured overall — branded NewType VOs, frozen dataclasses, ABC-based protocol contracts. However, there are critical architectural violations (implementation code in shared, non-Exception error types, duplicate VOs) and several structural inconsistencies that need resolution before downstream features can safely depend on this module.

---

## Findings

### Requirements Clarity

| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🔴 CRITICAL | FRD.md missing — no requirements document exists for the shared module | `modules/shared/FRD.md` (NOT FOUND) | Create FRD.md defining all functional requirements (FR IDs, descriptions, acceptance criteria) for every contract protocol, aggregate, and taxonomy type in the module |
| 2 | 🟡 WARNING | No FR reference in most contract files — only `dispatch_error.py`, `config_settings_metadata.py`, and security protocols reference FR IDs | `modules/shared/src/contract_*.py` (all) | Add FR ID reference in docstring of every contract and aggregate file (e.g., `"""FR-XXX-001: Description."""`) |
| 3 | 🟡 WARNING | `__init__.py` re-exports ~250 symbols but doesn't document the full public API contract or versioning policy | `modules/shared/src/__init__.py` | Document the public API surface and establish versioning/compatibility rules |

### Business Flow

| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 4 | 🔴 CRITICAL | Implementation classes (`McpResponseImpl`, `McpRoutingImpl`) live in shared/mcp instead of a feature's capabilities layer — contracts in shared should define behavior only | `mcp/mcp_response_formatter.py:14`, `mcp/mcp_routing_proxy.py:11` | Move `McpResponseImpl` and `McpRoutingImpl` to `modules/mcp/src/capabilities/` |
| 5 | 🔴 CRITICAL | `RenderError` and `SceneError` are dataclasses, not Exception subclasses — they cannot be raised/caught in error flows | `render/taxonomy_render_error.py:31`, `scene/taxonomy_scene_error.py:28` | Change `RenderError` and `SceneError` to subclass Exception (like `GatewayError`, `LauncherError`) |
| 6 | 🔴 CRITICAL | Duplicate VOs in gateway — two overlapping versions of ConnectionStatus, ConnectionConfig, ExecutionResult | `gateway/taxonomy_gateway_vo.py:34+` (new) vs `gateway/taxonomy_gateway_vo.py:140+` (old) | Consolidate: remove legacy VOs (`ConnectionStatus`, `ExecutionResult`, `CommandResult`, `TaskStatus`, `ServerMetrics`, `CodeSecurityPolicy`, `QueuedOperation`, `ServerConfig`, `ServerCommandSpec`, `ConnectionConfig`, `RetryPolicy`, `HeartbeatConfig`, `QueueConfig`, `TaskManagerConfig`) and keep the FR-annotated VOs (`ConnectionStatusVO`, `ConnectionConfigVO`, `CodeExecutionOutcomeVO`, etc.) |
| 7 | 🟡 WARNING | `utility_routing_proxy.py` duplicates logic from `mcp_routing_proxy.py` — same `route_tool_call` function exists in both | `mcp/utility_routing_proxy.py:19-51` vs `mcp/mcp_routing_proxy.py:17-45` | Remove the standalone utility version; routing belongs in the implementation class, not duplicated |
| 8 | 🟡 WARNING | `utility_response_formatter.py` duplicates `McpResponseImpl` logic — same envelope/truncation code | `mcp/utility_response_formatter.py` vs `mcp/mcp_response_formatter.py` | Remove the standalone utility version; keep the class-based implementation |

### Logic Implementation

| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 9 | 🟡 WARNING | `BlenderSocketClient` is a stateful class with connection state in a utility layer file — utility must be stateless standalone functions only (AES404) | `gateway/utility_socket_client.py:17` | Move `BlenderSocketClient` to `gateway/src/capabilities/` or refactor into stateless functions with explicit state passing |
| 10 | 🟡 WARNING | `utility_config_loader.py` contains domain-specific config loading logic — utility layer should not contain business decisions | `gateway/utility_config_loader.py:1-170` | Move `load_server_config()` to capabilities or the config feature; keep only stateless helpers in utility |
| 11 | 🟡 WARNING | `utility_validator_checker.py` contains a command catalog and domain-specific validation logic, not a stateless utility | `gateway/utility_validator_checker.py:1-195` | Move command catalog and `validate_command_args()` to capabilities; keep only pure helpers in utility |
| 12 | 🟡 WARNING | `mcp/__init__.py` imports implementation classes (`McpResponseImpl`, `McpRoutingImpl`) — shared should not expose implementations | `mcp/__init__.py:11-12` | Remove implementation imports from shared's `__init__.py`; implementations belong to the feature module |
| 13 | 🟡 WARNING | `taxonomy_mcp_event.py` explicitly states it is unused by any layer | `mcp/taxonomy_mcp_event.py:1-6` | Remove or mark with `# TODO(FR-MCP-003): implement event publishing when feature is complete` |
| 14 | 🟡 WARNING | `# noqa: F401` on 5 imports in `mcp/__init__.py` — suppressed imports indicate unused or incorrectly placed symbols | `mcp/__init__.py:4,7,10,13,16` | Remove the suppressed imports if they're truly unused; if needed, ensure proper re-export without noqa |

### Testability & Acceptance

| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 15 | 🟡 WARNING | `pyproject.toml` package list doesn't match actual directories — lists `["common", "config", "scene", "object", "render", "asset_io", "asset_provider", "job", "telemetry"]` but actual dirs include `asset, cli, diagnostics, dispatcher, gateway, launcher, mcp, security` | `modules/shared/pyproject.toml:12-13` | Update `packages` list to match actual directory structure |
| 16 | 🟢 INFO | No test files exist in the shared module | `modules/shared/tests/` (MISSING) | Add contract tests for all protocols, unit tests for utility functions, and type-checking tests for VOs |
| 17 | 🟡 WARNING | `mask_secrets()` in both `mcp_response_formatter.py` and `utility_response_formatter.py` are placeholders with no actual implementation | `mcp/mcp_response_formatter.py:77-81`, `mcp/utility_response_formatter.py:38-45` | Implement or delegate to `security/utility_security_redactor.py:redact_sensitive()` which has real logic |

### Traceability (FRD→Code)

| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 18 | 🔴 CRITICAL | No FRD exists → zero traceability from requirements to code | Entire shared module | Create FRD.md with FR IDs mapped to contract/aggregate/taxonomy files |
| 19 | 🟡 WARNING | `taxonomy_core_vo.py` defines 90+ types in a single file — hard to trace which type belongs to which feature FR | `common/taxonomy_core_vo.py` (240 lines) | Split into domain-specific VO files or add section headers mapping types to FR IDs |
| 20 | 🟡 WARNING | `taxonomy_gateway_vo.py` contains 30+ VOs/VO-like classes — no FR grouping visible | `gateway/taxonomy_gateway_vo.py` (290+ lines) | Group by FR (e.g., FR-GWY-001 connection, FR-GWY-003 transport) with section headers |
| 21 | 🟡 WARNING | Naming inconsistency: some aggregates use `I` prefix (`IAssetAggregate`, `IConfigAggregate`) while others don't (`AssetDownloadProtocol`, `ConnectionProtocol`) | Multiple contract files | Standardize: all aggregates use `I` prefix, all protocols use `Protocol` suffix |

---

## Violations

- **AES304**: `# noqa: F401` bypass comments in `mcp/__init__.py` (5 occurrences)
- **AES404**: `BlenderSocketClient` (stateful class) in utility layer (`utility_socket_client.py`)
- **AES404**: `load_server_config` with domain logic in utility layer (`utility_config_loader.py`)
- **AES404**: Command catalog + domain validation in utility layer (`utility_validator_checker.py`)
- **AES204**: `McpResponseImpl` and `McpRoutingImpl` in shared/contract layer (implementation code bypassing layer boundary)
- **AES401**: `DispatchErrorCategory` as class with `Final[str]` attributes in error file instead of constant file
- **Naming**: `ExecutionStatus = str` and `TaskState = str` as type aliases in VO file instead of constant file
- **AES302**: `asset/utility/__init__.py` is completely empty (0 lines)
- **AES303**: `common/taxonomy_app_config_vo.py` is a placeholder stub — single static `placeholder()` method

---

## Action Items

- [ ] 🔴 Create `modules/shared/FRD.md` with all FR IDs, descriptions, and acceptance criteria
- [ ] 🔴 Move `McpResponseImpl` and `McpRoutingImpl` out of shared to `modules/mcp/src/capabilities/`
- [ ] 🔴 Fix `RenderError` and `SceneError` to subclass Exception
- [ ] 🔴 Consolidate duplicate gateway VOs — remove legacy, keep FR-annotated versions
- [ ] 🟡 Update `pyproject.toml` package list to match actual directories
- [ ] 🟡 Move `BlenderSocketClient` from utility to capabilities
- [ ] 🟡 Remove `# noqa: F401` and fix import issues in `mcp/__init__.py`
- [ ] 🟡 Remove duplicate utility functions that mirror implementation classes
- [ ] 🟡 Standardize aggregate naming (all use `I` prefix)
- [ ] 🟡 Add FR ID references to all contract and aggregate file docstrings
- [ ] 🟢 Add contract tests for all protocols
- [ ] 🟢 Implement or wire `mask_secrets()` to real redaction utility

---

## Fixed Code

### 1. `modules/shared/src/render/taxonomy_render_error.py` — Fix non-Exception error

```python
"""Render taxonomy errors."""

from __future__ import annotations

from enum import Enum
from typing import NewType

from ..common.taxonomy_core_vo import Prompt

# Branded tuple type for render error detail chains
RenderErrorDetails = NewType("RenderErrorDetails", tuple[Prompt, ...])


class RenderErrorCategory(str, Enum):
    """Stable render error categories."""

    RENDER_OUTPUT = "render_output"
    CAMERA_SETUP = "camera_setup"
    SECURITY_VIOLATION = "security_violation"
    CAPACITY = "capacity"
    TIMEOUT = "timeout"
    VALIDATION = "validation"
    ASSET_NOT_FOUND = "asset_not_found"
    ENVIRONMENT_STATE = "environment_state"
    SCENE_STATE = "scene_state"
    EXECUTION = "execution"


class RenderError(Exception):
    """Render domain error — raised for render operation failures."""

    def __init__(
        self,
        category: RenderErrorCategory,
        message: Prompt,
        retryable: bool = False,
        details: RenderErrorDetails | None = None,
    ) -> None:
        self.category = category
        self.retryable = retryable
        self.details = details or RenderErrorDetails(())
        super().__init__(f"[{category.value}] {message}")
```

### 2. `modules/shared/src/scene/taxonomy_scene_error.py` — Fix non-Exception error

```python
"""Scene taxonomy errors."""

from __future__ import annotations

from enum import Enum
from typing import NewType

from ..common.taxonomy_core_vo import Prompt

# Branded tuple type for error detail chains
SceneErrorDetails = NewType("SceneErrorDetails", tuple[Prompt, ...])


class SceneErrorCategory(str, Enum):
    """Stable scene error categories."""

    CONNECTION = "connection"
    TIMEOUT = "timeout"
    SCENE_STATE = "scene_state"
    PROTECTION = "protection"
    VALIDATION = "validation"
    CONFIRMATION = "confirmation"
    DELEGATED_DELETION = "delegated_deletion"


class SceneError(Exception):
    """Scene domain error — raised for scene operation failures."""

    def __init__(
        self,
        category: SceneErrorCategory,
        message: Prompt,
        retryable: bool = False,
        details: SceneErrorDetails | None = None,
    ) -> None:
        self.category = category
        self.retryable = retryable
        self.details = details or SceneErrorDetails(())
        super().__init__(f"[{category.value}] {message}")
```

### 3. `modules/shared/src/mcp/__init__.py` — Remove implementation imports

```python
"""MCP taxonomy — VOs, constants, contracts for MCP surface type safety.

Implementations (McpResponseImpl, McpRoutingImpl) live in
modules/mcp/src/capabilities/, NOT in shared.
"""

from .contract_mcp_protocol import (
    McpResponseProtocol,
    McpRoutingProtocol,
    McpSchemaProtocol,
)
from .taxonomy_mcp_constant import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_SERVER_NAME,
    TOOL_EXECUTE_COMMAND,
    TOOL_HEALTH_CHECK,
    TOOL_LIST_COMMANDS,
    TOOL_READ_SKILL,
)
from .taxonomy_mcp_event import McpEvent, McpEventKind
from .taxonomy_mcp_vo import McpResponse, McpServerBootstrapVO, McpServerConfig, McpToolDef
from .utility_routing_proxy import normalize_payload, route_tool_call, validate_execute_command_input
from .utility_response_formatter import envelope_with_tracking, mask_secrets, truncate_oversized

__all__ = [
    "DEFAULT_SERVER_NAME",
    "DEFAULT_HOST",
    "DEFAULT_PORT",
    "TOOL_EXECUTE_COMMAND",
    "TOOL_HEALTH_CHECK",
    "TOOL_LIST_COMMANDS",
    "TOOL_READ_SKILL",
    "McpEventKind",
    "McpEvent",
    "McpToolDef",
    "McpServerConfig",
    "McpServerBootstrapVO",
    "McpResponse",
    "McpResponseProtocol",
    "McpRoutingProtocol",
    "McpSchemaProtocol",
    "envelope_with_tracking",
    "truncate_oversized",
    "mask_secrets",
    "normalize_payload",
    "route_tool_call",
    "validate_execute_command_input",
]
```
