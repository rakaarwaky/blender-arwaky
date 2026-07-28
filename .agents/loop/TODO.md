# ARWAKY LOOP TODO

Next concrete actions (filled by the loop):

- [X]  Run initial full test sweep to establish baseline.
- [X]  Audit each module FRD for unimplemented requirements.
- [X]  Replace first discovered dummy/stub with real tested code.
- [X]  Check structural compliance: one-FR-one-capability-one-protocol rules (asset + scene fixed)
- [ ]  LINTER: Run lint-arwaky-cli scan for remaining violations across all modules
- [ ]  SCOPE: Move cli lifecycle capability to launcher module (FRD says launcher owns process lifecycle)
- [ ]  SCOPE: Audit mcp orphan files — health, lifecycle, startup, discovery (not in FRD scope but part of bootstrap chain)
- [ ]  TESTS: Rewrite asset module tests to match actual implementation signatures
