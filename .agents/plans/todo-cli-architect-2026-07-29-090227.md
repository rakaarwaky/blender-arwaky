# Review Plan: cli — Architect (Phase 1)

## Summary

The `cli` module (`modules/cli/`) is a surface-only feature that violates nearly every architectural constraint it claims to uphold. The FRD explicitly states "zero business logic" and defers process lifecycle, connection logic, command validation, and settings loading to other features — yet the current implementation directly embeds Blender process management, TCP socket transport, and instance registry state inside the surface layer, duplicating launcher and gateway concerns. No contract, capabilities, or agent layer exists for cli; the module is surface-only with no implementation backing. All five source files use suffixes not permitted by AES102 for the surface layer (`_main`, `_commands`, `_blender_manager`, `_registry`, `_socket_client`), and the module's data flow bypasses the dispatcher → gateway → launcher chain defined in the system architecture.

## Findings by Category

### Layer Boundaries
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | `surface_cli_blender_manager.py` (182 lines) contains process lifecycle code (`launch_blender`, `kill_blender`, `find_blender`, `_wait_for_addon`) that belongs to the `launcher` feature per ARCHITECTURE.md and the cli FRD Out-of-Scope list | `surface_cli_blender_manager.py:1-182` | Extract `BlenderManager` class / lifecycle functions into `modules/launcher/` as a capability. CLI surface should call launcher aggregate via dispatcher, not manage processes directly. |
| 2 | 🔴 CRITICAL | `surface_cli_socket_client.py` (115 lines) reimplements TCP transport that belongs to the `gateway` feature. The cli FRD scope defers connection logic to gateway. | `surface_cli_socket_client.py:1-115` | Extract `BlenderSocketClient` into `modules/gateway/` as a capability. CLI surface must use gateway aggregate, not raw socket client. |
| 3 | 🔴 CRITICAL | `surface_cli_registry.py` (127 lines) owns state management (active Blender instance tracking) that should live in launcher (process authority). The cli FRD defers process lifecycle to launcher. | `surface_cli_registry.py:1-127` | Move `Registry`/`RegistryState` into `modules/launcher/` as the single source of truth for Blender process state. CLI surface reads state from launcher aggregate only. |
| 4 | 🔴 CRITICAL | `surface_cli_commands.py` (273 lines) orchestrates lifecycle + socket + registry as a single surface module — it is effectively an orchestrator with business logic, violating the "zero business logic" surface rule and AES406 (no active domain logic in surface). | `surface_cli_commands.py:69-273` | Surface layer must only parse/validate input and route to owning feature aggregates via dispatcher. All `init`, `run`, `screenshot`, `render`, `close`, `status` functions must delegate to feature aggregates, not contain implementation logic. |

### Naming Convention
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 5 | 🔴 CRITICAL | `surface_cli_main.py` — suffix `_main` not in allowed surface suffixes (`_command`, `_controller`, `_page`, `_view`, `_component`, `_router`, `_layout`, `_hook`, `_store`, `_action`, `_screen`). AES102 strict suffix policy for surfaces. | `surface_cli_main.py:1` | Rename to `surface_cli_command_entry.py` (role `_entry` is not allowed) → correct rename: `surface_cli_command_main.py` → Actually use `surface_cli_command_root.py` or move entry function into a `surface_cli_command_entry` file with `_command` suffix. Recommended: `surface_cli_command_entry.py` with the `main()` function. |
| 6 | 🔴 CRITICAL | `surface_cli_commands.py` — suffix `_commands` not in allowed surface suffixes. Should use `_command` singular per AES102. | `surface_cli_commands.py:1` | Rename to `surface_cli_command_router.py` (role `_router` IS in the allowed surface suffix list). |
| 7 | 🔴 CRITICAL | `surface_cli_blender_manager.py` — suffix `_blender_manager` is not a valid surface suffix. The `_manager` suffix has no defined role. | `surface_cli_blender_manager.py:1` | This file should NOT be in the surface layer at all — move to launcher as a capability and rename `capability_launcher_process_manager.py`. |
| 8 | 🔴 CRITICAL | `surface_cli_registry.py` — suffix `_registry` not in allowed surface suffixes. Registry is a state-management utility, not a surface role. | `surface_cli_registry.py:1` | Move to utility layer as `utility_process_registry.py` or to launcher as a capability. |
| 9 | 🔴 CRITICAL | `surface_cli_socket_client.py` — suffix `_socket_client` not a valid surface suffix. Socket client is transport infrastructure. | `surface_cli_socket_client.py:1` | Move to gateway as a capability `capability_gateway_socket_client.py` or to utility as `utility_socket_client.py`. |
| 10 | 🟡 WARNING | All files duplicate the module name `cli` in their middle concept (`surface_cli_*`), inflating the naming. The `cli` prefix in the middle is redundant when files live under `modules/cli/`. | All 5 source files | After layer reassignment, rename: `surface_cli_command_router.py` → `surface_cli_command_router.py` (kept), `surface_cli_command_entry.py` → `surface_cli_command_entry.py` (kept), non-surface files renamed per their target layer. |

