# Plan: asset — Revalidated Business Analyst Plan (2026-08-14)

## Summary

This is the revalidated successor to `todo-asset-business-analyst-20260808.md`. Every finding from the 2026-08-08 plan was reviewed against the current branch, the module FRD, the AES architecture rules, and the current source/test inventory. The classification policy is conservative: a finding is not marked resolved merely because it is old; only explicit verification statements are resolved, while implementation gaps remain open and uncertainty remains needs-clarification.

## Revalidation Result

The plan contains 6 unique findings after deduplication: 1 open, 5 needs clarification, 0 resolved, and 0 obsolete. No finding was silently discarded. Paths from the old plan that no longer match current filenames are retained as needs-clarification rather than being treated as proof that the requirement disappeared.

## Findings

| # | Previous severity | Status | Finding | Location | Decision |
|---:|---|---|---|---|---|
| 1 | 🟢 INFO | **needs-clarification** | FR-AST-001 "curated/default results for empty query" — not explicitly in search handler logic | `capabilities_asset_search_handler.py` | The finding is an uncertainty or documentation gap; confirm behavior with a focused source/test check before implementation. |
| 2 | 🟢 INFO | **needs-clarification** | FR-AST-002 "concurrent same-asset downloads resolve to one transfer" — deduplication mechanism not visible in download capability | `capabilities_asset_download.py` | The risk is plausible but the finding is phrased as a verification request; inspect the current implementation before changing code. |
| 3 | 🟢 INFO | **needs-clarification** | Search → download → extract → import pipeline relies on caller sequencing; no aggregate enforces end-to-end flow | `agent_asset_orchestrator.py` | The wording does not provide enough evidence for automatic closure; retain it for targeted review. |
| 4 | 🟢 INFO | **needs-clarification** | `capabilities_asset_search_handler.py` uses `_search_single_provider` but provider adapters not yet visible in codebase — may be external or TBD | `capabilities_asset_search_handler.py` | The risk is plausible but the finding is phrased as a verification request; inspect the current implementation before changing code. |
| 5 | 🟢 INFO | **open** | No integration test for full search→download→import flow visible in `tests/` | `tests/` | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 6 | 🟢 INFO | **needs-clarification** | FR-AST-005 "provider capability metadata" mapped to `capabilities_asset_provider.py` but no explicit `get_provider_capabilities` method found | `capabilities_asset_provider.py` | The risk is plausible but the finding is phrased as a verification request; inspect the current implementation before changing code. |

## Validated Execution Backlog

Only findings marked **open** should be considered implementation candidates. Findings marked **needs-clarification** require a focused source/test check first. Findings marked **resolved** become regression acceptance criteria and must not be reimplemented without evidence of regression.

| Priority | Status | Action |
|---|---|---|
| 🟢 INFO | needs-clarification | Add comment or docstring noting this edge case handling if implemented; otherwise clarify in FRD |
| 🟢 INFO | needs-clarification | Verify if implemented via cache check; document the deduplication strategy |
| 🟢 INFO | needs-clarification | Consider adding a convenience method for full pipeline if common use case |
| 🟢 INFO | needs-clarification | Confirm provider adapter location; ensure protocol/contract exists in shared |
| 🟢 INFO | open | Add E2E test covering pipeline with mocked providers |
| 🟢 INFO | needs-clarification | Verify method exists; add if missing |

## Violations

No new violation is asserted by this revalidation without a current source/test proof. Suspected AES violations remain needs-clarification when the old path or architecture context changed.

## Traceability

The module FRD remains the authoritative requirement source. The previous plan is preserved as historical evidence, while this plan is the current status ledger.

## Execution Guardrails

Before implementing any row, confirm the exact current file path, the FRD acceptance criterion, and an executable test. Do not implement recommendations that only say “verify,” “consider,” or “document” until the verification result is recorded. Do not duplicate findings already present in another module plan.

## References

- [`FRD.md`](../../modules/asset/FRD.md)
- [`ARCHITECTURE.md`](../../ARCHITECTURE.md)
- [`AES rules`](../../.agents/rules/RULES_AES.md)
- [`Previous plan`](./todo-asset-business-analyst-20260808.md)
