
Bisa. Saya desain ulang **semua FRD** agar punya **clear separation of concern**, tidak ada feature yang “mengurus semuanya”, dan tidak ada duplikasi/overlap antar feature.

Inti redesign:

1. **Feature domain** hanya mengurus domainnya: `object`, `scene`, `render`, `asset`.
2. **Feature platform** mengurus kemampuan lintas sistem: `config`, `security`, `launcher`, `gateway`, `dispatcher`, `job`, `diagnostics`, `telemetry`.
3. **CLI dan MCP bukan core engine**. Keduanya hanya **surface** yang memakai feature yang sama.
4. Semua concern berulang seperti:

   - settings,
   - background task,
   - queue/sequential execution,
   - security/path validation,
   - health/metrics/logs,
   - tracking ID,
   - error envelope,

   harus punya **satu owner** dan feature lain hanya **memakai**.

---

# 1. Prinsip Desain Ulang FRD

## 1.1 Satu Feature, Satu Tanggung Jawab

Setiap feature hanya boleh punya satu alasan untuk berubah.

Contoh salah:

```text
Server feature mengurus:
- connection
- command dispatch
- custom code execution
- queue
- background task
- metrics
- security
- timeout policy
- tracking
```

Ini terlalu bloat.

Contoh benar:

```text
Gateway:
- connection
- transport
- queue/scene lock
- raw code execution transport

Dispatcher:
- action catalog
- validation
- routing
- result normalization

Job:
- background task lifecycle

Security:
- path validation
- archive extraction safety
- code validation

Diagnostics:
- health
- metrics
- audit log
- tracing
```

---

## 1.2 Feature Platform Tidak Boleh Mengandung Domain 3D

Platform feature tidak boleh tahu soal cube, camera, HDRI, material, modifier, scene cleanup, dan sebagainya.

Contoh:

```text
Gateway tidak boleh tahu cara membuat cube.
Gateway hanya mengirim request ke Blender dan menerima response.
```

```text
Job tidak boleh tahu cara render.
Job hanya melacak status background task.
```

```text
Config tidak boleh tahu aturan material.
Config hanya load/get settings.
```

---

## 1.3 Feature Domain Tidak Boleh Mengurus Infrastruktur

Feature domain seperti `object`, `scene`, `render`, `asset` tidak boleh mendefinisikan ulang:

```text
settings loading
queue
socket connection
background task lifecycle
metrics
telemetry
path traversal protection
tracking ID generation
error serialization
```

Mereka hanya memakai platform feature.

---

## 1.4 CLI dan MCP Adalah Surface, Bukan Core

FRD lama mengatakan:

> CLI is the foundational execution engine.

Ini berbahaya secara arsitektur.

Desain baru:

```text
CLI = surface
MCP = surface
Core = dispatcher + domain features + gateway + platform services
```

CLI dan MCP harus punya perilaku 1:1 karena keduanya memanggil **aggregate yang sama**, bukan karena MCP membungkus CLI.

---

# 2. Peta Module Baru

Saya mengusulkan struktur feature berikut.

```text
modules/
├── config/
├── security/
├── launcher/
├── gateway/
├── dispatcher/
├── job/
├── diagnostics/
├── telemetry/
├── asset/
├── object/
├── scene/
├── render/
├── cli/
└── mcp/
```

Module lama `server` sebaiknya dipecah/diganti menjadi:

```text
server → gateway + dispatcher + security + diagnostics + job
```

Karena `server` saat ini menanggung terlalu banyak tanggung jawab.

---

# 3. Ownership Matrix

Ini tabel owner untuk semua concern yang sebelumnya sering duplikat.


| Concern                            | Owner                    | Konsumen                                |
| ------------------------------------ | -------------------------- | ----------------------------------------- |
| Load settings                      | `config`                 | semua feature                           |
| Get settings                       | `config`                 | semua feature                           |
| Project root/workspace             | `config`                 | asset, render, security                 |
| Secret redaction                   | `security` atau `config` | diagnostics, cli, mcp                   |
| Path allowed directory             | `security`               | asset, render, gateway/code execution   |
| Path traversal protection          | `security`               | asset, render                           |
| Archive extraction safety          | `security`               | asset                                   |
| Untrusted code validation          | `security`               | gateway                                 |
| Blender process locate             | `launcher`               | cli, mcp, diagnostics                   |
| Blender process launch             | `launcher`               | cli, mcp                                |
| Blender process shutdown           | `launcher`               | cli, mcp                                |
| Blender process status             | `launcher`               | cli, mcp, diagnostics                   |
| Runtime state persistence          | `launcher`               | cli                                     |
| Blender connection                 | `gateway`                | dispatcher, domain features             |
| Heartbeat/reconnect                | `gateway`                | diagnostics                             |
| Message framing                    | `gateway`                | dispatcher, domain features             |
| Scene operation queue              | `gateway`                | dispatcher, domain features             |
| Raw command transport              | `gateway`                | dispatcher, domain features             |
| Raw Python execution transport     | `gateway`                | dispatcher                              |
| Action catalog                     | `dispatcher`             | cli, mcp                                |
| Action validation                  | `dispatcher`             | cli, mcp                                |
| Action routing                     | `dispatcher`             | cli, mcp                                |
| Background task lifecycle          | `job`                    | dispatcher, asset, render, gateway/code |
| Health check                       | `diagnostics`            | cli, mcp                                |
| Operational metrics                | `diagnostics`            | cli, mcp, internal                      |
| Audit log                          | `diagnostics`            | security, gateway, dispatcher           |
| Structured logging policy          | `diagnostics`            | semua feature                           |
| Anonymous product analytics        | `telemetry`              | dispatcher, launcher, error handler     |
| Object CRUD/transform/material     | `object`                 | dispatcher                              |
| Scene inspect/cleanup              | `scene`                  | dispatcher                              |
| Render/screenshot/camera/HDRI      | `render`                 | dispatcher                              |
| Asset search/download/cache/import | `asset`                  | dispatcher, render                      |

