# Review Plan: cli — Tech Lead (Phase 3)

## Summary

The CLI module has significant security exposure and architectural violations. Error messages leak raw internal details including file paths and tracebacks without masking. The surface layer contains domain logic (process lifecycle, socket communication) that belongs to owning features, violating both the FRD's "zero business logic" constraint and AES406 surface role rules. File naming violates AES102 strict suffix policy for surface layers (multiple files use non-compliant suffixes like `_commands`, `_manager`, `_registry`, `_socket_client`). Several files lack class definitions (AES303). Error handling uses bare `except Exception` with swallowed `pass` blocks and no error categorization per the FRD's defined error categories.

## Findings by Category

### Security
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | Raw error strings (including internal paths and exception details) returned directly in CLI output with no secret masking | `surface_cli_main.py:119`, `surface_cli_commands.py:53,81,99,139,185` | Wrap upstream errors through a masking function that redacts file paths, tokens, and internal details before returning to the user. Reference security policy redaction rules from the FRD. |
| 2 | 🔴 CRITICAL | `close()` sends arbitrary `execute_code` via socket with embedded Python (`bpy.ops.wm.save_mainfile()`) — no authorization check before executing code in Blender | `surface_cli_commands.py:210-211` | The `close` command must route through the dispatcher aggregate rather than sending raw Python to the socket. The dispatcher should validate and authorize the action before forwarding. |
| 3 | 🟡 WARNING | `--python-expr` arguments in `launch_blender()` embed `filepath` and `addon_path` directly into Python source strings — potential injection if paths contain malicious content | `surface_cli_blender_manager.py:86-107` | Sanitize paths before embedding in `--python-expr` strings. Use `shlex.quote()` or validate paths against the security module's allowlist before passing to Blender. |
| 4 | 🟡 WARNING | No secret/value masking on error output — FRD requires "Secrets/tokens/credentials/code/paths masked via security policy before display" but no masking is implemented | All error return paths in `surface_cli_commands.py` | Integrate with the security module's redaction policy. Mask paths, tokens, and credentials in all error messages before display. |

### Performance
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 5 | 🟡 WARNING | Double-checked locking singleton pattern (`Registry`) is unnecessary overhead for a CLI tool that runs once per invocation and exits — thread safety adds complexity with zero benefit | `surface_cli_registry.py:31-45` | Remove the singleton pattern and thread locking. The CLI is single-threaded; a simple module-level instance or per-call instantiation is sufficient. |
| 6 | 🟢 INFO | `Registry._load()` re-reads from disk every time `Registry()` is called (despite singleton), but new instances after `reset()` or in fresh invocations re-read — acceptable for single-use CLI | `surface_cli_registry.py:53-65` | No change required for single-use CLI pattern. |

### Error Handling
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 7 | 🔴 CRITICAL | Broad `except Exception as e` in `main()` returns `str(e)` directly — violates FRD requirement "unexpected failure → generic error with diagnostic ref, never raw stack" | `surface_cli_main.py:118-119` | Replace with generic error response: `{"success": False, "error": "Unexpected error", "ref": "<diagnostic-id>"}`. Log the full exception internally. |
| 8 | 🔴 CRITICAL | `except Exception: pass` in `close()` silently swallows the save operation failure — makes debugging impossible and leaves user unaware of data loss risk | `surface_cli_commands.py:212-213` | At minimum log the failure. Better: attempt save, and on failure inform the user that the file may not have been saved before killing the process. |
| 9 | 🟡 WARNING | No error categorization — FRD defines "Owned" (validation_error, configuration_error) and "Displayed but unowned" categories (not_found, capacity, timeout, security_violation, connection, state, task) but all errors are returned as flat strings | All error returns in `surface_cli_commands.py` | Implement error categorization matching FRD categories. Return structured errors with `category` field so the renderer can apply appropriate formatting and exit codes. |
| 10 | 🟡 WARNING | No differentiated exit codes — FRD requires "deterministic exit codes per outcome class" (success, surface_validation_failure, upstream_categorized_failure, unexpected_failure) but the code only returns 0/1 | `surface_cli_main.py:130` | Implement exit code mapping: 0=success, 2=validation_error, 3=upstream_categorized_failure, 4=unexpected_failure. |
| 11 | 🟢 INFO | JSON decode error in `main()` exposes the full exception message including malformed input | `surface_cli_main.py:87-89` | Return a generic validation error message and log the debug detail internally. |

