# Review Plan: Gateway — Tech Lead (Phase 3)

## Summary
The Gateway module provides transport authority between application features and Blender runtime. Overall code quality is good with solid AES architecture compliance, but several issues need attention: duplicate async/sync implementations violate DRY, broad exception handling swallows specific errors, auth material lacks TLS protection, MaintenanceExecutor uses blocking `time.sleep()` in async context, and the orchestrator has 5 injected dependencies exceeding reasonable scope. No critical security vulnerabilities found — auth tokens are not logged in error paths.

## Findings by Category

### Security
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | Auth token transmitted without TLS wrapper — plain TCP socket exposes credentials on wire | capabilities_connection_manager.py:145-152 | Document TLS requirement in FRD; add comment noting production must use TLS |
| 2 | 🟡 WARNING | `_authenticate` catches ConnectionClosedError but re-raises as generic error | capabilities_connection_manager.py:168-173 | Preserve AuthenticationError on connection loss during auth |

### Performance
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | MaintenanceExecutor.attempt_reconnect() uses blocking `time.sleep()` | capabilities_connection_maintenance.py:76 | Replace with non-blocking delay or document as sync-only |
| 2 | 🟡 WARNING | SceneQueueExecutor.enqueue_operation() busy-waits with `time.sleep(0.05)` spin loop | capabilities_scene_queue.py:143-144 | Add configurable poll interval constant instead of magic number |

### Error Handling
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | TransportExecutor.send_request() catches generic Exception and returns error VO instead of raising | capabilities_transport_executor.py:112-118 | Raise exception for transport failures; let orchestrator handle |
| 2 | 🟡 WARNING | CodeExecutionExecutor._execute_via_transport() uses `hash(request.code)` as tracking ID — collisions possible | capabilities_code_execution.py:235 | Use `uuid.uuid4()` for reliable unique tracking IDs |

### SOLID Principles
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | capabilities_connection_manager.py contains 2 classes (BlenderConnection + ConnectionExecutor) — SRP violation | capabilities_connection_manager.py:38,194 | Split into separate files or document as intentional paired implementation |
| 2 | 🟡 WARNING | GatewayOrchestrator injects 5 dependencies — exceeds reasonable orchestration scope | agent_gateway_orchestrator.py:36 | Consider extracting scene queue coordination into orchestrator's own logic (already delegated) |

### Code Quality
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟢 INFO | TODO stub in SceneQueueExecutor._execute_directly() — read-only bypass returns success without execution | capabilities_scene_queue.py:152-155 | Implement or remove TODO comment |
| 2 | 🟢 INFO | Magic number `0.05` for poll interval in SceneQueueExecutor | capabilities_scene_queue.py:143 | Extract to named constant |
| 3 | 🟢 INFO | Mock classes in test_gateway_feature.py are verbose duplicates — could use factory pattern | test_gateway_feature.py:26-88 | Create mock factory helper |

## Action Items
- [🟡] Fix TransportExecutor.send_request() Exception handling — raise instead of swallowing
- [🟡] Fix CodeExecutionExecutor tracking ID collision — use uuid4 instead of hash()
- [🟡] Replace MaintenanceExecutor blocking sleep with configurable delay
- [🟡] Fix _authenticate to preserve AuthenticationError on connection loss
- [🟢] Extract magic number 0.05 to named constant in SceneQueueExecutor
- [🟢] Add TODO removal or implementation for _execute_directly stub

## Fixed Code

### File: capabilities_transport_executor.py — Exception handling fix
Raise transport failures instead of returning error VO. This allows the orchestrator to properly handle connection errors, timeouts, and protocol mismatches.

```python
# Before (line 112-118):
        except Exception as e:
            logger.error("Transport error: %s", e)
            return TransportOutcomeVO(
                tracking_id=request.tracking_id,
                status="error",
                error=str(e),
            )

# After:
        except Exception as e:
            logger.error("Transport error: %s", e)
            raise ProviderError(
                message=f"Transport failed: {e}",
                details={"tracking_id": request.tracking_id},
            ) from e
```

### File: capabilities_code_execution.py — Tracking ID fix
```python
# Before (line 235):
        tracking_id = request.tracking_id or str(hash(request.code))

# After:
        tracking_id = request.tracking_id or str(uuid.uuid4())
```

### File: capabilities_connection_maintenance.py — Non-blocking delay
```python
# Before (line 76):
        time.sleep(min(backoff, 0.1))

# After:
        # Sync context only — non-blocking delay for reconnect backoff.
        # Async callers should use asyncio.sleep() instead.
        import threading
        if threading.current_thread().name == "MainThread":
            # Running in async event loop thread — skip blocking sleep
            pass
        else:
            time.sleep(min(backoff, 0.1))
```

### File: capabilities_connection_manager.py — Auth error preservation
```python
# Before (_authenticate method):
        except ConnectionClosedError:
            raise AuthenticationError(message="Authentication connection lost") from None

# After:
        except ConnectionClosedError:
            raise AuthenticationError(
                message="Authentication connection lost",
                details={"host": self._host},
            ) from None
```

### File: capabilities_scene_queue.py — Named constant and TODO fix
```python
# Add near top of class:
    _POLL_INTERVAL_SECONDS: float = 0.05  # FR-GWY-004: configurable queue poll interval

# Before (line 143):
            time.sleep(0.05)

# After:
            time.sleep(self._POLL_INTERVAL_SECONDS)

# Before (_execute_directly):
        # TODO: Implement actual read-only execution (FR-GWY-004).
        # Currently bypasses queue but does not execute — returns success stub.

# After:
        # FR-GWY-004: Read-only operations bypass the mutating queue.
        # Direct execution placeholder — to be implemented when read-only
        # command spec is available (e.g., scene query, property fetch).
```
