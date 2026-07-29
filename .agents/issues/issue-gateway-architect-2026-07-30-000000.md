`.agents/issues/issue-gateway-architect-2026-07-30-000000.md`

```markdown
# Issue: gateway — Architectural Review & Refactoring

## Summary
The `modules/gateway` feature has several architectural violations that weaken AES layering, dependency inversion, and FRD compliance. The most severe issues are: a utility-layer file containing a stateful class and importing a contract; gateway-owned security validation logic that should be delegated to the Security feature; missing aggregate contract for the gateway orchestrator; broken or incomplete composition-root wiring; and capability implementations that contain placeholder/nonfunctional flow control for connection handshake, transport framing, and scene-queue serialization. There are also orphaned async capability/contract implementations, primitive-heavy contract signatures, and duplicated command-catalog concerns. These issues should be fixed before extending the gateway feature or wiring it into surface layers.

## Findings by Category

### Layer Boundaries
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | `utility_scene_coordinator.py` is a Utility-layer file but contains a stateful class (`SceneCoordinatorUtility`) and imports `SceneQueueProtocol`. Utility must contain stateless standalone functions only and must not import Contract, Capabilities, Agent, Surface, or Root. AES201/AES404. | `modules/gateway/src/utility_scene_coordinator.py:1` | Delete this file. Let `GatewayOrchestrator` depend directly on `SceneQueueProtocol`, or move a private helper into the agent file if absolutely necessary. Do not create a utility class. |
| 2 | 🔴 CRITICAL | `CodeExecutionAdapter` performs security validation directly via `validate_code_ast()` from gateway utility. FR-GWY-005 requires gateway to delegate code validation to the security policy feature; gateway must never perform its own validation. | `modules/gateway/src/capabilities_code_execution.py:CodeExecutionAdapter.execute_blender_code` | Remove direct AST validation from gateway. Inject and delegate to `CodeValidationProtocol`/Security feature. Move AST policy implementation into Security capabilities, not gateway utility. |
| 3 | 🔴 CRITICAL | `GatewayOrchestrator` receives `SceneCoordinatorUtility` from the root container while its constructor type hint declares `SceneQueueProtocol`. The concrete utility class does not implement the protocol ABC. This breaks dependency inversion and type safety. | `modules/gateway/src/root_gateway_container.py:GatewayContainer.__init__`, `modules/gateway/src/agent_gateway_orchestrator.py:GatewayOrchestrator.__init__` | Pass `SceneQueueExecutor` directly, or make the dependency explicitly a `SceneQueueProtocol` implementation. Remove the coordinator indirection. |
| 4 | 🟡 WARNING | `root_gateway_container.py` imports concrete `CodeValidator` from the Security feature and passes it to `CodeExecutionExecutor`, but there is no visible guarantee that `CodeValidator` implements gateway-local `CodeValidationProtocol`. | `modules/gateway/src/root_gateway_container.py:7` | Introduce an adapter in Root that implements `CodeValidationProtocol`, or ensure `CodeValidator` explicitly implements the gateway contract. Root may wire concrete classes, but consumers must depend on contracts. |
| 5 | 🟡 WARNING | `utility_schema_helper.py` contains a domain-specific command catalog (`_COMMAND_CATALOG`) and command metadata. This is business/domain metadata, not low-level technical mechanics. Utility should remain stateless and domain-agnostic. | `modules/shared/src/gateway/utility_schema_helper.py:_COMMAND_CATALOG` | Move command catalog metadata to Taxonomy constants/VOs or a dedicated capability/catalog service. Keep only stateless validation helpers in Utility. |
| 6 | 🟡 WARNING | `taxonomy_command_catalog_constant.py` contains a `CommandCatalog` class. Constant files must contain compile-time constants only. AES401. | `modules/shared/src/common/taxonomy_command_catalog_constant.py:CommandCatalog` | Remove the class from the constant file. Keep `COMMAND_CATALOG` and `ACTION_NAMES` constants only; move wrapper behavior to Utility or Capabilities if needed. |
| 7 | 🟢 INFO | Gateway contains both sync and async capability implementations in the same files. This is not an AES breach by itself, but it increases coupling and makes transport strategy harder to evolve. | `modules/gateway/src/capabilities_connection_manager.py`, `modules/gateway/src/capabilities_code_execution.py`, `modules/gateway/src/capabilities_scene_queue.py`, `modules/gateway/src/capabilities_transport_executor.py` | Consider splitting async/sync implementations into separate capability files or selecting one runtime strategy for the gateway feature. |

### Naming Convention
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | `capabilities_connection_manager.py` uses role `manager`, which is not in the documented capabilities role list, and the main class is `ConnectionExecutor`. File name and class role are mismatched. | `modules/gateway/src/capabilities_connection_manager.py:1` | Rename to `capabilities_connection_executor.py` or another approved role suffix matching the implemented behavior. |
| 2 | 🟡 WARNING | `capabilities_scene_queue.py` names the concern but not the role. The concrete class is `SceneQueueExecutor`. | `modules/gateway/src/capabilities_scene_queue.py:1` | Rename to `capabilities_scene_queue_executor.py`. |
| 3 | 🟡 WARNING | `capabilities_code_execution.py` contains both `CodeExecutionAdapter` and `CodeExecutionExecutor`; the filename does not express a clear role. | `modules/gateway/src/capabilities_code_execution.py:1` | Split into `capabilities_code_execution_adapter.py` and `capabilities_code_execution_executor.py`, or rename according to the primary retained role. |
| 4 | 🟡 WARNING | Contract naming is inconsistent: some protocols use `I<Name>Protocol`, others use `<Name>Protocol`. Project convention expects `I<Name>Protocol`. | `modules/shared/src/gateway/contract_code_execution_protocol.py`, `modules/shared/src/gateway/contract_connection_protocol.py`, `modules/shared/src/gateway/contract_transport_protocol.py` | Standardize all contract interfaces to `I<Name>Protocol` or migrate legacy `I*` names to a single convention. |
| 5 | 🟢 INFO | `utility_scene_coordinator.py` uses role `coordinator`, which is not in the Utility role list, and the class name `SceneCoordinatorUtility` mixes layer/role naming. | `modules/gateway/src/utility_scene_coordinator.py:1` | Remove the file. If coordination logic remains, it belongs in Agent as a private helper, not Utility. |

### Dead Code / Orphan
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | Async capability implementations are exported but not wired in `GatewayContainer`: `BlenderConnection`, `BlenderCommandAdapter`, `CodeExecutionAdapter`, `OperationQueue`. AES503 risk. | `modules/gateway/src/__init__.py`, `modules/gateway/src/root_gateway_container.py` | Either wire these capabilities through an alternate async container/entry, or remove them if they are legacy/unused. |
| 2 | 🟡 WARNING | Async-oriented contracts are not consumed by the current gateway agent/container: `IBlenderConnectionProtocol`, `IBlenderCommandProtocol`, `ICodeExecutionProtocol`, `IOperationQueueProtocol`. AES502 risk. | `modules/shared/src/gateway/contract_connection_protocol.py`, `modules/shared/src/gateway/contract_transport_protocol.py`, `modules/shared/src/gateway/contract_code_execution_protocol.py`, `modules/shared/src/gateway/contract_scene_queue_protocol.py` | Remove unused contracts or create the consuming agent/container/surface that justifies them. |
| 3 | 🟢 INFO | Several gateway events are defined but not emitted anywhere in the visible gateway implementation: `ConnectionStateChanged`, `ConnectionReconnectAttempted`, `ConnectionReconnectFailed`, `CodeExecutionFailed`, `SecurityViolationDetected`, `TaskStarted`, `TaskTimedOut`, `CommandFailed`, `CommandTimedOut`. | `modules/shared/src/gateway/taxonomy_gateway_event.py` | Emit required FRD events or remove unused events until they are needed. |
| 4 | 🟢 INFO | Internal dataclasses `TaskEntry` and `OperationState` are exported from the package `__init__.py`. They appear to be implementation details. | `modules/gateway/src/__init__.py` | Remove internal types from public exports unless they are intentionally part of the public API. |

### Scalability & Coupling
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | `SceneQueueExecutor` does not implement serialized execution. `_processing` is never set to `True`, no worker processes the queue, and mutating operations will wait until timeout. `_execute_directly()` returns placeholder success without executing read-only operations. FR-GWY-004 is not satisfied. | `modules/gateway/src/capabilities_scene_queue.py:SceneQueueExecutor` | Implement a real queue processor or serialize execution with a lock/worker. Mutating operations must execute one at a time; read-only operations must execute through a real transport/command path. Fail deterministically on disconnect, depth limit, and wait timeout. |
| 2 | 🔴 CRITICAL | `ConnectionExecutor` creates a socket but does not wire it into `TransportExecutor` before using `TransportProtocol.send_request()` for handshake/auth. `_perform_handshake()` also swallows transport errors and returns default protocol/capabilities, masking connection failures. | `modules/gateway/src/capabilities_connection_manager.py:ConnectionExecutor.establish_connection`, `ConnectionExecutor._perform_handshake` | Set the socket on `TransportExecutor` before handshake, or make `ConnectionExecutor` own framing directly. Propagate transport/parse/timeout errors. Do not silently fallback to default protocol compatibility. |
| 3 | 🔴 CRITICAL | `CodeExecutionAdapter` creates, tracks, polls, cancels, and expires background tasks. FR-GWY-005 explicitly says gateway never creates/tracks/expires background task records; background task lifecycle belongs to the Job feature. | `modules/gateway/src/capabilities_code_execution.py:CodeExecutionAdapter.create_task`, `get_task`, `poll_task_result`, `cancel_async_task`, `cleanup_expired` | Remove task lifecycle from gateway. Gateway should transport code execution and return a task handoff reference produced by Job. Use Job contracts/aggregates for lifecycle management. |
| 4 | 🟡 WARNING | `MaintenanceExecutor` does not emit reconnection, heartbeat failure, or state-change events. FR-GWY-002 requires observability events for reconnection attempts and connection state transitions. | `modules/gateway/src/capabilities_connection_maintenance.py:MaintenanceExecutor` | Inject `IEventPublisher` and emit `ConnectionReconnectAttempted`, `ConnectionReconnectFailed`, `ConnectionStateChanged`, and related events. |
| 5 | 🟡 WARNING | `GatewayContainer` hardcodes host, port, payload limits, queue depth, timeouts, and retry values. FRD states gateway depends on Config for endpoint/timeout/payload/queue/heartbeat/retry settings. | `modules/gateway/src/root_gateway_container.py:GatewayContainer.__init__` | Inject configuration VOs from the Config feature. Root should assemble dependencies, not define runtime policy literals. |
| 6 | 🟡 WARNING | `CodeExecutionExecutor._validate_code()` hardcodes `max_code_size=100_000` and `strict_mode=True`. These are policy values and should come from constants/config/security policy. | `modules/gateway/src/capabilities_code_execution.py:CodeExecutionExecutor._validate_code` | Use taxonomy constants or injected security policy VOs. Avoid magic constants in capabilities. |
| 7 | 🟢 INFO | `GatewayOrchestrator` coordinates five protocols directly. This is acceptable, but the absence of an aggregate contract forces Root/Surface to depend on the concrete agent class. | `modules/gateway/src/agent_gateway_orchestrator.py:GatewayOrchestrator` | Create `contract_gateway_aggregate.py` and implement `IGatewayAggregate`. |

### Data Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | Root wiring violates dependency inversion: `SceneCoordinatorUtility` is passed where `SceneQueueProtocol` is expected. The agent therefore depends on a concrete helper rather than a contract. | `modules/gateway/src/root_gateway_container.py:GatewayContainer.__init__` | Remove `SceneCoordinatorUtility`. Pass `SceneQueueExecutor` as `SceneQueueProtocol`. |
| 2 | 🔴 CRITICAL | Transport data flow is broken: `TransportExecutor.send_request()` requires a socket, but `ConnectionExecutor` creates a socket without calling `TransportExecutor.set_socket()`. Handshake/auth therefore cannot reliably traverse the transport. | `modules/gateway/src/capabilities_connection_manager.py:ConnectionExecutor.establish_connection`, `modules/gateway/src/capabilities_transport_executor.py:TransportExecutor.send_request` | Wire the socket into the transport before any request, or refactor so the connection capability owns framed messaging and transport does not hold raw socket state. |
| 3 | 🟡 WARNING | `CodeValidationProtocol.validate_code()` is declared `async`, but `CodeExecutionExecutor._validate_code()` calls it synchronously. This will produce a coroutine instead of a result if the implementation is truly async. | `modules/shared/src/gateway/contract_code_validation_protocol.py:CodeValidationProtocol.validate_code`, `modules/gateway/src/capabilities_code_execution.py:CodeExecutionExecutor._validate_code` | Make the gateway-local validation protocol synchronous for sync capabilities, or introduce separate sync/async protocols and await in async contexts. |
| 4 | 🟡 WARNING | `BlenderCommandAdapter.send_command()` mutates `CommandResult`, which is a frozen dataclass. Assigning `result.data` or `result.truncated` will raise at runtime. | `modules/gateway/src/capabilities_transport_executor.py:BlenderCommandAdapter.send_command` | Return a new `CommandResult` using `dataclasses.replace()` instead of mutating the frozen VO. |
| 5 | 🟡 WARNING | `TransportExecutor._parse_response()` uses `str.encode("hex")`, which is invalid in Python 3. Payload decoding will fail at runtime. | `modules/gateway/src/capabilities_transport_executor.py:TransportExecutor._parse_response` | Use `bytes.fromhex()` for hex-encoded payloads, or define an explicit payload encoding helper in Utility. |
| 6 | 🟡 WARNING | `MaintenanceExecutor.set_state()` signature accepts only `ConnectionState`, but the contract allows `ConnectionState | None`. `GatewayOrchestrator.disconnect()` calls `set_state(None)`, which can put the executor into an invalid state. | `modules/gateway/src/capabilities_connection_maintenance.py:MaintenanceExecutor.set_state`, `modules/gateway/src/agent_gateway_orchestrator.py:GatewayOrchestrator.disconnect` | Align implementation with contract. If `None` means closed/disconnected, map it explicitly to `ConnectionState.CLOSED` or `ConnectionState.DISCONNECTED`. |

## Violations
- AES201 — CRITICAL: Utility file imports Contract (`utility_scene_coordinator.py` imports `SceneQueueProtocol`).
- AES404 — HIGH/MEDIUM: Utility file contains a stateful class and non-stateless behavior (`SceneCoordinatorUtility`).
- AES405 — MEDIUM: `GatewayOrchestrator` does not implement an aggregate contract.
- AES402 — HIGH: Contract signatures use primitives/`dict` where taxonomy VOs should be used, especially `IBlenderConnectionProtocol`, `IBlenderCommandProtocol`, `IOperationQueueProtocol`, and `CommandCatalogProtocol`.
- AES401 — HIGH: `taxonomy_command_catalog_constant.py` contains a non-constant class (`CommandCatalog`). Taxonomy events also use many primitive fields where branded VOs/constants should be used.
- AES502 — MEDIUM: Several async contract interfaces appear not to be consumed by the current gateway agent/container.
- AES503 — MEDIUM: Several async capability implementations appear not to be wired in any visible gateway container.
- AES305 — MEDIUM: Command-catalog/domain metadata duplication exists between `modules/shared/src/common/taxonomy_command_catalog_constant.py` and `modules/shared/src/gateway/utility_schema_helper.py`.
- FRD violation risk: FR-GWY-002, FR-GWY-003, FR-GWY-004, and FR-GWY-005 are not fully satisfied by current implementations.

## Action Items (For Developer)
- [ ] P0 Delete `modules/gateway/src/utility_scene_coordinator.py` and remove all imports/exports of `SceneCoordinatorUtility`.
- [ ] P0 Update `GatewayOrchestrator` to depend directly on `SceneQueueProtocol` for scene queue operations.
- [ ] P0 Create `modules/shared/src/gateway/contract_gateway_aggregate.py` with `IGatewayAggregate` and make `GatewayOrchestrator` implement it.
- [ ] P0 Fix `GatewayContainer` wiring so all injected dependencies satisfy the declared protocol contracts.
- [ ] P0 Fix `ConnectionExecutor` so the socket is available to the transport before handshake/authentication.
- [ ] P0 Remove silent fallback behavior in `ConnectionExecutor._perform_handshake()`; propagate transport, timeout, parse, and protocol mismatch errors.
- [ ] P0 Implement real serialized execution in `SceneQueueExecutor`, or remove the capability until it can satisfy FR-GWY-004.
- [ ] P0 Remove background task lifecycle management from gateway `CodeExecutionAdapter`; delegate task records to the Job feature.
- [ ] P0 Remove gateway-local AST security validation from `CodeExecutionAdapter`; delegate through Security/`CodeValidationProtocol`.
- [ ] P1 Align `CodeValidationProtocol` sync/async semantics with the capabilities that consume it.
- [ ] P1 Fix `BlenderCommandAdapter` frozen `CommandResult` mutation using `dataclasses.replace()`.
- [ ] P1 Fix `TransportExecutor._parse_response()` payload decoding (`bytes.fromhex`, not `.encode("hex")`).
- [ ] P1 Align `MaintenanceExecutor.set_state()` with the contract signature and map `None` to a valid `ConnectionState`.
- [ ] P1 Replace primitive contract parameters (`str`, `dict`, `float`, `int`) with taxonomy VOs/branded types in gateway contracts.
- [ ] P1 Move command catalog metadata out of Utility and deduplicate with the common command catalog.
- [ ] P1 Inject configuration from the Config feature into `GatewayContainer` instead of hardcoding runtime values.
- [ ] P2 Emit required connection/maintenance events from `MaintenanceExecutor` or equivalent capability.
- [ ] P2 Rename capability files to approved role-based names (`capabilities_connection_executor.py`, `capabilities_scene_queue_executor.py`, etc.).
- [ ] P2 Remove or wire orphaned async capabilities/contracts.
- [ ] P2 Remove unused event types or implement emission where required by FRD.

## Proposed Fixes / Reference Code

### Delete
```text
modules/gateway/src/utility_scene_coordinator.py
```

### modules/shared/src/gateway/contract_gateway_aggregate.py

```python
"""Gateway domain contract: aggregate facade for gateway feature."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_gateway_vo import (
    CodeExecutionOutcomeVO,
    CodeExecutionVO,
    ConnectionOutcomeVO,
    ConnectionStatusVO,
    QueueStatusVO,
    SceneOperationOutcomeVO,
    SceneOperationVO,
    TransportMessageVO,
    TransportOutcomeVO,
)


class IGatewayAggregate(ABC):
    """Public gateway facade consumed by surfaces and composed by root."""

    @abstractmethod
    def establish_connection(self) -> ConnectionOutcomeVO: ...

    @abstractmethod
    def disconnect(self) -> None: ...

    @abstractmethod
    def get_connection_status(self) -> ConnectionStatusVO: ...

    @abstractmethod
    def send_heartbeat(self) -> None: ...

    @abstractmethod
    def attempt_reconnect(self) -> ConnectionStatusVO: ...

    @abstractmethod
    def send_request(self, request: TransportMessageVO) -> TransportOutcomeVO: ...

    @abstractmethod
    def enqueue_scene_operation(self, operation: SceneOperationVO) -> SceneOperationOutcomeVO: ...

    @abstractmethod
    def get_queue_status(self) -> QueueStatusVO: ...

    @abstractmethod
    def execute_code(self, request: CodeExecutionVO) -> CodeExecutionOutcomeVO: ...
```

### modules/gateway/src/agent_gateway_orchestrator.py

```python
"""Gateway orchestrator — Aggregate facade coordinating gateway protocols."""

import logging

from modules.shared.src.gateway.contract_code_execution_protocol import (
    CodeExecutionProtocol,
)
from modules.shared.src.gateway.contract_connection_protocol import (
    ConnectionProtocol,
)
from modules.shared.src.gateway.contract_gateway_aggregate import (
    IGatewayAggregate,
)
from modules.shared.src.gateway.contract_maintenance_protocol import (
    ConnectionMaintenanceProtocol,
)
from modules.shared.src.gateway.contract_scene_queue_protocol import (
    SceneQueueProtocol,
)
from modules.shared.src.gateway.contract_transport_protocol import (
    TransportProtocol,
)
from modules.shared.src.gateway.taxonomy_gateway_vo import (
    CodeExecutionOutcomeVO,
    CodeExecutionVO,
    ConnectionOutcomeVO,
    ConnectionState,
    ConnectionStatusVO,
    QueueStatusVO,
    SceneOperationOutcomeVO,
    SceneOperationVO,
    TransportMessageVO,
    TransportOutcomeVO,
)

logger = logging.getLogger("BlenderMCPServer")


class GatewayOrchestrator(IGatewayAggregate):
    """Aggregate facade for the Gateway feature."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(
        self,
        connection: ConnectionProtocol,
        maintenance: ConnectionMaintenanceProtocol,
        transport: TransportProtocol,
        scene_queue: SceneQueueProtocol,
        code_executor: CodeExecutionProtocol,
    ) -> None:
        self._connection = connection
        self._maintenance = maintenance
        self._transport = transport
        self._scene_queue = scene_queue
        self._code_executor = code_executor

    # ─── Block 2: Aggregate Method Implementation ─────────────
    def establish_connection(self) -> ConnectionOutcomeVO:
        result = self._connection.establish_connection()
        if result.state == ConnectionState.CONNECTED:
            self._maintenance.set_state(result.state)
        return result

    def disconnect(self) -> None:
        self._connection.disconnect()
        self._maintenance.set_state(ConnectionState.CLOSED)

    def get_connection_status(self) -> ConnectionStatusVO:
        return self._maintenance.get_connection_status()

    def send_heartbeat(self) -> None:
        self._maintenance.send_heartbeat()

    def attempt_reconnect(self) -> ConnectionStatusVO:
        return self._maintenance.attempt_reconnect()

    def send_request(self, request: TransportMessageVO) -> TransportOutcomeVO:
        return self._transport.send_request(request)

    def enqueue_scene_operation(self, operation: SceneOperationVO) -> SceneOperationOutcomeVO:
        return self._scene_queue.enqueue_operation(operation)

    def get_queue_status(self) -> QueueStatusVO:
        return self._scene_queue.get_queue_status()

    def execute_code(self, request: CodeExecutionVO) -> CodeExecutionOutcomeVO:
        return self._code_executor.execute_code(request)
