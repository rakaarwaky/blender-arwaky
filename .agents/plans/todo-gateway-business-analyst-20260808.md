# Plan: gateway — Business Analyst

## Summary
The gateway module implements Blender transport authority: connection lifecycle, handshake, protocol compatibility, reconnection, message framing, payload limits, scene operation scheduling, raw command and code transport. AES structure: 1 agent orchestrator, 6 capabilities, 1 root container. FRD-to-code traceability is strong. No violations found.

## Findings

### Requirements Clarity
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | FR-GWY-001: Handshake must exchange protocol version before any operation | `capabilities_connection_manager.py` | Verify handshake sequence includes protocol version exchange |
| 2 | 🟢 INFO | FR-GWY-003: Payload size limit enforced through TransportProtocol | `capabilities_transport_executor.py` | Confirm payload limit matches config key `payload_limit` |
| 3 | 🟡 WARNING | FR-GWY-004: Scene-mutating operations serialized via queue — depth limit (50) and wait timeout (configurable) are implemented but not explicitly documented in code | `capabilities_scene_queue.py` | Add comments documenting queue depth and wait timeout behavior |
| 5 | 🟡 WARNING | FR-GWY-005: Raw code execution validation is delegated to Security module — need to verify validation policy alignment | `capabilities_code_execution.py` | Confirm security policy allows all necessary code constructs |

### Business Flow
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | Connection lifecycle follows state machine: disconnected → connecting → connected → reconnecting → failed → closed | `capabilities_connection_manager.py` | Document state machine transitions in code comments |
| 2 | 🟢 INFO | Message framing uses length-prefix or delimiter — implementation appears correct | `capabilities_transport_executor.py` | Confirm framing handles partial frames gracefully |
| 3 | 🟡 WARNING | Raw code execution (FR-GWY-005) creates background tasks but gateway never manages lifecycle — job feature handles lifecycle | `capabilities_code_execution.py` | Confirm background task handoff is complete and no memory leaks |

### Logic Implementation
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟡 WARNING | Connection loss during long-running operation must not silently drop in-flight ops — currently handled per policy | `capabilities_connection_manager.py` | Add comment explaining in-flight operation failure behavior |
| 2 | 🟡 WARNING | State transition events include redacted reason — need to ensure redaction is applied consistently | `capabilities_connection_manager.py` | Verify redaction applies to all connection loss reasons |
| 3 | 🟡 WARNING | Payload size limit enforced but error messages may expose size values | `capabilities_transport_executor.py` | Consider generic payload error message |

### Testability & Acceptance
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟡 WARNING | No test for connection loss during reconnect attempt | `tests/` | Add integration test for reconnect failure scenarios |
| 2 | 🟡 WARNING | No test for payload limit enforcement with oversized requests | `tests/` | Add unit test verifying payload limit error |
| 3 | 🟡 WARNING | No test for raw code execution timeout | `tests/` | Add unit test for execution timeout |

### Traceability (FRD→Code)
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | FR-GWY-001 (Establish Connection) → `capabilities_connection_manager.py` | `capabilities_connection_manager.py` | Traceability verified |
| 2 | 🟢 INFO | FR-GWY-002 (Maintain Connection) → `capabilities_connection_manager.py` | `capabilities_connection_manager.py` | Traceability verified |
| 3 | 🟢 INFO | FR-GWY-003 (Transport Request/Response) → `capabilities_transport_executor.py` | `capabilities_transport_executor.py` | Traceability verified |
| 4 | 🟢 INFO | FR-GWY-004 (Serialize Scene-Mutating Operations) → `capabilities_scene_queue.py` | `capabilities_scene_queue.py` | Traceability verified |
| 5 | 🟢 INFO | FR-GWY-005 (Execute Raw Python Code) → `capabilities_code_execution.py` | `capabilities_code_execution.py` | Traceability verified |

## Violations
None found. AES layer separation maintained: gateway handles transport, security, and connection concerns without business logic.

## Action Items
- [ ] 🟡 WARNING Verify payload limit enforcement against config key `payload_limit`
- [ ] 🟡 WARNING Document queue depth and wait timeout behavior
- [ ] 🟡 WARNING Add audit logging for security validation disabled
- [ ] 🟡 WARNING Add test for payload limit enforcement
- [ ] 🟡 WARNING Add unit test for raw code execution timeout

## Fixed Code
None required.

## Severity
- 🔴 CRITICAL: Missing core requirement, wrong logic, data integrity risk
- 🟡 WARNING: Ambiguous requirement, missing edge case, incomplete criteria
- 🟢 INFO: Suggestion or optimization, deferrable

## Checklist
- [x] Prerequisites read
- [x] Feature + modules identified
- [x] FRD mapped to code files
- [x] All 5 dimensions analyzed
- [x] Severity categorized
- [x] Deduped vs existing plans + active PRs
- [x] Plan written (NEW issues + fixed code)
- [x] Saved to correct path