---

# 4. Redesain FRD per Module

---

## 4.1 `config` FRD

## Nama Feature

```text
Configuration & Workspace Feature
```

## Purpose

Mengurus bagaimana aplikasi membaca, memvalidasi, dan menyediakan settings.

## Owns

- Load settings dari file, environment, dan default.
- Precedence rules.
- Type conversion.
- Validation schema.
- Immutable settings snapshot.
- Hierarchical setting retrieval.
- Project workspace resolution.
- Settings metadata.
- Redaction policy untuk secret values.

## Does Not Own

- Runtime process state.
- Blender connection state.
- Background task state.
- Feature-specific business rules.
- Command catalog.
- Logging infrastructure.

## Functional Requirements

### FR-CFG-001: Load and Apply Settings

Sama seperti FR-CFG-001 lama, tetapi lebih tegas:

```text
Config adalah satu-satunya feature yang load settings.
Feature lain tidak boleh membaca file config langsung.
```

### FR-CFG-002: Retrieve Settings Values

```text
Feature lain meminta setting melalui config.
Config mengembalikan nilai immutable atau deep copy.
```

### FR-CFG-003: Resolve Project Workspace Directory

```text
Config menentukan project root.
Asset dan render tidak menentukan sendiri aturan project root.
```

### FR-CFG-004: Provide Settings Metadata

```text
Config menyediakan sumber config, jumlah override, dan warning.
Metadata tidak boleh membocorkan secret.
```

### FR-CFG-005: Provide Redaction Rules

```text
Config atau security menyediakan daftar key yang sensitif.
Diagnostics, CLI, dan MCP memakai aturan ini untuk masking.
```

## Consumes

Tidak ada feature lain.

## Provides To

Semua feature.

---

## 4.2 `security` FRD

Ini module baru yang sangat penting untuk menghilangkan duplikasi aturan keamanan.

## Nama Feature

```text
Security Policy Feature
```

## Purpose

Mengurus kebijakan keamanan file, archive, code, dan secret redaction.

## Owns

- Allowed directory policy.
- Path traversal validation.
- Safe archive extraction.
- Untrusted Python code validation.
- Sensitive value redaction.
- Security audit event definition.

## Does Not Own

- Connection authentication.
- Network transport.
- Background task.
- Asset provider logic.
- Render output logic.
- Object/scene logic.

## Functional Requirements

### FR-SEC-001: Validate File Path Access

```text
Semua feature yang ingin menulis file harus memanggil security.
Security mengecek apakah path berada dalam allowed directory.
Security menolak path traversal, symlink escape, dan path di luar allowed dirs.
```

### FR-SEC-002: Safely Extract Archive

```text
Asset tidak boleh implement path traversal protection sendiri.
Asset memakai security untuk ekstraksi archive.
```

### FR-SEC-003: Validate Untrusted Code

```text
Gateway tidak boleh implement AST validator sendiri secara terpisah.
Gateway memakai security untuk validasi code.
```

### FR-SEC-004: Redact Sensitive Values

```text
Security menyediakan fungsi redaction untuk log, diagnostics, CLI, dan MCP.
Raw code, token, credential, dan path sensitif tidak boleh muncul di log.
```

### FR-SEC-005: Emit Security Audit Events

```text
Setiap security violation menghasilkan audit event.
Diagnostics mengonsumsi audit event ini.
```

## Consumes

- `config`

## Provides To

- `gateway`
- `asset`
- `render`
- `diagnostics`
- `cli`
- `mcp`

---

## 4.3 `launcher` FRD

Ini mengambil sebagian besar FR-CLI lama.

## Nama Feature

```text
Blender Runtime Launcher Feature
```

## Purpose

Mengurus lifecycle process Blender: locate, launch, shutdown, status, dan runtime state.

## Owns

