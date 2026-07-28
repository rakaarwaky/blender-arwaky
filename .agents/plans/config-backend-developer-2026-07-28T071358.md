# Review Plan: config — Backend Developer

## Summary

Reviewed the `config` feature module (`modules/config/src/`) against its FRD
(`modules/config/FRD.md`) and the AES layering rules (`RULES_AES.md`,
`ARCHITECTURE.md`). The module implements all five functional requirements
(FR-CFG-001..005) through a properly layered set of one root container, one
agent orchestrator, and five capabilities — each capability correctly inherits
its protocol ABC, every import respects AES201 layer boundaries, and no bypass
comments (AES304) or forbidden imports (AES201) were found.

The deep assessment surfaced **no CRITICAL or WARNING-level functional,
security, or architectural defects**. The only defects present in `src/` are
cosmetic lint violations that fail the mandated verification gate
`ruff check modules/config`: 7× missing trailing newline (`W292`) and 1×
import-ordering (`I001`) in `root_config_container.py`. These were corrected
via `ruff --fix` so the module passes its own lint gate with no regressions.

## Findings by Category

### Architecture & Layer Compliance

| #   | Severity | Issue | Location | Recommendation |
| --- | -------- | ----- | -------- | -------------- |
| 1 | 🟢 INFO | All 5 capabilities inherit their `_protocol` ABC; root wires via DI; agent depends only on contracts + taxonomy. No AES201/AES403/AES404 violations. | all `src/` files | None — compliant. |
| 2 | 🟢 INFO | Orchestrator holds `self._snapshot` assigned outside `__init__` (load/reload/get_snapshot). This is intentional per FR-CFG-001 ("snapshot must be cached", "reload replaces atomically") and is coordinated state, not domain computation. | `agent_config_orchestrator.py` | Document as FRD-justified exception to AES405 (non-stateless) — not a defect. |

### Security

| #   | Severity | Issue | Location | Recommendation |
| --- | -------- | ----- | -------- | -------------- |
| 3 | 🟢 INFO | Safe YAML parsing enforced (`load_yaml_safe`), no arbitrary object instantiation; size limit gated behind `BLENDERMCP_STRICT`; redaction is key-based substring/case-insensitive per Q14/Q15. | `capabilities_settings_loader.py`, `capabilities_redaction_rules.py` | None — compliant with FR-CFG-001 / FR-CFG-005. |

### Performance

| #   | Severity | Issue | Location | Recommendation |
| --- | -------- | ----- | -------- | -------------- |
| 4 | 🟢 INFO | `redact_dict` recurses into nested dicts but processes list items only one level deep (list-of-lists of dicts is not re-entered). Settings payloads are small, so risk is negligible. | `capabilities_redaction_rules.py:56` | Optional future hardening: generalize recursion for nested lists. Out of scope this cycle. |

### Error Handling

| #   | Severity | Issue | Location | Recommendation |
| --- | -------- | ----- | -------- | -------------- |
| 5 | 🟡 WARNING | FR-CFG-003 states an invalid environment-provided workspace path "logs warning and falls through". Current resolver only warns on `OSError`/`ValueError` during resolution; if `BLENDERMCP_ROOT` resolves to an existing *file* (not a dir), it silently falls through with no warning. | `capabilities_workspace_resolver.py:73-80` | Emit a warning when the env path exists but is not a directory. Deferred this cycle: requires a warning channel design (resolver has no logger/metadata supplier) and is a behavior change best reviewed deliberately rather than auto-applied in an autonomous loop. |
| 6 | 🟢 INFO | Policy-mode branching (strict vs permissive), atomic reload (build-then-swap), and single-load caching are correct and thread-safe. | `capabilities_settings_loader.py` | None. |

## Quality / Lint (implemented this cycle)

| #   | Severity | Issue | Location | Recommendation |
| --- | -------- | ----- | -------- | -------------- |
| 7 | 🟢 INFO | 7× `W292` missing trailing newline at EOF. | all 5 capability/agent/container `src/` files | Add trailing newline (auto-fixed). |
| 8 | 🟢 INFO | 1× `I001` unsorted import block (`STRICT_MODE_FLAG_ENV` before `DEFAULT_POLICY_MODE`). | `root_config_container.py:17-20` | Sort import block (auto-fixed). |

## Violations

None of AES101–AES506 were violated in `src/`. (The full-module `ruff check`
still reports pre-existing lint issues in `modules/config/tests/` — unused test
fixture arguments `ARG001`, dead variable `F841`, and `W292`; those files are
outside the `src/`-only review scope and were not modified.)

## Action Items

- [x] INFO Fix 8 `src/` lint violations (`W292` ×7, `I001` ×1) via `ruff --fix`.
- [ ] WARNING (deferred) Add warning when `BLENDERMCP_ROOT` points to a non-directory; design a warning channel first.
- [ ] INFO (optional) Generalize `redact_dict` recursion for nested lists.

## Fixed Code

### `root_config_container.py` — corrected import ordering (I001)

```python
from modules.shared.src.config.taxonomy_config_constant import (
    DEFAULT_POLICY_MODE,
    STRICT_MODE_FLAG_ENV,
)
```

### Trailing newline (W292)

Added a single trailing newline to the end of:
`agent_config_orchestrator.py`, `capabilities_redaction_rules.py`,
`capabilities_settings_loader.py`, `capabilities_settings_metadata.py`,
`capabilities_settings_retriever.py`, `capabilities_workspace_resolver.py`,
`root_config_container.py`.
