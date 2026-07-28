# ARWAKY LOOP ASSUMPTIONS

- `Host` defined as `NewType("Host", str)` (sibling of `PortNumber`); only used as the `host: str` param in gateway entity/event. Smallest safe interpretation since `Host` was defined nowhere in the repo.
- Concurrency: multiple agents edit this repo simultaneously. I recorded only my own 17 edits; verified the COMBINED working tree imports cleanly (41/41) and all 340 tests pass. Did not modify sibling-agent edits.
- `ConnectionError` re-export collision (F811): kept gateway's `ConnectionError` as the single top-level `modules.shared.src.ConnectionError` and dropped the common-domain re-export. No consumer imports top-level `ConnectionError` (cli uses the builtin, scene defines its own), so this is safe and avoids renaming a public API.
- I will NOT commit — auto-commit is the user's prerogative.
- CORRECTION (cycle 5): mcp orphan capability files (health/lifecycle/startup/tool_discovery) are NOT part of the bootstrap chain — verified via full-repo grep; they duplicate surface_* classes and are never imported. Safe to delete; tracked by git so fully recoverable (git restore restores them).


<featuresname></featuresname>