- Locate Blender executable.
- Register Blender path.
- Launch Blender dengan integration component.
- Graceful shutdown.
- Force shutdown fallback.
- Process status.
- Runtime state persistence.

## Does Not Own

- 3D scene actions.
- Command catalog.
- MCP protocol.
- CLI formatting.
- Blender socket connection.
- Background task.
- Telemetry.

## Functional Requirements

### FR-LAU-001: Locate and Register Application

Dari FR-CLI-001 lama.

```text
Launcher mencari Blender executable.
Launcher memvalidasi executable.
Launcher menyimpan path melalui config atau state store.
```

### FR-LAU-002: Launch Application

Dari FR-CLI-002 lama.

```text
Launcher memulai Blender.
Launcher memastikan integration component aktif.
Launcher menunggu Blender siap.
```

### FR-LAU-003: Shut Down Application

Dari FR-CLI-003 lama.

```text
Launcher melakukan graceful shutdown.
Jika unresponsive, launcher force terminate.
```

### FR-LAU-004: Check Runtime Status

Dari FR-CLI-004 lama.

```text
Launcher mengecek apakah process benar-benar hidup.
Launcher mendeteksi stale state.
```

### FR-LAU-005: Persist Runtime State

Dari FR-CLI-007 lama.

```text
Launcher menyimpan state path dan running status.
State corruption tidak boleh membuat aplikasi crash.
```

## Consumes

- `config`
- `diagnostics` untuk health composition

## Provides To

- `cli`
- `mcp`
- `diagnostics`

---

## 4.4 `gateway` FRD

Ini pengganti utama `server` lama, tetapi jauh lebih fokus.

## Nama Feature

```text
Blender Gateway Feature
```

## Purpose

Mengurus komunikasi tingkat rendah antara aplikasi dan Blender.

## Owns

- Connection lifecycle ke Blender.
- Handshake.
- Authentication transport.
- Protocol version compatibility.
- Heartbeat/liveness.
- Reconnect.
- Message framing.
- Request/response correlation.
- Payload size limit.
- Scene operation scheduler/queue.
- Raw command transport.
- Raw Python code execution transport.

## Does Not Own

- Action catalog.
- Domain command schema.
- Object/scene/render business rules.
- Background task lifecycle.
- Product analytics.
- Operational metrics storage.
- Settings loading.
- Process launching.

## Functional Requirements

### FR-GWY-001: Establish Connection

```text
Gateway menghubungkan aplikasi ke Blender.
Gateway melakukan handshake.
Gateway memverifikasi protocol version.
Gateway melakukan authentication jika diperlukan.
```

### FR-GWY-002: Maintain Connection

```text
Gateway mengirim heartbeat.
Gateway mendeteksi stale connection.
Gateway melakukan reconnect dengan retry policy.
Gateway melaporkan connection state.
```

### FR-GWY-003: Transport Request and Response

```text
Gateway mengirim command generic ke Blender.
Gateway menerima response.
Gateway enforce timeout transport.
Gateway enforce payload limit.
Gateway menyertakan tracking ID.
```

### FR-GWY-004: Serialize Scene-Mutating Operations

```text
Gateway memiliki queue untuk operasi yang mengubah scene.
Gateway memproses operasi scene satu per satu.
Read-only operations boleh bypass queue.
Queue depth limit dan wait timeout diatur oleh config.
```

Ini memindahkan aturan sequential execution yang sebelumnya duplikat di:

```text
object FRD
scene FRD
render FRD
server FRD
cli FRD
mcp FRD
```

Sekarang hanya ada di `gateway`.

### FR-GWY-005: Execute Raw Python Code

```text
Gateway mengirim Python code ke Blender.
Gateway memakai security untuk validasi code.
Gateway enforce execution timeout.
Gateway truncate output jika terlalu besar.
Gateway tidak menyimpan task lifecycle.
```

Jika code execution dijalankan sebagai background task, maka lifecycle task tetap milik `job`.

## Consumes

- `config`
- `security`
- `diagnostics` untuk emit event/metrics

## Provides To

- `dispatcher`
- `object`
- `scene`
- `render`
- `asset`

---

## 4.5 `dispatcher` FRD

Ini module baru untuk menghilangkan duplikasi antara CLI execute, MCP execute, command catalog, dan validasi action.

## Nama Feature

```text
Action Dispatcher Feature
```

## Purpose

Mengurus katalog action, validasi request, routing ke feature domain, dan normalisasi result.

## Owns

- Action catalog.
- Action schema.
- Action metadata:
  - timeout default
  - max timeout
  - idempotent
  - mutates scene
  - background allowed
  - destructive
- Request validation.
- Routing action ke feature yang benar.
- Background submission coordination.
- Unified result envelope.
- Tracking ID propagation.

## Does Not Own

- Blender transport.
- Queue.
- Task lifecycle.
- Security validation.
- Domain business rules.
- Logging/metrics storage.

## Functional Requirements

### FR-DSP-001: Register Action Catalog

