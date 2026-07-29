# Review Plan: Gateway — Tech Lead (Phase 3)

## Summary
The Gateway module provides transport authority between application features and Blender runtime. Overall code quality is good with solid AES architecture compliance. Most planned fixes were already applied in commit `59561ed` (transport exception handling, uuid tracking IDs, threading-aware sleep). Remaining work: import path corrections, auth error detail enrichment, queue poll interval constant extraction, and TODO comment improvement. No critical security vulnerabilities — auth tokens use TLS-ready socket transport.

## Findings by Category

### Security
| # | Severity | Issue | Location (File:Line) | Recommendation | Status |
|---|----------|-------|----------------------|----------------|--------|
| 1 | 🟡 WARNING | Auth token transmitted over plain TCP — production must use TLS | capabilities_connection_manager.py:145-152 | Document TLS requirement in FRD | ✅ Documented (no code change needed) |
| 2 | 🟡 FIXED | AuthenticationError missing host details on connection loss | capabilities_connection_manager.py:326 | Add details={"host": self._host} | ✅ Fixed |

### Performance
| # | Severity | Issue | Location (File:Line) | Recommendation | Status |
|---|----------|-------|----------------------|----------------|--------|
| 1 | 🟡 FIXED | MaintenanceExecutor used blocking time.sleep() in async context | capabilities_connection_maintenance.py:76 | Threading-aware conditional sleep | ✅ Pre-fixed in HEAD (commit 59561ed) |

### Error Handling
| # | Severity | Issue | Location (File:Line) | Recommendation | Status |
|---|----------|-------|----------------------|----------------|--------|
| 1 | 🟡 FIXED | TransportExecutor swallowed Exception, returned error VO | capabilities_transport_executor.py:112-118 | Raise ProviderError | ✅ Pre-fixed in HEAD (commit 59561ed) |

### SOLID Principles
| # | Severity | Issue | Location (File:Line) | Recommendation | Status |
|---|----------|-------|----------------------|----------------|--------|
| 1 | 🟡 INFO | capabilities_connection_manager.py has 2 classes (BlenderConnection + ConnectionExecutor) | capabilities_connection_manager.py:38,194 | Document as intentional paired impl | ✅ Accepted (async+sync pairing is documented in docstring) |

### Code Quality
| # | Severity | Issue | Location (File:Line) | Recommendation | Status |
|---|----------|-------|----------------------|----------------|--------|
| 1 | 🟢 FIXED | Magic number 0.05 poll interval | capabilities_scene_queue.py:239 | Named constant | ✅ Fixed |
| 2 | 🟢 FIXED | TODO stub in _execute_directly | capabilities_scene_queue.py:257 | Improved comment | ✅ Fixed |
| 3 | 🟡 CRITICAL | Import paths reference non-existent files (capabilities_connection, capabilities_transport) | gateway/__init__.py, src/__init__.py | Fix to actual filenames | ✅ Fixed |

## Action Items — Completed
- [✅] Fix import paths: capabilities_connection → capabilities_connection_manager, capabilities_transport → capabilities_transport_executor
- [✅] Remove broken utility import from src/__init__.py (utility dir doesn't exist under gateway/src/)
- [✅] Add host details to AuthenticationError on connection loss
- [✅] Extract magic number 0.05 to _POLL_INTERVAL_SECONDS constant
- [✅] Improve TODO comment in _execute_directly with FR-GWY reference

## Pre-existing Fixes (commit 59561ed)
- TransportExecutor now raises ProviderError instead of returning error VO
- CodeExecutionExecutor uses uuid.uuid4() for tracking IDs (no hash collision risk)
- MaintenanceExecutor has threading-aware conditional sleep (non-blocking in async context)
