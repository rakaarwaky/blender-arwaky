# ARWAKY LOOP QUESTIONS

FRD ambiguities / open questions surfaced by the loop:

- (none yet)
- OPEN: cli `capabilities_cli_lifecycle.py` (CliLifecycleManager) is wired into the live cli composition root (CliContainer.wire) and the cli orchestrator implements CliLifecycleProtocol, but cli FRD states process lifecycle is "owned by launcher feature". Launcher already implements full lifecycle (FR-LAU-001..005). Removing/repointing the cli lifecycle would break the Blender bootstrap and cannot be runtime-verified here. DEFERRED pending user decision: keep cli lifecycle as a thin facade delegating to launcher, or remove and repoint cli to consume launcher. (Not addressed in cycle 5 to avoid irreversible breakage.)