```text
Domain features mendaftarkan action ke dispatcher.
Dispatcher menyimpan metadata action.
```

### FR-DSP-002: Discover Actions

```text
CLI dan MCP meminta daftar action dari dispatcher.
Dispatcher mengembalikan katalog yang sama ke keduanya.
```

### FR-DSP-003: Validate Action Request

```text
Dispatcher memvalidasi action name dan parameters.
Unknown action menghasilkan ValidationError.
Invalid parameters menghasilkan ValidationError.
```

### FR-DSP-004: Dispatch Synchronous Action

```text
Dispatcher meneruskan action ke feature domain atau gateway.
Dispatcher mengembalikan result terstandar.
```

### FR-DSP-005: Submit Background Action

```text
Jika action mendukung background execution, dispatcher membuat job.
Dispatcher mengembalikan task ID.
Dispatcher tidak mengelola lifecycle task secara langsung.
```

### FR-DSP-006: Normalize Operation Result

```text
Semua hasil action dikembalikan dalam envelope yang sama.
Envelope berisi:
- success
- data
- error category
- message
- tracking_id
- warnings
- metadata
```

## Consumes

- `gateway`
- `object`
- `scene`
- `render`
- `asset`
- `job`
- `security`
- `diagnostics`

## Provides To

- `cli`
- `mcp`

---

## 4.6 `job` FRD

FRD job relatif tetap, tetapi sekarang menjadi satu-satunya owner background task.

## Nama Feature

```text
Background Job Tracking Feature
```

## Purpose

Melacak lifecycle background task.

## Owns

- Task creation.
- Task ID.
- Task state.
- Progress.
- Cancellation request.
- Final result reference.
- Error state.
- Retention/cleanup.
- Capacity limit.

## Does Not Own

- Execution logic.
- Download logic.
- Render logic.
- Code execution logic.
- Connection state.
- Metrics storage.

## Functional Requirements

Pertahankan FR-JOB lama:

```text
FR-JOB-001 Track and update task lifecycle
FR-JOB-002 Monitor task status
FR-JOB-003 Cancel task
FR-JOB-004 Automatic cleanup
```

Tambahkan aturan:

```text
Job tidak boleh dieksekusi langsung oleh feature domain tanpa tracking ID.
Semua background operation harus mendaftar ke job.
```

## Consumes

- `config`
- `diagnostics` untuk event

## Provides To

- `dispatcher`
- `asset`
- `render`
- `gateway`

---

## 4.7 `diagnostics` FRD

Ini module baru untuk health, metrics, audit, dan logging.

## Nama Feature

```text
Diagnostics & Observability Feature
```

## Purpose

Mengurus health check, operational metrics, structured logging, audit events, dan tracing.

## Owns

- Health status composition.
- Operational metrics.
- Structured local logs.
- Audit events.
- Trace correlation by tracking ID.
- Diagnostics snapshot.

## Does Not Own

- Anonymous product analytics.
- Business rules.
- Settings loading.
- Task execution.
- Connection mechanics.

## Functional Requirements

### FR-DIA-001: Compose System Health

```text
Diagnostics mengecek:
- launcher status
- gateway connection status
- config validity
- asset provider availability optional
- job capacity
```

### FR-DIA-002: Collect Operational Metrics

```text
Diagnostics mengumpulkan:
- pending operations
- reconnect count
- execution latency
- command latency
- failed request count
- security violation count
- task created/failed/completed count
```

### FR-DIA-003: Emit Audit Events

```text
Security violation, connection failure, task failure, dan destructive action harus audit-able.
```

### FR-DIA-004: Structured Logging Policy

```text
Semua feature mengirim log melalui kebijakan diagnostics.
Log harus terstruktur.
Log tidak boleh mengandung raw code, token, atau secret.
```

### FR-DIA-005: Provide Diagnostics Snapshot

```text
CLI dan MCP mengambil health/metrics dari diagnostics.
Mereka tidak menghitung sendiri.
```

## Consumes

- `launcher`
- `gateway`
- `dispatcher`
- `job`
- `security`
- `config`

## Provides To

- `cli`
- `mcp`
- internal observability

---

## 4.8 `telemetry` FRD

Telemetry tetap, tetapi harus dipisahkan dari diagnostics.

## Nama Feature

```text
Anonymous Product Telemetry Feature
```

## Purpose

Mengumpulkan anonymous usage analytics secara opt-in.

## Owns

- Opt-in consent.
- Anonymous event recording.
- Session ID.
- Environment metadata.
- Event categorization.
- Background transmission.

## Does Not Own

- Operational logs.
- Health check.
- Metrics for debugging.
- Error diagnostics.
- Security audit.

## Functional Requirements

Pertahankan FR-TLM lama:

```text
FR-TLM-001 Record anonymous usage event
FR-TLM-002 Classify events
FR-TLM-003 Manage sessions
FR-TLM-004 Enrich environment metadata
```

Tambahkan aturan tegas:

