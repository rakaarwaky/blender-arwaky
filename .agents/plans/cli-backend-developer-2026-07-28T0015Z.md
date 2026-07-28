# Review Plan: cli — Backend Developer

## Summary

The `modules/cli` module is in a mid-migration, internally inconsistent state. It
contains two competing designs:

1. A **FRD-aligned** design (`capabilities_cli_error.py`, `capabilities_cli_render.py`,
   `capabilities_cli_command_router.py`, `capabilities_cli_lifecycle.py`,
   `agent_orchestrator.py`, `root_cli_container.py`, `surface_cli_command.py`) that is
   intended to be a thin surface routing to owning-feature aggregates.
2. A **legacy monolith** (`surface_cli_main.py`, `surface_cli_commands.py`,
   `surface_cli_registry.py`, `surface_cli_socket_client.py`,
   `surface_cli_blender_manager.py`) that hard-codes process lifecycle, socket
   connection, and a state registry — all explicitly **Out of Scope** in `FRD.md`.

**The headline finding is CRITICAL:** the FRD-aligned code imports
`modules.shared.src.cli.*` and `modules.shared.src.common.*`, which **do not exist
anywhere in the repository** (verified by repo-wide search). The entire intended CLI
implementation is therefore dead/non-importable. Only the stdlib-only legacy helpers
are import-safe.

