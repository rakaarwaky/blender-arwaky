# Plan: scene — Revalidated Business Analyst Plan (2026-08-14)

## Summary

This is the revalidated successor to `todo-scene-business-analyst-20260808.md`. Every finding from the 2026-08-08 plan was reviewed against the current branch, the module FRD, the AES architecture rules, and the current source/test inventory. The classification policy is conservative: a finding is not marked resolved merely because it is old; only explicit verification statements are resolved, while implementation gaps remain open and uncertainty remains needs-clarification.

## Revalidation Result

The plan contains 10 unique findings after deduplication: 3 open, 3 needs clarification, 4 resolved, and 0 obsolete. No finding was silently discarded. Paths from the old plan that no longer match current filenames are retained as needs-clarification rather than being treated as proof that the requirement disappeared.

## Findings

| # | Previous severity | Status | Finding | Location | Decision |
|---:|---|---|---|---|---|
| 1 | 🟡 WARNING | **needs-clarification** | FR-SCN-002 "Child policy: delete hierarchy/detach/reject" — test coverage misses complex hierarchies | `tests/test_scene_cleanup.py` | The wording does not provide enough evidence for automatic closure; retain it for targeted review. |
| 2 | 🟡 WARNING | **needs-clarification** | FR-SCN-001 "Large scenes → summarized detail level to avoid oversized response" — summarization strategy not specified | `capabilities_scene_inspection_executor.py` | The wording does not provide enough evidence for automatic closure; retain it for targeted review. |
| 3 | 🟢 INFO | **resolved** | Inspection flow: request → filtering → detail level → summary → response | `capabilities_scene_inspection_executor.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 4 | 🟢 INFO | **resolved** | Cleanup flow: policy resolution → dry-run preview → confirmation → execution → report | `capabilities_scene_cleanup_executor.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 5 | 🟡 WARNING | **needs-clarification** | Scene inspection results lack size monitoring and detail limits | `contract_scene_inspection_protocol.py` | The wording does not provide enough evidence for automatic closure; retain it for targeted review. |
| 6 | 🟡 WARNING | **open** | Cleanup logic lacks explicit handling of linked object references | `scene_capabilities_cleanup.py` | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 7 | 🟡 WARNING | **open** | No tests for scene inspection pagination behavior | `tests/test_scene_inspection.py` | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 8 | 🟡 WARNING | **open** | No tests for linked object cleanup scenarios | `tests/test_scene_cleanup.py` | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 9 | 🟢 INFO | **resolved** | FR-SCN-001 (Scene Inspection) → `contract_scene_inspection_protocol.py` | `contract_scene_inspection_protocol.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 10 | 🟢 INFO | **resolved** | FR-SCN-002 (Scene Cleanup) → `scene_capabilities_cleanup.py` | `scene_capabilities_cleanup.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |

## Validated Execution Backlog

Only findings marked **open** should be considered implementation candidates. Findings marked **needs-clarification** require a focused source/test check first. Findings marked **resolved** become regression acceptance criteria and must not be reimplemented without evidence of regression.

| Priority | Status | Action |
|---|---|---|
| 🟡 WARNING | needs-clarification | Add property-based testing for child/dependent policies |
| 🟡 WARNING | needs-clarification | Implement size-based inspection summarization (first/last N objects) |
| 🟡 WARNING | needs-clarification | Add scene size monitoring |
| 🟡 WARNING | open | Add linked object reference tracking |
| 🟡 WARNING | open | Add pagination test cases |
| 🟡 WARNING | open | Add linked object handling tests |

## Violations

No new violation is asserted by this revalidation without a current source/test proof. Suspected AES violations remain needs-clarification when the old path or architecture context changed.

## Traceability

The module FRD remains the authoritative requirement source. The previous plan is preserved as historical evidence, while this plan is the current status ledger.

## Execution Guardrails

Before implementing any row, confirm the exact current file path, the FRD acceptance criterion, and an executable test. Do not implement recommendations that only say “verify,” “consider,” or “document” until the verification result is recorded. Do not duplicate findings already present in another module plan.

## References

- [`FRD.md`](../../modules/scene/FRD.md)
- [`ARCHITECTURE.md`](../../ARCHITECTURE.md)
- [`AES rules`](../../.agents/rules/RULES_AES.md)
- [`Previous plan`](./todo-scene-business-analyst-20260808.md)