```text
Telemetry tidak boleh dipakai untuk operational debugging.
Telemetry tidak boleh menyimpan PII.
Telemetry tidak boleh memblokir operasi utama.
```

---

## 4.9 `asset` FRD

Asset perlu dirapikan karena saat ini overlap dengan object, render, security, job, dan config.

## Nama Feature

```text
External Asset Feature
```

## Purpose

Mengurus pencarian, download, cache, ekstraksi, dan import asset eksternal.

## Owns

- Provider search.
- Provider authentication usage.
- Asset metadata normalization.
- Download to cache.
- Cache reuse.
- Overwrite policy.
- Resolution preference.
- Safe archive extraction.
- Asset import into Blender.
- License/attribution metadata.

## Does Not Own

- Object manipulation setelah import.
- Scene cleanup.
- HDRI lighting setup.
- Render output.
- Path traversal protection.
- Background task lifecycle.
- Settings loading.

## Functional Requirements Baru

### FR-AST-001: Search Assets Across Providers

Gabungan FR-AST-001, FR-AST-003, FR-AST-005 lama.

```text
Asset menyediakan satu search operation.
Provider-specific behavior ditangani oleh provider adapter internal.
```

### FR-AST-002: Download Asset to Cache

Gabungan FR-AST-002 dan FR-AST-004 lama.

```text
Asset download file ke cache.
Asset memakai security untuk validasi path.
Asset memakai job jika download besar.
```

### FR-AST-003: Extract Asset Archive

```text
Asset memakai security untuk ekstraksi.
Asset tidak boleh implement path traversal protection sendiri.
```

### FR-AST-004: Import Asset into Blender

```text
Asset meng-import file asset ke Blender.
Asset mengembalikan object reference.
Setelah import, object manipulation menjadi tanggung jawab object feature.
```

### FR-AST-005: Manage Provider Metadata

```text
Asset menormalisasi metadata:
- name
- provider
- type
- categories
- preview
- license
- download availability
```

## Boundary Penting

### Asset vs Object

```text
Asset: download + import asset menjadi object.
Object: manipulate object yang sudah ada.
```

Contoh:

```text
asset.import_asset(model.glb) → object refs
object.set_transform(object_ref, location) → transform
```

### Asset vs Render

```text
Asset: download HDRI file.
Render: setup HDRI lighting di scene.
```

Contoh:

```text
asset.download_asset(hdri_id) → local file
render.configure_hdri(local_file, strength) → world lighting
```

---

## 4.10 `object` FRD

Object feature harus fokus ke manipulasi object.

## Nama Feature

```text
Object Management Feature
```

## Purpose

Mengurus object 3D yang sudah ada di scene.

## Owns

- Create primitive.
- Place existing object.
- Transform object.
- Material assignment.
- Modifier management.
- Delete object.
- Get object info.

## Does Not Own

- Asset download.
- Asset import.
- Scene cleanup bulk.
- Render.
- Camera lens/framing.
- HDRI.
- Queue.
- Background task.

## Functional Requirements

Pertahankan FR-OBJ lama, tetapi ubah FR-OBJ-001.

### FR-OBJ-001: Place Existing Object

Bukan lagi:

```text
Place object or asset reference with automatic import.
```

Menjadi:

```text
Place existing object reference.
Jika asset belum di-import, caller harus memakai asset feature.
```

Ini menghilangkan overlap dengan asset.

### FR-OBJ-002: Create Primitive

Tetap.

### FR-OBJ-003: Set Transform

Tetap.

### FR-OBJ-004: Set Material

Tetap.

### FR-OBJ-005: Manage Modifiers

Tetap.

### FR-OBJ-006: Delete Object

Tetap untuk single object.

### FR-OBJ-007: Get Object Info

Tetap.

## Boundary Penting

### Object vs Scene

```text
Object: operasi satu object.
Scene: operasi scene-level/bulk.
```

Contoh:

```text
object.delete_object(object_ref)
scene.cleanup_scene(preserve_cameras=true)
```

### Object vs Render

```text
Object dapat mengubah transform camera secara generic.
Render memiliki camera setup khusus: lens, framing, active camera, depth of field.
```

Aturan:

```text
Untuk camera workflow, gunakan render.configure_camera.
Untuk direct transform generic, gunakan object.set_transform.
```

---

## 4.11 `scene` FRD

Scene feature fokus ke scene-level inspection dan cleanup.

## Nama Feature

```text
Scene Management Feature
```

## Purpose

Mengurus inspeksi scene dan cleanup bulk.

## Owns

- Inspect scene state.
- Scene metadata.
- Object summary.
- Camera/light summary.
- Render settings summary.
- Bulk cleanup.
- Preservation policy.
- Dry-run cleanup.

## Does Not Own

- Single object CRUD.
- Material detail.
- Modifier detail.
- Render execution.
- Asset import.
- Queue.
- Background task.

## Functional Requirements

### FR-SCN-001: Inspect Scene State

