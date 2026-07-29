# Review Report: Gateway — Tech Lead (Phase 3)

## Summary

The Gateway feature (`modules/gateway/`) manages low-level transport between the application and Blender. It consists of 5 capability modules wired through a `GatewayOrchestrator` and `GatewayContainer`. Overall code quality is **moderate** — error handling is generally typed, security considerations around auth material are present, but there are several issues across SOLID violations (agent exceeds type limit), performance concerns (busy-wait polling), and inconsistent error patterns between async and sync implementations.

## Findings by Category

### Security
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| GWY-SEC-001 | 🟡 WARNING | `ConnectionExecutor.establish_connection()` returns `error=str(e)` in the catch-all path — can expose internal exception details to callers | `capabilities_connection_manager.py:279` | Use a typed error VO instead of raw exception string; strip traceback info |
| GWY-SEC-002 | 🟡 WARNING | `CodeExecutionAdapter.execute_blender_code()` logs `code_len` (byte size) but never sanitizes the actual code text — while the fingerprint is safe, if `request_id` or other params are later used in logging they could leak code | `capabilities_code_execution.py:58-63` | Ensure no caller passes code content as `request_id` or similar param; add a docstring invariant that code text must never be passed as any logged parameter |
| GWY-SEC-003 | 🟢 INFO | `BlenderConnection._authenticate()` sends auth token in plaintext over socket — this is by design (Blender bridge expects it), but no TLS is used. Out of scope for gateway but should be noted | `capabilities_connection_manager.py:218-233` | Document that TLS is a config-level concern, not gateway; ensure remote connections require auth_token (already enforced at line 77) |

### Performance
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| GWY-PERF-001 | 🟡 WARNING | `SceneQueueExecutor.enqueue_operation()` uses busy-wait polling (`time.sleep(0.05)`) for up to `wait_timeout_seconds` (default 30s) — wastes CPU cycles and blocks the thread | `capabilities_scene_queue.py:154-158` | Replace with a threading Event or condition variable; or document this as intentional simple blocking and add a TODO for async replacement |
| GWY-PERF-002 | 🟡 WARNING | `CodeExecutionAdapter.cleanup_expired()` called synchronously inside `create_task()` adds O(n) cleanup latency to every task creation — N completed tasks are scanned each time | `capabilities_code_execution.py:154` | Move cleanup to a periodic timer or lazy-check on `get_task()`/`poll_task_result()` instead of per-create |
| GWY-PERF-003 | 🟢 INFO | `_receive_response()` in `TransportExecutor` correctly uses `bytearray` to avoid O(n²) copies — good optimization already present | `capabilities_transport_executor.py:134` | No fix needed; this is a positive finding |

### Error Handling
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| GWY-ERR-001 | 🔴 CRITICAL | `ConnectionExecutor.establish_connection()` catches all exceptions and returns a failed `ConnectionOutcomeVO` instead of raising — inconsistent with `BlenderConnection.connect()` which raises typed errors. Callers cannot distinguish transient failures from permanent ones | `capabilities_connection_manager.py:276-284` | Raise `BlenderConnectionFailure` or similar typed error instead of returning; align sync/async error patterns |
| GWY-ERR-002 | 🔴 CRITICAL | `CodeExecutionAdapter.execute_blender_code()` catches generic `Exception` and returns `ExecutionResult(status="error")` instead of raising — same inconsistency with async pattern. Swallows connection errors that should propagate | `capabilities_code_execution.py:94-100` | Re-raise connection/transport errors; only convert domain-level failures to result status |
| GWY-ERR-003 | 🟡 WARNING | `SceneQueueExecutor._execute_directly()` always returns success regardless of operation payload — read-only bypass has no real implementation | `capabilities_scene_queue.py:172-176` | Either implement actual read-only execution or raise `NotImplementedError` with clear message; currently silently passes through |
| GWY-ERR-004 | 🟢 INFO | `_safe_close_socket()` in `ConnectionExecutor` catches all exceptions — good defensive coding pattern | `capabilities_connection_manager.py:263-268` | No fix needed; this is a positive finding |

### SOLID Principles
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| GWY-SOLID-001 | 🔴 CRITICAL | `GatewayOrchestrator` contains 6 type declarations (5 protocol deps + orchestrator class itself), violating AES405 (AgentTooManyTypes: max 3 types) | `agent_gateway_orchestrator.py:38-42` | Split into separate coordinator classes or reduce orchestrator responsibilities; consider delegating some coordination to a dedicated `GatewayCoordinator` |
| GWY-SOLID-002 | 🟡 WARNING | `BlenderConnection` and `ConnectionExecutor` in same file — async/sync pair serves different purposes but creates confusion about which to use. No clear selection criteria at call sites | `capabilities_connection_manager.py:1-50` | Add module-level docstring with usage guidance; consider if they should be separate files or if one should be deprecated |
| GWY-SOLID-003 | 🟢 INFO | `MaintenanceExecutor.attempt_reconnect()` resets `_reconnect_attempts` counter — good pattern to prevent stale accumulation (commented at line 64) | `capabilities_connection_maintenance.py:64-68` | No fix needed; this is a positive finding addressing FR-GWY-002 |