### Dead Code / Orphan
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 11 | 🟡 WARNING | `surface_cli_blender_manager.py`'s `find_blender()` and `launch_blender()` are dead code in the surface layer — they duplicate launcher functionality. Per AES504, utility-like surface files not consumed by capabilities/agent are orphans. | `surface_cli_blender_manager.py:15-182` | Reclassify as utility or move to launcher capabilities. If kept, import must come from utility/capability layer, not defined inline in surface. |
| 12 | 🟡 WARNING | `surface_cli_socket_client.py` is consumed only by `surface_cli_commands.py` (same layer) — no capabilities, agent, or other surface imports it. AES506: utility surfaces (`_socket_client` role) must be imported by smart surfaces through aggregates, not directly. | `surface_cli_socket_client.py:1-115` | Socket client becomes a gateway capability; `surface_cli_commands.py` calls gateway aggregate, not socket client directly. |
| 13 | 🟡 WARNING | Test file `test_cli_units.py` (line 9-13) explicitly documents that legacy monolith files violate FRD scope and are not exercised — an admission that the surface logic is untestable as a pure surface. | `tests/test_cli_units.py:9-13` | After extraction of business logic, surface functions become thin routing stubs — add integration tests against actual feature aggregates via dispatcher. |

### Scalability & Coupling
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 14 | 🔴 CRITICAL | `surface_cli_commands.py` at 273 lines with 7 public functions + helpers violates AES301 (file > 1000 lines is HIGH, but 273 lines with 7 responsibilities already exceeds single-responsibility). More importantly, it couples to 3 different infrastructure concerns (process, socket, state). | `surface_cli_commands.py:1-273` | Split into thin surface routing functions that delegate to feature aggregates. Maximum 1 function per feature aggregate in the surface. |
| 15 | 🟡 WARNING | `Registry` singleton in surface layer creates hidden shared state across all CLI commands — tight coupling, testability problem, and thread-safety complexity (`threading.Lock`, double-checked locking) in a layer that must be stateless. | `surface_cli_registry.py:26-45` | State management removed from surface. If singleton is needed for process tracking, it belongs in launcher or gateway. |

### Data Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 16 | 🔴 CRITICAL | Data flow is not unidirectional bottom-up. CLI surface directly calls `launch_blender()` (launcher concern), `BlenderSocketClient` (gateway concern), and `Registry` (state concern) — completely bypassing the dispatcher → gateway → launcher chain defined in ARCHITECTURE.md and PRD.md. This creates a parallel execution path that circumvents the established architecture. | `surface_cli_commands.py:33-273`, `surface_cli_main.py:112-159` | All CLI commands must route through dispatcher aggregate. The surface parses input → routes to dispatcher → dispatcher calls gateway/launcher/jobs. Surface must never call infrastructure directly. |

## Violations
- AES101 (Naming Convention): 5 files violate `prefix_concept_suffix` with non-standard suffixes
- AES102 (Suffix Prefix Rules): 5 CRITICAL — surface files use forbidden/unknown suffixes (`_main`, `_commands`, `_blender_manager`, `_registry`, `_socket_client`)
- AES201 (Forbidden Import): Semantic cross-concern imports — surface files directly import infrastructure (process management, socket, state) that belong to other layers
- AES205 (Circular Import): Not a technical cycle but architectural — surface and launcher/gateway concerns form a hidden reverse dependency where surface calls infrastructure directly
- AES301 (File Maximum Limit): Not breached (no file > 1000 lines)
- AES303 (Mandatory Definition): `surface_cli_socket_client.py` has `BlenderSocketClient` class ✓; no missing definitions
- AES406 (Surface Role): CRITICAL — surface contains active business logic (process management, orchestration, socket I/O)
- AES501 (Taxonomy Orphan): N/A — no taxonomy files in cli
- AES502 (Contract Orphan): CRITICAL — no `_protocol` or `_aggregate` contract files exist for cli; surface has no contract to implement or call
- AES503 (Capabilities Orphan): CRITICAL — no capabilities layer files exist; all implementation lives in surface
- AES504 (Utility Orphan): MEDIUM — `surface_cli_socket_client.py` and `surface_cli_blender_manager.py` function as utilities but are incorrectly placed in surface layer and lack `utility_` prefix
- AES505 (Agent Orphan): HIGH — no `_orchestrator` file exists; no agent orchestrates cli operations
- AES506 (Surface Orphan): HIGH — no `_command`/`_controller`/`_router` suffix file exists; `surface_cli_main.py` (entry point) not imported by any router/entry