Backend health: importable subset is clean after this cycle's lint fixes and gains a
pytest baseline; the FRD-justified surface design cannot be exercised until the shared
contract/dependency layer is supplied (cross-module, out of this module's scope).

## Findings by Category

### Architecture & Layer Compliance

| #   | Severity | Issue | Location | Recommendation |
| --- | -------- | ----- | -------- | -------------- |
| A1  | 🔴 CRITICAL | FRD-aligned code imports `modules.shared.src.cli.*` / `modules.shared.src.common.*`, which do not exist → entire intended CLI is dead code (AES503/506 orphan) | `capabilities_cli_*.py`, `agent_orchestrator.py`, `root_cli_container.py`, `surface_cli_command.py` | Implement the shared contract/taxonomy layer (cross-module; tracked by loop). Until then, FRD-001/002/003 cannot run. |
| A2  | 🟡 WARNING | Legacy monolith implements process lifecycle, socket connection, and state registry — all Out of Scope per CLI FRD (owned by launcher/gateway/security features) | `surface_cli_main.py`, `surface_cli_commands.py`, `surface_cli_registry.py`, `surface_cli_socket_client.py`, `surface_cli_blender_manager.py` | Deprecate/remove once FRD-aligned wiring exists. Do not extend. |
| A3  | 🟡 WARNING | AES102 naming: `agent_orchestrator.py` has only 2 words (`agent`+`orchestrator`); AES101 requires ≥3 | `agent_orchestrator.py` | Rename to `agent_cli_orchestrator.py` (coordinate with importers). |
| A4  | 🟡 WARNING | AES102 naming: surface suffix violations — `_main` (no entry exception for surfaces), `_socket_client` (`_client` is a capabilities suffix, forbidden for surfaces), `_manager`, `_registry`, `_commands` (plural not allowed) | `surface_cli_main.py`, `surface_cli_socket_client.py`, `surface_cli_blender_manager.py`, `surface_cli_registry.py`, `surface_cli_commands.py` | Rename to allowed surface suffixes (`_command`/`_controller`/…) once design is settled. |
| A5  | 🟡 WARNING | AES102 naming: `capabilities_cli_error.py` uses forbidden capabilities suffix `_error` (flexible policy forbids `_error`) | `capabilities_cli_error.py` | Rename to e.g. `capabilities_cli_error_reporter.py` / `_formatter`. |
| A6  | 🟢 INFO | Two competing surface entry points (`surface_cli_command.py` generic dispatcher vs `surface_cli_commands.py` commands) — design duplication smell (AES305) | `surface_cli_command.py`, `surface_cli_commands.py` | Converge on a single FRD-aligned entry once shared layer exists. |

### Security

| #   | Severity | Issue | Location | Recommendation |
| --- | -------- | ----- | -------- | -------------- |
| S1  | 🔴 CRITICAL | `capabilities_cli_error.py` claims "Secrets are masked" but performs **no masking**; `capabilities_cli_render.py` emits `result` verbatim via `json.dumps`. FR-CLI-002/003 require masking in both text and JSON; masking failure must suppress the value. Raw `str(e)` can leak paths/secrets. | `capabilities_cli_error.py`, `capabilities_cli_render.py`, `surface_cli_main.py` | Add a local fallback redactor applied to message/detail/result before any render path (FRD: "Always enabled, not user-disableable for secrets"); delegate to security-policy feature when wired. |
| S2  | 🟡 WARNING | Legacy `surface_cli_main.py` surfaces raw `str(e)` on error/JSON path | `surface_cli_main.py` | Covered by S1 remediation. |

### Performance

| #   | Severity | Issue | Location | Recommendation |
| --- | -------- | ----- | -------- | -------------- |
| P1  | 🟢 INFO | `find_blender` spawns `which blender` subprocess every launch; `_wait_for_addon` opens a socket per poll iteration | `surface_cli_blender_manager.py` | Cache resolved Blender path; add jitter/backoff to poll loop. Low priority. |

### Error Handling

| #   | Severity | Issue | Location | Recommendation |
| --- | -------- | ----- | -------- | -------------- |
| E1  | 🟡 WARNING | `capabilities_cli_command_router.py` does `from .container import get_container`, but the file is `root_cli_container.py` and exposes `CliContainer`/`create_cli_feature` (no `get_container`) → runtime `ImportError`/crash | `capabilities_cli_command_router.py:139` | Point at `root_cli_container` and add a `get_container()` accessor; blocked until shared layer supplies DI. |
| E2  | 🟡 WARNING (FIXED) | `surface_cli_command.py` `get_orchestrator` reads `cls._orchestrator` never defined as class attribute → `AttributeError` if invoked | `surface_cli_command.py` | Added `_orchestrator: ClassVar[Any] = None`. |
| E3  | 🟡 WARNING | `surface_cli_command.py` relative import `from ..common.taxonomy_core_vo import ...` resolves to non-existent `modules.cli.common` | `surface_cli_command.py:24` | Repoint to `modules.shared.src.common.*` once that layer exists. |
| E4  | 🟢 INFO | Legacy `surface_cli_main.py` collapses all outcomes to exit code 0/1; FR-CLI-001 requires four deterministic classes (success / surface validation / upstream categorized / unexpected internal) | `surface_cli_main.py` | Implement 4-class exit codes in the FRD-aligned entry. |

### FRD Functional-Coverage Gaps (FR-CLI-002 / FR-CLI-003)

| #   | Severity | Issue | Location | Recommendation |
| --- | -------- | ----- | -------- | -------------- |
| F1  | 🟡 WARNING | No table rendering for list-shaped results (action catalogs, task records) with stable column ordering | `capabilities_cli_render.py` | Add table renderer with fixed columns. |
| F2  | 🟡 WARNING | No truncation of large payloads in text mode + continuation hint (JSON must stay complete) | `capabilities_cli_render.py` | Add size guard + hint. |
| F3  | 🟡 WARNING | `interactive` flag accepted but unused — no color/decoration adaptation per terminal capability | `capabilities_cli_render.py` | Use flag to gate decoration; defaults to off. |
| F4  | 🟡 WARNING | Field-level validation detail not rendered distinctly (FR-CLI-003) | `capabilities_cli_error.py` | Render `detail`/`field` pointing at offending argument. |

## Violations

- **AES102** (naming): `agent_orchestrator.py`, `surface_cli_main.py`, `surface_cli_socket_client.py`,
  `surface_cli_blender_manager.py`, `surface_cli_registry.py`, `surface_cli_commands.py`,
  `capabilities_cli_error.py` — see A3/A4/A5.
- **AES503 / AES506** (orphans): FRD-aligned capabilities/agent/container/surface cannot resolve their
  contract/aggregate dependencies (`modules.shared.*` absent) → unreachable at runtime (A1).
- **FRD scope (Out of Scope)**: legacy monolith owns process lifecycle / connection / registry (A2).
- No **AES304** bypass comments (`noqa`/`type: ignore`/`unwrap`/`panic`) found in the module.
- No **AES201** cross-layer import violations beyond the missing-dependency breakage (A1/E3).

## Action Items

- [x] 🟢 Fix ruff issues (17 → 0): newlines, SIM105, UP037, F821, ARG002×2
- [x] 🟢 Add `_orchestrator` class attribute (fixes latent AttributeError, E2)
- [x] 🟢 Establish pytest baseline for import-safe utilities (9 tests passing)
- [ ] 🔴 Supply `modules.shared.src.cli.*` + `modules.shared.src.common.*` (cross-module) so FRD-aligned code runs (A1, E1, E3)
- [ ] 🔴 Implement secret masking in render/error paths (S1)
- [ ] 🟡 Add table rendering, truncation, terminal-capability, field-detail (F1–F4)
- [ ] 🟡 Resolve AES102 naming violations (A3–A5) and deprecate legacy monolith (A2)

## Fixed Code

### E2 — `surface_cli_command.py` (latent AttributeError)

```python
from typing import TYPE_CHECKING, Any, ClassVar

class CliCommandHandler:
    """Handler for CLI help command."""

    _orchestrator: ClassVar[Any] = None

    @classmethod
    def get_orchestrator(cls) -> Any:
        """Lazy-load CoreAgentOrchestrator from DI container."""
        if cls._orchestrator is None:
            container = cls._get_container()
            cls._orchestrator = container.core_agent_orchestrator
        return cls._orchestrator
```

### SIM105 — `surface_cli_socket_client.py` (disconnect)

```python
import contextlib
...

    def disconnect(self) -> None:
        """Disconnect from Blender addon."""
        if self._sock:
            with contextlib.suppress(Exception):
                self._sock.close()
            self._sock = None
```

### ARG002 — `capabilities_cli_render.py` / `capabilities_cli_command_router.py`

```python
# render_output: accept the protocol flag but mark intentionally unused (no decoration today)
async def render_output(self, result, format="text", _interactive=True) -> str:
    ...
    return self._render_text(result, _interactive)

# parse_and_route: flags not consumed by surface (semantics belong to owning feature)
async def parse_and_route(self, command, args=None, _flags=None) -> dict[str, Any]:
    ...
```
