# Plan: shared — Revalidated Business Analyst Plan (2026-08-14)

## Summary

This is the revalidated successor to `todo-shared-business-analyst-20260808.md`. Every finding from the 2026-08-08 plan was reviewed against the current branch, the module FRD, the AES architecture rules, and the current source/test inventory. The classification policy is conservative: a finding is not marked resolved merely because it is old; only explicit verification statements are resolved, while implementation gaps remain open and uncertainty remains needs-clarification.

## Revalidation Result

The plan contains 6 unique findings after deduplication: 3 open, 2 needs clarification, 1 resolved, and 0 obsolete. No finding was silently discarded. Paths from the old plan that no longer match current filenames are retained as needs-clarification rather than being treated as proof that the requirement disappeared.

## Findings

| # | Previous severity | Status | Finding | Location | Decision |
|---:|---|---|---|---|---|
| 1 | 🟡 WARNING | **open** | Abstract methods in `WorkflowProtocol` use `pass` without implementation, causing ambiguous requirements. | `/home/raka/mcp-arwaky/blender-arwaky/modules/shared/src/common/contract_workflow_protocol.py` | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 2 | 🟡 WARNING | **open** | Import statements reference sibling modules without explicit layer justification, risking Group 2 import rule violations. | `/home/raka/mcp-arwaky/blender-arwaky/modules/shared/src/common/contract_command_catalog_protocol.py` | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 3 | 🟢 INFO | **resolved** | No business-flow anomalies detected; layer adheres to defined taxonomy. | — | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 4 | 🟡 WARNING | **open** | Several protocol methods are left as `pass`, indicating missing logic and risking incomplete contract fulfillment. | Multiple files (`contract_workflow_protocol.py`, `contract_command_catalog_protocol.py`, `contract_execute_action_protocol.py`) | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 5 | 🟡 WARNING | **needs-clarification** | No test files found alongside protocol modules; unit-test coverage unknown. | All `*.py` under `/src/common` & related dirs | The risk is plausible but the finding is phrased as a verification request; inspect the current implementation before changing code. |
| 6 | 🟢 INFO | **needs-clarification** | FRD scope directly maps to taxonomy VO/event/constant modules; mapping is clear. | FRD.md ↔ `src/*/taxonomy_*.py` | The wording does not provide enough evidence for automatic closure; retain it for targeted review. |

## Validated Execution Backlog

Only findings marked **open** should be considered implementation candidates. Findings marked **needs-clarification** require a focused source/test check first. Findings marked **resolved** become regression acceptance criteria and must not be reimplemented without evidence of regression.

| Priority | Status | Action |
|---|---|---|
| 🟡 WARNING | open | Implement minimal logic or add TODO with target release. |
| 🟡 WARNING | open | Review against AES import rules; adjust if forbidden. |
| 🟡 WARNING | open | Add minimal stub implementations or deprecation notices. |
| 🟡 WARNING | needs-clarification | Add minimal test scaffolding to verify signatures and contract compliance. |
| 🟢 INFO | needs-clarification | Keep comment-based registry linking FRD items to code. |

## Violations

No new violation is asserted by this revalidation without a current source/test proof. Suspected AES violations remain needs-clarification when the old path or architecture context changed.

## Traceability

The module FRD remains the authoritative requirement source. The previous plan is preserved as historical evidence, while this plan is the current status ledger.

## Execution Guardrails

Before implementing any row, confirm the exact current file path, the FRD acceptance criterion, and an executable test. Do not implement recommendations that only say “verify,” “consider,” or “document” until the verification result is recorded. Do not duplicate findings already present in another module plan.

## References

- [`FRD.md`](../../modules/shared/FRD.md)
- [`ARCHITECTURE.md`](../../ARCHITECTURE.md)
- [`AES rules`](../../.agents/rules/RULES_AES.md)
- [`Previous plan`](./todo-shared-business-analyst-20260808.md)