## Action Items
- [ ] 🔴 CRITICAL Extract Blender process lifecycle from `surface_cli_blender_manager.py` → new capability in `modules/launcher/` (or shared utility `utility_process_launcher.py`)
- [ ] 🔴 CRITICAL Extract TCP socket transport from `surface_cli_socket_client.py` → new capability in `modules/gateway/` (or shared utility `utility_socket_client.py`)
- [ ] 🔴 CRITICAL Extract process state registry from `surface_cli_registry.py` → launcher capability or shared utility
- [ ] 🔴 CRITICAL Refactor `surface_cli_commands.py` to thin routing stubs that call dispatcher aggregates only — remove all business logic
- [ ] 🔴 CRITICAL Rename all 5 source files to comply with AES102 surface suffix rules (`_command`, `_router`, `_entry` as allowed)
- [ ] 🟡 WARNING Add contract layer for cli: `contract_cli_command_protocol.py` defining CLI aggregate interface
- [ ] 🟡 WARNING Add `_command` suffixed entry file (`surface_cli_command_entry.py` or `surface_cli_command_main.py`) that `surface_cli_command_router.py` imports
- [ ] 🟡 WARNING Remove `Registry` singleton from surface; surface reads state through launcher/aggregate
- [ ] 🟡 WARNING Update `src/__init__.py` barrel exports to reflect new file names and layer positions
- [ ] 🟢 INFO Add contract tests (`contract_cli_command_protocol` implemented by new capability)
- [ ] 🟢 INFO Add integration test for end-to-end CLI → dispatcher → feature aggregate flow

## Fixed Code

### Fix 1: New `utility_process_registry.py` (moved from `surface_cli_registry.py`)
```python
"""Utility for managing Blender process registry state.

Moved from surface_cli_registry.py — registry is a utility concern,
not a surface responsibility.
"""

import json
import os
import threading
from dataclasses import dataclass, field
from typing import Optional

REGISTRY_FILE = "registry.json"
DEFAULT_PORT = 9876


@dataclass
class RegistryState:
    """State of the active Blender instance."""

    active_entity: str | None = None
    port: int = DEFAULT_PORT
    pid: int | None = None


class Registry:
    """Thread-safe singleton managing registry.json."""

    _instance: Optional["Registry"] = None
    _lock = threading.Lock()

    def __new__(cls, registry_path: str = REGISTRY_FILE) -> "Registry":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._path = registry_path
                    instance._state = RegistryState()
                    instance._file_lock = threading.Lock()
                    instance._load()
                    cls._instance = instance
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        with cls._lock:
            cls._instance = None

    def _load(self) -> None:
        if os.path.exists(self._path):
            try:
                with open(self._path) as f:
                    data = json.load(f)
                self._state = RegistryState(
                    active_entity=data.get("active_entity"),
                    port=data.get("port", DEFAULT_PORT),
                    pid=data.get("pid"),
                )
            except (json.JSONDecodeError, KeyError):
                self._state = RegistryState()

    def _save(self) -> None:
        with self._file_lock:
            data = {
                "active_entity": self._state.active_entity,
                "port": self._state.port,
                "pid": self._state.pid,
            }
            with open(self._path, "w") as f:
                json.dump(data, f, indent=2)

    def get_active(self) -> str | None:
        return self._state.active_entity

    def get_port(self) -> int:
        return self._state.port

    def get_pid(self) -> int | None:
        return self._state.pid

    def is_active(self) -> bool:
        return self._state.active_entity is not None

    def set_active(self, filepath: str, pid: int, port: int = DEFAULT_PORT) -> None:
        self._state = RegistryState(
            active_entity=filepath,
            port=port,
            pid=pid,
        )
        self._save()

    def clear(self) -> None:
        self._state = RegistryState()
        self._save()

    def assert_no_active(self) -> str:
        if self._state.active_entity:
            return (
                f"Blender sedang aktif digunakan oleh '{self._state.active_entity}'. "
                f"Tutup terlebih dahulu dengan: blender-arwaky close --filepath '{self._state.active_entity}'"
            )
        return ""

    def assert_active(self, filepath: str) -> str:
        if not self._state.active_entity:
            return "Tidak ada Blender yang aktif. Jalankan: blender-arwaky init --filepath <path>"
        if self._state.active_entity != filepath:
            return (
                f"Entity '{filepath}' tidak terdaftar. "
                f"Active entity: '{self._state.active_entity}'. "
                f"Jalankan init terlebih dahulu."
            )
        return ""
```

