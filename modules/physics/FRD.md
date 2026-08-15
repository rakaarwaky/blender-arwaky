# FRD — Physics Feature

## Purpose

Provide bounded rigid body and cloth configuration, state inspection, and scene cache lifecycle through canonical dispatcher actions.

## Canonical actions

| Action | Type | Contract |
|---|---|---|
| `get_physics_state` | Read-only | Rigid body, cloth, and modifier state for one object |
| `configure_rigid_body` | Mutation | Enable/disable and configure active/passive rigid body settings |
| `configure_cloth_simulation` | Mutation | Enable/disable and configure bounded cloth quality/pin group |
| `bake_physics_simulation` | Long-running destructive mutation | Bake the active scene cache over a bounded frame range; background/job eligible |
| `clear_physics_bake` | Destructive mutation | Remove active scene point-cache data |

## Invariants

Physics actions are limited to rigid body and cloth in this wave. Mass, quality, frame range, and cache operations are bounded. No fluid, particle, or external solver provider is added speculatively. Bake and clear actions are marked destructive; long-running bake dispatch must use the shared `job` lifecycle and never a private physics queue.

## Verification

Unit tests cover numeric bounds, body-type allow-list, and orchestration. Blender smoke tests cover rigid body configuration, cloth modifier configuration, state inspection, invalid object errors, and cache lifecycle handler readiness. Full bake execution remains environment-sensitive and is tested through the real bounded handler contract.
