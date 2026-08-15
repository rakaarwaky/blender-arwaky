# FRD — Compositor Feature

## Purpose

Provide bounded compositor node graph inspection and mutation for the active scene through canonical dispatcher actions.

## Canonical actions

| Action | Type | Contract |
|---|---|---|
| `inspect_compositor_nodes` | Read-only | Bounded node, socket, and link metadata |
| `configure_compositor` | Mutation | Enable or disable compositor node usage |
| `create_compositor_node` | Mutation | Create one allow-listed node type |
| `set_compositor_link` | Mutation | Link exact existing output/input sockets |

## Invariants

Inspection is bounded to 1000 nodes and links. Node creation uses an explicit allow-list and never accepts arbitrary Blender type strings. Link mutation requires exact node and socket names and is idempotent when the link already exists. No compositor action opens sockets, executes arbitrary code, or creates jobs.

## Verification

Unit tests cover allow-lists and typed graph output. Blender smoke tests cover enabling nodes, creating RGB and Composite nodes, linking sockets, inspection, and missing-node errors.
