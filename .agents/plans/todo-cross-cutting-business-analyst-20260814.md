# Plan: Cross-cutting — Business Analyst Review (2026-08-14)

## Summary

The required business-analyst workflow was applied across all 14 PRD feature modules: Asset, CLI, Config, Diagnostics, Dispatcher, Gateway, Job, Launcher, MCP, Object, Render, Scene, Security, and Telemetry. Existing per-feature plans from 2026-08-08 were found for all 14 modules, and no active GitHub PR currently claims a feature. The feature-level deduplication result is **14 modules covered, 0 new feature-specific issues**.

## New Cross-cutting Finding

| # | Severity | Issue | Location | Recommendation |
|---|---|---|---|---|
| 1 | 🟡 WARNING | The attachment requires `.agents/rules/README.md`, but that file does not exist in the repository. The rules directory instead contains individual rule files, including `RULES_AES.md` and `RULES_RUFF.md`. | `.agents/rules/` | Add a rules index README that links to every available rule file and declares the canonical prerequisite-reading order. This is a documentation/process change only. |

## Impact

The missing index does not invalidate the feature review because the available AES architecture rules, architecture specification, PRD, and skills index were read directly. It does reduce reproducibility for future agents and makes the required workflow ambiguous.

## Propose Change

Create `.agents/rules/README.md` with a table containing rule filename, scope, severity system, and invocation context. Include explicit links to `RULES_AES.md`, `RULES_RUFF.md`, `RULES_MYPY.md`, `RULES_BANDIT.md`, `RULES_RADON.md`, `RULES_CARGO_AUDIT.md`, `RULES_CLIPPY.md`, `RULES_RUSTFMT.md`, `RULES_ESLINT.md`, and `RULES_TSC.md`. State that `RULES_AES.md` and `ARCHITECTURE.md` are mandatory for feature-module analysis, while language-specific rules apply only when that language is modified.

## Action Items

| Priority | Action | Execution status |
|---|---|---|
| Warning | Add the missing rules index README. | Proposal only; not executed. |
| Info | Keep the 14 existing feature plans as the deduplication source of truth. | No code execution. |

## References

- [`ARCHITECTURE.md`](../../ARCHITECTURE.md)
- [`PRD.md`](../../PRD.md)
- [`Rules directory`](../rules/)
- [`Skills index`](../skills/README.md)
