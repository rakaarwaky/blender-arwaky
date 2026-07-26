Benar — saya akui itu kesalahan desain di plan v1. Seharusnya **upgrade protocol yang sudah ada**, bukan membuat contract baru. Prinsip repo Anda: **1 FR = 1 Capability = 1 Protocol**.

Karena Anda sudah terlanjur mengimplementasikan plan v1, plan v2 ini adalah **plan koreksi + migrasi**, bukan rewrite buta. Plan v2:

- tetap sadar bahwa plan v1 sudah diimplementasikan,
- menghapus/melebur artefak v1 yang melanggar prinsip,
- hanya meng-upgrade 4 contract yang sudah ada,
- tidak membuat contract file baru,
- mempertahankan 3 capability sesuai 3 FR.

Simpan sebagai:

```text
.agents/plan/plan-server-remediation-v2.md
```

```markdown
# Plan v2: Server Remediation — Koreksi Arsitektur & Migrasi dari Plan v1

> **Status:** Plan v2 merevisi plan v1.
>
> **Alasan revisi:** Plan v1 membuat contract dan capability baru untuk queue, event bus, dan metrics. Itu melanggar prinsip:
>
> ```text
> 1 FR = 1 Capability = 1 Protocol
> ```
>
> Plan v2 memperbaiki struktur tanpa membuang keputusan perilaku yang sudah disetujui.

---

## 0. Kesalahan Plan v1 yang Harus Dikoreksi

Plan v1 membuat artefak baru yang seharusnya tidak ada:

| Artefak Plan v1 | Masalah | Koreksi v2 |
| --- | --- | --- |
| `contract_operation_queue_protocol.py` | Contract baru untuk queue | Hapus. Queue adalah bagian FR-003. Upgrade `contract_command_protocol.py`. |
| `capabilities_operation_queue.py` | Capability baru tanpa FR | Hapus. Pindahkan logika queue ke `capabilities_blender_command_adapter.py`. |
| `contract_event_bus_protocol.py` | Contract baru untuk observability | Hapus. Event emission pindah ke Utility stateless. |
| `capabilities_event_bus_inmemory.py` | Capability baru tanpa FR | Hapus. Ganti dengan `utility_server_telemetry.py`. |
| `contract_metrics_protocol.py` | Contract baru untuk metrics | Hapus. Metrics dikomposisi Agent dari diagnostik 3 protocol existing. |
| `capabilities_metrics_collector.py` | Capability baru tanpa FR | Hapus. Counter dimiliki masing-masing capability existing. |

**Aturan keras v2:**

```text
Tidak boleh ada file contract_* baru di modules/shared/src/server.
Tidak boleh ada file capabilities_* baru di modules/server/src.
Semua perubahan dilakukan dengan upgrade file yang sudah ada.
```

Pengecualian tunggal:

```text
modules/shared/src/server/utility_server_telemetry.py
```

Utility baru ini boleh dibuat karena Utility bukan contract dan bukan capability.

---

## 1. Struktur Akhir yang Benar

### 1.1 Server Feature

```text
modules/server/src/
├── __init__.py
├── agent_server_orchestrator.py
├── capabilities_blender_connection.py
├── capabilities_code_execution_adapter.py
├── capabilities_blender_command_adapter.py
├── root_server_container.py
└── surface_server_diagnostics_controller.py   ← opsional, tetap sah sebagai Surface
```

Tepat 3 capability:

```text
FR-001 → capabilities_blender_connection.py
FR-002 → capabilities_code_execution_adapter.py
FR-003 → capabilities_blender_command_adapter.py
```

### 1.2 Shared Server Contracts

```text
modules/shared/src/server/
├── contract_connection_protocol.py
├── contract_command_protocol.py
├── contract_code_execution_protocol.py
└── contract_server_aggregate.py
```

Tepat 4 contract file:

```text
3 protocol untuk 3 capability
1 aggregate untuk Agent
```

Tidak ada contract ke-5.

---

## 2. Prinsip Arsitektur v2

### 2.1 Mapping FR → Capability → Protocol

| FR | Capability | Protocol |
| --- | --- | --- |
| FR-001 Connection | `BlenderConnection` | `IBlenderConnectionProtocol` |
| FR-002 Code Execution | `CodeExecutionAdapter` | `ICodeExecutionProtocol` |
| FR-003 Command Dispatch + Execution Queue | `BlenderCommandAdapter` | `IBlenderCommandProtocol` |
| Aggregate facade | `ServerOrchestrator` | `IBlenderServerAggregate` |

### 2.2 Queue

Queue bukan feature baru.

Queue adalah bagian dari FR-003:

```text
Command Dispatch & ExecutionQueue
```

Maka:

```text
State queue → BlenderCommandAdapter
Worker loop → ServerOrchestrator
```

Ini sesuai AES:

- Capability memiliki state teknis dalam scope-nya.
- Agent mengontrol flow: loop, sequential execution, cancellation, error handling.

### 2.3 Events

Event bukan FR terpisah.

Maka event emission tidak boleh menjadi capability atau contract baru.

Gunakan Utility stateless:

```text
utility_server_telemetry.py
```

Event diterbitkan sebagai structured log.

### 2.4 Metrics

Metrics bukan FR terpisah.

Setiap capability menyimpan counter internal dan membuka metode diagnostik pada protocol existing.

Agent mengkomposisi `ServerMetrics`.

---

## 3. Keputusan Plan v1 yang Tetap Berlaku

Semua keputusan perilaku berikut tetap berlaku, kecuali yang secara eksplisit direvisi di §4.

### 3.1 Connection

- Reconnect default: reject operasi baru saat reconnect.
- Pending operation dibatalkan saat disconnect.
- Pending operation dibatalkan saat koneksi gagal permanen.
- Handshake versi selalu dilakukan.
- Auth token wajib untuk remote.
- Localhost tidak wajib auth.
- Kompatibilitas versi: major sama.

### 3.2 Queue

- Custom code execution selalu masuk queue.
- Command scene-mutating masuk queue.
- Command non-scene boleh bypass queue.
- Queue full → `TooManyPendingOperationsError`.
- Queue wait timeout → `OperationWaitTimeoutError`.
- FIFO.

### 3.3 Security

- Validasi AST terpusat di Utility.
- File write hanya boleh jika path literal terbukti berada dalam allowed directory.
- Dynamic path write ditolak.
- Raw code tidak boleh dilog.
- Security violation harus emit audit event.

### 3.4 Background Task

- Task state: pending, running, success, error, timeout, cancelled.
- `poll_task_result` mengembalikan `TaskStatus`.
- Cancel task harus tersedia di aggregate.
- Cancel running task bersifat best-effort.
- Task storage in-memory.

### 3.5 Error Naming

Jika belum diterapkan di plan v1, rename error berikut secara in-place:

```text
QueueFullError → TooManyPendingOperationsError
QueueTimeoutError → OperationWaitTimeoutError
ProtocolVersionMismatchError → VersionMismatchError
```

Jika sudah diterapkan, pertahankan.

---

## 4. Revisi Keputusan Plan v1

| ID | Plan v1 | Plan v2 | Alasan |
| --- | --- | --- | --- |
| Queue ownership | Queue capability baru | Queue tetap di `BlenderCommandAdapter` | FR-003 sejak awal adalah Command Dispatch & ExecutionQueue |
| Event bus | Contract + capability baru | Utility stateless `publish_event()` | Event emission adalah mekanika teknis, bukan FR |
| Metrics | Contract + capability baru | Diagnostik per capability + komposisi Agent | Metrics bukan FR terpisah |
| Contract baru | 3 contract baru | 0 contract baru | Prinsip 1 FR = 1 capability = 1 protocol |
| Capability baru | 3 capability baru | 0 capability baru | Server hanya punya 3 FR |

---

## 5. Spesifikasi Upgrade Contract Existing

Semua perubahan di bawah dilakukan dengan mengedit file contract yang sudah ada.

Jangan membuat file contract baru.

---

## 5.1 Upgrade `contract_connection_protocol.py`

File:

```text
modules/shared/src/server/contract_connection_protocol.py
```

Protocol akhir:

```python
class IBlenderConnectionProtocol(ABC):
    """FR-001: Blender connection lifecycle."""

    @abstractmethod
    async def connect(self, config: ConnectionConfig) -> ConnectionStatus:
        """Establish connection, handshake, version check, auth if required."""
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """Idempotent graceful disconnect."""
        ...

    @abstractmethod
    async def is_connected(self) -> bool:
        """Return True if connection is alive."""
        ...

    @abstractmethod
    async def send_command(
        self,
        command_type: ActionName,
        params: Details | None = None,
        request_id: RequestId | None = None,
        timeout_ms: float | None = None,
    ) -> CommandResult:
        """Send low-level command to Blender addon.

        Returns CommandResult.
        Raises BlenderConnectionFailure, ConnectionClosedError, ExecutionError.
        """
        ...

    @abstractmethod
    async def receive_full_response(self, buffer_size: int = 8192) -> bytes:
        """Receive complete framed response bytes."""
        ...

    @abstractmethod
    def set_active_operation_in_progress(self, active: bool) -> None:
        """Tell connection whether a long-running operation is active.

        Used to prevent heartbeat false alarm during long operations.
        """
        ...

    @abstractmethod
    async def get_diagnostics(self) -> ConnectionDiagnostics:
        """Return cumulative connection diagnostics for metrics composition."""
        ...
