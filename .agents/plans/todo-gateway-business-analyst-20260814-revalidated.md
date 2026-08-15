# Plan: gateway — Revalidated Business Analyst Plan (2026-08-14)

## Summary

This is the revalidated successor to `todo-gateway-business-analyst-20260808.md`. Every finding from the 2026-08-08 plan was reviewed against the current branch, the module FRD, the AES architecture rules, and the current source/test inventory. The classification policy is conservative: a finding is not marked resolved merely because it is old; only explicit verification statements are resolved, while implementation gaps remain open and uncertainty remains needs-clarification.

## Revalidation Result

The plan contains 18 unique findings after deduplication: 2 open, 11 needs clarification, 5 resolved, and 0 obsolete. No finding was silently discarded. Paths from the old plan that no longer match current filenames are retained as needs-clarification rather than being treated as proof that the requirement disappeared.

## Findings

| # | Previous severity | Status | Finding | Location | Decision |
|---:|---|---|---|---|---|
| 1 | 🟢 INFO | **needs-clarification** | FR-GWY-001: Handshake must exchange protocol version before any operation | `capabilities_connection_manager.py` | The finding is an uncertainty or documentation gap; confirm behavior with a focused source/test check before implementation. |
| 2 | 🟢 INFO | **needs-clarification** | FR-GWY-003: Payload size limit enforced through TransportProtocol | `capabilities_transport_executor.py` | The finding is an uncertainty or documentation gap; confirm behavior with a focused source/test check before implementation. |
| 3 | 🟡 WARNING | **needs-clarification** | FR-GWY-004: Scene-mutating operations serialized via queue — depth limit (50) and wait timeout (configurable) are implemented but not explicitly documented in code | `capabilities_scene_queue.py` | The finding is an uncertainty or documentation gap; confirm behavior with a focused source/test check before implementation. |
| 4 | 🟡 WARNING | **needs-clarification** | FR-GWY-005: Raw code execution validation is delegated to Security module — need to verify validation policy alignment | `capabilities_code_execution.py` | The finding is an uncertainty or documentation gap; confirm behavior with a focused source/test check before implementation. |
| 5 | 🟢 INFO | **needs-clarification** | Connection lifecycle follows state machine: disconnected → connecting → connected → reconnecting → failed → closed | `capabilities_connection_manager.py` | The wording does not provide enough evidence for automatic closure; retain it for targeted review. |
| 6 | 🟢 INFO | **needs-clarification** | Message framing uses length-prefix or delimiter — implementation appears correct | `capabilities_transport_executor.py` | The finding is an uncertainty or documentation gap; confirm behavior with a focused source/test check before implementation. |
| 7 | 🟡 WARNING | **needs-clarification** | Raw code execution (FR-GWY-005) creates background tasks but gateway never manages lifecycle — job feature handles lifecycle | `capabilities_code_execution.py` | The risk is plausible but the finding is phrased as a verification request; inspect the current implementation before changing code. |
| 8 | 🟡 WARNING | **needs-clarification** | Connection loss during long-running operation must not silently drop in-flight ops — currently handled per policy | `capabilities_connection_manager.py` | The wording does not provide enough evidence for automatic closure; retain it for targeted review. |
| 9 | 🟡 WARNING | **needs-clarification** | State transition events include redacted reason — need to ensure redaction is applied consistently | `capabilities_connection_manager.py` | The finding is an uncertainty or documentation gap; confirm behavior with a focused source/test check before implementation. |
| 10 | 🟡 WARNING | **needs-clarification** | Payload size limit enforced but error messages may expose size values | `capabilities_transport_executor.py` | The finding is an uncertainty or documentation gap; confirm behavior with a focused source/test check before implementation. |
| 11 | 🟡 WARNING | **open** | No test for connection loss during reconnect attempt | `tests/` | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 12 | 🟡 WARNING | **needs-clarification** | No test for payload limit enforcement with oversized requests | `tests/` | The risk is plausible but the finding is phrased as a verification request; inspect the current implementation before changing code. |
| 13 | 🟡 WARNING | **open** | No test for raw code execution timeout | `tests/` | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 14 | 🟢 INFO | **resolved** | FR-GWY-001 (Establish Connection) → `capabilities_connection_manager.py` | `capabilities_connection_manager.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 15 | 🟢 INFO | **resolved** | FR-GWY-002 (Maintain Connection) → `capabilities_connection_manager.py` | `capabilities_connection_manager.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 16 | 🟢 INFO | **resolved** | FR-GWY-003 (Transport Request/Response) → `capabilities_transport_executor.py` | `capabilities_transport_executor.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 17 | 🟢 INFO | **resolved** | FR-GWY-004 (Serialize Scene-Mutating Operations) → `capabilities_scene_queue.py` | `capabilities_scene_queue.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 18 | 🟢 INFO | **resolved** | FR-GWY-005 (Execute Raw Python Code) → `capabilities_code_execution.py` | `capabilities_code_execution.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |

## Validated Execution Backlog

Only findings marked **open** should be considered implementation candidates. Findings marked **needs-clarification** require a focused source/test check first. Findings marked **resolved** become regression acceptance criteria and must not be reimplemented without evidence of regression.

| Priority | Status | Action |
|---|---|---|
| 🟢 INFO | needs-clarification | Verify handshake sequence includes protocol version exchange |
| 🟢 INFO | needs-clarification | Confirm payload limit matches config key `payload_limit` |
| 🟡 WARNING | needs-clarification | Add comments documenting queue depth and wait timeout behavior |
| 🟡 WARNING | needs-clarification | Confirm security policy allows all necessary code constructs |
| 🟢 INFO | needs-clarification | Document state machine transitions in code comments |
| 🟢 INFO | needs-clarification | Confirm framing handles partial frames gracefully |
| 🟡 WARNING | needs-clarification | Confirm background task handoff is complete and no memory leaks |
| 🟡 WARNING | needs-clarification | Add comment explaining in-flight operation failure behavior |
| 🟡 WARNING | needs-clarification | Verify redaction applies to all connection loss reasons |
| 🟡 WARNING | needs-clarification | Consider generic payload error message |
| 🟡 WARNING | open | Add integration test for reconnect failure scenarios |
| 🟡 WARNING | needs-clarification | Add unit test verifying payload limit error |
| 🟡 WARNING | open | Add unit test for execution timeout |

## Violations

No new violation is asserted by this revalidation without a current source/test proof. Suspected AES violations remain needs-clarification when the old path or architecture context changed.

## Traceability

The module FRD remains the authoritative requirement source. The previous plan is preserved as historical evidence, while this plan is the current status ledger.

## Execution Guardrails

Before implementing any row, confirm the exact current file path, the FRD acceptance criterion, and an executable test. Do not implement recommendations that only say “verify,” “consider,” or “document” until the verification result is recorded. Do not duplicate findings already present in another module plan.

## References

- [`FRD.md`](../../modules/gateway/FRD.md)
- [`ARCHITECTURE.md`](../../ARCHITECTURE.md)
- [`AES rules`](../../.agents/rules/RULES_AES.md)
- [`Previous plan`](./todo-gateway-business-analyst-20260808.md)
