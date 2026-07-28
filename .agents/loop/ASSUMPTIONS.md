# ARWAKY LOOP ASSUMPTIONS

- `Host` defined as `NewType("Host", str)` (sibling of `PortNumber`); only used as the `host: str` param in gateway entity/event. Smallest safe interpretation since `Host` was defined nowhere in the repo.
- Concurrency: multiple agents edit this repo simultaneously. I recorded only my own 17 edits; verified the COMBINED working tree imports cleanly (41/41) and all 340 tests pass. Did not modify sibling-agent edits.
- `ConnectionError` re-export collision (F811): kept gateway's `ConnectionError` as the single top-level `modules.shared.src.ConnectionError` and dropped the common-domain re-export. No consumer imports top-level `ConnectionError` (cli uses the builtin, scene defines its own), so this is safe and avoids renaming a public API.
- I will NOT commit — auto-commit is the user's prerogative.
- CORRECTION (cycle 5): mcp orphan capability files (health/lifecycle/startup/tool_discovery) are NOT part of the bootstrap chain — verified via full-repo grep; they duplicate surface_* classes and are never imported. Safe to delete; tracked by git so fully recoverable (git restore restores them).


<featuresname></featuresname>

- Tar extraction `filter` must be version-guarded: `requires-python = ">=3.10"` but the `filter` kwarg on `tarfile.extract` only exists on Python 3.12+. Passing it unconditionally would raise `TypeError` on 3.10/3.11, so `filter='data'` is applied only when `sys.version_info >= (3, 12)` (see cycle 11, capabilities_asset_extract.py).
- Concurrency: a sibling loop agent advanced the loop to cycle 10 (orchestrator aggregate inheritance; taxonomy error files) during this run. My cycle-11 tar fix touched only `modules/asset/src/capabilities_asset_extract.py` and its test — disjoint from the sibling's files — so no file-level conflict. Loop state markdown files were concurrently edited; I rewrote STATE.md coherently and recorded my work as cycle 11.
- GatewayOrchestrator must NOT inherit `IBlenderServerAggregate`: the latter is the async *server* aggregate (start/shutdown/connect/execute_code/send_command/async-task/metrics); GatewayOrchestrator is the sync gateway-feature orchestrator implementing the gateway protocols (FR-GWY-001..005). The correct AES202 resolution for the gateway orchestrator is a dedicated gateway aggregate or server-aggregate wiring at the root/mcp entry orchestrator, done deliberately — not a blanket base-class inheritance that breaks instantiation (reverted in cycle 11 after a concurrent sibling edit introduced the broken base).
