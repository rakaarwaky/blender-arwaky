# Plan: mcp — Revalidated Business Analyst Plan (2026-08-14)

## Summary

This is the revalidated successor to `todo-mcp-business-analyst-20260808.md`. Every finding from the 2026-08-08 plan was reviewed against the current branch, the module FRD, the AES architecture rules, and the current source/test inventory. The classification policy is conservative: a finding is not marked resolved merely because it is old; only explicit verification statements are resolved, while implementation gaps remain open and uncertainty remains needs-clarification.

## Revalidation Result

The plan contains 16 unique findings after deduplication: 2 open, 9 needs clarification, 5 resolved, and 0 obsolete. No finding was silently discarded. Paths from the old plan that no longer match current filenames are retained as needs-clarification rather than being treated as proof that the requirement disappeared.

## Findings

| # | Previous severity | Status | Finding | Location | Decision |
|---:|---|---|---|---|---|
| 1 | 🟢 INFO | **needs-clarification** | FR-MCP-001 "Schemas assembled from owning features: action tools from dispatcher catalog, settings from config, health from diagnostics, task tools from job, skill context from static docs" — verify all tool types covered | `surface_tool_registry.py` | The finding is an uncertainty or documentation gap; confirm behavior with a focused source/test check before implementation. |
| 2 | 🟢 INFO | **needs-clarification** | FR-MCP-001 "Description for AI consumption" — verify descriptions are AI-optimized, not just machine-stable | `surface_list_commands.py` | The finding is an uncertainty or documentation gap; confirm behavior with a focused source/test check before implementation. |
| 3 | 🟡 WARNING | **needs-clarification** | FR-MCP-002 "Tracking ID generated when client omits" — verify UUID generation is collision-resistant | `surface_execute_command.py` | The finding is an uncertainty or documentation gap; confirm behavior with a focused source/test check before implementation. |
| 4 | 🟢 INFO | **needs-clarification** | Tool call flow: client → MCP surface → dispatcher aggregate → domain features. No retries/reordering at surface (correct). | `surface_execute_command.py` | The finding is an uncertainty or documentation gap; confirm behavior with a focused source/test check before implementation. |
| 5 | 🟡 WARNING | **needs-clarification** | Protocol negotiation "rejects incompatible versions" — verify version check implementation | `surface_server_instance.py` | The finding is an uncertainty or documentation gap; confirm behavior with a focused source/test check before implementation. |
| 6 | 🟡 WARNING | **needs-clarification** | FR-MCP-003 "Every response structured per MCP spec" — verify response shape compliance with MCP spec | `surface_server_instance.py` | The finding is an uncertainty or documentation gap; confirm behavior with a focused source/test check before implementation. |
| 7 | 🟡 WARNING | **needs-clarification** | "Oversized strategy: summarize/substitute/truncate" — verify substitution strategy produces valid refs | `surface_execute_command.py` | The finding is an uncertainty or documentation gap; confirm behavior with a focused source/test check before implementation. |
| 8 | 🟢 INFO | **needs-clarification** | "Binary content as ref or bounded excerpt" — verify image handling in viewport capture | `surface_scene_tools.py` | The finding is an uncertainty or documentation gap; confirm behavior with a focused source/test check before implementation. |
| 9 | 🟡 WARNING | **open** | No test for protocol version mismatch rejection | `tests/` | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 10 | 🟡 WARNING | **open** | No test for oversized payload handling (summarize/substitute/truncate) | `tests/` | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 11 | 🟡 WARNING | **needs-clarification** | No test for tracking ID propagation to response | `tests/` | The risk is plausible but the finding is phrased as a verification request; inspect the current implementation before changing code. |
| 12 | 🟢 INFO | **resolved** | FR-MCP-001 → `surface_tool_registry.py`, `surface_list_commands.py` | `surface_tool_registry.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 13 | 🟢 INFO | **resolved** | FR-MCP-002 → `surface_execute_command.py` | `surface_execute_command.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 14 | 🟢 INFO | **resolved** | FR-MCP-003 → `surface_server_instance.py` | `surface_server_instance.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 15 | 🟢 INFO | **resolved** | Tool mapping → `surface_scene_tools.py`, `surface_asset_tools.py`, etc. | `surface_scene_tools.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 16 | 🟢 INFO | **resolved** | `read_skill_context` → `surface_read_skill.py` | `surface_read_skill.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |

## Validated Execution Backlog

Only findings marked **open** should be considered implementation candidates. Findings marked **needs-clarification** require a focused source/test check first. Findings marked **resolved** become regression acceptance criteria and must not be reimplemented without evidence of regression.

| Priority | Status | Action |
|---|---|---|
| 🟢 INFO | needs-clarification | Confirm all owning features are wired |
| 🟢 INFO | needs-clarification | Review descriptions for clarity |
| 🟡 WARNING | needs-clarification | Confirm tracking ID implementation |
| 🟢 INFO | needs-clarification | Flow confirmed correct |
| 🟡 WARNING | needs-clarification | Add version check test |
| 🟡 WARNING | needs-clarification | Audit against latest MCP spec |
| 🟡 WARNING | needs-clarification | Add test for oversized response handling |
| 🟢 INFO | needs-clarification | Confirm binary handling |
| 🟡 WARNING | open | Add unit test for incompatible protocol version |
| 🟡 WARNING | open | Add test for each oversized strategy |
| 🟡 WARNING | needs-clarification | Add test verifying tracking ID in all responses |

## Violations

No new violation is asserted by this revalidation without a current source/test proof. Suspected AES violations remain needs-clarification when the old path or architecture context changed.

## Traceability

The module FRD remains the authoritative requirement source. The previous plan is preserved as historical evidence, while this plan is the current status ledger.

## Execution Guardrails

Before implementing any row, confirm the exact current file path, the FRD acceptance criterion, and an executable test. Do not implement recommendations that only say “verify,” “consider,” or “document” until the verification result is recorded. Do not duplicate findings already present in another module plan.

## References

- [`FRD.md`](../../modules/mcp/FRD.md)
- [`ARCHITECTURE.md`](../../ARCHITECTURE.md)
- [`AES rules`](../../.agents/rules/RULES_AES.md)
- [`Previous plan`](./todo-mcp-business-analyst-20260808.md)