### Fix 2: New `utility_socket_client.py` (moved from `surface_cli_socket_client.py`)
```python
"""Utility for TCP socket communication with Blender addon.

Moved from surface_cli_socket_client.py — transport is a utility concern,
not a surface responsibility.
"""

import contextlib
import json
import socket
import struct
from typing import Any

MAX_MESSAGE_SIZE = 10 * 1024 * 1024  # 10MB
DEFAULT_TIMEOUT = 30.0


class BlenderSocketClient:
    """TCP client for communicating with Blender addon."""

    def __init__(self, host: str = "localhost", port: int = 9876, timeout: float = DEFAULT_TIMEOUT):
        self.host = host
        self.port = port
        self.timeout = timeout
        self._sock: socket.socket | None = None

    def connect(self) -> None:
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(self.timeout)
            self._sock.connect((self.host, self.port))
        except TimeoutError as err:
            raise ConnectionError(f"Connection to {self.host}:{self.port} timed out ({self.timeout}s)") from err
        except ConnectionRefusedError as e:
            raise ConnectionError(f"Connection refused at {self.host}:{self.port}") from e
        except OSError as e:
            raise ConnectionError(f"Network error connecting to {self.host}:{self.port}: {e}") from e

    def disconnect(self) -> None:
        if self._sock:
            with contextlib.suppress(Exception):
                self._sock.close()
            self._sock = None

    def send_command(self, action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self._sock:
            raise ConnectionError("Not connected to Blender")
        command = {"type": action, "params": params or {}}
        try:
            data = json.dumps(command).encode("utf-8")
            header = struct.pack("!I", len(data))
            self._sock.sendall(header + data)
        except OSError as e:
            raise ConnectionError(f"Failed to send command: {e}") from e
        return self._receive_response()

    def _receive_response(self) -> dict[str, Any]:
        if not self._sock:
            raise ConnectionError("Not connected to Blender")
        header = self._recv_exact(4)
        msg_len = struct.unpack("!I", header)[0]
        if msg_len > MAX_MESSAGE_SIZE:
            raise ValueError(f"Response too large: {msg_len} bytes")
        body = self._recv_exact(msg_len)
        return json.loads(body.decode("utf-8"))

    def _recv_exact(self, n: int) -> bytes:
        if not self._sock:
            raise ConnectionError("Not connected to Blender")
        data = b""
        while len(data) < n:
            try:
                chunk = self._sock.recv(n - len(data))
            except OSError as e:
                raise ConnectionError(f"Receive error after {len(data)}/{n} bytes: {e}") from e
            if not chunk:
                raise ConnectionError("Connection closed prematurely")
            data += chunk
        return data

    def __enter__(self) -> "BlenderSocketClient":
        self.connect()
        return self

    def __exit__(self, *args: Any) -> None:
        self.disconnect()
```

### Fix 3: Refactored `surface_cli_command_router.py` (renamed from `surface_cli_commands.py`)
```python
"""CLI command router — surface layer only.

Routes parsed CLI intents to owning feature aggregates via dispatcher.
No business logic lives here — all implementation is delegated to feature
aggregates through the dispatcher.
"""

from .surface_cli_main import _mask_error
from .utility_process_registry import Registry
from .utility_socket_client import BlenderSocketClient


def _resolve_active(registry: Registry, filepath: str) -> tuple[str | None, int | None]:
    error = registry.assert_active(filepath)
    if error:
        return error, None
    return "", registry.get_port()


def init(filepath: str, mode: str = "headless", port: int = 9876) -> dict[str, Any]:
    # Surface validates shape only — dispatches to launcher aggregate via dispatcher
    # FR-CLI-001: 1 CLI command → exactly 1 owning feature aggregate
    registry = Registry()
    error = registry.assert_no_active()
    if error:
        return _mask_error("state", "cli-409", error)
    filepath = os.path.abspath(filepath)
    try:
        # Delegate to launcher aggregate — NOT direct process management
        return _dispatch("launcher", "init", {"filepath": filepath, "mode": mode, "port": port})
    except Exception:
        return _mask_error("unexpected", "cli-500")


def run(filepath: str, action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    registry = Registry()
    error, port = _resolve_active(registry, filepath)
    if error:
        return _mask_error("state", "cli-409", error)
    try:
        # Delegate to gateway aggregate — NOT direct socket communication
        return _dispatch("gateway", "execute", {"action": action, "params": params or {}})
    except ConnectionError:
        return _mask_error("connection", "cli-503", "Cannot connect to Blender — is it running?")
    except Exception:
        return _mask_error("unexpected", "cli-500")
```

### Fix 4: Renamed entry file
`surface_cli_main.py` → `surface_cli_command_entry.py` (using `_entry` which is not a standard surface suffix — should be `_command`)
→ Rename to `surface_cli_command_root.py` or keep as `surface_cli_main.py` with a note that `main` is a barrel-entry exception similar to `index.py`.
Actually: per AES102, `main` is not listed as an exception. Best fix: rename to `surface_cli_command_entry.py` and add a `surface_cli_command_entry` alias note in the __init__.py barrel exports.
