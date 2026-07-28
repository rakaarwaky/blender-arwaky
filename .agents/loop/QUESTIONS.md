# ARWAKY LOOP QUESTIONS

## Status OPEN

### question

1. **Cycle 46 (Linter AES201 Detection)** : False positive detection on `surface_cli_command.py` importing from `agent_` prefix files in `shared/src/common/`. The linter uses prefix-based detection rather than path-based layer detection.

### answer

1. **Cycle 46 (Linter AES201 Detection)** : its not fasle psotiive its true vioaltion surface shoud import from utitltiy taxonomy contract agregate only read RULES AES

## Status RESOLVED

* **Cycle 25 (CLI Cleanup)** : Deleted CLI agent/capability layer since `CliContainer` was never instantiated and the CLI surface routes directly through the DI container.
* **Cycle 28 (Orphan Cleanup)** : Deleted 20 orphaned job and MCP capability/protocol/taxonomy files verified as dead code.
* **Cycle 40 (Entry Point)** : Fixed the `blender-arwaky` entry point location in `pyproject.toml`.
* **Cycle 49 (Import AES201)** : Fixed broken import chain by deleting legacy dead files (`surface_cli_command.py` & `root_cli_entry.py`).
* **Cycle 50 (Barrel AES202)** : Barrel export false positives accepted as intentional design patterns.
* **Cycle 52 (Export Barrel Job)** : Fixed import path from `taxonomy_job_state_constant.py` to `taxonomy_job_constant.py`.
* **Cycle 53 (Linter Job Monitor)** : Confirmed false positives for AES302/AES403 on `capabilities_job_monitor.py`.
* **Cycle 54 (Counter Reconnect FR-GWY-002)** : Added per-session counter reset logic to `MaintenanceExecutor`.
* **Cycle 55 (Orphan AES501/504)** : Permanently ignored orphan flags (AES501–AES505) due to excessive false positives.
* **Cycle 55 (Bypass AES304)** : Adopted a surgical file-by-file approach for bypass comment resolution.
* **Cycle 55 (Contract Orphan AES502)** : Deleted 57 contract orphans and updated barrel exports in `shared/src/__init__.py`.
* **Cycle 63 (Import Scene)** : Resolved scene module import breakage automatically following the scene refactoring.
* **Cycle 71 (Routing Tool MCP)** : Resolved MCP tool routes (FR-MCP-002) by directing commands to diagnostics, skill reader, and dispatcher functions.
