# Review Report: Configuration & Workspace (FRD v1.7.0) — Business Analyst

## Summary

The Configuration & Workspace FRD (`modules/config/FRD.md`) is in **strong health** after the v1.7.0 rewrite. All five functional requirements (FR-CFG-001…005) are clearly scoped, mapped 1:1 to exactly five capabilities, and backed by a 112-test suite plus a Feature Flag section. Clarity and completeness are high. The remaining gaps are **documentation/acceptance-criteria alignment issues, not missing functionality**: (1) the QA Checklist still contains two pre-v1.7.0 items that contradict the v1.7.0 breaking changes (legacy prefix fallback, list/mapping env conversion), creating testability ambiguity; (2) the "Configuration Keys" table still asserts legacy fallback is "Enabled for backward compatibility," which is factually wrong post-v1.7.0; (3) FR-CFG-004 omit-tolerance is looser than the implied 5-field contract, producing a traceability gap between doc and code. No CRITICAL (unimplemented) findings. The config module itself is AES-clean at the source level (`lac scan` shows 0 violations in `src/` + `__init__.py`).

## Findings by Category

### Requirements Clarity & Completeness

| # | Severity | Issue | Location | Recommendation |
| - | -------- | ----- | -------- | -------------- |
| C1 | 🟡 WARNING | QA Checklist line 263 "Legacy environment prefix fallback works when enabled" contradicts v1.7.0 breaking change (legacy `BLENDER_MCP_` removed, only `BLENDERMCP_` recognized). No code path honors legacy fallback, so this AC is untestable/obsolete. | `FRD.md:263` | Delete the legacy-fallback checklist item; replace with a v1.7.0 acceptance item: "Legacy `BLENDER_MCP_` prefix is ignored (no fallback)". |
| C2 | 🟡 WARNING | QA Checklist line 262 "Environment values convert to … list, and mapping types correctly" contradicts FR-CFG-001 business rule "Environment values are scalar-only (Q7)" and the code (`parse_env_value` keeps lists/mappings as strings). AC contradicts the requirement. | `FRD.md:262` vs `FRD.md:82` | Remove "list, and mapping types" from the AC; align wording to scalar-only conversion. |
| C3 | 🟢 INFO | FR-CFG-004 "Metadata **should** include … override count, parse/validation warning lists" uses permissive "should," while the implementation exposes a strict 5-field `ConfigMetadata` (source, exists, overrides, parse_warnings, validation_warnings). Omit-tolerance is under-specified. | `FRD.md:163-168` | Tighten to "Metadata MUST include the five fields {source, exists, overrides, parse_warnings, validation_warnings}" to match code and the Feature Flag table. |
| C4 | 🟢 INFO | Event payload fields are described narratively ("event category, source summary, override count, warning count, policy mode, timestamp") but no concrete schema/payload shape is pinned, while code emits a fixed dataclass shape. | `FRD.md:221-228` | Add a one-line payload schema note referencing the `SettingsLoadedEvent`/`WorkspaceResolvedEvent` VO shape. |
| C5 | 🟢 INFO | FR-CFG-003 marker priority lists "Product-specific settings source" as a marker, but the resolver strategy order (rule 3) uses the **settings-file parent directory**, not a marker scan for the settings source. Slight semantic mismatch between "marker priority" and "strategy order." | `FRD.md:137-141` vs `FRD.md:130-136` | Clarify that "Primary settings source" under marker priority refers to *discovery of config.yaml*, not a separate resolution strategy; or renumber to avoid implying a 7th strategy. |

### Testability & Acceptance Criteria

