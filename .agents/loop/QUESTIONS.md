# ARWAKY LOOP QUESTIONS

FRD ambiguities / open questions surfaced by the loop:

* **RESOLVED (Cycle 25)** : Entire CLI capability/agent layer deleted; `CliContainer` was never instantiated and the CLI surface routes directly through the DI container.
* **RESOLVED (Cycle 28)** : Cleaned up 20 orphaned job and MCP capability/protocol/taxonomy files verified dead via full-repo grep; core FR coverage remains intact.
* **OPEN (Cycles 37, 39)** : Strategy decision needed for bulk lint-arwaky remediation; `lint-arwaky` orphan flags (AES501/504) produce false positives and require full-repo grep verification before action.
* **OPEN (Cycle 46)** : AES201 flagged `surface_cli_command.py` importing from `agent_` prefix file — confirmed false positive (file lives in shared/src/common/, not agent layer). Linter's prefix-based detection cannot distinguish `agent_di_container.py` (shared DI utility) from actual agent orchestrators. Should the linter be configured to use path-based layer detection instead of filename-prefix?
* **OPEN (Cycle 46)** : AES304 bypass comments (439) — bulk removal would break inheritance chains between contract protocols and capability implementations. Decision needed: (a) defer indefinitely, (b) resolve per-file with targeted type widening, or (c) create a shared `type: ignore`豁免清单` with justification per file?
* **RESOLVED (Cycle 49)** : AES201 broken import chain — FIXED by deleting dead/orphan files (`surface_cli_command.py` with CliCommandHandler, `root_cli_entry.py`) that imported from non-existent `modules.shared.src.common.agent_di_container`. AES201 violations reduced to 0.
* **RESOLVED (Cycle 50)** : AES202 barrel false positives — ACCEPTED as intentional false positives (barrel pattern + GatewayOrchestrator design). Documented in ASSUMPTIONS.md and AUDIT.md. No code changes required.
* **OPEN (Cycle 50)** : AES502 contract orphan remediation — 58 abandoned requirements (zero FRD match, zero implementations, zero consumers). Exported from shared/src/__init__.py (public API) so removal = breaking change. Fix options: (a) delete orphan contracts and update barrel exports, (b) implement them in capabilities layer, or (c) keep as-is and document as architectural debt. Which approach?
* **RESOLVED (Cycle 40)** : Stale `blender-arwaky` entry point fixed in `pyproject.toml` to reference `modules.cli.src.surface_cli_main:main`.
