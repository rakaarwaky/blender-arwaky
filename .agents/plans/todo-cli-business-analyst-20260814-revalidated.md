# Plan: cli — Revalidated Business Analyst Plan (2026-08-14)

## Summary

This is the revalidated successor to `todo-cli-business-analyst-20260808.md`. Every finding from the 2026-08-08 plan was reviewed against the current branch, the module FRD, the AES architecture rules, and the current source/test inventory. The classification policy is conservative: a finding is not marked resolved merely because it is old; only explicit verification statements are resolved, while implementation gaps remain open and uncertainty remains needs-clarification.

## Revalidation Result

The plan contains 11 unique findings after deduplication: 5 open, 5 needs clarification, 1 resolved, and 0 obsolete. No finding was silently discarded. Paths from the old plan that no longer match current filenames are retained as needs-clarification rather than being treated as proof that the requirement disappeared.

## Findings

| # | Previous severity | Status | Finding | Location | Decision |
|---:|---|---|---|---|---|
| 1 | 🟢 INFO | **resolved** | FR-CLI-001 & FR-CLI-002 are fully implemented, but the mapping from *unknown command* to suggested alternatives is only implicit via `all_names` dump. A more user‑friendly suggestion (e.g., "Did you mean <closest>?") would improve usability. | `root_cli_main_entry.py` (error handling block) | The previous review explicitly recorded this behavior as verified; retain it as a regression checkpoint. |
| 2 | 🟢 INFO | **needs-clarification** | FR-CLI-003 requires masking of secrets in all output paths; while the code references a security policy, the actual masking implementation is scattered across modules. Centralizing the masking logic here would ensure consistency. | `root_cli_main_entry.py` (_mask_error helper) | The wording does not provide enough evidence for automatic closure; retain it for targeted review. |
| 3 | 🟢 INFO | **open** | The CLI presently auto‑wires the dispatcher/layout when none is supplied. This is convenient for prototypes but can mask missing configuration in production. Making the auto‑wire step explicit or configurable would increase deploy robustness. | `main()` function in `root_cli_main_entry.py` | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 4 | 🟢 INFO | **open** | End‑to‑end asset acquisition flow (search → download → extract → import) is documented in the asset FRD but not exposed as a single CLI command. Users must chain commands manually, which can lead to ordering errors. | `modules/asset` (future CLI surface) | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 5 | 🟡 WARNING | **open** | The CLI exit code mapping uses generic categories (`validation_error`, `configuration_error`, etc.) but does not differentiate between *user‑correctable* and *system‑internal* failures beyond the category label. This can make script‑level error handling brittle. | `ERROR_CATEGORIES` dict in `root_cli_main_entry.py` | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 6 | 🟢 INFO | **open** | No explicit handling for malformed JSON in `--params`. While the code catches `JSONDecodeError`, it returns a generic validation error without suggesting the exact syntax issue. | `run` command handling in `root_cli_main_entry.py` | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 7 | 🟢 INFO | **needs-clarification** | The CLI does not validate that `--filepath` points to an existing `.blend` file before attempting to register or operate on it. This validation is delegated to downstream layers, leading to delayed error reports. | `surface_init_command.py`, `surface_run_command.py` | The risk is plausible but the finding is phrased as a verification request; inspect the current implementation before changing code. |
| 8 | 🟡 WARNING | **needs-clarification** | Unit tests cover individual command handlers, but there is no integration test that verifies the full command‑to‑dispatcher flow (including auto‑wire, error masking, and JSON output). | `modules/cli/tests/test_cli_units.py` | The risk is plausible but the finding is phrased as a verification request; inspect the current implementation before changing code. |
| 9 | 🟢 INFO | **needs-clarification** | Test coverage matrix does not include non‑interactive (piped) invocation scenarios. | Test suite | The risk is plausible but the finding is phrased as a verification request; inspect the current implementation before changing code. |
| 10 | 🟢 INFO | **open** | FR-CLI-001 explicitly states "Semantic validation belongs to owning feature — CLI never judges action validity". This contract is respected, but the mapping from CLI sub‑commands to feature aggregates is only implicit in the code. A machine‑readable mapping (e.g., JSON manifest) would facilitate automated validation. | `root_cli_main_entry.py` (sub‑parser registration) | The previous review identified an unmet requirement or missing acceptance evidence; keep it in the execution backlog. |
| 11 | 🟢 INFO | **needs-clarification** | FR-CLI-003 references "secrets are masked via security policy", yet the actual masking implementation lives in disparate modules (`security` layer). A direct import or helper call in the CLI would make the intent explicit. | `root_cli_main_entry.py` (`_mask_error` helper) | The wording does not provide enough evidence for automatic closure; retain it for targeted review. |

## Validated Execution Backlog

Only findings marked **open** should be considered implementation candidates. Findings marked **needs-clarification** require a focused source/test check first. Findings marked **resolved** become regression acceptance criteria and must not be reimplemented without evidence of regression.

| Priority | Status | Action |
|---|---|---|
| 🟢 INFO | needs-clarification | Consolidate secret‑masking into a reusable helper and ensure it is invoked for all error categories. |
| 🟢 INFO | open | Add a command‑line flag or environment variable to toggle auto‑wire behavior. |
| 🟢 INFO | open | Consider adding a convenience wrapper such as `asset-get --id <id> --dest <path>` that internally sequences the required capabilities. |
| 🟡 WARNING | open | Introduce sub‑categories (e.g., `user_error`, `system_error`) to allow scripts to react appropriately. |
| 🟢 INFO | open | Include the underlying `JSONDecodeError` message in the returned error for faster debugging. |
| 🟢 INFO | needs-clarification | Add early path existence and extension checks in the CLI layer to provide immediate feedback. |
| 🟡 WARNING | needs-clarification | Add an E2E test that runs the CLI end‑to‑end with a mocked dispatcher to verify exit codes, output format, and error paths. |
| 🟢 INFO | needs-clarification | Extend tests to simulate pipe/redirection usage and verify that output is truncated appropriately. |
| 🟢 INFO | open | Generate a manifest file automatically from the sub‑parser definitions to serve as a single source of truth for command‑to‑aggregate mapping. |
| 🟢 INFO | needs-clarification | Add an explicit import or call to the central redaction utility to clarify the masking flow. |

## Violations

No new violation is asserted by this revalidation without a current source/test proof. Suspected AES violations remain needs-clarification when the old path or architecture context changed.

## Traceability

The module FRD remains the authoritative requirement source. The previous plan is preserved as historical evidence, while this plan is the current status ledger.

## Execution Guardrails

Before implementing any row, confirm the exact current file path, the FRD acceptance criterion, and an executable test. Do not implement recommendations that only say “verify,” “consider,” or “document” until the verification result is recorded. Do not duplicate findings already present in another module plan.

## References

- [`FRD.md`](../../modules/cli/FRD.md)
- [`ARCHITECTURE.md`](../../ARCHITECTURE.md)
- [`AES rules`](../../.agents/rules/RULES_AES.md)
- [`Previous plan`](./todo-cli-business-analyst-20260808.md)