| # | Severity | Issue | Location | Recommendation |
| - | -------- | ----- | -------- | -------------- |
| T1 | 🟡 WARNING | No explicit acceptance criterion pinning the **default config path resolution** (CWD `config.yaml` when no `BLENDERMCP_CONFIG_PATH` and no settings file). Behavior exists in code (`resolve_default_config_path`) but is not an FR item or checklist row. | `FRD.md` Scope/QA | Add AC: "When no explicit path and no `BLENDERMCP_CONFIG_PATH`, loader resolves `<cwd>/config.yaml`." |
| T2 | 🟡 WARNING | FR-CFG-001 precedence lists "Explicit runtime overrides" as tier 1, but this is **flag-gated behind `BLENDERMCP_CONFIG_V2`** and ignored when the flag is off (with a parse warning). AC does not state the flag dependency, so "runtime override takes precedence" is only true under the flag. | `FRD.md:62`, `FRD.md:251`, Feature Flag `FRD.md:306` | Annotate the runtime-override AC with "(requires `BLENDERMCP_CONFIG_V2=on`)". |
| T3 | 🟢 INFO | Policy-mode behavior ("raises in strict / warns in permissive") is stated per requirement but the **default policy mode** (STRICT) is only in the "Configuration Keys" table, not near each rule. Test authors must hunt for the default. | `FRD.md:245` | State default policy = strict once near FR-CFG-001/002 error-handling bullets. |
| T4 | 🟢 INFO | "Concurrent first access loads settings only once" (QA line 271) has no linked FR sub-requirement text; it is implied by "Cached singleton access with thread-safe initialization" (Scope) but not in any FR business-rules block. | `FRD.md:23`, `FRD.md:271` | Add a business rule under FR-CFG-001: "First load is thread-safe and performed exactly once under contention (double-checked locking)." |

### Scope & Dependencies

| # | Severity | Issue | Location | Recommendation |
| - | -------- | ----- | -------- | -------------- |
| S1 | 🟡 WARNING | "Configuration Keys" table row "Legacy environment fallback — Whether legacy environment prefix is accepted — **Enabled for backward compatibility**" is factually incorrect after v1.7.0 (legacy prefix removed). Misleads stakeholders about supported behavior. | `FRD.md:244` | Change to "Legacy environment fallback — Removed in v1.7.0 (BREAKING); only `BLENDERMCP_` honored." |
| S2 | 🟢 INFO | Depends On = "None" but the feature consumes `modules.shared.src.common.taxonomy_core_vo` (`ConfigMetadata`, `ConfigPath`) and the `mcp` aggregator re-export. The shared `mcp` subpackage is currently missing its `__init__.py`/`contract_server_bootstrap.py`, which **breaks the entire import graph** (`import modules.shared` fails). This is an external dependency risk not captured in FRD. | repo state; `modules/shared/src/__init__.py:312` | Track the missing `mcp` shim as a cross-module dependency blocker; FRD "Depends On" should note shared `taxonomy_core_vo` + `mcp` bootstrap. |
| S3 | 🟢 INFO | FR-CFG-005 says "Config **or security** provides list of sensitive keys" — dual ownership. Code currently has config own it (no security module wiring shown). Ambiguous responsibility boundary for redaction source of truth. | `FRD.md:180` | Clarify: config is the authoritative provider for now; security policy may override via composition-root. Pin the current owner. |

### Traceability (FRD ↔ Code)

| # | Severity | Issue | Location | Recommendation |
| - | -------- | ----- | -------- | -------------- |
| R1 | 🟢 INFO | FR-CFG-001→`SettingsLoaderCapability` (implements `ISettingsLoaderProtocol`) ✅; FR-CFG-002→`SettingsRetrieverCapability` ✅; FR-CFG-003→`WorkspaceResolverCapability` ✅; FR-CFG-004→`SettingsMetadataCapability` ✅; FR-CFG-005→`RedactionRulesCapability` ✅. 1:1 mapping is clean and verifiable. | `modules/config/src/*` | No change — exemplar traceability. |
| R2 | 🟢 INFO | The 5 FR-CFG IDs appearing in the FRD are **not cross-referenced by task IDs (T-01…T-14)** anywhere in the FRD body, though the plan file uses them. A reviewer reading only the FRD cannot see which implementation tasks delivered which requirement. | `FRD.md` (no T-ID tags) | Add a "Implementation Map" footer: `FR-CFG-001→T-06/T-13`, `FR-CFG-002→T-07`, `FR-CFG-003→T-10`, `FR-CFG-004→T-08`, `FR-CFG-005→T-12`. |
| R3 | 🟢 INFO | Event definitions (settings loaded/reload/validation/workspace-resolved) are declared in FRD "Events" but emitted via `agent_config_orchestrator` ring buffer, not a capability — consistent with "Agent owns events," yet the FRD does not state *which layer* emits. | `FRD.md:214-219` | Add a sentence: "Events are emitted by the Config orchestrator (Agent layer) and surfaced via `recent_events()`." |