```

### Perubahan dari v1.6.5

Dari code existing:

```python
async def send_command(
    self,
    command_type: ActionName,
    params: Details | None = None,
) -> CommandResult:
```

Menjadi:

```python
async def send_command(
    self,
    command_type: ActionName,
    params: Details | None = None,
    request_id: RequestId | None = None,
    timeout_ms: float | None = None,
) -> CommandResult:
```

Tambah:

```python
def set_active_operation_in_progress(self, active: bool) -> None: ...
async def get_diagnostics(self) -> ConnectionDiagnostics: ...
```

---

## 5.2 Upgrade `contract_command_protocol.py`

File:

```text
modules/shared/src/server/contract_command_protocol.py
```

Protocol akhir:

```python
class IBlenderCommandProtocol(ABC):
    """FR-003: Command dispatch and execution queue."""

    # ── Dispatch ─────────────────────────────────────────────
    @abstractmethod
    async def send_command(
        self,
        action: ActionName,
        params: dict | None = None,
        timeout_ms: float | None = None,
        request_id: RequestId | None = None,
    ) -> CommandResult:
        """Dispatch command directly.

        Queue vs direct decision is made by Agent based on command metadata.
        """
        ...

    # ── Queue State ──────────────────────────────────────────
    @abstractmethod
    async def enqueue(self, operation: QueuedOperation) -> int:
        """Enqueue operation.

        Returns queue depth after enqueue.
        Raises TooManyPendingOperationsError.
        Event: ItemEnqueued.
        """
        ...

    @abstractmethod
    async def dequeue(self) -> QueuedOperation | None:
        """Return next FIFO operation or None if empty.

        Event: ItemDequeued.
        """
        ...

    @abstractmethod
    async def mark_started(self, request_id: RequestId) -> None:
        """Mark queued operation as started."""
        ...

    @abstractmethod
    async def complete(
        self,
        request_id: RequestId,
        result: CommandResult | ExecutionResult | str,
    ) -> None:
        """Resolve waiter with successful result."""
        ...

    @abstractmethod
    async def fail(self, request_id: RequestId, error: Exception) -> None:
        """Resolve waiter with typed error."""
        ...

    @abstractmethod
    async def wait_for_started(
        self,
        request_id: RequestId,
        timeout_ms: float,
    ) -> None:
        """Wait until operation starts.

        Raises OperationWaitTimeoutError.
        """
        ...

    @abstractmethod
    async def wait_for_completion(
        self,
        request_id: RequestId,
        timeout_ms: float | None = None,
    ) -> CommandResult | ExecutionResult | str:
        """Wait for final result.

        Upgrade dari metode existing `wait_for_completion`.
        Return type diperluas agar bisa dipakai command dan code execution.
        """
        ...

    @abstractmethod
    async def cancel_pending(self, error: Exception) -> int:
        """Cancel all pending operations with given error.

        Used on disconnect, shutdown, permanent connection failure.
        Returns number cancelled.
        """
        ...

    @abstractmethod
    async def cancel_by_task_id(self, task_id: str, error: Exception) -> bool:
        """Cancel pending operation belonging to a background task."""
        ...

    @abstractmethod
    async def get_depth(self) -> int:
        """Return current queue depth."""
        ...

    @abstractmethod
    async def get_queue_stats(self) -> QueueStats:
        """Return queue diagnostics for metrics composition."""
        ...