Tetap.

### FR-SCN-002: Cleanup Scene Objects

Tetap, tetapi harus memakai object feature untuk deletion primitives.

```text
Scene cleanup menentukan policy.
Object deletion melaksanakan penghapusan teknis.
```

Ini mencegah duplikasi aturan delete.

---

## 4.12 `render` FRD

Render feature fokus ke visual output dan camera/environment workflow.

## Nama Feature

```text
Rendering & Viewport Feature
```

## Purpose

Mengurus screenshot, render, camera setup, dan HDRI lighting.

## Owns

- Viewport screenshot.
- Scene render.
- Render settings.
- Camera configuration.
- HDRI environment lighting.
- Output file policy untuk render.

## Does Not Own

- Asset download internals.
- Generic object manipulation.
- Scene cleanup.
- Background task lifecycle.
- Queue.
- Path traversal protection.

## Functional Requirements

### FR-RND-001: Capture Viewport Screenshot

Tetap.

### FR-RND-002: Render Scene Image

Tetap, tetapi:

```text
Render memakai security untuk validasi output path.
Render memakai job untuk long-running render.
Render memakai diagnostics untuk metrics/log.
```

### FR-RND-003: Configure Camera

Tetap.

Boundary:

```text
Render owns camera-specific setup.
Object owns generic transform.
```

### FR-RND-004: Configure HDRI Lighting

Tetap, tetapi:

```text
Render tidak download HDRI sendiri.
Render memakai asset feature untuk mendapatkan HDRI file.
```

---

## 4.13 `cli` FRD

CLI harus menjadi surface saja.

## Nama Feature

```text
CLI Surface
```

## Purpose

Menyediakan interface terminal untuk user.

## Owns

- Command parsing.
- Terminal output formatting.
- Human-readable errors.
- Command help.
- Masking output sensitive values.
- Mapping CLI command ke aggregate.

## Does Not Own

- Business rules.
- Process lifecycle logic.
- Connection logic.
- Command validation.
- Settings loading.
- Health computation.
- Task lifecycle.

## Functional Requirements Baru

### FR-CLI-001: Parse and Route Commands

```text
CLI menerima command.
CLI menerjemahkan ke aggregate call.
CLI tidak memproses bisnis sendiri.
```

### FR-CLI-002: Render Terminal Output

```text
CLI menampilkan hasil dalam format yang jelas.
CLI mendukung JSON output jika diminta.
```

### FR-CLI-003: Display Errors

```text
CLI menampilkan error category dan pesan actionable.
CLI tidak menampilkan secret.
```

## Command Mapping


| CLI Command   | Target Feature             |
| --------------- | ---------------------------- |
| `init`        | `launcher`                 |
| `run`         | `launcher`                 |
| `close`       | `launcher`                 |
| `status`      | `diagnostics` + `launcher` |
| `execute`     | `dispatcher`               |
| `list`        | `dispatcher`               |
| `config`      | `config`                   |
| `health`      | `diagnostics`              |
| `task status` | `job`                      |
| `task cancel` | `job`                      |

---

## 4.14 `mcp` FRD

MCP juga harus menjadi surface saja.

## Nama Feature

```text
MCP Surface
```

## Purpose

Menyediakan MCP tools untuk AI client.

## Owns

- MCP service lifecycle.
- Tool schema exposure.
- MCP protocol compliance.
- Tool input parsing.
- Tool output serialization.
- Error formatting sesuai MCP.

## Does Not Own

- 3D execution logic.
- Command catalog logic.
- Health computation.
- Config loading.
- Task lifecycle.
- Connection logic.

## Functional Requirements Baru

### FR-MCP-001: Expose MCP Tools

```text
MCP menampilkan tool schema.
Tool schema diambil dari dispatcher, config, diagnostics, job.
```

### FR-MCP-002: Route Tool Calls

```text
MCP meneruskan tool call ke aggregate yang sama dengan CLI.
```

### FR-MCP-003: Format MCP Responses

```text
MCP mengembalikan structured response.
MCP menyertakan tracking ID.
MCP tidak memuat payload terlalu besar.
```

## Tool Mapping


| MCP Tool             | Target Feature      |
| ---------------------- | --------------------- |
| `execute_command`    | `dispatcher`        |
| `list_commands`      | `dispatcher`        |
| `health_check`       | `diagnostics`       |
| `get_config`         | `config`            |
| `read_skill_context` | static docs surface |
| `get_task_status`    | `job`               |
| `cancel_task`        | `job`               |

---

# 5. Perubahan Besar dari FRD Lama

## 5.1 Server FRD Harus Dipecah

FRD server lama terlalu bloat.


| Server Lama                 | Pindah Ke                      |
| ----------------------------- | -------------------------------- |
| Connection                  | `gateway`                      |
| Heartbeat/reconnect         | `gateway`                      |
| Custom code execution       | `gateway` + `security`         |
| Standard commands           | `dispatcher` + domain features |
| Queue/sequential processing | `gateway`                      |
| Background tasks            | `job`                          |
| Metrics                     | `diagnostics`                  |
| Logging                     | `diagnostics`                  |
| Security violation          | `security` + `diagnostics`     |
| Tracking ID                 | shared taxonomy +`diagnostics` |