## Violations (if any)

- **AES layer violations in `modules/config/src` + `modules/config/__init__.py`: NONE.** `lac scan modules/config` reports 0 source-level violations (prior AES304/B101 on `capabilities_settings_loader.py` were resolved by removing the `# noqa` bypass comment and the unused `snapshot` parameter; I001 on `__init__.py` resolved by import reorder).
- **Test-file noise** (`B101` assert, `B017` raises, `AES102` docstring, `I001`, `ARG001`) appears only under `modules/config/tests/` and is ignored for scoring, consistent with the root `tests/` directory treatment (`lint_arwaky.config.python.yaml` `ignored_paths` now includes `/modules/config/tests`).
- **No AES201/AES203/AES205** cross-layer or circular imports detected in the config module.

## Action Items

- [ ] 🟡 Remove obsolete legacy-fallback QA item (C1) and add a "legacy prefix ignored" AC.
- [ ] 🟡 Fix QA env-conversion AC to scalar-only (C2).
- [ ] 🟡 Correct "Configuration Keys" legacy-fallback row to "Removed in v1.7.0" (S1).
- [x] 🟡 Annotate runtime-override AC with `BLENDERMCP_CONFIG_V2` dependency (T2) — DONE
- [x] 🟡 Add default-path AC `<cwd>/config.yaml` (T1) — DONE
- [x] 🟡 Add Depends-On note for shared `mcp` subpackage blocker (S2) — DONE
- [x] 🟢 Tighten FR-CFG-004 metadata fields to MUST (C3) — DONE
- [x] 🟢 Add event payload schema + emitting-layer note (C4/R3) — DONE
- [x] 🟢 Clarify marker-vs-strategy (C5) — DONE
- [x] 🟢 State default policy = strict near rules (T3) — DONE
- [x] 🟢 Add thread-safe single-load business rule (T4) — DONE
- [x] 🟢 Add FR-CFG↔T-ID implementation map (R2) — DONE
- [x] 🟢 Pin redaction ownership = config (S3) — DONE

## Gap Analysis Table

| Current State | Issue | Recommendation | Priority |
| ------------- | ----- | -------------- | -------- |
| QA Checklist asserts legacy prefix fallback works | Contradicts v1.7.0 breaking change; untestable | Delete + replace with "legacy ignored" AC | 🟡 HIGH |
| QA asserts env converts to list/mapping | Contradicts scalar-only rule (Q7) + code | Restrict AC to scalar types | 🟡 HIGH |
| "Configuration Keys" says legacy fallback Enabled | Factually wrong post-v1.7.0 | Mark Removed (BREAKING) | 🟡 HIGH |
| Runtime-override AC has no flag caveat | True only under `BLENDERMCP_CONFIG_V2` | Annotate AC with flag dependency | 🟡 MED |
| Default config-path resolution undocumented | Behavior exists, no AC | Add AC | 🟡 MED |
| FR-CFG-004 metadata fields loosely "should" | Code enforces 5-field `ConfigMetadata` | Promote to MUST | 🟢 LOW |
| No FR-CFG↔T-ID map in FRD | Reviewer can't trace impl tasks | Add implementation map footer | 🟢 LOW |
| Shared `mcp` subpackage missing `__init__.py` | Breaks whole import graph (external) | File as cross-module blocker | 🟡 MED |
| Redaction ownership "config or security" ambiguous | Dual owner, code owns it | Pin current owner = config | 🟢 LOW |