```

### Perubahan dari v1.6.5

Existing:

```python
async def enqueue(
    self,
    request_id: str,
    payload: dict,
) -> int:
```

Upgrade menjadi:

```python
async def enqueue(self, operation: QueuedOperation) -> int:
```

Existing:

```python
async def dequeue(self) -> str | None:
```

Upgrade menjadi:

```python
async def dequeue(self) -> QueuedOperation | None:
```

Existing:

```python
async def wait_for_completion(
    self,
    request_id: str,
    timeout_ms: float | None = None,
) -> ExecutionResult:
```

Upgrade menjadi:

```python
async def wait_for_completion(
    self,
    request_id: RequestId,
    timeout_ms: float | None = None,
) -> CommandResult | ExecutionResult | str:
```

Tambah metode queue worker:

```python
mark_started
complete
fail
wait_for_started
cancel_pending
cancel_by_task_id
get_queue_stats
```

---

## 5.3 Upgrade `contract_code_execution_protocol.py`

File:

```text
modules/shared/src/server/contract_code_execution_protocol.py
```

Protocol akhir:

```python
class ICodeExecutionProtocol(ABC):
    """FR-002: Code execution and background task lifecycle."""

    @abstractmethod
    async def execute_blender_code(
        self,
        code: Prompt,
        request_id: RequestId | None = None,
    ) -> ExecutionResult:
        """Execute code synchronously through Blender."""
        ...

    @abstractmethod
    async def execute_task(
        self,
        task_id: str,
        code: Prompt,
        request_id: RequestId | None = None,
    ) -> ExecutionResult:
        """Execute code for a background task.

        Called by Agent queue worker.
        """
        ...

    @abstractmethod
    async def submit_async_task(
        self,
        code: Prompt,
        request_id: RequestId,
    ) -> str:
        """Validate code, create pending task, return task_id.

        Actual execution is queued by Agent.
        """
        ...

    @abstractmethod
    async def poll_task_result(
        self,
        task_id: str,
        request_id: RequestId | None = None,
    ) -> TaskStatus:
        """Return task status.

        Upgrade dari v1.6.5 yang mengembalikan ExecutionResult.
        """
        ...

    @abstractmethod
    async def cancel_async_task(
        self,
        task_id: str,
        request_id: RequestId | None = None,
    ) -> TaskStatus:
        """Cancel pending task or best-effort cancel running task."""
        ...

    @abstractmethod
    def create_task(self, request_id: RequestId) -> str:
        """Create pending task and return task_id."""
        ...

    @abstractmethod
    def get_task(self, task_id: str) -> TaskStatus:
        """Return task status or raise TaskNotFoundError."""
        ...

    @abstractmethod
    def cleanup_expired(self) -> int:
        """Remove expired tasks. Return number removed."""
        ...

    @abstractmethod
    async def get_task_stats(self) -> TaskStats:
        """Return task diagnostics for metrics composition."""
        ...
