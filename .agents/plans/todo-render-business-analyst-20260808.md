# Plan: render — Business Analyst

## Summary
The render module implements image production and camera optics per FR-RND-001..005. AES structure: 1 agent orchestrator, 4 capabilities, 1 root container. FRD-to-code traceability is strong. Naming conventions compliant. Found 3 risk areas requiring attention. No AES violations found.

## Findings

### Requirements Clarity
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🔴 CRITICAL | FR-RND "Background render submission through job feature" — job module integration not yet implemented in render capabilities | `agent_render_orchestrator.py` | Integrate job feature for long-running renders |
| 2 | 🟡 WARNING | FR-RND "Output destination validated through security policy before render begins" — need to verify security policy validation in render execution path | `capabilities_render_scene_image_executor.py` | Add explicit security policy validation |
| 3 | 🟡 WARNING | FR-RND "Existing artifact → configured overwrite policy" — overwrite policy enforcement not visible | `capabilities_render_scene_image_executor.py` | Verify overwrite policy implementation |

### Business Flow
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | Viewport capture → camera config → HDRI config → render flow works via separate capabilities | `agent_render_orchestrator.py` | Flow verified |
| 2 | 🟡 WARNING | Background render submission depends on job module — not yet integrated | `agent_render_orchestrator.py` | Add job submission for long renders |

### Logic Implementation
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🔴 CRITICAL | HDRI lighting config "uses asset feature for download (never direct)" — verify render doesn't download files directly | `capabilities_render_hdri_config_executor.py` | Confirm no direct download; delegate to asset feature |
| 2 | 🟡 WARNING | "HDRI not found" error category is "delegated" to asset — verify error propagation | `capabilities_render_hdri_config_executor.py` | Confirm asset not found error propagates correctly |

### Testability & Acceptance
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟡 WARNING | No test for HDRI config with missing asset (asset not found scenario) | `tests/` | Add test for asset not found propagation |
| 2 | 🟡 WARNING | No test for background render submission via job feature | `tests/` | Add test once job integration is complete |
| 3 | 🟡 WARNING | No test for overwrite policy on existing output | `tests/` | Add test for overwrite/reject/unique behavior |

### Traceability (FRD→Code)
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | FR-RND Viewport Capture → `capabilities_render_viewport_capture_executor.py` | `capabilities_render_scene_image_executor.py` | Traceability verified |
| 2 | 🟢 INFO | FR-RND Camera Configuration → `capabilities_render_camera_config_executor.py` | `capabilities_render_camera_config_executor.py` | Traceability verified |
| 3 | 🟢 INFO | FR-RND HDRI Configuration → `capabilities_render_hdri_config_executor.py` | `capabilities_render_hdri_config_executor.py` | Traceability verified |
| 4 | 🟢 INFO | FR-RND Scene Render → `capabilities_render_scene_image_executor.py` | `capabilities_render_scene_image_executor.py` | Traceability verified |

## Violations
None found. AES naming and import rules followed.

## Action Items
- [ ] 🔴 CRITICAL Integrate job module for long-running render background submission
- [ ] 🔴 CRITICAL Confirm render does not download files directly (delegate to asset feature)
- [ ] 🟡 WARNING Add explicit security policy validation for output paths
- [ ] 🟡 WARNING Verify overwrite policy enforcement on existing artifacts
- [ ] 🟡 WARNING Add tests for HDRI asset not found propagation, background render, overwrite policy

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