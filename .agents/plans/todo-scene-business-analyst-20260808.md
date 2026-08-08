# Plan: scene — Business Analyst

## Summary
The scene module implements scene inspection and cleanup capabilities through a well-structured protocol-based architecture. Key components include inspection protocol for scene state retrieval and cleanup protocol for protected object management. The implementation uses the Rule-Based Cleanup Pattern and protocol aggregator approach.

## Findings

### Requirements Clarity
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟡 WARNING | FR-SCN-002 "Child policy: delete hierarchy/detach/reject" — test coverage misses complex hierarchies | `tests/test_scene_cleanup.py` | Add property-based testing for child/dependent policies |
| 2 | 🟡 WARNING | FR-SCN-001 "Large scenes → summarized detail level to avoid oversized response" — summarization strategy not specified | `capabilities_scene_inspection_executor.py` | Implement size-based inspection summarization (first/last N objects) |

### Business Flow
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | Inspection flow: request → filtering → detail level → summary → response | `capabilities_scene_inspection_executor.py` | Flow verified |
| 2 | 🟢 INFO | Cleanup flow: policy resolution → dry-run preview → confirmation → execution → report | `capabilities_scene_cleanup_executor.py` | Flow verified |

### Logic Implementation
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟡 WARNING | Scene inspection results lack size monitoring and detail limits | `contract_scene_inspection_protocol.py` | Add scene size monitoring |
| 2 | 🟡 WARNING | Cleanup logic lacks explicit handling of linked object references | `scene_capabilities_cleanup.py` | Add linked object reference tracking |

### Testability & Acceptance
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟡 WARNING | No tests for scene inspection pagination behavior | `tests/test_scene_inspection.py` | Add pagination test cases |
| 2 | 🟡 WARNING | No tests for linked object cleanup scenarios | `tests/test_scene_cleanup.py` | Add linked object handling tests |

### Traceability (FRD→Code)
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | FR-SCN-001 (Scene Inspection) → `contract_scene_inspection_protocol.py` | `contract_scene_inspection_protocol.py` | Traceability verified |
| 2 | 🟢 INFO | FR-SCN-002 (Scene Cleanup) → `scene_capabilities_cleanup.py` | `scene_capabilities_cleanup.py` | Traceability verified |

## Violations
No AES violations found. Scene module properly isolates concerns using protocol-based design.

## Action Items
- [ ] 🟡 WARNING Add scene size monitoring and detail limits for large scene inspection
- [ ] 🟡 WARNING Add linked object reference tracking in cleanup logic
- [ ] 🟡 WARNING Add pagination test cases for scene inspection
- [ ] 🟡 WARNING Add linked object handling tests

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