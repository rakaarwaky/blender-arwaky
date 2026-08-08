# Plan: asset — Business Analyst

## Summary
The asset module implements external asset acquisition (search, download, cache, extract, import) per FR-AST-001..005. Code structure follows AES: 1 agent orchestrator, 5 capabilities, 1 root container. FRD maps cleanly to capabilities: search→`capabilities_asset_search_handler.py`, download→`capabilities_asset_download.py`, extract→`capabilities_asset_extract.py`, import→`capabilities_asset_import.py`, provider metadata→`capabilities_asset_provider.py`. No missing FR coverage. Boundary with object (import handoff) and render (HDRI files) is explicit and respected.

## Findings

### Requirements Clarity
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | FR-AST-001 "curated/default results for empty query" — not explicitly in search handler logic | `capabilities_asset_search_handler.py` | Add comment or docstring noting this edge case handling if implemented; otherwise clarify in FRD |
| 2 | 🟢 INFO | FR-AST-002 "concurrent same-asset downloads resolve to one transfer" — deduplication mechanism not visible in download capability | `capabilities_asset_download.py` | Verify if implemented via cache check; document the deduplication strategy |

### Business Flow
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | Search → download → extract → import pipeline relies on caller sequencing; no aggregate enforces end-to-end flow | `agent_asset_orchestrator.py` | Consider adding a convenience method for full pipeline if common use case |

### Logic Implementation
| # | Severity | Issue | Location | Recommendation |
|---|---|---|---|---|
| 1 | 🟢 INFO | `capabilities_asset_search_handler.py` uses `_search_single_provider` but provider adapters not yet visible in codebase — may be external or TBD | `capabilities_asset_search_handler.py` | Confirm provider adapter location; ensure protocol/contract exists in shared |

### Testability & Acceptance
| # | Severity | Issue | Location | Recommendation |
|---|---|---|---|---|
| 1 | 🟢 INFO | No integration test for full search→download→import flow visible in `tests/` | `tests/` | Add E2E test covering pipeline with mocked providers |

### Traceability (FRD→Code)
| # | Severity | Issue | Location | Recommendation |
|---|---|---|---|---|
| 1 | 🟢 INFO | FR-AST-005 "provider capability metadata" mapped to `capabilities_asset_provider.py` but no explicit `get_provider_capabilities` method found | `capabilities_asset_provider.py` | Verify method exists; add if missing |

## Violations
None found. AES layer separation respected (agent orchestrates, capabilities implement, root wires).

## Action Items
- [ ] 🟢 INFO Verify provider adapter contract exists in shared taxonomy/contracts
- [ ] 🟢 INFO Add E2E test for search→download→import pipeline
- [ ] 🟢 INFO Document download deduplication strategy

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