### SOLID Principles
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 12 | 🔴 CRITICAL | CLI `commands.py` directly imports and calls concrete modules (`launch_blender`, `BlenderSocketClient`, `Registry`) instead of routing through a dispatcher aggregate — violates FRD "routes to owning feature aggregate" and the dependency rule that CLI depends on dispatcher, not directly on feature internals | `surface_cli_commands.py:11-13`, all command functions | Route all commands through the dispatcher aggregate. The dispatcher validates, routes, and returns standardized envelopes. CLI should never call `launch_blender()` or `BlenderSocketClient` directly. |
| 13 | 🟡 WARNING | Adding new CLI commands requires modifying `surface_cli_main.py` (adding new `elif` branch) — violates Open/Closed Principle. FRD states "Adding a capability never requires CLI changes beyond mapping a new command" | `surface_cli_main.py:82-116` | Implement a command registry pattern where commands register themselves. The main parser dispatches via the registry, so new commands only need to register — no core file changes. |
| 14 | 🟡 WARNING | No protocol/interface defining the command contract — commands module has no abstract base class or protocol | `surface_cli_commands.py` | Define a `Command` protocol that each command implements. Enables testing with mocks and allows dynamic command discovery/registration. |
| 15 | 🟡 WARNING | Domain logic (process lifecycle, socket communication) lives in the surface layer instead of being delegated to owning feature aggregates — violates AES406 and FRD's "zero business logic" constraint | `surface_cli_blender_manager.py` (entire file), `surface_cli_commands.py` (all command functions) | Move process lifecycle to launcher aggregate and socket communication to gateway aggregate. CLI surface should only parse, route, and render — delegating all operations to dispatcher→feature aggregates. |

### Code Quality
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 16 | 🔴 CRITICAL | AES102 suffix policy violation: `surface_cli_commands.py` uses suffix `_commands` (plural) but surface-allowed suffix is `_command` (singular) | `surface_cli_commands.py` | Rename to `surface_cli_command.py` (or rename to a non-surface role like `capabilities_cli_commands.py` if it owns behavior). |
| 17 | 🔴 CRITICAL | AES102 suffix + layer violation: `surface_cli_blender_manager.py` has prefix `surface_` but suffix `_manager` is not a valid surface role — this is a utility/manager, not a surface | `surface_cli_blender_manager.py` | Rename to `utility_cli_process_manager.py` or move to a utility layer file. The `surface_` prefix implies it's a surface role, which it is not. |
| 18 | 🔴 CRITICAL | AES102 suffix + layer violation: `surface_cli_registry.py` has prefix `surface_` but suffix `_registry` is not a valid surface role | `surface_cli_registry.py` | Rename to `utility_cli_registry.py` — registry is a utility concern, not a surface role. |
| 19 | 🔴 CRITICAL | AES102 suffix + layer violation: `surface_cli_socket_client.py` has prefix `surface_` but suffix `_socket_client` is not a valid surface role | `surface_cli_socket_client.py` | Rename to `utility_cli_socket_client.py` — socket client is a utility/transport, not a surface role. |
| 20 | 🔴 CRITICAL | AES102 suffix + layer violation: `surface_cli_main.py` has suffix `_main` which is not in the allowed surface suffix list | `surface_cli_main.py` | Rename to `root_cli_main_entry.py` — it's an entry point, matching the root layer convention. |
| 21 | 🟡 WARNING | AES303 missing class definition: `surface_cli_main.py` has no class — only a standalone `main()` function with module-level constants | `surface_cli_main.py` | Add a `CLIConfig` class or `CommandRouter` class to satisfy mandatory definition requirement. Alternatively, add docstring clarifying this is a barrel/entry exception if appropriate. |
| 22 | 🟡 WARNING | AES303 missing class definition: `surface_cli_commands.py` has no class — only standalone functions | `surface_cli_commands.py` | Add a `CommandBus` or `CLIController` class wrapping the command functions. |
| 23 | 🟡 WARNING | AES303 missing class definition: `surface_cli_blender_manager.py` has no class — only standalone functions | `surface_cli_blender_manager.py` | Add a `BlenderProcessManager` class encapsulating the process lifecycle functions. |
| 24 | 🟡 WARNING | AES305 duplication: The pattern `registry = Registry()` → `error = registry.assert_active(filepath)` → `if error: return ...` → `port = registry.get_port()` → `try/except with BlenderSocketClient` is identical across `run`, `screenshot`, `render`, `close`, and `status` — 5 repetitions of the same boilerplate | `surface_cli_commands.py:67-81, 107-139, 160-186, 196-225, 234-257` | Extract a `_resolve_active()` helper (or capability) that handles registry lookup and active-entity validation, reducing the 5-repetition pattern to a single call. |
| 25 | 🟢 INFO | `__init__.py` exports functions that don't follow AES naming — `main` is an entry point, not a surface command | `__init__.py` | Ensure `__init__.py` barrel exports align with the layer's public API contract. |