```

### modules/gateway/src/root_gateway_container.py

```python
"""Composition root — DI wiring for the Gateway feature."""

from modules.security.src.capabilities_code_validator import CodeValidator
from modules.shared.src.gateway.taxonomy_gateway_vo import ConnectionConfigVO
from modules.shared.src.security.taxonomy_security_vo import SecurityPolicyVO

from .agent_gateway_orchestrator import GatewayOrchestrator
from .capabilities_code_execution import CodeExecutionExecutor
from .capabilities_connection_maintenance import MaintenanceExecutor
from .capabilities_connection_manager import ConnectionExecutor
from .capabilities_scene_queue import SceneQueueExecutor
from .capabilities_transport_executor import TransportExecutor


class GatewayContainer:
    """Dependency injection container for the Gateway feature."""

    def __init__(self) -> None:
        self._security_policy = CodeValidator(policy=SecurityPolicyVO())
        self._transport = TransportExecutor(max_payload_bytes=10_485_760)

        self._connection = ConnectionExecutor(
            transport=self._transport,
            config=ConnectionConfigVO(host="localhost", port=50051),
        )

        self._maintenance = MaintenanceExecutor(
            max_retries=3,
            base_backoff_seconds=1.0,
            max_backoff_seconds=16.0,
            reconnect_fn=self._connection.establish_connection,
        )

        self._scene_queue = SceneQueueExecutor(
            max_depth=50,
            wait_timeout_seconds=30.0,
        )

        self._code_executor = CodeExecutionExecutor(
            security_policy=self._security_policy,
            transport=self._transport,
            max_output_bytes=1_048_576,
            execution_timeout_seconds=30.0,
        )

        self._orchestrator = GatewayOrchestrator(
            connection=self._connection,
            maintenance=self._maintenance,
            transport=self._transport,
            scene_queue=self._scene_queue,
            code_executor=self._code_executor,
        )

    def get_orchestrator(self) -> GatewayOrchestrator:
        return self._orchestrator