---

## 5.2 CLI FRD Harus Dikecilkan

CLI lama mengandung terlalu banyak bisnis.


| CLI Lama         | Pindah Ke                    |
| ------------------ | ------------------------------ |
| Locate app       | `launcher`                   |
| Launch app       | `launcher`                   |
| Shutdown app     | `launcher`                   |
| Status app       | `launcher` + `diagnostics`   |
| Execute action   | `dispatcher`                 |
| List actions     | `dispatcher`                 |
| Config           | `config`                     |
| Persist state    | `launcher`                   |
| Error formatting | tetap di CLI sebagai surface |

---

## 5.3 MCP FRD Harus Dikecilkan

MCP lama mencoba menjelaskan behavior yang seharusnya milik core.


| MCP Lama            | Pindah Ke                                          |
| --------------------- | ---------------------------------------------------- |
| Execute 3D action   | `dispatcher`                                       |
| Discover actions    | `dispatcher`                                       |
| Health check        | `diagnostics`                                      |
| Get config          | `config`                                           |
| 1:1 parity with CLI | hasil dari CLI dan MCP memakai aggregate yang sama |

---

## 5.4 Asset FRD Harus Lebih Fokus


| Asset Lama                              | Perbaikan                                               |
| ----------------------------------------- | --------------------------------------------------------- |
| Search library dan marketplace terpisah | jadikan satu search abstraction dengan provider adapter |
| Download dan import bercampur           | pisahkan download, extract, import                      |
| Path traversal rules                    | pindah ke`security`                                     |
| Background download                     | pakai`job`                                              |
| HDRI lighting                           | tetap di`render`, asset hanya download                  |

---

## 5.5 Render FRD Harus Lebih Fokus


| Render Lama                            | Perbaikan                         |
| ---------------------------------------- | ----------------------------------- |
| HDRI download                          | pakai`asset`                      |
| Output path safety                     | pakai`security`                   |
| Background render                      | pakai`job`                        |
| Camera transform overlap dengan object | render owns camera-specific setup |

---

## 5.6 Object FRD Harus Lebih Fokus


| Object Lama                    | Perbaikan                                                |
| -------------------------------- | ---------------------------------------------------------- |
| Place asset reference          | asset import dulu, object hanya place existing object    |
| Delete object vs scene cleanup | object owns single delete, scene owns bulk cleanup       |
| Transform camera               | boleh generic, tetapi camera workflow utama milik render |

---

## 5.7 Scene FRD Harus Lebih Fokus


| Scene Lama            | Perbaikan                                         |
| ----------------------- | --------------------------------------------------- |
| Cleanup object detail | scene owns policy, object owns deletion execution |
| Inspect object detail | scene memberi summary, object memberi detail      |

---

# 6. Dependency Rules

## 6.1 Dependency Direction

```text
cli
mcp
 ↓
dispatcher
 ↓
object / scene / render / asset
 ↓
gateway
 ↓
Blender
```

Platform services:

```text
config
security
job
diagnostics
telemetry
launcher
```

dipakai secara horizontal oleh feature yang membutuhkan.

---

## 6.2 Rules

### Rule 1

```text
Surface tidak boleh memanggil capability domain langsung jika ada dispatcher.
```

CLI dan MCP memakai dispatcher untuk action execution.

---

### Rule 2

```text
Domain feature tidak boleh membuka socket sendiri.
```

Semua komunikasi Blender melalui `gateway`.

---

### Rule 3

```text
Domain feature tidak boleh mengelola background task sendiri.
```

Semua background task melalui `job`.

---

### Rule 4

```text
Domain feature tidak boleh membaca config file sendiri.
```

Semua settings melalui `config`.

---

### Rule 5

```text
Feature tidak boleh implement path safety sendiri.
```

Semua path/archive/code validation melalui `security`.

---

### Rule 6

```text
Feature tidak boleh menghitung health/metrics sendiri untuk user.
```

Health dan metrics melalui `diagnostics`.

---

### Rule 7

```text
Telemetry hanya untuk anonymous product analytics.
```

Operational debugging bukan milik telemetry.

---

# 7. Unified Result Envelope

Semua FRD harus memakai result envelope yang sama.

```text
OperationResult
{
  success: bool
  message: str
  data: object | null
  error: {
    category: str
    code: str
    message: str
    details: object | null
  } | null
  warnings: list[str]
  tracking_id: str
  metadata: object
}
```

Dengan begini, setiap FRD tidak perlu mendefinisikan ulang format hasil.

---

# 8. Unified Error Categories

Error juga harus terpusat.

## Common Errors

