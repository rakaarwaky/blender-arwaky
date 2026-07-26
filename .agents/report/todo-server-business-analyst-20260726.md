# Review Report: Server Feature — Business Analyst

## Summary

The Server Feature requirements in `FRD.md` define a robust, secure, and resilient communication bridge between external AI clients and Blender, covering connection lifecycle management (FR-001), AST-validated custom code execution (FR-002), and serialized standard command dispatch (FR-003). While the current implementation in `modules/server` establishes core TCP socket communication, AST pre-filtering, and queuing primitives, a business analyst audit reveals critical gaps in security enforcement (missing file boundary checks and execution timeouts), protocol compliance (missing handshake/token authentication and version verification), resilience (stale status reporting and lack of non-scene immediate dispatch), and AES architectural rules (file naming policy and class co-location). Addressing these issues will ensure full traceability to FRD commitments and high system reliability.

## Findings by Category

### Requirements Clarity & Completeness

| #   | Severity | Issue | Location | Recommendation |
| --- | -------- | ----- | -------- | -------------- |
| 1 | 🔴 **CRITICAL** | Code execution timeout (30s default) is defined in FR-002 but not enforced during execution | [capabilities_code_execution_adapter.py](file:///home/raka/mcp-arwaky/blender-arwaky/modules/server/src/capabilities_code_execution_adapter.py#L107-L113) | Wrap `run_in_executor` with `asyncio.wait_for(..., timeout=timeout_s)` and raise `ExecutionTimeoutError`. |
| 2 | 🔴 **CRITICAL** | Initial handshake version verification and token authentication required by FR-001 are omitted | [capabilities_blender_connection.py](file:///home/raka/mcp-arwaky/blender-arwaky/modules/server/src/capabilities_blender_connection.py#L96-L112) | Implement handshake protocol in `connect()` to verify protocol version and authenticate token before marking status `connected`. |
| 3 | 🟡 **WARNING** | Restricted allowed file directory enforcement (FR-002) is absent from AST validation | [capabilities_code_execution_adapter.py](file:///home/raka/mcp-arwaky/blender-arwaky/modules/server/src/capabilities_code_execution_adapter.py#L219-L267) | Add AST visitors to detect file write operations (e.g. `open(..., 'w')`, `Path.write_text`) outside user-configured allowed directories. |
| 4 | 🟡 **WARNING** | Local-only connection default restriction (FR-001) is not validated | [capabilities_blender_connection.py](file:///home/raka/mcp-arwaky/blender-arwaky/modules/server/src/capabilities_blender_connection.py#L243-L256) | Validate host against allowed bindings (`localhost`/`127.0.0.1`) unless remote access is explicitly flagged in config. |
| 5 | 🟢 **INFO** | Disconnect state `closed` and pending operation cancellation with `ConnectionClosedError` missing | [capabilities_blender_connection.py](file:///home/raka/mcp-arwaky/blender-arwaky/modules/server/src/capabilities_blender_connection.py#L139-L150) | Update state to `closed` on graceful disconnect and signal queue/task manager to reject pending ops with `ConnectionClosedError`. |

### Testability & Acceptance Criteria

| #   | Severity | Issue | Location | Recommendation |
| --- | -------- | ----- | -------- | -------------- |
| 1 | 🔴 **CRITICAL** | `execute_blender_code` error handler returns `Prompt` object instead of `ExecutionResult` on failure | [capabilities_code_execution_adapter.py](file:///home/raka/mcp-arwaky/blender-arwaky/modules/server/src/capabilities_code_execution_adapter.py#L134) | Return standard `ExecutionResult(status="error", ...)` to honor contract return type and enable automated assertions. |
| 2 | 🟡 **WARNING** | `ServerOrchestrator.get_status()` returns hardcoded `state="connected"` ignoring actual connection state | [agent_server_orchestrator.py](file:///home/raka/mcp-arwaky/blender-arwaky/modules/server/src/agent_server_orchestrator.py#L72-L82) | Delegate `get_status()` to `await self._connection.get_status()` to accurately report `disconnected`, `reconnecting`, or `failed`. |
| 3 | 🟡 **WARNING** | Async task cancellation criteria specified in QA Checklist cannot be tested via Aggregate API | [agent_server_orchestrator.py](file:///home/raka/mcp-arwaky/blender-arwaky/modules/server/src/agent_server_orchestrator.py#L36-L50) | Expose `cancel_task(task_id)` on `IBlenderServerAggregate` and `ServerOrchestrator`. |
| 4 | 🟢 **INFO** | Execution output size limit (10KB) is hardcoded instead of being configurable per FRD | [capabilities_code_execution_adapter.py](file:///home/raka/mcp-arwaky/blender-arwaky/modules/server/src/capabilities_code_execution_adapter.py#L119) | Inject `max_output_bytes` via configuration port/VO into `CodeExecutionAdapter`. |

### Scope & Dependencies

| #   | Severity | Issue | Location | Recommendation |
| --- | -------- | ----- | -------- | -------------- |
| 1 | 🟡 **WARNING** | Scene vs. non-scene command bypass logic (FR-003) is not evaluated during command serialization | [agent_server_orchestrator.py](file:///home/raka/mcp-arwaky/blender-arwaky/modules/server/src/agent_server_orchestrator.py#L206) | Inspect command metadata (`is_scene_operation`) to allow read-only/non-scene commands to bypass FIFO execution queue. |
| 2 | 🟡 **WARNING** | Command response payload truncation (FR-003) is missing from `BlenderCommandAdapter` | [capabilities_blender_command_adapter.py](file:///home/raka/mcp-arwaky/blender-arwaky/modules/server/src/capabilities_blender_command_adapter.py#L98-L102) | Apply output truncation check on command response payload matching code execution adapter behavior. |
| 3 | 🟢 **INFO** | Async task state tracking duplicated across `CodeExecutionAdapter` and `TaskManager` | [capabilities_code_execution_adapter.py](file:///home/raka/mcp-arwaky/blender-arwaky/modules/server/src/capabilities_code_execution_adapter.py#L74) | Consolidate async task lifecycle management into `TaskManager` capability and remove ad-hoc `_tasks` dict from `CodeExecutionAdapter`. |

### Traceability (FRD ↔ Code)

| #   | Severity | Issue | Location | Recommendation |
| --- | -------- | ----- | -------- | -------------- |
| 1 | 🔴 **CRITICAL** | FR-001 Handshake & Authentication rules mapped to non-existent handshake methods | [FRD.md](file:///home/raka/mcp-arwaky/blender-arwaky/modules/server/FRD.md#L24) / [capabilities_blender_connection.py](file:///home/raka/mcp-arwaky/blender-arwaky/modules/server/src/capabilities_blender_connection.py#L78) | Add handshake protocol exchange to `capabilities_blender_connection.py`. |
| 2 | 🔴 **CRITICAL** | FR-002 Code Execution 30s Timeout rule unmapped in synchronous execution wrapper | [FRD.md](file:///home/raka/mcp-arwaky/blender-arwaky/modules/server/FRD.md#L46) / [capabilities_code_execution_adapter.py](file:///home/raka/mcp-arwaky/blender-arwaky/modules/server/src/capabilities_code_execution_adapter.py#L107) | Add timeout wrapper to code executor. |
| 3 | 🟡 **WARNING** | FR-003 Sequential scene operation constraint forces non-scene operations into queue | [FRD.md](file:///home/raka/mcp-arwaky/blender-arwaky/modules/server/FRD.md#L78) / [agent_server_orchestrator.py](file:///home/raka/mcp-arwaky/blender-arwaky/modules/server/src/agent_server_orchestrator.py#L206) | Bypass queue for non-scene operations. |

## Violations (if any)

- **AES102 (Suffix Rules Violation)**:
  - File `capabilities_blender_connection.py` uses suffix `_connection`, which is not in the allowed capabilities suffix list (`_adapter`, `_connector`, `_client`, etc.).
  - *Recommendation*: Rename or refine suffix policy if required, e.g., `capabilities_blender_connection_adapter.py` or `capabilities_blender_socket_connector.py`.
- **AES405 (Agent Role Violation)**:
  - `ServerOrchestrator.__init__` uses loose `Any` typing for `code_executor` parameter instead of contract protocol `ICodeExecutionProtocol`.
  - `ServerOrchestrator` maintains fallback state (`_tasks`) instead of delegating entirely to capabilities via contract abstractions.
- **Co-located Capability Classes**:
  - `capabilities_blender_command_adapter.py` defines both `BlenderCommandAdapter` and `ExecutionQueue`.
  - `capabilities_code_execution_adapter.py` defines both `CodeExecutionAdapter` and `TaskManager`.

## Action Items

- [ ] 🔴 **P0** Enforce 30s timeout in `execute_blender_code` via `asyncio.wait_for` and raise `ExecutionTimeoutError`.
- [ ] 🔴 **P0** Fix return type in `CodeExecutionAdapter.execute_blender_code` to return `ExecutionResult` on exception instead of `Prompt`.
- [ ] 🔴 **P0** Implement initial handshake verification (version compatibility + token auth) in `BlenderConnection.connect()`.
- [ ] 🟡 **P1** Update `ServerOrchestrator.get_status()` to delegate to `self._connection.get_status()` instead of returning hardcoded values.
- [ ] 🟡 **P1** Add directory restriction AST checks to `CodeExecutionAdapter._validate_code_ast()` for file writing operations.
- [ ] 🟡 **P1** Allow non-scene commands (e.g. `get_scene_info`) to bypass execution queue serialization per FR-003.
- [ ] 🟡 **P1** Expose task cancellation API on `IBlenderServerAggregate` and `ServerOrchestrator`.
- [ ] 🟢 **P2** Clean up co-located capability classes and fix type annotations in `ServerOrchestrator`.

## Gap Analysis Table

| Current State | Issue | Recommendation | Priority |
| ------------- | ----- | -------------- | -------- |
| Code execution has no runtime timeout wrapper in adapter | Execution can hang indefinitely if Blender locks up | Wrap execution in `asyncio.wait_for(timeout=30.0)` | 🔴 CRITICAL |
| Connection setup performs raw socket connect only | No handshake version or token authentication verified | Implement handshake message exchange on connect | 🔴 CRITICAL |
| `execute_blender_code` exception fallback returns `Prompt` object | Breaks `ExecutionResult` contract return type | Return `ExecutionResult(status="error", ...)` | 🔴 CRITICAL |
| `ServerOrchestrator.get_status()` returns static `"connected"` state | Obscures actual socket connection failures or reconnect states | Delegate to `_connection.get_status()` | 🟡 WARNING |
| AST validator checks module/function denylist only | File write operations outside allowed dir are not blocked | Add AST visitors to check file write paths | 🟡 WARNING |
| All commands unconditionally enqueued in `ServerOrchestrator` | Non-scene read-only commands delayed unnecessarily | Check command schema `is_scene_operation` before queueing | 🟡 WARNING |
| Duplicate task state logic in `CodeExecutionAdapter` and `TaskManager` | Maintenance overhead and fragmented status tracking | Refactor adapter to use `TaskManager` exclusively | 🟢 INFO |
