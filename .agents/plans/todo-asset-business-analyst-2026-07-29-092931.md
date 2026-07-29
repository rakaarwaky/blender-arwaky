# Review Plan: Asset — Business Analyst (Phase 2)

## Summary

The Asset module provides a complete feature for searching, downloading, extracting, and importing external assets. The implementation follows the AES architecture with shared contracts/taxonomy and modular capabilities. However, there are **critical import failures** that break the entire module — `__init__.py` references a non-existent file (`capabilities_asset_search`) while the actual file is named `capabilities_asset_search_handler.py`. The dispatcher also does not wire to the Asset orchestrator, leaving the feature orphaned from command routing. Several capability methods remain as stubs raising `NotImplementedError`, indicating incomplete provider adapter wiring.

## Findings by Category

### Requirements Clarity
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟢 INFO | FR-AST-002 "Atomic write (temp → final)" not implemented | `capabilities_asset_download.py:149` | Implement atomic write in `_perform_download` |
| 2 | 🟢 INFO | FR-AST-002 "Concurrent same-asset downloads resolve to one transfer" not addressed | `capabilities_asset_download.py:88-115` | Add file lock or mutex for same-asset downloads |

### Business Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | Module import broken — `__init__.py` references non-existent file | `__init__.py:23` | Fix import to `capabilities_asset_search_handler` + rename class to match |
| 2 | 🔴 CRITICAL | Container imports wrong module and class name | `root_asset_container.py:47` | Import from correct file, use `AssetSearchHandler` |
| 3 | 🟡 WARNING | Dispatcher surface asset action (`surface_asset_action.py`) not wired to `AssetOrchestrator` | `dispatcher/src/surface_asset_action.py` | Wire dispatcher → `IAssetAggregate` via container |
| 4 | 🟡 WARNING | Download capability stubs raise `NotImplementedError` — provider adapter not wired | `capabilities_asset_download.py:153,162,178` | Complete `_estimate_download_size`, `_submit_background_download`, `_perform_download` |

### Logic Implementation
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | `_verify_integrity` only checks existence and size > 0, not checksum | `capabilities_asset_download.py:132-141` | Implement SHA-256 checksum verification when provider supplies one |
| 2 | 🟡 WARNING | `_get_cache_path` uses truncated hash — potential collision for large caches | `capabilities_asset_download.py:107-108` | Use longer hash or add prefix; consider directory sharding |
| 3 | 🟢 INFO | Provider metadata cache TTL hardcoded to 3600s, not configurable from config feature | `capabilities_asset_provider.py:52` | Inject TTL from config getter |
| 4 | 🟢 INFO | `_extract_thumbnail` rejects non-HTTPS URLs silently without warning caller | `capabilities_asset_provider.py:120-122` | Return structured error or warning instead of silent None |

### Testability & Acceptance Criteria
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | Tests cannot run — import error blocks test collection | `modules/asset/tests/test_asset_download.py`, `test_asset_search.py` | Fix module import first, then verify all 55 tests pass |
| 2 | 🟡 WARNING | No integration tests for search → download → extract → import flow | `modules/asset/tests/` | Add end-to-end test covering full asset lifecycle |
| 3 | 🟢 INFO | QA checklist items not traceable to specific test files | `FRD.md:QA Checklist` | Map each `[ ]` item to a test function |

### Traceability (FRD → Code)
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | FR-AST-001 "Duplicate assets deduplicated when equivalence is safely determinable" not implemented | `capabilities_asset_search_handler.py:65-85` | Add deduplication logic (e.g., by asset ID + provider) |
| 2 | 🟡 WARNING | FR-AST-001 "Credentials never in results/logs/events" — no redaction applied to search results | `capabilities_asset_search_handler.py:56-62` | Ensure provider auth tokens are stripped before normalization |
| 3 | 🟡 WARNING | FR-AST-002 "Corrupted artifact → re-download or cache error" — only triggers on empty file | `capabilities_asset_download.py:136-137` | Extend integrity check to detect corruption beyond zero-size |
| 4 | 🟢 INFO | FR-AST-005 "Cache within freshness window" — cache key includes TTL but stale refresh not triggered | `capabilities_asset_provider.py:58-62` | Add stale-while-revalidate pattern for metadata cache |

## Violations
| Code | File | Description |
|------|------|-------------|
| AES101 | `__init__.py:23` | Import references non-existent module `capabilities_asset_search` |
| RUF100 | `capabilities_asset_search_handler.py:37-39` | Unused `noqa` directives for ARG002 — linter doesn't flag unused `_` params |

## Action Items
- [ ] **CRITICAL** Fix `__init__.py` import: change `capabilities_asset_search` → `capabilities_asset_search_handler`, rename class reference to `AssetSearchHandler`
- [ ] **CRITICAL** Fix `root_asset_container.py` import: update module path and class name
- [ ] **CRITICAL** Fix tests: verify test imports work after module fix
- [ ] **WARNING** Wire dispatcher → `IAssetAggregate`: add `surface_asset_action.py` routing to `AssetOrchestrator`
- [ ] **WARNING** Fix lint: remove unused `noqa: ARG002` directives in `capabilities_asset_search_handler.py`
- [ ] **WARNING** Implement stub methods: `_perform_download`, `_submit_background_download`, `_estimate_download_size`
- [ ] **INFO** Add search result deduplication logic
- [ ] **INFO** Strengthen integrity verification with checksum support

## Fixed Code
{Will apply fixes after plan approval}
