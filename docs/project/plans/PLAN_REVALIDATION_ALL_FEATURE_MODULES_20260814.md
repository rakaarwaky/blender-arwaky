# Plan Revalidation — All Feature Modules

## Objective

This document verifies whether the 2026-08-08 business-analyst plans are still relevant and safe to execute. It does not execute code. It classifies every unique historical finding as `open`, `needs-clarification`, `resolved`, or `obsolete`, and it preserves unresolved uncertainty instead of presenting assumptions as facts.

## Classification Policy

| Status | Meaning | Execution rule |
|---|---|---|
| `open` | The previous plan identifies a concrete unmet requirement, missing test, missing integration, or violation that remains plausible. | Candidate for implementation after a focused acceptance test is defined. |
| `needs-clarification` | The finding uses verify/confirm/appears language, references a stale path, or lacks enough current evidence. | Do not modify code until the behavior is checked. |
| `resolved` | The previous plan explicitly recorded the behavior as verified or the current change set provides direct evidence. | Keep as regression acceptance criteria; do not reimplement blindly. |
| `obsolete` | The requirement or finding is superseded by an authoritative FRD/architecture change. | Remove only with a recorded replacement rationale. |

## Module Summary

| Module | Findings | Open | Needs clarification | Resolved | Obsolete | Revised plan |
|---|---:|---:|---:|---:|---:|---|
| asset | 6 | 1 | 5 | 0 | 0 | `todo-asset-business-analyst-20260814-revalidated.md` |
| cli | 11 | 5 | 5 | 1 | 0 | `todo-cli-business-analyst-20260814-revalidated.md` |
| config | 5 | 0 | 2 | 3 | 0 | `todo-config-business-analyst-20260814-revalidated.md` |
| diagnostics | 12 | 3 | 9 | 0 | 0 | `todo-diagnostics-business-analyst-20260814-revalidated.md` |
| dispatcher | 15 | 1 | 8 | 6 | 0 | `todo-dispatcher-business-analyst-20260814-revalidated.md` |
| gateway | 18 | 2 | 11 | 5 | 0 | `todo-gateway-business-analyst-20260814-revalidated.md` |
| job | 18 | 4 | 5 | 9 | 0 | `todo-job-business-analyst-20260814-revalidated.md` |
| launcher | 5 | 0 | 0 | 5 | 0 | `todo-launcher-business-analyst-20260814-revalidated.md` |
| mcp | 16 | 2 | 9 | 5 | 0 | `todo-mcp-business-analyst-20260814-revalidated.md` |
| object | 15 | 0 | 1 | 13 | 1 | `todo-object-business-analyst-20260814-revalidated.md` |
| render | 14 | 5 | 2 | 6 | 1 | `todo-render-business-analyst-20260814-revalidated.md` |
| scene | 10 | 3 | 3 | 4 | 0 | `todo-scene-business-analyst-20260814-revalidated.md` |
| security | 19 | 6 | 1 | 12 | 0 | `todo-security-business-analyst-20260814-revalidated.md` |
| shared | 6 | 3 | 2 | 1 | 0 | `todo-shared-business-analyst-20260814-revalidated.md` |
| telemetry | 6 | 5 | 0 | 1 | 0 | `todo-telemetry-business-analyst-20260814-revalidated.md` |

## Important Interpretation

The old plans are still valuable as a historical audit backlog, but they are not safe as direct implementation instructions. Several rows use stale filenames or phrases such as “verify,” “confirm,” and “consider.” Those rows are intentionally not marked resolved or open without qualification. The revised plans are therefore the execution gate: first resolve clarification rows, then implement only confirmed open rows, and use resolved rows as tests rather than work items.

The evidence for the most consequential decisions is recorded in [`PLAN_REVALIDATION_EVIDENCE_20260814.md`](PLAN_REVALIDATION_EVIDENCE_20260814.md). This ledger is required review context before any backlog item is implemented.

## Cross-cutting Finding

The required `.agents/rules/README.md` index is still absent. This remains a documentation/process warning and is tracked separately in `todo-cross-cutting-business-analyst-20260814.md`.

## References

- [`ARCHITECTURE.md`](../../../ARCHITECTURE.md)
- [`PRD.md`](../../../PRD.md)
- [`RULES_AES.md`](../../../.agents/rules/RULES_AES.md)
- [`Original plans`](../../../.agents/plans/)
- [`Evidence ledger`](PLAN_REVALIDATION_EVIDENCE_20260814.md)