```

### Metode yang Dihapus dari Public Contract

Metode berikut ada di v1.6.5:

```python
mark_running
mark_completed
mark_error
mark_timeout
cancel_task
```

Di v2, metode tersebut menjadi internal capability.

Jangan hapus logikanya. Turunkan visibilitasnya menjadi private/protected:

```python
_mark_running
_mark_completed
_mark_error
_mark_timeout
```

`cancel_task` diganti oleh:

```python
cancel_async_task
```

---

## 5.4 Upgrade `contract_server_aggregate.py`

File:

```text
modules/shared/src/server/contract_server_aggregate.py
```

Aggregate akhir:

```python
class IBlenderServerAggregate(ABC):
    """Server feature facade."""

    # ── Lifecycle ────────────────────────────────────────────
    @abstractmethod
    async def start(self) -> None:
        """Start queue worker and internal background tasks."""
        ...

    @abstractmethod
    async def shutdown(self) -> None:
        """Stop worker, cancel pending operations, disconnect."""
        ...

    # ── Connection ───────────────────────────────────────────
    @abstractmethod
    async def connect(
        self,
        config: ConnectionConfig,
        request_id: RequestId | None = None,
    ) -> ConnectionStatus:
        ...

    @abstractmethod
    async def disconnect(
        self,
        request_id: RequestId | None = None,
    ) -> None:
        ...

    @abstractmethod
    async def get_status(
        self,
        request_id: RequestId | None = None,
    ) -> ConnectionStatus:
        ...

    # ── Code Execution ───────────────────────────────────────
    @abstractmethod
    async def execute_code(
        self,
        code: str,
        request_id: RequestId | None = None,
    ) -> ExecutionResult:
        ...

    @abstractmethod
    async def submit_async_task(
        self,
        code: str,
        request_id: RequestId | None = None,
    ) -> str:
        ...

    @abstractmethod
    async def poll_task_result(
        self,
        task_id: str,
        request_id: RequestId | None = None,
    ) -> TaskStatus:
        ...

    @abstractmethod
    async def cancel_async_task(
        self,
        task_id: str,
        request_id: RequestId | None = None,
    ) -> TaskStatus:
        ...

    # ── Command Dispatch ─────────────────────────────────────
    @abstractmethod
    async def send_command(
        self,
        action: str,
        params: dict | None = None,
        timeout_ms: float | None = None,
        request_id: RequestId | None = None,
    ) -> CommandResult:
        ...

    # ── Observability ────────────────────────────────────────
    @abstractmethod
    async def get_metrics(
        self,
        request_id: RequestId | None = None,
    ) -> ServerMetrics:
        ...
```

### Perubahan Penting

Existing aggregate:

```python
async def send_command(...) -> dict:
```

Upgrade menjadi:

```python
async def send_command(...) -> CommandResult:
```

Existing aggregate:

```python
async def poll_task_result(self, task_id: str) -> ExecutionResult:
```

Upgrade menjadi:

```python
async def poll_task_result(
    self,
    task_id: str,
    request_id: RequestId | None = None,
) -> TaskStatus:
```

Tambah:

```python
start
shutdown
cancel_async_task
get_metrics
```

---

## 6. Upgrade Taxonomy Existing

File:

```text
modules/shared/src/server/taxonomy_server_vo.py
```

Tambahkan VO berikut. Jangan buat file taxonomy baru.

### 6.1 QueuedOperation

```python
@dataclass(frozen=True)
class QueuedOperation:
    request_id: RequestId
    operation_type: str  # "code_sync" | "code_async" | "command"
    payload: dict
    task_id: str | None = None
    action: str | None = None
    timeout_ms: float | None = None
    enqueued_at: float = 0.0
```

### 6.2 QueueStats

```python
@dataclass(frozen=True)
class QueueStats:
    depth: int
    enqueued_total: int
    completed_total: int
    failed_total: int
    rejected_full_total: int
    rejected_wait_timeout_total: int
    cancelled_total: int
    command_total: int
    avg_wait_ms: float
    avg_command_time_ms: float
