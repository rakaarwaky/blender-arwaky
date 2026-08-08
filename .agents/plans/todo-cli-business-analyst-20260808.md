# Plan: CLI Surface — Business Analyst

## Summary
A concise business analyst review of the CLI surface module, focusing on FRD compliance, requirements clarity, business flow, logic implementation, testability, and traceability. The analysis identifies minor gaps in error handling, edge‑case documentation, and end‑to‑end test coverage, and proposes concrete action items to close those gaps.

## Findings

### Requirements Clarity
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | FR-CLI-001 & FR-CLI-002 are fully implemented, but the mapping from *unknown command* to suggested alternatives is only implicit via `all_names` dump. A more user‑friendly suggestion (e.g., “Did you mean <closest>?”) would improve usability. | `root_cli_main_entry.py` (error handling block) | Add a deterministic “closest match” algorithm or a lookup table to provide explicit suggestions. |
| 2 | 🟢 INFO | FR-CLI-003 requires masking of secrets in all output paths; while the code references a security policy, the actual masking implementation is scattered across modules. Centralizing the masking logic here would ensure consistency. | `root_cli_main_entry.py` (_mask_error helper) | Consolidate secret‑masking into a reusable helper and ensure it is invoked for all error categories. |
| 3 | 🟢 INFO | The CLI presently auto‑wires the dispatcher/layout when none is supplied. This is convenient for prototypes but can mask missing configuration in production. Making the auto‑wire step explicit or configurable would increase deploy robustness. | `main()` function in `root_cli_main_entry.py` | Add a command‑line flag or environment variable to toggle auto‑wire behavior. |

### Business Flow
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | End‑to‑end asset acquisition flow (search → download → extract → import) is documented in the asset FRD but not exposed as a single CLI command. Users must chain commands manually, which can lead to ordering errors. | `modules/asset` (future CLI surface) | Consider adding a convenience wrapper such as `asset-get --id <id> --dest <path>` that internally sequences the required capabilities. |
| 2 | 🟡 WARNING | The CLI exit code mapping uses generic categories (`validation_error`, `configuration_error`, etc.) but does not differentiate between *user‑correctable* and *system‑internal* failures beyond the category label. This can make script‑level error handling brittle. | `ERROR_CATEGORIES` dict in `root_cli_main_entry.py` | Introduce sub‑categories (e.g., `user_error`, `system_error`) to allow scripts to react appropriately. |

### Logic Implementation
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | No explicit handling for malformed JSON in `--params`. While the code catches `JSONDecodeError`, it returns a generic validation error without suggesting the exact syntax issue. | `run` command handling in `root_cli_main_entry.py` | Include the underlying `JSONDecodeError` message in the returned error for faster debugging. |
| 2 | 🟢 INFO | The CLI does not validate that `--filepath` points to an existing `.blend` file before attempting to register or operate on it. This validation is delegated to downstream layers, leading to delayed error reports. | `surface_init_command.py`, `surface_run_command.py` | Add early path existence and extension checks in the CLI layer to provide immediate feedback. |

### Testability & Acceptance
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟡 WARNING | Unit tests cover individual command handlers, but there is no integration test that verifies the full command‑to‑dispatcher flow (including auto‑wire, error masking, and JSON output). | `modules/cli/tests/test_cli_units.py` | Add an E2E test that runs the CLI end‑to‑end with a mocked dispatcher to verify exit codes, output format, and error paths. |
| 2 | 🟢 INFO | Test coverage matrix does not include non‑interactive (piped) invocation scenarios. | Test suite | Extend tests to simulate pipe/redirection usage and verify that output is truncated appropriately. |

### Traceability (FRD→Code)
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | FR-CLI-001 explicitly states “Semantic validation belongs to owning feature — CLI never judges action validity”. This contract is respected, but the mapping from CLI sub‑commands to feature aggregates is only implicit in the code. A machine‑readable mapping (e.g., JSON manifest) would facilitate automated validation. | `root_cli_main_entry.py` (sub‑parser registration) | Generate a manifest file automatically from the sub‑parser definitions to serve as a single source of truth for command‑to‑aggregate mapping. |
| 2 | 🟢 INFO | FR-CLI-003 references “secrets are masked via security policy”, yet the actual masking implementation lives in disparate modules (`security` layer). A direct import or helper call in the CLI would make the intent explicit. | `root_cli_main_entry.py` (`_mask_error` helper) | Add an explicit import or call to the central redaction utility to clarify the masking flow. |

## Violations
- **None** found that constitute 🔴 CRITICAL or 🟡 WARNING severity impacting core functionality. All identified items are 🟢 INFO suggestions or minor improvements.

## Action Items
- [ ] 🟢 INFO Implement a deterministic “closest match” suggestion for unknown commands (e.g., using difflib or a static mapping).  
- [ ] 🟢 INFO Centralize secret‑masking logic in the CLI error‑handling helper and verify it covers all error categories.  
- [ ] 🟢 INFO Add a CLI flag (`--no-auto-wire`) to disable automatic dispatcher initialization for production scenarios.  
- [ ] 🟡 WARNING Introduce sub‑categories for exit codes (`user_error`, `system_error`) to improve script robustness.  
- [ ] 🟢 INFO Add early file‑existence validation for `--filepath` arguments in relevant commands.  
- [ ] 🟡 WARNING Add an integration test covering the full CLI flow (auto‑wire, error handling, JSON output).  
- [ ] 🟢 INFO Generate a manifest file that maps CLI sub‑commands to their owning feature aggregates.  

## Fixed Code
None required for this analytical review. The suggestions above aim to enhance clarity, consistency, and testability without altering existing functional behavior.