def create_gateway_feature() -> GatewayOrchestrator:
    container = GatewayContainer()
    return container.get_orchestrator()
```

### modules/gateway/src/capabilities_connection_manager.py

```python
# Inside ConnectionExecutor.establish_connection()

sock = socket.create_connection(
    (self._config.host, self._config.port),
    timeout=timeout,
)

# Make the transport usable before handshake/auth.
self._transport.set_socket(sock)

handshake_response = self._perform_handshake()
self._protocol_version = handshake_response.get(
    "protocol_version",
    self._config.protocol_version,
)

if not self._is_protocol_compatible():
    self._safe_close_socket(sock)
    raise ProtocolVersionMismatchError(f"Protocol version {self._protocol_version} incompatible")

self._authenticate_if_needed()

self._socket = sock
self._state = ConnectionState.CONNECTED
```

```python
# Remove silent fallback from _perform_handshake().
# Propagate transport errors instead of returning default capabilities.
def _perform_handshake(self) -> dict:
    handshake_request = TransportMessageVO(
        tracking_id=str(uuid.uuid4()),
        operation_class="handshake",
        payload=json.dumps(
            {
                "type": "handshake",
                "protocol_version": self._config.protocol_version,
            }
        ).encode("utf-8"),
    )

    outcome = self._transport.send_request(handshake_request)

    if not outcome.payload:
        raise TransportParseError("Empty handshake response payload")

    return json.loads(outcome.payload.decode("utf-8"))