```

### 6.3 ConnectionDiagnostics

```python
@dataclass(frozen=True)
class ConnectionDiagnostics:
    state: ConnectionState
    connections_total: int
    reconnect_count: int
    heartbeat_failures_total: int
    connection_lost_total: int
    last_heartbeat_at: float | None
    session_id: str | None
    active_directory: str | None
    protocol_version: str | None
```

### 6.4 TaskStats

```python
@dataclass(frozen=True)
class TaskStats:
    created_total: int
    completed_total: int
    failed_total: int
    timeout_total: int
    cancelled_total: int
    active_count: int
    security_violation_total: int
    executed_total: int
    avg_execution_time_ms: float
```

### 6.5 ServerMetrics

```python
@dataclass(frozen=True)
class ServerMetrics:
    pending_operations: int
    running_operations: int
    reconnect_count: int
    failed_request_count: int
    security_violation_count: int
    code_execution_count: int
    command_count: int
    task_created_count: int
    task_completed_count: int
    task_failed_count: int
    task_timeout_count: int
    task_cancelled_count: int
    average_code_latency_ms: float
    average_command_latency_ms: float
    last_updated_at: float
    request_id: RequestId | None = None
```

### 6.6 Upgrade VO Lama

Upgrade juga VO berikut jika belum dilakukan plan v1.

#### ConnectionStatus

Tambah field:

```python
request_id: RequestId | None = None
last_heartbeat_at: float | None = None
heartbeat_interval_seconds: int = 10
heartbeat_failure_threshold: int = 3
session_id: str | None = None
active_file_path: str | None = None
active_directory: str | None = None
```

#### ExecutionResult

Upgrade `data`:

```python
data: dict | str | bytes | None = None
```

Tambah:

```python
request_id: RequestId | None = None
```

#### CommandResult

Upgrade menjadi:

```python
@dataclass(frozen=True)
class CommandResult:
    status: str
    data: dict | str | None = None
    error: ExecutionErrorDetail | None = None
    execution_time_ms: float = 0.0
    truncated: bool = False
    request_id: RequestId | None = None
```

#### TaskStatus

Tambah:

```python
request_id: RequestId | None = None
created_at: float | None = None
completed_at: float | None = None
cancel_requested: bool = False
```

---

## 7. Utility Baru yang Diperbolehkan

File baru satu-satunya:

```text
modules/shared/src/server/utility_server_telemetry.py
```

Isi minimum:

```python
"""Utility: structured event emission.

Stateless standalone functions only.
Replaces event bus capability from plan v1.
"""

from typing import Any

def event_to_record(event: object) -> dict[str, Any]:
    """Convert frozen dataclass event to structured dict."""
    ...

def publish_event(event: object) -> None:
    """Publish event as structured log line.

    Logger name: BlenderMCPServer.events
    Must never raise.
    """
    ...

def new_request_id() -> str:
    """Return UUID4 string for request correlation."""
    ...
