# ARWAKY LOOP QUESTIONS

FRD ambiguities / open questions surfaced by the loop:

* **RESOLVED (Cycle 25)** : Entire CLI capability/agent layer deleted; `CliContainer` was never instantiated and the CLI surface routes directly through the DI container.
* **RESOLVED (Cycle 28)** : Cleaned up 20 orphaned job and MCP capability/protocol/taxonomy files verified dead via full-repo grep; core FR coverage remains intact.
* **OPEN (Cycles 37, 39)** : Strategy decision needed for bulk lint-arwaky remediation; `lint-arwaky` orphan flags (AES501/504) produce false positives and require full-repo grep verification before action.
* **RESOLVED (Cycle 40)** : Stale `blender-arwaky` entry point fixed in `pyproject.toml` to reference `modules.cli.src.surface_cli_main:main`.