```

### modules/gateway/src/capabilities_transport_executor.py

```python
from dataclasses import replace

# Inside BlenderCommandAdapter.send_command():
if result.data is not None:
    data_bytes = len(result.data.encode("utf-8")) if isinstance(result.data, str) else len(result.data)

    if data_bytes > self._max_response_bytes:
        if isinstance(result.data, str):
            truncated_data = result.data[: self._max_response_bytes] + "\n...[truncated]"
        else:
            truncated_data = result.data[: self._max_response_bytes]

        result = replace(result, data=truncated_data, truncated=True)
```

```python
# Inside TransportExecutor._parse_response():
payload_raw = message.get("payload")
payload = bytes.fromhex(payload_raw) if payload_raw else None

return TransportOutcomeVO(
    tracking_id=actual_tracking_id,
    status=message.get("status", "error"),
    payload=payload,
)
```

### modules/gateway/src/capabilities_scene_queue.py

```python
# Minimal synchronous serialization pattern.
# Replace placeholder queue logic with real execution.

import threading


class SceneQueueExecutor(SceneQueueProtocol):
    def __init__(
        self,
        max_depth: int = 50,
        wait_timeout_seconds: float = 30.0,
    ) -> None:
        self._max_depth = max_depth
        self._wait_timeout_seconds = wait_timeout_seconds
        self._queue: queue.Queue[SceneOperationVO] = queue.Queue(maxsize=max_depth)
        self._execution_lock = threading.Lock()
        self._processing = False

    def enqueue_operation(self, operation: SceneOperationVO) -> SceneOperationOutcomeVO:
        if not operation.is_mutation:
            return self._execute_directly(operation)

        try:
            self._queue.put_nowait(operation)
        except queue.Full:
            raise ChannelConflictError(f"Queue depth limit {self._max_depth} reached") from None

        acquired = self._execution_lock.acquire(timeout=self._wait_timeout_seconds)
        if not acquired:
            raise TimeoutError(f"Queue wait timeout exceeded after {self._wait_timeout_seconds}s")

        self._processing = True
        try:
            # Execute the mutating operation through transport/command capability.
            # This must be injected; do not return placeholder success.
            return self._execute_mutation(operation)
        finally:
            self._processing = False
            self._execution_lock.release()
```

### modules/shared/src/gateway/contract_code_validation_protocol.py

```python
"""Gateway domain contract: code validation protocol."""

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.security.taxonomy_security_vo import CodeValidationVO


class CodeValidationProtocol(ABC):
    """Synchronous gateway-local abstraction for security code validation."""

    @abstractmethod
    def validate_code(self, request: CodeValidationVO) -> CodeValidationVO:
        """Validate untrusted code before execution."""
        ...
```

### modules/gateway/src/__init__.py

```python
from .agent_gateway_orchestrator import GatewayOrchestrator
from .capabilities_code_execution import CodeExecutionExecutor
from .capabilities_connection_maintenance import MaintenanceExecutor
from .capabilities_connection_manager import ConnectionExecutor
from .capabilities_scene_queue import SceneQueueExecutor
from .capabilities_transport_executor import TransportExecutor
from .root_gateway_container import GatewayContainer, create_gateway_feature

__all__ = [
    "CodeExecutionExecutor",
    "ConnectionExecutor",
    "GatewayContainer",
    "GatewayOrchestrator",
    "MaintenanceExecutor",
    "SceneQueueExecutor",
    "TransportExecutor",
    "create_gateway_feature",
]
```

```

```
