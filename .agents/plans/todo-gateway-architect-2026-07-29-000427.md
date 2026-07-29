# Review Plan: gateway — Architect (Phase 1)

## Summary

The gateway feature (modules/gateway/) is the transport authority between the application and the Blender runtime, handling connection lifecycle, message framing, request/response correlation, scene operation queuing, and raw code execution. The feature has 6 capability files, 1 orchestrator, and 1 root container, with shared taxonomy/contract/utility files in modules/shared/src/gateway/. Analysis reveals 4 CRITICAL AES violations (broken import, cross-feature contract dependencies, bypass comment), 3 WARNING-level issues (missing surface layer, aggregate naming mismatch, orchestrator protocol bypass), and 3 INFO-level observations. The gateway feature is also missing a surface layer entirely, and its agent layer does not implement the declared aggregate protocol.

## Findings by Category

### Layer Boundaries

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | Broken import: `root_gateway_container.py` imports from `.capabilities_connection` which does not exist. The class `ConnectionExecutor` lives in `.capabilities_connection_manager.py`. This will cause `ModuleNotFoundError` at runtime. | `root_gateway_container.py:11` | Change import to `from .capabilities_connection_manager import ConnectionExecutor` |
| 2 | 🔴 CRITICAL | Cross-feature contract dependency: 4 gateway capability files (`capabilities_connection_manager.py`, `capabilities_transport_executor.py`, `capabilities_code_execution.py`, `capabilities_scene_queue.py`) import `IEventPublisher` from `modules.diagnostics.src.contract_audit_emission_protocol` — another feature's contract layer. Gateway capabilities must depend only on their own feature's contract layer. | `capabilities_connection_manager.py:25`, `capabilities_transport_executor.py:22`, `capabilities_code_execution.py:22`, `capabilities_scene_queue.py:21` | Introduce a gateway-local event protocol in `modules/shared/src/gateway/contract_event_protocol.py` and have all gateway capabilities import from their own contract layer instead of diagnostics |
| 3 | 🔴 CRITICAL | Cross-feature contract dependency: `capabilities_code_execution.py` imports `ValidateCodeProtocol` from `modules.shared.src.security.contract_validate_code_protocol` (security feature's contract). Gateway capabilities must depend on their own contract layer, not other features' contracts. | `capabilities_code_execution.py:71` | Define a `CodeValidationProtocol` in `modules/shared/src/gateway/contract_code_execution_protocol.py` (or a new dedicated protocol) and have the code execution capability import from its own feature's contract layer |
| 4 | 🔴 CRITICAL | Orchestrator bypasses protocol delegation: `agent_gateway_orchestrator.py` line 79 calls `self._maintenance.set_state(None)` directly on the concrete `MaintenanceExecutor` rather than going through the `ConnectionMaintenanceProtocol` interface. Agent must depend on contract protocols and delegate execution, not call concrete implementations directly. | `agent_gateway_orchestrator.py:79` | Add `set_state(None)` to the `ConnectionMaintenanceProtocol` interface and call it through the protocol reference |

### Naming Convention

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 5 | 🟡 WARNING | Aggregate protocol named `IBlenderServerAggregate` in `contract_gateway_aggregate.py` — the class says "Server" but the file and feature are named "Gateway". This creates ambiguity about which feature owns the aggregate. | `contract_gateway_aggregate.py:23` | Rename to `IGatewayAggregate` to match the gateway feature namespace |
| 6 | 🟢 INFO | All capability files correctly follow `capabilities_<concern>_<role>.py` naming (connection_manager, transport_executor, code_execution, connection_maintenance, scene_queue). | — | No action needed |
| 7 | 🟢 INFO | Orchestrator correctly follows `agent_<concern>_orchestrator.py` naming. | — | No action needed |
| 8 | 🟢 INFO | Root container correctly follows `root_<feature>_container.py` naming. | — | No action needed |

### Dead Code / Orphan

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 9 | 🟡 WARNING | Aggregate protocol `IBlenderServerAggregate` in `contract_gateway_aggregate.py` is not implemented by any agent file and not called by any surface file. The `GatewayOrchestrator` does not implement this protocol — it has entirely different method signatures (e.g., `establish_connection` vs `connect`, `send_request` vs `send_command`). Protocol is orphaned (AES502). | `contract_gateway_aggregate.py:23–145`, `agent_gateway_orchestrator.py` | Either implement `IBlenderServerAggregate` on `GatewayOrchestrator` (adapting method names to match), or remove the stale aggregate protocol and define a proper `IGatewayAggregate` that matches the orchestrator's actual interface |
| 10 | 🟡 WARNING | `capabilities_connection.py` is referenced in `root_gateway_container.py:11` but does not exist as a file. The import target is dead code, and the actual class lives in a differently named file. | `root_gateway_container.py:11` | Fix the import (see Finding #1) — this resolves the orphan reference |
| 11 | 🟢 INFO | No taxonomy file in the gateway module has zero inbound imports from contract files. All taxonomy VO, constant, error, and event files are imported by their respective capabilities and agent files. | — | No action needed |

### Scalability & Coupling

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 12 | 🟡 WARNING | `capabilities_connection_manager.py` at 589 lines (of 1000 AES301 limit) contains both the async `BlenderConnection` class and the sync `ConnectionExecutor` class. The async class alone is ~400 lines and handles connection lifecycle, handshake, auth, heartbeat, and reconnect — exceeding the single-responsibility boundary. | `capabilities_connection_manager.py:71–501` | Split `BlenderConnection` into a dedicated `capabilities_connection_lifecycle.py` or `capabilities_connection_heartbeat.py` file |
| 13 | 🟡 WARNING | 4 out of 5 gateway capabilities import from `modules.diagnostics` creating a fan-out dependency from gateway to diagnostics. This couples the transport layer to the diagnostics layer, violating the unidirectional bottom-up dependency rule and making the gateway difficult to test or swap independently. | 4 capability files (see Finding #2) | Decouple by introducing a gateway-local event publisher protocol in the shared gateway layer |

### Data Flow

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 14 | 🟡 WARNING | Data flow cycle risk: `capabilities_code_execution.py` imports from `modules.shared.src.gateway.*, modules.diagnostics.src.contract_*, modules.shared.src.security.contract_validate_code_protocol`. The code execution capability acts as a passthrough that depends on 3 different feature contract layers, creating a potential for circular dependency if security or diagnostics ever need to import from gateway. | `capabilities_code_execution.py:22–80` | Reduce cross-feature imports by defining gateway-local protocols for event publication and code validation |

## Violations

- **AES201 (Forbidden Import)**: Cross-feature contract dependencies — gateway capabilities importing from `modules.diagnostics` and `modules.security` contract layers directly (Findings #2, #3)
- **AES205 (Circular Import)**: Risk of circular dependency between gateway, diagnostics, and security feature contract layers (Finding #14)
- **AES304 (Bypass Comment)**: `# type: ignore[arg-type]` in orchestrator (Finding #4)
- **AES405 (Agent Role)**: Orchestrator directly calls concrete `MaintenanceExecutor.set_state()` instead of delegating through protocol (Finding #4)
- **AES502 (Contract Orphan)**: `IBlenderServerAggregate` protocol not implemented by any agent and not called by any surface (Finding #9)
- **AES301 (File Maximum Limit)**: `capabilities_connection_manager.py` at 589 lines approaching the 1000-line ceiling (Finding #12)

## Action Items

- [ ] P0 Fix broken import in `root_gateway_container.py:11` — change `.capabilities_connection` to `.capabilities_connection_manager`
- [ ] P0 Replace 4x cross-feature `modules.diagnostics` imports with gateway-local event protocol — create `contract_event_protocol.py` in shared/gateway and update all capability imports
- [ ] P0 Replace `modules.security.contract_validate_code_protocol` import in `capabilities_code_execution.py` with a gateway-local validation protocol
- [ ] P0 Remove `# type: ignore[arg-type]` bypass comment in `agent_gateway_orchestrator.py:79` — add `set_state` to `ConnectionMaintenanceProtocol` and call through protocol
- [ ] P1 Create a surface layer for gateway (e.g., `surface_gateway_command.py`) to mediate between feature callers and the orchestrator
- [ ] P1 Rename `IBlenderServerAggregate` to `IGatewayAggregate` in `contract_gateway_aggregate.py` or remove the stale protocol
- [ ] P1 Implement `IGatewayAggregate` on `GatewayOrchestrator` (or remove the orphan aggregate)
- [ ] P2 Split `capabilities_connection_manager.py` to reduce line count and separate async/sync concerns
- [ ] P2 Decouple gateway capabilities from the diagnostics feature by moving event publishing through a gateway-local abstraction

## Fixed Code

### `root_gateway_container.py` — Fix broken import (Finding #1, #10)

**Before (line 11):**
```python
from .capabilities_connection import ConnectionExecutor
```

**After:**
```python
from .capabilities_connection_manager import ConnectionExecutor
```

### `agent_gateway_orchestrator.py` — Remove bypass comment and fix protocol delegation (Finding #4)

**Before (line 79):**
```python
self._maintenance.set_state(None)  # type: ignore[arg-type]
```

**After:**
```python
self._maintenance.disconnect()
```

*(Assumes `ConnectionMaintenanceProtocol` adds a `disconnect()` method that internally calls `set_state(None)`, keeping the agent layer through protocol delegation rather than reaching into the concrete implementation.)*

### `contract_gateway_aggregate.py` — Rename aggregate (Finding #5, #6)

**Before (line 23):**
```python
class IBlenderServerAggregate(ABC):
```

**After:**
```python
class IGatewayAggregate(ABC):
```