```

Aturan:

```text
Utility ini stateless.
Tidak ada class.
Tidak ada subscriber registry.
Tidak ada event bus object.
```

---

## 8. Migrasi dari Implementasi Plan v1

Karena plan v1 sudah terlanjur diimplementasikan, jalankan fase berikut secara berurutan.

Jangan big-bang.

---

## Fase 0 — Characterization Tests

Tujuan: mengunci perilaku v1 sebelum struktur diubah.

### Langkah

1. Jalankan test suite penuh:

```bash
uv run pytest
```

2. Catat baseline:

```text
jumlah test
status pass/fail
coverage
```

3. Tambahkan test perilaku untuk:

```text
queue FIFO
queue full
queue wait timeout
cancel pending saat disconnect
cancel pending saat connection failed
event emission
metrics values
task lifecycle
security violation
command validation
```

4. Test harus lolos tanpa mengubah kode produksi.

### Exit Criteria

```text
Baseline hijau.
Test karakterisasi di-commit terpisah.
```

### Rollback

Tidak ada perubahan produksi.

---

## Fase 1 — Taxonomy Additive

Tujuan: menambahkan VO baru tanpa mengubah perilaku.

### Langkah

1. Edit:

```text
modules/shared/src/server/taxonomy_server_vo.py
```

2. Tambahkan:

```text
QueuedOperation
QueueStats
ConnectionDiagnostics
TaskStats
ServerMetrics
```

3. Upgrade:

```text
ConnectionStatus
ExecutionResult
CommandResult
TaskStatus
```

4. Export di:

```text
modules/shared/src/server/__init__.py
```

### Exit Criteria

```bash
uv run ruff check .
uv run mypy modules/shared/src/server
uv run pytest
```

Semua hijau.

### Rollback

Revert commit taxonomy.

---

## Fase 2 — Ganti Event Bus dengan Utility Telemetry

Tujuan: menghapus event bus capability dan contract tanpa mengubah event yang terbit.

### Langkah

1. Buat:

```text
modules/shared/src/server/utility_server_telemetry.py
```

2. Export:

```text
publish_event
event_to_record
new_request_id
```

3. Cari semua pemakaian event bus v1:

```bash
rg "event_publisher"
rg "IEventPublisher"
rg "InMemoryEventBus"
```

4. Ganti:

```python
await self._event_publisher.publish(event)
```

Menjadi:

```python
publish_event(event)
```

5. Hapus parameter constructor:

```python
event_publisher: IEventPublisher
```

dari:

```text
capabilities_blender_connection.py
capabilities_code_execution_adapter.py
capabilities_blender_command_adapter.py
agent_server_orchestrator.py
```

6. Hapus file v1:

```text
modules/shared/src/server/contract_event_bus_protocol.py
modules/server/src/capabilities_event_bus_inmemory.py
```

7. Update test event:

Dari subscriber-based menjadi structured log assertion:

```python
caplog
```

### Exit Criteria

```text
Semua event v1 masih terbit sebagai structured log.
Tidak ada import IEventPublisher tersisa.
pytest hijau.
```

### Rollback

Revert commit fase 2.

---

## Fase 3 — Kembalikan Queue ke BlenderCommandAdapter

Ini fase paling besar.

Tujuan: menghapus queue capability baru dan meng-upgrade command protocol existing.

### Langkah

1. Edit:

```text
modules/shared/src/server/contract_command_protocol.py
```

2. Terapkan signature akhir dari §5.2.

3. Pindahkan implementasi queue dari:

```text
modules/server/src/capabilities_operation_queue.py
```

ke:

```text
modules/server/src/capabilities_blender_command_adapter.py
```

4. `BlenderCommandAdapter` harus memiliki:

```text
_queue
_pending futures
_queue_lock
_queue_stats
```

5. Implementasikan semua metode queue pada `IBlenderCommandProtocol`.

6. Hapus file:

```text
modules/server/src/capabilities_operation_queue.py
modules/shared/src/server/contract_operation_queue_protocol.py
```

7. Update:

```text
agent_server_orchestrator.py
```

Worker loop harus memakai:

```python
self._command_adapter.dequeue()
self._command_adapter.mark_started()
self._command_adapter.complete()
self._command_adapter.fail()
self._command_adapter.cancel_pending()
```

Bukan:

```python
IOperationQueueProtocol
```

### Exit Criteria

```text
Test FIFO dari Fase 0 lolos tanpa perubahan assertion.
Test queue full lolos.
Test queue wait timeout lolos.
Test cancel pending lolos.
Tidak ada file operation queue terpisah.
```

### Rollback

Revert commit fase 3.

---

## Fase 4 — Diagnostik dan Metrics Tanpa Contract Baru

Tujuan: menghapus metrics collector capability dan contract metrics.

### Langkah

1. Tambahkan counter internal di tiap capability.

#### BlenderConnection

Counter:

```text
connections_total
reconnect_count
heartbeat_failures_total
connection_lost_total
```

Implementasikan:

```python
async def get_diagnostics(self) -> ConnectionDiagnostics:
    ...
```

#### BlenderCommandAdapter

Counter:

```text
enqueued_total
completed_total
failed_total
rejected_full_total
rejected_wait_timeout_total
cancelled_total
command_total
avg_wait_ms
avg_command_time_ms
```

Implementasikan:

```python
async def get_queue_stats(self) -> QueueStats:
    ...
```

#### CodeExecutionAdapter

Counter:

```text
created_total
completed_total
failed_total
timeout_total
cancelled_total
active_count
security_violation_total
executed_total
avg_execution_time_ms
```

Implementasikan:

```python
async def get_task_stats(self) -> TaskStats:
    ...
```

2. Update `ServerOrchestrator.get_metrics()`:

```python
async def get_metrics(
    self,
    request_id: RequestId | None = None,
) -> ServerMetrics:
    connection_diag = await self._connection.get_diagnostics()
    queue_stats = await self._command_adapter.get_queue_stats()
    task_stats = await self._code_executor.get_task_stats()

    return ServerMetrics(
        pending_operations=queue_stats.depth,
        running_operations=self._running_count,
        reconnect_count=connection_diag.reconnect_count,
        failed_request_count=self._failed_count,
        security_violation_count=task_stats.security_violation_total,
        code_execution_count=task_stats.executed_total,
        command_count=queue_stats.command_total,
        task_created_count=task_stats.created_total,
        task_completed_count=task_stats.completed_total,
        task_failed_count=task_stats.failed_total,
        task_timeout_count=task_stats.timeout_total,
        task_cancelled_count=task_stats.cancelled_total,
        average_code_latency_ms=task_stats.avg_execution_time_ms,
        average_command_latency_ms=queue_stats.avg_command_time_ms,
        last_updated_at=time.time(),
        request_id=request_id,
    )
