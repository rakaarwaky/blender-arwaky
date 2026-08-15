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

Physics actions are limited to rigid body and cloth in the Wave 3 baseline. Mass, quality, frame range, and cache operations are bounded. Bake and clear actions are marked destructive; long-running bake dispatch must use the shared `job` lifecycle and never a private physics queue.

## Wave 4 advanced simulation actions

| Action | Type | Contract |
|---|---|---|
| `get_simulation_state` | Read-only | Bounded particle, force-field, fluid, rigid body, and cloth modifier summary |
| `get_simulation_cache_status` | Read-only | Active scene frame range and bounded cache/bake state |
| `configure_particle_system` | Mutation | One particle system with bounded count, lifetime, frame range, and physics type |
| `configure_force_field` | Mutation | Existing object force field with bounded type, strength, and noise |
| `configure_fluid_domain` | Mutation | Baseline fluid domain modifier with bounded domain type, resolution, and cache mode |

Wave 4 does not expose a fluid bake action or external solver. It only configures real Blender modifiers and reads their state. Particle, force-field, and fluid operations are routed through the existing Blender gateway and never create a private task registry.

## Verification

Unit tests cover numeric bounds, body-type allow-list, and orchestration. Blender smoke tests cover rigid body configuration, cloth modifier configuration, state inspection, invalid object errors, and cache lifecycle handler readiness. Full bake execution remains environment-sensitive and is tested through the real bounded handler contract.
