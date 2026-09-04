# Plan: render — Revalidated Business Analyst Plan (2026-08-14)

## Summary

This is the revalidated successor to `todo-render-business-analyst-20260808.md`. Every finding from the 2026-08-08 plan was reviewed against the current branch, the module FRD, the AES architecture rules, and the current source/test inventory. The classification policy is conservative: a finding is not marked resolved merely because it is old; only explicit verification statements are resolved, while implementation gaps remain open and uncertainty remains needs-clarification.

## Revalidation Result

The plan contains 14 unique findings after deduplication: 5 open, 2 needs clarification, 6 resolved, and 1 obsolete. The duplicate background-render integration row is retained in the ledger as obsolete rather than being executed twice. No finding was silently discarded. Paths from the old plan that no longer match current filenames are retained as needs-clarification rather than being treated as proof that the requirement disappeared.

## Findings

| # | Previous severity | Status | Finding | Location | Decision |
|---:|---|---|---|---|---|
| 1 | 🔴 CRITICAL | **open** | FR-RND "Background render submission through job feature" — job module integration not yet implemented in render capabilities | `agent_render_orchestrator.py` | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 2 | 🟡 WARNING | **resolved** | FR-RND "Output destination validated through security policy before render begins" — need to verify security policy validation in render execution path | `capabilities_render_scene_image_executor.py` | Current source calls the injected `ValidatePathProtocol` before render code execution; retain as a regression acceptance criterion. |
| 3 | 🟡 WARNING | **open** | FR-RND "Existing artifact → configured overwrite policy" — overwrite policy enforcement not visible | `capabilities_render_scene_image_executor.py` | Current validation accepts an overwrite policy, but the render code builder does not apply it; define and implement the policy before treating this as resolved. |
| 4 | 🟢 INFO | **resolved** | Viewport capture → camera config → HDRI config → render flow works via separate capabilities | `agent_render_orchestrator.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 5 | 🟡 WARNING | **obsolete** | Background render submission depends on job module — not yet integrated | `agent_render_orchestrator.py` | Duplicate of finding 1; keep only finding 1 as the canonical job-integration backlog item. |
| 6 | 🔴 CRITICAL | **needs-clarification** | HDRI lighting config "uses asset feature for download (never direct)" — verify render doesn't download files directly | `capabilities_render_hdri_config_executor.py` | The risk is plausible but the finding is phrased as a verification request; inspect the current implementation before changing code. |
| 7 | 🟡 WARNING | **needs-clarification** | "HDRI not found" error category is "delegated" to asset — verify error propagation | `capabilities_render_hdri_config_executor.py` | The finding is an uncertainty or documentation gap; confirm behavior with a focused source/test check before implementation. |
| 8 | 🟡 WARNING | **open** | No test for HDRI config with missing asset (asset not found scenario) | `tests/` | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 9 | 🟡 WARNING | **open** | No test for background render submission via job feature | `tests/` | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 10 | 🟡 WARNING | **open** | No test for overwrite policy on existing output | `tests/` | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 11 | 🟢 INFO | **resolved** | FR-RND Viewport Capture → `capabilities_render_viewport_capture_executor.py` | `capabilities_render_scene_image_executor.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 12 | 🟢 INFO | **resolved** | FR-RND Camera Configuration → `capabilities_render_camera_config_executor.py` | `capabilities_render_camera_config_executor.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 13 | 🟢 INFO | **resolved** | FR-RND HDRI Configuration → `capabilities_render_hdri_config_executor.py` | `capabilities_render_hdri_config_executor.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 14 | 🟢 INFO | **resolved** | FR-RND Scene Render → `capabilities_render_scene_image_executor.py` | `capabilities_render_scene_image_executor.py` | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |

## Validated Execution Backlog

Only findings marked **open** should be considered implementation candidates. Findings marked **needs-clarification** require a focused source/test check first. Findings marked **resolved** become regression acceptance criteria and must not be reimplemented without evidence of regression.

| Priority | Status | Action |
|---|---|---|
| 🔴 CRITICAL | open | Integrate job feature for long-running renders |
| 🟡 WARNING | resolved | Keep security path validation as a regression acceptance criterion |
| 🟡 WARNING | open | Implement and test overwrite/reject/unique behavior |
| 🟡 WARNING | obsolete | Duplicate of the canonical background-render integration item |
| 🔴 CRITICAL | needs-clarification | Confirm no direct download; delegate to asset feature |
| 🟡 WARNING | needs-clarification | Confirm asset not found error propagates correctly |
| 🟡 WARNING | open | Add test for asset not found propagation |
| 🟡 WARNING | open | Add test once job integration is complete |
| 🟡 WARNING | open | Add test for overwrite/reject/unique behavior |

## Violations

No new violation is asserted by this revalidation without a current source/test proof. Suspected AES violations remain needs-clarification when the old path or architecture context changed.

## Traceability

The module FRD remains the authoritative requirement source. The previous plan is preserved as historical evidence, while this plan is the current status ledger.

## Execution Guardrails

Before implementing any row, confirm the exact current file path, the FRD acceptance criterion, and an executable test. Do not implement recommendations that only say “verify,” “consider,” or “document” until the verification result is recorded. Do not duplicate findings already present in another module plan.

## References

- [`FRD.md`](../../modules/render/FRD.md)
- [`ARCHITECTURE.md`](../../ARCHITECTURE.md)
- [`AES rules`](../../.agents/rules/RULES_AES.md)
- [`Previous plan`](./todo-render-business-analyst-20260808.md)
