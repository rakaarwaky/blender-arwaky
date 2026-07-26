# Review Report: config module — Business Analyst

## Summary

The `modules/config` feature is in **healthy, production-grade shape**. It implements all five
functional requirements (FR-CFG-001..005) with a clean AES 7-layer split (Agent orchestrator → 5
Capabilities → Contract aggregate + 5 protocols → Utility helpers → Taxonomy VO/constant/error/event).
FRD→code traceability is strong: every FR has a dedicated capability, the FRD's Q-annotations (Q3, Q4,
Q6, Q7, Q8, Q14, Q15, Q19, A5) are all reflected in code and backed by regression tests. The full
module test suite passes (**112 passed**), and no AES layer/import violations were found in the
module's own `src/`.

Findings are **minor/process** in nature — mostly requirement-clarity and version-consistency gaps
rather than missing or broken behavior. No 🔴 CRITICAL defects. The most material item is a
**version mismatch**: the FRD documents a v1.7.0 breaking change (legacy `BLENDER_MCP_` prefix
removal) but the module's `pyproject.toml` still declares `version = "1.6.5"`, which contradicts the
repo CHANGELOG that already cut `1.7.0`.

## Findings by Category

### Requirements Clarity & Completeness

| #   | Severity | Issue | Location | Recommendation |
| --- | -------- | ----- | -------- | -------------- |
| C1  | 🟡 WARNING | FRD `Configuration Keys` table and QA checklist line 267 state env values convert to "boolean, integer, float, null, **list, and mapping** types", but FR-CFG-001 business rule (Q7) and `parse_env_value` explicitly say env values are **scalar-only** and lists/mappings stay strings. The two statements contradict each other. | `FRD.md:267` vs `FRD.md:85` + `utility_config_helpers.py:25` | Remove "list, and mapping" from the QA checklist / Configuration Keys phrasing; keep Q7 (scalar-only) as authoritative. Aligns doc with implemented behavior. |
| C2  | 🟡 WARNING | FRD version context is inconsistent: it cites "v1.7.0 (BREAKING)" for legacy prefix removal, yet the module manifest says `1.6.5` while the repo `CHANGELOG.md` already has a `[1.7.0]` section. Readers cannot tell which release shipped the breaking change. | `modules/config/pyproject.toml:3` vs `FRD.md:87,248,268` vs `CHANGELOG.md:7` | Bump `modules/config/pyproject.toml` to `1.7.0` (or clarify that FRD version refs are forward-looking) so the breaking-change provenance is unambiguous. |
| C3  | 🟢 INFO | FR-CFG-005 "Out of Scope" (line 39) says enforcement of redaction belongs to consuming features, but none of the consuming modules (gateway/asset/render/etc.) are in this repo to inspect. The FRD's redaction traceability claim ("masking in diagnostics, CLI, MCP") cannot be verified from within `modules/config`. | `FRD.md:39,294-297`; consumers not present in tree | Document (or link) where consumers wire `get_redaction_rule()`/`redact_dict()`, or add an integration test that asserts a consumer applies the rule. Out of scope for this module but a gap in end-to-end FRD verification. |

### Testability & Acceptance Criteria

| #   | Severity | Issue | Location | Recommendation |
| --- | -------- | 🟢 INFO | No explicit acceptance-criteria blocks exist per FR; QA checklist (lines 253-301) is the de-facto acceptance list but is a flat 49-item bullet list, not mapped to FR IDs in the checklist text. Traceability from QA item → FR is by reader inference. | `FRD.md:253-301` | Add an `FR` tag to each QA checklist item (e.g. `- [ ] (FR-CFG-001) Settings load from file…`) so coverage is auditable. (Tests already cover these; this is doc hygiene.) |
| T2  | 🟢 INFO | `ConfigMetadata` `overrides` field semantics: QA checklist line 286 says "Legacy BLENDERMCP_* environment variables are ignored (Q8)" — covered. But the field is an `OverrideCount` that counts **env** overrides only; runtime overrides (A5, caller-scoped) are intentionally not counted. This nuance is not stated in FR-CFG-004's metadata field definitions. | `FRD.md:166-171` + `capabilities_settings_loader.py:262` | Add one line to FR-CFG-004 clarifying `overrides` = count of applied *environment* overrides, excluding caller-scoped runtime overrides. Prevents stakeholder confusion. |

### Scope & Dependencies

| #   | Severity | Issue | Location | Recommendation |
| --- | -------- | 🟢 INFO | FRD `Depends On` names `shared taxonomy primitives` and the `mcp bootstrap aggregator`, but the config module reaches into `modules.shared.src.common.taxonomy_core_vo` (ConfigMetadata, ConfigPath, etc.) and `modules.shared.src.config.*`. The dependency is satisfied, but the FRD does not list the full set of shared symbols relied upon (OverrideCount, ParseWarning, ValidationWarning, SourceLocation, Timestamp, ErrorString, WorkspacePath, SettingsSnapshot, RedactionRule). | `FRD.md:43` vs `capabilities_*.py` imports | Enumerate the shared VO/constant/error/event symbols the feature consumes, or reference the shared `config` taxonomy module as the dependency. Improves impact analysis on shared-layer changes. |
| S2  | 🟢 INFO | Module has no service-level `README`/`PRD.md` of its own; consumers rely on the aggregated `PRD.md` at repo root. Acceptable for a single-feature module, but a one-page module README would speed onboarding. | `modules/config/` (no README) | Optional: add `modules/config/README.md` summarizing the 5 capabilities and the strict/permissive + `BLENDERMCP_STRICT` gating model. |