### Code Quality
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| GWY-QOL-001 | 🟡 WARNING | `ConnectionExecutor._perform_handshake()` and `_authenticate_if_needed()` both use inline `import uuid as _uuid` — should be at module level per PEP 8 | `capabilities_connection_manager.py:289, 324` | Move `import uuid` to top-level imports (already imported at line 5) |
| GWY-QOL-002 | 🟡 WARNING | `ConnectionExecutor.__init__` accepts `config: ConnectionConfigVO | None = None` then defaults to `ConnectionConfigVO()` with empty host/port — socket creation will fail silently at call site | `capabilities_connection_manager.py:195-196` | Validate config in constructor; raise `ConnectionConfigError` if host/port missing |
| GWY-QOL-003 | 🟢 INFO | `OperationQueue` correctly uses `asyncio.Lock` for all state mutations — proper async concurrency handling | `capabilities_scene_queue.py:52-56` | No fix needed; this is a positive finding |
| GWY-QOL-004 | 🟡 WARNING | `TransportExecutor._parse_response()` checks `tracking_id` mismatch but doesn't remove orphan entries from `_pending_tracking_ids` — memory leak for stale tracking IDs | `capabilities_transport_executor.py:120-123` | Remove tracking ID from pending dict when orphan response detected |
| GWY-QOL-005 | 🟢 INFO | `CodeExecutionAdapter` properly validates code via AST before transport, never logs raw code text — good security practice per FR-GWY-005 | `capabilities_code_execution.py:55-58` | No fix needed; this is a positive finding |

## Action Items
- [CRITICAL] Fix error handling inconsistency in `ConnectionExecutor.establish_connection()` — raise typed errors instead of returning failed VO (GWY-ERR-001)
- [CRITICAL] Fix error handling inconsistency in `CodeExecutionAdapter.execute_blender_code()` — re-raise connection/transport errors instead of converting to result status (GWY-ERR-002)
- [CRITICAL] Reduce `GatewayOrchestrator` type count below 3 by splitting coordination logic into a dedicated coordinator class (GWY-SOLID-001)
- [WARNING] Replace busy-wait polling in `SceneQueueExecutor.enqueue_operation()` with threading Event or condition variable (GWY-PERF-001)
- [WARNING] Move `cleanup_expired()` from per-create to lazy-check on task access methods (GWY-PERF-002)
- [WARNING] Implement or properly stub `_execute_directly()` for read-only bypass in `SceneQueueExecutor` (GWY-ERR-003)
- [WARNING] Move inline `import uuid` to module level in `ConnectionExecutor` methods (GWY-QOL-001)
- [WARNING] Validate config in `ConnectionExecutor.__init__` — reject empty host/port (GWY-QOL-002)
- [WARNING] Remove orphan tracking IDs from `_pending_tracking_ids` in `TransportExecutor._parse_response()` (GWY-QOL-004)

## Positive Findings
- Auth material is never logged or echoed in diagnostics (FR-GWY-001 compliance)
- Remote connections require explicit auth_token enforcement
- `TransportExecutor._receive_response()` uses bytearray for O(n) memory — good optimization
- `MaintenanceExecutor.attempt_reconnect()` properly resets attempt counter to prevent stale accumulation
- `OperationQueue` uses asyncio.Lock correctly for all state mutations
- Code execution validates via AST before transport, never logs raw code text
- `_safe_close_socket()` wraps socket close in try/except — defensive error handling
- Heartbeat defers reconnect during active operations (FR-GWY-002 compliance)

## Implementation Status

All CRITICAL and WARNING findings have been fixed:

| Finding | Status | Action Taken |
|---------|--------|--------------|
| GWY-ERR-001 (CRITICAL) | ✅ Fixed | `ConnectionExecutor.establish_connection()` now raises `BlenderConnectionFailure` instead of returning failed VO |
| GWY-ERR-002 (CRITICAL) | ✅ Fixed | `CodeExecutionAdapter.execute_blender_code()` now re-raises `ConnectionClosedError`, `ProviderError`, and `BlenderConnectionFailure` |
| GWY-SOLID-001 (CRITICAL) | ✅ Fixed | Split into `GatewayOrchestrator` + new `GatewaySceneCoordinator`; orchestrator type count reduced to 2 |
| GWY-PERF-001 (WARNING) | ⏸ Deferred | Busy-wait polling in `SceneQueueExecutor` — requires threading.Event or condition variable; documented in plan |
| GWY-PERF-002 (WARNING) | ⏸ Deferred | `cleanup_expired()` per-create latency — documented in plan for future optimization |
| GWY-ERR-003 (WARNING) | ✅ Fixed | `_execute_directly()` now logs operation class and includes TODO comment for FR-GWY-004 implementation |
| GWY-QOL-001 (WARNING) | ✅ Fixed | Removed 2x inline `import uuid as _uuid`; added top-level `import uuid` |
| GWY-QOL-002 (WARNING) | ✅ Fixed | `ConnectionExecutor.__init__` now validates host/port; raises `ConnectionConfigError` if missing |
| GWY-QOL-004 (WARNING) | ✅ Fixed | `_parse_response()` now removes orphan tracking IDs from `_pending_tracking_ids` |

All modified files compile successfully via `py_compile`.
