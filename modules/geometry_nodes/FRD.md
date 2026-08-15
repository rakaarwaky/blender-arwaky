# FRD — Geometry Nodes Feature

## Purpose

Expose bounded Geometry Nodes graph inspection and mutation through the canonical dispatcher. The feature owns node-group semantics and modifier binding; transport remains owned by the gateway.

## Canonical actions

| Action | Type | Contract |
|---|---|---|
| `inspect_geometry_node_group` | Read-only | Group name, bounded nodes/links/interface sockets |
| `create_geometry_node_group` | Mutation | Create/reuse a Geometry Nodes group and optionally bind a `NODES` modifier |
| `set_geometry_node_link` | Mutation | Link existing output/input sockets by exact node and socket names |
| `set_geometry_node_modifier` | Mutation | Bind an existing group to an object modifier |

## Invariants

Group and object references are exact names. Node and socket lookups fail with structured command errors rather than creating speculative graph elements. Graph inspection is bounded to 256 links and interface items. The feature never opens sockets, registers MCP tools, or creates a private job store.

## Security and verification

Only Blender data-block references are accepted. No arbitrary Python source, filesystem path, or external provider is accepted by these actions. Unit tests cover contract wiring and validation; Blender smoke tests cover group creation, modifier binding, inspection, and structured missing-reference errors.