### Traceability (FRD ↔ Code)

| #   | Severity | Issue | Location | Recommendation |
| --- | -------- | 🟢 INFO | All 5 FRs map 1:1 to a capability and a protocol. `ConfigOrchestrator` implements `IConfigAggregate` and wires all 5 via `ConfigContainer`. Events (T-09) covered. Traceability is **complete and verified by tests** (`test_layer_imports.py`, `test_settings_loader.py:201` legacy, `:223` Q19 32-thread single-load). | whole module | No action — recorded as a positive traceability confirmation. |
| R2  | 🟢 INFO | FR-CFG-003 marker priority: FRD states manifest markers (`pyproject.toml`) precede VCS (`.git`). `PROJECT_MARKERS` tuple order confirms this (`taxonomy_config_constant.py:51-59`), and `test_project_markers_order_manifest_before_vcs` asserts it. Verified. | `FRD.md:139-143` | No action. |

## Violations (if any)

Ran a targeted AES scan over `modules/config/src` and the module's `tests`:

- **AES304 (Bypass Comment)** — two hits, both **legitimate**:
  - `tests/test_constants.py:32` `# noqa: F401` inside a `pytest.raises(ImportError)` block that *proves* the legacy symbol was removed. Intentional negative test.
  - `tests/test_constants.py:66` `# type: ignore[misc]` on a deliberate `FrozenInstanceError` trigger. Intentional.
  - No `#[allow]`, `unwrap()`, `expect()`, `panic!`, or live `noqa`/`type: ignore` in `src/` (AES304 CRITICAL clean).
- **AES201 (Forbidden Import)** — clean. Capabilities import only `taxonomy_*`, `contract_*`, and `utility_config_helpers`. Agent imports only `contract_*`, `taxonomy_*`, and shared core VO. No capability→capability or agent→capability imports (enforced by `test_layer_imports.py`).
- **AES301/302 (File size)** — all files well under 1000 lines; no empty files.
- **AES403/404/405** — every capability implements its protocol; utilities are stateless functions; agent is orchestration-only (zero I/O, zero business logic, zero domain computation — confirmed by docstrings and body).
- No AES orphan violations detected within the module.

**Conclusion: zero AES violations in the module.**

## Action Items

- [x] 🟡 C1 — Fix env type-conversion contradiction in FRD (drop "list, and mapping" from QA/Config-Keys; Q7 scalar-only is authoritative). **DONE** (FRD.md QA checklist + Configuration Keys).
- [x] 🟡 C2 — Reconcile version: bump `modules/config/pyproject.toml` to `1.7.0` to match repo CHANGELOG/root pyproject. **DONE**.
- [x] 🟢 C3 — Add consumer-side redaction wiring evidence to FR-CFG-005 (get_redaction_rule()/redact_dict() via aggregate + composition-root extension). **DONE**.
- [x] 🟢 T1 — Tag each QA-checklist item with its FR id for auditable coverage. **DONE** (checklist regrouped under FR-CFG-001..005 + Cross-cutting).
- [x] 🟢 T2 — Clarify `overrides` = env-override count only (excludes caller-scoped runtime overrides) in FR-CFG-004. **DONE**.
- [x] 🟢 S1 — Enumerate shared `config` taxonomy symbols consumed, or reference the shared module as the dependency. **DONE** (FRD Depends On expanded).
- [x] 🟢 S2 — Add `modules/config/README.md` for onboarding. **DONE**.
- [x] 🟢 BONUS — Normalize stale `BLENDERMCP_CONFIG_V2` → `BLENDERMCP_STRICT` across CHANGELOG.md, README.md, and `.agents/finding/*.md` (code already used STRICT). **DONE** (zero stale tokens repo-wide).

## Gap Analysis Table

| Current State | Issue | Recommendation | Priority |
| ------------- | ----- | -------------- | -------- |
| FRD says env converts to list/mapping; code enforces scalar-only (Q7) | Self-contradicting requirement text | Edit FRD to make Q7 authoritative; remove list/mapping claim | 🟡 MED |
| Module version 1.6.5 but FRD/CHANGELOG reference 1.7.0 breaking change | Version provenance ambiguity | Align `pyproject.toml` version with CHANGELOG | 🟡 MED |
| Redaction enforcement lives in external consumers not in this repo | Cannot verify FR-CFG-005 end-to-end from config module | Add consumer wiring doc/integration test | 🟢 LOW |
| QA checklist not mapped to FR ids | Coverage not auditable at a glance | Tag checklist items with FR ids | 🟢 LOW |
| `overrides` metadata field semantics undocumented (env-only) | Possible stakeholder misinterpretation | One-line clarification in FR-CFG-004 | 🟢 LOW |
| Shared dependency listed loosely as "shared taxonomy primitives" | Weak impact analysis on shared changes | Enumerate consumed shared symbols | 🟢 LOW |

---
*Verification performed: `uv run pytest modules/config/tests -q` → 112 passed. AES layer/import/bypass scan over `modules/config/src` and `tests` → no violations. FRD re-read against `capabilities_*.py`, `agent_config_orchestrator.py`, `root_config_container.py`, and shared `contract_*` / `taxonomy_config_*` / `utility_config_helpers.py`.*
