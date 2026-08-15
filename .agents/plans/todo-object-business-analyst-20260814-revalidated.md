# Plan: object — Revalidated Business Analyst Plan (2026-08-14)

## Summary

This is the revalidated successor to `todo-object-business-analyst-20260808.md`. Every finding from the 2026-08-08 plan was reviewed against the current branch, the module FRD, the AES architecture rules, and the current source/test inventory. The classification policy is conservative: a finding is not marked resolved merely because it is old; only explicit verification statements are resolved, while implementation gaps remain open and uncertainty remains needs-clarification.

## Revalidation Result

The plan contains 15 unique findings after deduplication: 0 open, 1 needs clarification, 13 resolved, and 1 obsolete. The old AES401 path is obsolete after taxonomy ownership moved to shared, and the old AES505 claim is closed by current container wiring. No finding was silently discarded. Paths from the old plan that no longer match current filenames are retained as needs-clarification rather than being treated as proof that the requirement disappeared.

## Findings

| # | Previous severity | Status | Finding | Location | Decision |
|---:|---|---|---|---|---|
| 1 | 🟢 INFO | **needs-clarification** | FR-OBJ-001 "Reference resolution deterministic: unique ID → exact name → qualified path/collection" — verify implementation | `capabilities_place_asset_executor.py` | The finding is an uncertainty or documentation gap; confirm behavior with a focused source/test check before implementation. |
| 2 | 🟢 INFO | **resolved** | FR-OBJ-002 "Transform values must be finite 3-vectors" — validation visible | `capabilities_set_transform_executor.py` | Current implementation validates transform vectors; retain as a regression criterion. |
| 3 | 🟢 INFO | **resolved** | Create → place → transform → material → modifier → delete flow works via separate capabilities | `agent_object_orchestrator.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 4 | 🟢 INFO | **resolved** | Destructive actions require confirmation (apply modifier, delete protected) | `capabilities_apply_modifier_executor.py`, `capabilities_delete_object_executor.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 5 | 🔴 CRITICAL | **obsolete** | **AES401 Violation**: `taxonomy_object_vo.py` uses `_vo` suffix but includes non-constant declarations (dataclasses with fields) | `modules/object/src/taxonomy_object_vo.py` | The referenced module path no longer owns the taxonomy; current object VOs live under shared taxonomy and this old location-specific claim must not be applied. |
| 6 | 🔴 CRITICAL | **resolved** | **AES505 Violation**: `agent_object_orchestrator.py` uses `_orchestrator` suffix without being wired in any container | `modules/object/src/agent_object_orchestrator.py` | Current `ObjectContainer.wire()` constructs the orchestrator and exposes it through `create_object_feature`; retain wiring as a regression criterion. |
| 7 | 🟢 INFO | **resolved** | Unit tests cover edge cases (ambiguous references, invalid scales, protection policies) | `tests/test_object_feature.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 8 | 🟢 INFO | **resolved** | PeP8 Compliant — code style adheres to Python standards | — | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 9 | 🟢 INFO | **resolved** | FR-OBJ-001 (Create Primitives) → `capabilities_create_primitive_executor.py` | `capabilities_create_primitive_executor.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 10 | 🟢 INFO | **resolved** | FR-OBJ-002 (Place Existing Object) → `capabilities_place_asset_executor.py` | `capabilities_place_asset_executor.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 11 | 🟢 INFO | **resolved** | FR-OBJ-003 (Transform Object) → `capabilities_set_transform_executor.py` | `capabilities_set_transform_executor.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 12 | 🟢 INFO | **resolved** | FR-OBJ-004 (Material Assignment) → `capabilities_set_material_executor.py` | `capabilities_set_material_executor.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 13 | 🟢 INFO | **resolved** | FR-OBJ-005 (Modifier Management) → `capabilities_apply_modifier_executor.py` | `capabilities_apply_modifier_executor.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 14 | 🟢 INFO | **resolved** | FR-OBJ-006 (Delete Single Object) → `capabilities_delete_object_executor.py` | `capabilities_delete_object_executor.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 15 | 🟢 INFO | **resolved** | FR-OBJ-007 (Get Object Info) → `capabilities_get_object_info_executor.py` | `capabilities_get_object_info_executor.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |

## Validated Execution Backlog

Only findings marked **open** should be considered implementation candidates. Findings marked **needs-clarification** require a focused source/test check first. Findings marked **resolved** become regression acceptance criteria and must not be reimplemented without evidence of regression.

| Priority | Status | Action |
|---|---|---|
| 🟢 INFO | needs-clarification | Confirm reference resolution order |
| 🟢 INFO | resolved | Keep finite transform validation as a regression criterion |
| 🔴 CRITICAL | obsolete | Old module path no longer represents current taxonomy ownership; do not apply this change blindly |
| 🔴 CRITICAL | resolved | Keep explicit ObjectContainer wiring as a regression criterion |

## Violations

No new violation is asserted by this revalidation without a current source/test proof. Suspected AES violations remain needs-clarification when the old path or architecture context changed.

## Traceability

The module FRD remains the authoritative requirement source. The previous plan is preserved as historical evidence, while this plan is the current status ledger.

## Execution Guardrails

Before implementing any row, confirm the exact current file path, the FRD acceptance criterion, and an executable test. Do not implement recommendations that only say “verify,” “consider,” or “document” until the verification result is recorded. Do not duplicate findings already present in another module plan.

## References

- [`FRD.md`](../../modules/object/FRD.md)
- [`ARCHITECTURE.md`](../../ARCHITECTURE.md)
- [`AES rules`](../../.agents/rules/RULES_AES.md)
- [`Previous plan`](./todo-object-business-analyst-20260808.md)
