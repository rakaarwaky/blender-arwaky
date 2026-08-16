# Competitor Source Refresh Report

**Snapshot date:** 2026-08-15  
**Branch:** `feat/core-capability-migration-aes`  
**Purpose:** Record the exact public source snapshots used as migration references for Blender core capability work.

## Important disposition

The repositories below were cloned into a temporary audit directory outside this repository. No competitor source code is committed by this report. The audit used source listing, license/header inspection, and feature mapping; it did not execute competitor code.

A competitor repository license applies to that repository's source under its terms. It does not automatically grant rights to copy dependencies, model adapters, external assets, provider SDKs, or generated output. Every actual code port requires a file-level attribution and dependency review.

## Refreshed source snapshots

| Source | Upstream | Snapshot commit | Observed license | Migration disposition |
|---|---|---|---|---|
| Ahuja BlenderMCP | [ahujasid/blender-mcp][1] | `3ab892510cc0e5435ba5e611c01fb1021fbde8de` | MIT; copyright Siddharth Ahuja | Selective code port may be considered for internal Blender behavior after attribution, dependency review, and AES rewrite. |
| Djeada Blender MCP Server | [djeada/blender-mcp-server][2] | `7eed33edf4aca2ab0ca84a6da27321f89f68b504` | MIT; copyright Adam Djellouli | Selective code port may be considered for internal Blender behavior after attribution, dependency review, and AES rewrite. |
| Sandraschi Blender MCP | [sandraschi/blender-mcp][3] | `63e6fa112268917f1a9b4bc5c0b6625489650846` | MIT; copyright Sandra Schipal | Selective code port may be considered for internal Blender behavior after attribution, dependency review, and AES rewrite. |
| Official Blender Lab MCP | [projects.blender.org/lab/blender_mcp][4] | `4309a39646e644261624bfcd2bca669b343b7621` | GPL-3.0-or-later SPDX headers in addon source and manifest | Reference-only for the MIT core unless maintainers explicitly approve a compatible licensing/isolation strategy. Do not copy GPL implementation into the core. |

The upstream commit dates in this refresh were 2026-08-03 for Ahuja, 2026-06-21 for Djeada, 2026-08-06 for Sandraschi, and 2026-08-06 for Blender Lab. The snapshot is a research baseline, not a claim that upstream repositories are frozen.

## Candidate internal Blender capability references

| Capability | Candidate source evidence | Arwaky destination | Porting posture |
|---|---|---|---|
| Scene inspection and hierarchy | Djeada named scene/object/hierarchy tools; Blender Lab scene/data-block exploration | `modules/scene` | Reimplement through Arwaky scene contracts; use source for behavior comparison. |
| Undo/redo | Djeada history tools | `modules/scene` | Small selective port/reference; preserve confirmation and event policy. |
| Material authoring | Ahuja and Djeada material/color/texture workflows | `modules/object` | Extend existing object/material contract; do not create a new MCP tool per property. |
| Async jobs and cancellation | Djeada async Python/job operations; Arwaky already owns job lifecycle | `modules/job` plus domain executors | Reconcile state machines; do not copy private job stores. |
| Geometry Nodes | Blender Lab analysis/documentation examples; Sandraschi Geometry Nodes operations | `modules/geometry_nodes` | New FRD and graph contract; Blender Lab source is GPL reference-only. |
| Animation/keyframes | Djeada script library and Sandraschi animation examples | `modules/animation` | Reimplement against Arwaky action schemas and gateway protocols. |
| Mesh/edit/sculpt | Sandraschi mesh/sculpt capabilities | `modules/mesh` | Extract only internal Blender semantics; provider/dashboard code is out of scope. |
| Compositor | Sandraschi compositor operations | `modules/compositor` | New node graph contract and render integration. |
| VSE | Sandraschi VSE operations | `modules/vse` | New sequence contract and job-backed render lifecycle. |
| Physics/simulation | Djeada Mantaflow/rigid-body scripts; Sandraschi physics references | `modules/physics` | New FRD; baking is job-backed and security-bounded. |

## License-sensitive source handling

The MIT snapshots can be considered for selective porting, but MIT does not remove the need to preserve the copyright notice and license text. We must also inspect nested dependencies and avoid importing competitor-specific provider or dashboard code into the core.

The Blender Lab addon source carries `SPDX-License-Identifier: GPL-3.0-or-later`. Its behavior and public examples can inform an independent implementation, but its GPL implementation must not be copied into Blender Arwaky's MIT core without an approved licensing strategy. This is especially important for addon bridge code, socket execution, and tool wrappers.

## Refresh procedure

Run the following procedure when refreshing the audit baseline:

```bash
rm -rf /tmp/blender_mcp_competitors
mkdir -p /tmp/blender_mcp_competitors
gh repo clone ahujasid/blender-mcp /tmp/blender_mcp_competitors/ahujasid-blender-mcp -- --depth 1
gh repo clone djeada/blender-mcp-server /tmp/blender_mcp_competitors/djeada-blender-mcp-server -- --depth 1
gh repo clone sandraschi/blender-mcp /tmp/blender_mcp_competitors/sandraschi-blender-mcp -- --depth 1
git clone --depth 1 https://projects.blender.org/lab/blender_mcp.git /tmp/blender_mcp_competitors/blender-lab-mcp
```

Then record `git log -1`, the upstream URL, license files or SPDX headers, candidate capability paths, and the migration disposition. Do not run untrusted source during a source refresh. Any test execution requires an explicit review of the source and its dependencies first.

## Next audit outputs

Before any code port, create a per-capability record with:

| Field | Required content |
|---|---|
| Capability | Core Blender domain and proposed Arwaky owner |
| Upstream evidence | URL, commit SHA, file or behavior reference |
| License disposition | Portable, reference-only, or rejected |
| Arwaky contract | FRD, action schemas, inputs, outputs, errors, events |
| Security review | Paths, code execution, destructive operations, limits, redaction |
| Migration plan | Files to create/change and dependencies |
| Verification | Unit, contract, integration, Blender smoke, and quality gates |

## References

[1]: https://github.com/ahujasid/blender-mcp "Ahuja BlenderMCP"
[2]: https://github.com/djeada/blender-mcp-server "Djeada Blender MCP Server"
[3]: https://github.com/sandraschi/blender-mcp "Sandraschi Blender MCP"
[4]: https://projects.blender.org/lab/blender_mcp "Official Blender Lab MCP source"