```text
ValidationError
NotFoundError
TimeoutError
CapacityError
StateError
PermissionError
SecurityViolationError
ProviderError
ExecutionError
ConnectionError
ConfigurationError
UnsupportedError
```

## Feature-Specific Errors

Feature hanya boleh menambah error jika benar-benar domain-specific.

Contoh:

```text
ObjectNotFoundError
SceneStateError
ProtectionError
TransformLockError
AssetNotFoundError
AssetImportError
RenderOutputError
CameraSetupError
TaskNotFoundError
ProtocolVersionMismatchError
AuthenticationError
BlenderProcessNotRunningError
ChannelConflictError
```

Feature tidak boleh membuat error generik baru yang sudah ada di common.

---

# 9. Unified Tracking and Observability

Setiap operasi harus punya:

```text
tracking_id
operation_name
feature_owner
start_time
end_time
status
error_category
```

Owner:

```text
Tracking ID generation: dispatcher atau shared utility
Operational log: diagnostics
Product analytics: telemetry
Security audit: security + diagnostics
```

---

# 10. Contoh Flow Baru

## 10.1 User/AI Execute Action

```text
CLI/MCP
  → dispatcher.execute_action("create_primitive", params)
      → dispatcher validates action
      → dispatcher routes to object feature
          → object feature prepares Blender request
          → gateway sends request
          → gateway enforces queue if mutates_scene
          → Blender responds
      → dispatcher normalizes result
      → diagnostics records metrics/log
      → telemetry records anonymous event if opt-in
  ← CLI/MCP returns result
```

---

## 10.2 Render Background

```text
CLI/MCP
  → dispatcher.execute_action("render_scene", params, background=true)
      → dispatcher creates job via job feature
      → dispatcher submits render operation
          → render feature prepares render request
          → security validates output path
          → gateway sends request
      → job tracks progress
  ← dispatcher returns task_id

CLI/MCP
  → job.get_task_status(task_id)
```

---

## 10.3 Asset Download and HDRI Setup

```text
CLI/MCP
  → dispatcher.execute_action("configure_hdri", params)
      → render feature checks HDRI availability
      → render feature requests asset feature to download HDRI
          → asset feature downloads to cache
          → security validates path
          → job tracks if large
      → render feature applies HDRI lighting via gateway
  ← result
```

---

## 10.4 Scene Cleanup

```text
CLI/MCP
  → dispatcher.execute_action("cleanup_scene", params)
      → scene feature determines preservation policy
      → scene feature asks object feature to delete selected objects
          → object feature deletes via gateway
      → scene feature compiles cleanup report
  ← result
```

---

# 11. FRD Template Baru

Setiap FRD baru sebaiknya memakai struktur ini:

```markdown
# FRD — <Feature Name>

## Purpose
One paragraph explaining the single responsibility.

## Scope
What this feature owns.

## Out of Scope
What this feature must not handle.

## Depends On
- config
- security
- gateway
- job
- diagnostics

## Provides To
- dispatcher
- cli
- mcp

## Functional Requirements
FR-XXX-001 ...
FR-XXX-002 ...

## Error Categories
Reference common errors and feature-specific errors.

## Events
Domain events emitted.

## Configuration Keys
Keys consumed from config.

## QA Checklist
Test scenarios.
```

Dengan template ini, FRD tidak akan lagi mencampur aduk tanggung jawab.

---

# 12. Ringkasan Redesign

## Feature yang tetap

```text
config
job
telemetry
asset
object
scene
render
```

## Feature yang dipecah/diganti

```text
server → gateway + dispatcher + security + diagnostics + job
cli → launcher + cli surface + dispatcher + diagnostics
mcp → mcp surface + dispatcher + diagnostics + config
```

## Feature baru yang disarankan

```text
security
launcher
gateway
dispatcher
diagnostics
```

---

# 13. Rekomendasi Final

Saya merekomendasikan Anda menyetujui struktur baru ini:

```text
Platform:
- config
- security
- launcher
- gateway
- dispatcher
- job
- diagnostics
- telemetry

Domain:
- asset
- object
- scene
- render

Surface:
- cli
- mcp
```

Dengan struktur ini:

```text
Tidak ada feature yang mengurus settings, queue, task, security, logging, dan domain logic sekaligus.
```

Setiap FRD menjadi lebih kecil, jelas, testable, dan mudah diimplementasikan tanpa tabrakan antar tim/agent.

Jika Anda setuju, langkah berikutnya saya bisa langsung generate:

```text
modules/config/FRD.md
modules/security/FRD.md
modules/launcher/FRD.md
modules/gateway/FRD.md
modules/dispatcher/FRD.md
modules/job/FRD.md
modules/diagnostics/FRD.md
modules/telemetry/FRD.md
modules/asset/FRD.md
modules/object/FRD.md
modules/scene/FRD.md
modules/render/FRD.md
modules/cli/FRD.md
modules/mcp/FRD.md
```

masing-masing sudah dalam format FRD final yang siap dipakai developer.