```

3. Hapus file v1:

```text
modules/shared/src/server/contract_metrics_protocol.py
modules/server/src/capabilities_metrics_collector.py
```

### Exit Criteria

```text
get_metrics mengembalikan nilai identik dengan baseline v1.
Tidak ada IMetricsProvider tersisa.
pytest hijau.
```

### Rollback

Revert commit fase 4.

---

## Fase 5 — Upgrade Orchestrator dan Aggregate

Tujuan: menyelaraskan Agent dengan contract akhir.

### Langkah

1. Edit:

```text
modules/shared/src/server/contract_server_aggregate.py
```

2. Terapkan signature akhir dari §5.4.

3. Edit:

```text
modules/server/src/agent_server_orchestrator.py
```

4. Pastikan orchestrator:

```text
- generate request_id jika kosong
- mengecek connection state sebelum operasi baru
- reject operasi saat reconnect
- enqueue code_sync dan scene command
- bypass non-scene command
- menjalankan queue worker
- set active operation di connection
- cancel pending saat disconnect/shutdown/permanent failure
- komposisi metrics
- return typed VO, bukan dict
```

5. Hapus semua return `dict` dari metode publik aggregate.

### Exit Criteria

```text
send_command mengembalikan CommandResult.
poll_task_result mengembalikan TaskStatus.
cancel_async_task tersedia.
get_metrics tersedia.
pytest hijau.
```

---

## Fase 6 — Root Container Simplification

Tujuan: wiring akhir hanya 3 capability + 1 orchestrator.

### Langkah

1. Edit:

```text
modules/server/src/root_server_container.py
```

2. Wiring akhir:

```python
connection = BlenderConnection()

command_adapter = BlenderCommandAdapter(
    connection_port=connection,
    queue_config=queue_config,
)

code_executor = CodeExecutionAdapter(
    connection_port=connection,
    task_config=task_config,
    security_policy=security_policy,
)

orchestrator = ServerOrchestrator(
    connection=connection,
    code_executor=code_executor,
    command_adapter=command_adapter,
)

await orchestrator.start()
```

3. Hapus wiring:

```text
event bus
metrics collector
operation queue terpisah
```

4. `shutdown()` harus:

```python
await orchestrator.shutdown()
```

Bukan memanggil coroutine tanpa await.

### Exit Criteria

```text
Container tidak mengimport artefak v1 yang dihapus.
start/shutdown async benar.
pytest integration hijau.
```

---

## Fase 7 — Cleanup dan Audit AES

### Langkah

1. Hapus semua import mati.

2. Update:

```text
modules/shared/src/server/__init__.py
modules/server/src/__init__.py
```

3. Jalankan:

```bash
uv run ruff check .
uv run mypy modules/server modules/shared/src/server
uv run pytest
lint-arwaky-cli scan .
```

4. Tambahkan test audit struktur:

```python
from pathlib import Path


def test_server_has_exactly_three_capabilities():
    files = list(Path("modules/server/src").glob("capabilities_*.py"))
    names = sorted(f.name for f in files)

    assert names == [
        "capabilities_blender_command_adapter.py",
        "capabilities_blender_connection.py",
        "capabilities_code_execution_adapter.py",
    ]


def test_server_shared_has_exactly_four_contracts():
    files = list(Path("modules/shared/src/server").glob("contract_*.py"))
    names = sorted(f.name for f in files)

    assert names == [
        "contract_code_execution_protocol.py",
        "contract_command_protocol.py",
        "contract_connection_protocol.py",
        "contract_server_aggregate.py",
    ]
