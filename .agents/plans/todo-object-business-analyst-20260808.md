# Plan: object — Business Analyst

## Summary
The object module implements single-object technical operations per FR-OBJ-001..007. AES structure: 1 agent orchestrator, 7 capabilities, 1 root container. FRD-to-code traceability is strong. Found 2 AES violations requiring fixes.

## Findings

### Requirements Clarity
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | �� 🟢 INFO | FR-OBJ-001 "Reference resolution deterministic: unique ID → exact name → qualified path/collection" — verify implementation | `capabilities_place_asset_executor.py` | Confirm reference resolution order |
| 2 | �� 🟢 INFO | FR-OBJ-002 "Transform values must be finite 3-vectors" — validation visible | `capabilities_set_transform_executor.py` | Validation confirmed |

### Business Flow
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | �� 🟢 INFO | Create → place → transform → material → modifier → delete flow works via separate capabilities | `agent_object_orchestrator.py` | Flow verified |
| 2 | �� 🟢 INFO | Destructive actions require confirmation (apply modifier, delete protected) | `capabilities_apply_modifier_executor.py`, `capabilities_delete_object_executor.py` | Confirmation enforced |

### Logic Implementation
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | �� 🔴 CRITICAL | **AES401 Violation**: `taxonomy_object_vo.py` uses `_vo` suffix but includes non-constant declarations (dataclasses with fields) | `modules/object/src/taxonomy_object_vo.py` | Replace non-constant fields with constants or remove `_vo` suffix |
| 2 | �� 🔴 CRITICAL | **AES505 Violation**: `agent_object_orchestrator.py` uses `_orchestrator` suffix without being wired in any container | `modules/object/src/agent_object_orchestrator.py` | Ensure orchestrator is explicitly initialized and used via container |

### Testability & Acceptance
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | �� 🟢 INFO | Unit tests cover edge cases (ambiguous references, invalid scales, protection policies) | `tests/test_object_feature.py` | Test coverage verified |
| 2 | �� 🟢 INFO | PeP8 Compliant — code style adheres to Python standards | — | No action needed |

### Traceability (FRD→Code)
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | �� 🟢 INFO | FR-OBJ-001 (Create Primitives) → `capabilities_create_primitive_executor.py` | `capabilities_create_primitive_executor.py` | Traceability verified |
| 2 | �� 🟢 INFO | FR-OBJ-002 (Place Existing Object) → `capabilities_place_asset_executor.py` | `capabilities_place_asset_executor.py` | Traceability verified |
| 3 | �� 🟢 INFO | FR-OBJ-003 (Transform Object) → `capabilities_set_transform_executor.py` | `capabilities_set_transform_executor.py` | Traceability verified |
| 4 | �� 🟢 INFO | FR-OBJ-004 (Material Assignment) → `capabilities_set_material_executor.py` | `capabilities_set_material_executor.py` | Traceability verified |
| 5 | �� 🟢 INFO | FR-OBJ-005 (Modifier Management) → `capabilities_apply_modifier_executor.py` | `capabilities_apply_modifier_executor.py` | Traceability verified |
| 6 | �� 🟢 INFO | FR-OBJ-006 (Delete Single Object) → `capabilities_delete_object_executor.py` | `capabilities_delete_object_executor.py` | Traceability verified |
| 7 | �� 🟢 INFO | FR-OBJ-007 (Get Object Info) → `capabilities_get_object_info_executor.py` | `capabilities_get_object_info_executor.py` | Traceability verified |

## Violations
- �� 🔴 CRITICAL AES401: `taxonomy_object_vo.py` violates constant purity
- �� 🔴 CRITICAL AES505: `agent_object_orchestrator.py` uses orchestrator suffix without container wiring

## Action Items
- [ ] �� 🔴 CRITICAL Fix AES401 violation in `taxonomy_object_vo.py`
- [ ] �� 🔴 CRITICAL Fix AES505 violation by ensuring orchestrator is wired in container
- [ ] �� 🟢 INFO Verify reference resolution order implements unique ID → exact name → qualified path/collection
- [ ] �� 🟢 INFO Confirm finite 3-vector validation for transform values

## Fixed Code
None required yet — violations need fixing.

## Severity
- �� 🔴 CRITICAL: Missing core requirement, wrong logic, data integrity risk
- �� 🟡 WARNING: Ambiguous requirement, missing edge case, incomplete criteria
- �� 🟢 INFO: Suggestion or optimization, deferrable

## Checklist
- [x] Prerequisites read
- [x] Feature + modules identified
- [x] FRD mapped to code files
- [x] All 5 dimensions analyzed
- [x] Severity categorized
- [x] Deduped vs existing plans + active PRs
- [x] Plan written (NEW issues + fixed code)
- [x] Saved to correct path