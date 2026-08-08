# Plan: mcp — Business Analyst

## Summary
The mcp module implements the MCP (Model Context Protocol) surface layer — machine-facing counterpart of CLI. Routes tool calls to the same aggregates as CLI. AES structure: 1 root container, 9 surface modules. FRD-to-code traceability is strong. Surface-only layer (zero business logic) confirmed. No violations found for layer separation.

## Findings

### Requirements Clarity
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | FR-MCP-001 "Schemas assembled from owning features: action tools from dispatcher catalog, settings from config, health from diagnostics, task tools from job, skill context from static docs" — verify all tool types covered | `surface_tool_registry.py` | Confirm all owning features are wired |
| 2 | 🟢 INFO | FR-MCP-001 "Description for AI consumption" — verify descriptions are AI-optimized, not just machine-stable | `surface_list_commands.py` | Review descriptions for clarity |
| 3 | 🟡 WARNING | FR-MCP-002 "Tracking ID generated when client omits" — verify UUID generation is collision-resistant | `surface_execute_command.py` | Confirm tracking ID implementation |

### Business Flow
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | Tool call flow: client → MCP surface → dispatcher aggregate → domain features. No retries/reordering at surface (correct). | `surface_execute_command.py` | Flow confirmed correct |
| 2 | 🟡 WARNING | Protocol negotiation "rejects incompatible versions" — verify version check implementation | `surface_server_instance.py` | Add version check test |

### Logic Implementation
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟡 WARNING | FR-MCP-003 "Every response structured per MCP spec" — verify response shape compliance with MCP spec | `surface_server_instance.py` | Audit against latest MCP spec |
| 2 | 🟡 WARNING | "Oversized strategy: summarize/substitute/truncate" — verify substitution strategy produces valid refs | `surface_execute_command.py` | Add test for oversized response handling |
| 3 | 🟢 INFO | "Binary content as ref or bounded excerpt" — verify image handling in viewport capture | `surface_scene_tools.py` | Confirm binary handling |

### Testability & Acceptance
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟡 WARNING | No test for protocol version mismatch rejection | `tests/` | Add unit test for incompatible protocol version |
| 2 | 🟡 WARNING | No test for oversized payload handling (summarize/substitute/truncate) | `tests/` | Add test for each oversized strategy |
| 3 | 🟡 WARNING | No test for tracking ID propagation to response | `tests/` | Add test verifying tracking ID in all responses |

### Traceability (FRD→Code)
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | FR-MCP-001 → `surface_tool_registry.py`, `surface_list_commands.py` | `surface_tool_registry.py` | Traceability verified |
| 2 | 🟢 INFO | FR-MCP-002 → `surface_execute_command.py` | `surface_execute_command.py` | Traceability verified |
| 3 | 🟢 INFO | FR-MCP-003 → `surface_server_instance.py` | `surface_server_instance.py` | Traceability verified |
| 4 | 🟢 INFO | Tool mapping → `surface_scene_tools.py`, `surface_asset_tools.py`, etc. | `surface_scene_tools.py` | Traceability verified |
| 5 | 🟢 INFO | `read_skill_context` → `surface_read_skill.py` | `surface_read_skill.py` | Traceability verified |

## Violations
None found. Surface layer correctly contains no business logic.

## Action Items
- [ ] 🟡 WARNING Add test for protocol version mismatch rejection
- [ ] 🟡 WARNING Add test for oversized payload handling strategies
- [ ] 🟡 WARNING Add test for tracking ID propagation
- [ ] 🟡 WARNING Audit response shape against latest MCP spec
- [ ] 🟢 INFO Confirm tracking ID collision resistance

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