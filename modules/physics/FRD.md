# FRD — Physics Feature

## System Overview
The Physics module provides bounded rigid body, cloth, particle, force-field, and fluid configuration, state inspection, and scene cache lifecycle. It routes operations through the Gateway and uses the shared Job lifecycle for long-running bakes.

## Functional Requirements

### FR-001: Rigid Body and Cloth Configuration
- **Description**: Enable/disable and configure rigid body and cloth modifiers, and inspect physics state.
- **Input**: `object_name`, `enabled`, `body_type`, `mass`, `quality`, `pin_group`.
- **Output**: `UnifiedEnvelope` confirming mutation or state summary.
- **Business Rules**: Mass, quality, and frame ranges are bounded. Actions require explicit object names.
- **Edge Cases**: Non-mesh object for cloth; invalid body type; negative mass.
- **Error Handling**: `validation_error` for out-of-bounds values; `not_found` for missing objects.

### FR-002: Simulation Cache Lifecycle
- **Description**: Bake active scene cache over bounded frame range and clear point-cache data.
- **Input**: `frame_start`, `frame_end`.
- **Output**: `UnifiedEnvelope` or task reference for background bake.
- **Business Rules**: Bake and clear are marked destructive. Long-running bake dispatch uses shared `job` lifecycle. Never creates a private physics queue.
- **Edge Cases**: Frame range out of bounds; cache directory unwritable; bake interrupted.
- **Error Handling**: `validation_error` for invalid ranges; `capacity_error` if job queue full; `execution_error` for Blender cache failures.

### FR-003: Advanced Simulation (Wave 4)
- **Description**: Configure particle systems, force fields, and fluid domains, and inspect simulation state.
- **Input**: `object_name`, `count`, `lifetime`, `field_type`, `strength`, `domain_type`, `resolution`.
- **Output**: `UnifiedEnvelope` with modifier summary.
- **Business Rules**: Bounded count, lifetime, and resolution. Fluid bake action not exposed; only configures real Blender modifiers.
- **Edge Cases**: Particle count exceeds limits; fluid domain resolution too high for memory.
- **Error Handling**: `validation_error` for numeric bounds; `unsupported` for missing modifiers.

## API Contract

| Operation | Input | Output | Description |
|---|---|---|---|
| `get_physics_state` | `object_name` | `UnifiedEnvelope` | Rigid body/cloth state |
| `configure_rigid_body` | `object_name`, `enabled`, `mass` | `UnifiedEnvelope` | Configure rigid body |
| `configure_cloth_simulation`| `object_name`, `enabled`, `quality`| `UnifiedEnvelope` | Configure cloth modifier |
| `bake_physics_simulation` | `frame_start`, `frame_end` | `UnifiedEnvelope` | Bake scene cache (job eligible) |
| `clear_physics_bake` | None | `UnifiedEnvelope` | Remove point-cache data |
| `get_simulation_state` | `object_name` | `UnifiedEnvelope` | Particle/force/fluid summary |
| `configure_particle_system` | `object_name`, `count`, `lifetime` | `UnifiedEnvelope` | Configure particle system |
| `configure_force_field` | `object_name`, `field_type`, `strength`| `UnifiedEnvelope` | Configure force field |
| `configure_fluid_domain` | `object_name`, `domain_type`, `resolution`| `UnifiedEnvelope` | Configure fluid domain |

## Integration Points

- **3rd Party**: No 3rd party integrations.
- **Internal**: `gateway` (command transport), `dispatcher` (routing), `job` (background bake tracking).

## Non-functional Requirements (Detailed)

- **Performance**: Simulation state inspection bounded to prevent payload exhaustion.
- **Security**: Destructive cache clear operations require confirmation.
- **Scalability**: Long-running bakes offloaded to `job` feature to prevent blocking the main thread.

## Test Scenarios / QA Checklist

- [ ] Verify `configure_rigid_body` rejects negative mass values.
- [ ] Verify `bake_physics_simulation` returns a task reference when submitted as background.
- [ ] Verify `clear_physics_bake` requires confirmation flag.
- [ ] Verify Wave 4 actions only configure real Blender modifiers and do not expose external solvers.

## Assumptions & Constraints

- Physics actions are limited to rigid body, cloth, particle, force-field, and fluid in the baseline.
- External solvers and custom simulation code execution are out of scope.

## Glossary

- **Point-Cache**: Blender's system for storing baked simulation data on disk/memory.
- **Domain**: The bounding box object that defines the volume for fluid or particle simulations.
- **UnifiedEnvelope**: The standardized JSON response wrapper containing success indicator, data payload, error category, tracking ID, and warnings.

## Reference

- PRD: `./PRD.md`
- Depends On: `gateway`, `dispatcher`, `job`