## Action Items
- [ ] 🔴 P0 Fix error masking: implement redaction of internal paths and exception details in all error outputs
- [ ] 🔴 P0 Fix raw exception leak: replace `str(e)` in `main()` with generic error + diagnostic ref
- [ ] 🔴 P0 Fix swallowed error: replace `except Exception: pass` in `close()` with proper error logging
- [ ] 🔴 P0 Implement error categorization matching FRD categories (validation_error, configuration_error, not_found, etc.)
- [ ] 🔴 P0 Implement differentiated exit codes per outcome class (success=0, validation=2, upstream=3, unexpected=4)
- [ ] 🔴 P0 Remove surface_ prefix from non-surface files (utility, registry, socket_client, manager)
- [ ] 🔴 P0 Fix AES102 suffix violations: rename files to use correct suffixes for their actual layer
- [ ] 🔴 P0 Move domain logic out of surface layer: CLI commands should route through dispatcher aggregate only
- [ ] 🟡 P1 Add command registry pattern to eliminate elif chain in main.py
- [ ] 🟡 P1 Define Command protocol for interface segregation
- [ ] 🟡 P1 Extract `_resolve_active()` helper to eliminate code duplication
- [ ] 🟡 P1 Add class definitions to module files to satisfy AES303
- [ ] 🟡 P1 Add error categorization to all return dicts
- [ ] 🟢 P2 Add secret masking integration with security module
- [ ] 🟢 P2 Sanitize `--python-expr` path arguments
- [ ] 🟢 P2 Remove unnecessary singleton/locking from Registry

## Fixed Code

### Fix 1: Error masking and generic error responses (`surface_cli_main.py`)

```python
    except Exception as e:
        # Never expose raw exception details to the user — log internally,
        # return a generic message with a diagnostic reference.
        import logging
        logging.exception("Unexpected CLI error")
        result = {"success": False, "error": "Unexpected error", "ref": "cli-500"}
```

### Fix 2: Error categorization and exit codes (`surface_cli_main.py`)

```python
ERROR_CATEGORIES = {
    "validation_error": 2,
    "configuration_error": 2,
    "not_found": 3,
    "capacity": 3,
    "timeout": 3,
    "security_violation": 3,
    "connection": 3,
    "state": 3,
    "task": 3,
}

def _exit_code(result: dict[str, Any]) -> int:
    if result.get("success"):
        return 0
    category = result.get("category", "unexpected")
    return ERROR_CATEGORIES.get(category, 4)
```

### Fix 3: Masked error returns (`surface_cli_commands.py`)

```python
def _mask_error(e: Exception) -> dict[str, Any]:
    """Mask internal details from error response."""
    return {"success": False, "error": "Operation failed", "category": "unexpected", "ref": "cli-500"}

# Replace every `except Exception as e: return {"success": False, "error": str(e)}` with:
except Exception:
    return _mask_error(e)
```

### Fix 4: Remove `except Exception: pass` in close() (`surface_cli_commands.py:212`)

```python
    # Try to save the file first
    save_error = None
    try:
        with BlenderSocketClient(port=port) as client:
            client.send_command("execute_code", {"code": "import bpy\nbpy.ops.wm.save_mainfile()"})
    except Exception as save_err:
        save_error = str(save_err)

    # Kill Blender process
    if pid and is_running(pid):
        kill_blender(pid)

    # Clear registry
    registry.clear()

    if save_error:
        return {
            "success": True,
            "message": f"Blender closed for '{os.path.basename(filepath)}' (save failed: {save_error})",
            "warnings": ["File may not have been saved before close"],
        }
```

### Fix 5: Rename files to correct layer suffixes (`AES102 compliance`)

| Old File | New File | Reason |
|---|---|---|
| `surface_cli_commands.py` | `capabilities_cli_command.py` | Contains command routing logic — capability role |
| `surface_cli_main.py` | `root_cli_main_entry.py` | Entry point — root role |
| `surface_cli_blender_manager.py` | `utility_cli_blender_process.py` | Process lifecycle utility — utility role |
| `surface_cli_registry.py` | `utility_cli_registry.py` | State management utility — utility role |
| `surface_cli_socket_client.py` | `utility_cli_socket_client.py` | Transport utility — utility role |

### Fix 6: Extract `_resolve_active()` helper to eliminate duplication (`capabilities_cli_command.py`)

```python
def _resolve_active(registry: Registry, filepath: str) -> tuple[str | None, int | None, str | None]:
    """Validate active Blender instance and return (error, port, pid)."""
    error = registry.assert_active(filepath)
    if error:
        return error, None, None
    return "", registry.get_port(), registry.get_pid()
```

### Fix 7: Add Command protocol for interface segregation (`capabilities_cli_command.py`)

```python
from typing import Protocol

class Command(Protocol):
    def execute(self, **kwargs: Any) -> dict[str, Any]: ...
```

### Fix 8: Add class wrappers for AES303 compliance

Each utility file gets a minimal class:
- `utility_cli_blender_process.py` → `BlenderProcessManager` class wrapping all functions
- `utility_cli_registry.py` → `Registry` already has a class — no change needed (already compliant)
- `utility_cli_socket_client.py` → `BlenderSocketClient` already has a class — no change needed
- `capabilities_cli_command.py` → `CLICommandBus` class wrapping command dispatch
- `root_cli_main_entry.py` → `CLIEntryPoint` class wrapping `main()`