```

### Exit Criteria

```text
Tepat 3 capability.
Tepat 4 contract.
Tidak ada contract baru.
Tidak ada capability baru.
AES lint pass.
```

---

## 9. File Disposition Table

| File | Status v2 | Aksi |
| --- | --- | --- |
| `contract_connection_protocol.py` | UPGRADE | Tambah `request_id`, `timeout_ms`, `set_active_operation_in_progress`, `get_diagnostics` |
| `contract_command_protocol.py` | UPGRADE | Queue dikembalikan dan diperkuat |
| `contract_code_execution_protocol.py` | UPGRADE | `TaskStatus`, `cancel_async_task`, `execute_task`, `get_task_stats` |
| `contract_server_aggregate.py` | UPGRADE | `CommandResult`, `TaskStatus`, `cancel_async_task`, `get_metrics`, lifecycle |
| `taxonomy_server_vo.py` | UPGRADE | Tambah VO diagnostik, queue, metrics |
| `taxonomy_server_event.py` | TETAP/UPRADE | Event tetap ada, publish via utility |
| `taxonomy_server_error.py` | TETAP/UPRADE | Rename error jika belum |
| `utility_server_telemetry.py` | BARU | Satu-satunya file baru yang diperbolehkan |
| `capabilities_blender_connection.py` | UPGRADE | Async benar, diagnostics, publish via utility |
| `capabilities_code_execution_adapter.py` | UPGRADE | Task lifecycle, stats, publish via utility |
| `capabilities_blender_command_adapter.py` | UPGRADE | Memiliki queue lagi |
| `agent_server_orchestrator.py` | UPGRADE | Worker loop, metrics composition, typed return |
| `root_server_container.py` | UPGRADE | Wiring sederhana |
| `surface_server_diagnostics_controller.py` | TETAP | Boleh ada, mengonsumsi aggregate |
| `contract_operation_queue_protocol.py` | HAPUS | Merge ke command protocol |
| `contract_event_bus_protocol.py` | HAPUS | Ganti utility telemetry |
| `contract_metrics_protocol.py` | HAPUS | Ganti diagnostik protocol existing |
| `capabilities_operation_queue.py` | HAPUS | Merge ke command adapter |
| `capabilities_event_bus_inmemory.py` | HAPUS | Ganti utility telemetry |
| `capabilities_metrics_collector.py` | HAPUS | Counter pindah ke capability existing |

---

## 10. Acceptance Criteria Delta

Suite plan v1 tetap berlaku. Tambahan khusus v2:

```gherkin
Feature: Koreksi arsitektur v2

  Scenario: Tidak ada contract baru
    When audit file contract dijalankan
    Then shared/server memiliki tepat 4 contract file
    And tidak ada contract_operation_queue_protocol.py
    And tidak ada contract_event_bus_protocol.py
    And tidak ada contract_metrics_protocol.py

  Scenario: Tidak ada capability baru
    When audit file capability dijalankan
    Then modules/server/src memiliki tepat 3 capability file
    And tidak ada capabilities_operation_queue.py
    And tidak ada capabilities_event_bus_inmemory.py
    And tidak ada capabilities_metrics_collector.py

  Scenario: Queue tetap milik FR-003
    Given operasi scene dikirim
    When operasi masuk queue
    Then queue state dimiliki oleh BlenderCommandAdapter
    And worker loop dijalankan oleh ServerOrchestrator

  Scenario: Event tetap terbit tanpa event bus
    Given execute_code berhasil
    When event CodeExecuted diterbitkan
    Then structured log menerima event tersebut
    And tidak ada InMemoryEventBus yang dipakai

  Scenario: Metrics dikomposisi dari protocol existing
    Given satu eksekusi code sukses
    And satu command sukses
    And satu security violation
    When get_metrics dipanggil
    Then ServerMetrics dibangun dari ConnectionDiagnostics, QueueStats, dan TaskStats
    And tidak ada IMetricsProvider dipakai
```

---

## 11. Definition of Done v2

### Struktur

- [ ] Tepat 3 capability di `modules/server/src`.
- [ ] Tepat 4 contract di `modules/shared/src/server`.
- [ ] Tidak ada contract baru.
- [ ] Tidak ada capability baru.
- [ ] Satu-satunya file baru adalah `utility_server_telemetry.py`.

### Perilaku

- [ ] Queue FIFO berjalan.
- [ ] Queue full menghasilkan `TooManyPendingOperationsError`.
- [ ] Queue wait timeout menghasilkan `OperationWaitTimeoutError`.
- [ ] Pending operation dibatalkan saat disconnect.
- [ ] Pending operation dibatalkan saat koneksi gagal permanen.
- [ ] Task polling mengembalikan `TaskStatus`.
- [ ] Task cancellation tersedia melalui aggregate.
- [ ] Command return `CommandResult`.
- [ ] Metrics return `ServerMetrics`.
- [ ] Event terbit sebagai structured log.
- [ ] Raw code tidak pernah dilog.

### Kualitas

- [ ] `uv run pytest` hijau.
- [ ] `uv run ruff check .` hijau.
- [ ] `uv run mypy modules/server modules/shared/src/server` hijau.
- [ ] `lint-arwaky-cli scan .` hijau.
- [ ] Test audit struktur lolos.
- [ ] Nilai metrics identik dengan baseline v1.

---

## 12. Urutan Kerja Developer

```text
Fase 0 → characterization tests
Fase 1 → taxonomy additive
Fase 2 → telemetry utility, hapus event bus
Fase 3 → queue kembali ke command adapter
Fase 4 → diagnostics & metrics composition
Fase 5 → orchestrator & aggregate upgrade
Fase 6 → root container simplification
Fase 7 → cleanup & AES audit
```

Aturan commit:

```text
Satu fase = satu pull request.
Jangan campur dua fase dalam satu PR.
Setiap PR harus melampirkan hasil pytest, ruff, mypy, dan AES lint.
```

---

## 13. Penegasan Akhir

Plan v2 ini mengoreksi kesalahan plan v1 dengan aturan tegas:

```text
1 FR = 1 Capability = 1 Protocol.
Contract existing di-upgrade.
Tidak ada contract baru.
Tidak ada capability baru.
Observability diselesaikan lewat Utility dan diagnostik capability.
Agent mengkomposisi metrics, bukan memiliki capability metrics terpisah.
```
```