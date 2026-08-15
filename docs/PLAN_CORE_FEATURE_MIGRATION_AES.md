# Core Blender Feature Migration Plan — Competitor Source to AES

**Status:** Proposed plan  
**Branch:** `feat/core-capability-migration-aes`  
**Owner:** Blender Arwaky maintainers  
**Scope:** Internal Blender core capabilities only

## Executive decision

Blender Arwaky will not copy an entire competitor repository into the product. The migration will use competitor source as an **audited implementation reference** and, where the license permits, as a source of selectively ported implementation ideas or code with attribution. Every migrated capability must be reshaped into the Blender Arwaky AES architecture, canonical dispatcher contract, security policy, and test strategy.

The public MCP surface remains exactly five tools: `execute_command`, `list_commands`, `health_check`, `get_config`, and `help`. New capabilities add canonical actions, not one new MCP tool per operation.

> **Migration rule:** We migrate capability value and proven behavior into our contracts; we do not migrate tool sprawl, private task stores, direct surface-to-Blender calls, or unreviewed source trees.

## Scope boundary

### Included core Blender domains

The first migration wave covers scene state/history, richer object and material authoring, background execution lifecycle, Geometry Nodes, animation/keyframes, mesh/edit-mode operations, compositor, VSE, and physics/simulation. These are internal Blender domains with durable state and clear operator semantics.

### Excluded from this plan

External asset providers, generative model APIs, VRM/VRChat integrations, Gaussian splats, dashboards, `.mcpb` packaging, PyPI/`uvx` distribution, Docker/native/fleet deployment, telemetry products, and local LLM adapters are not feature modules in this migration. They may be separate initiatives later.

## Source and license policy

| Source category | Treatment |
|---|---|
| MIT competitor source | May be selectively ported after code review, attribution, dependency review, and compatibility adaptation. Preserve required copyright and license notices. |
| GPL-licensed source | Reference-only for this MIT project unless maintainers explicitly choose a compatible licensing/isolation strategy after legal review. Do not copy GPL implementation into the MIT core. |
| Public README, API behavior, or demo | May be used as a behavior reference. Reimplement behavior through Arwaky contracts instead of assuming source-level compatibility. |
| External dependencies/assets | Must be reviewed independently. A competitor's repository license does not automatically cover its dependencies, model providers, assets, or service terms. |

The source refresh report records exact upstream commit SHAs and license findings in [`COMPETITOR_SOURCE_REFRESH.md`](COMPETITOR_SOURCE_REFRESH.md).

## AES migration architecture

Each internal Blender capability follows the existing module pattern:

```text
modules/<feature>/
├── FRD.md
├── src/
│   ├── __init__.py
│   ├── root_<feature>_container.py
│   ├── agent_<feature>_orchestrator.py
│   ├── capabilities_<feature>_*.py
│   └── utility_<feature>_*.py
└── tests/
```

Cross-feature contracts are placed in the matching shared taxonomy namespace:

```text
modules/shared/src/<feature>/
├── contract_<feature>_*_protocol.py
├── taxonomy_<feature>_vo.py
├── taxonomy_<feature>_error.py
├── taxonomy_<feature>_event.py
└── taxonomy_<feature>_constant.py
```

The dispatcher owns action metadata and routing. MCP and CLI submit actions to the dispatcher; they must not call feature agents directly. The gateway remains the only transport authority to Blender, while security remains the authority for code, path, archive, confirmation, and redaction policies.

## Migration waves

### Wave 0 — Provenance and source refresh

Pin each source to an audit snapshot, record license and commit metadata, identify candidate files, and reject source with incompatible licensing for direct porting. No competitor code is merged during this wave.

**Exit criteria:** source refresh report completed; every candidate has a license disposition; no unreviewed source is copied into the repository.

### Wave 1 — Close gaps in existing modules

Extend `scene`, `object`, `render`, and `job` before adding new feature folders:

| Capability | Owning module | Initial actions |
|---|---|---|
| Scene graph and history | `modules/scene` | `list_scene_objects`, `get_object_hierarchy`, `undo`, `redo` |
| Material authoring | `modules/object` | `create_material`, `set_material_properties`, `set_material_texture` |
| Render configuration | `modules/render` | `set_render_settings` |
| Task lifecycle | `modules/job` | `submit_task`, `list_tasks`, `get_capacity_status`, `get_task_status`, `cancel_task` |

**Exit criteria:** existing FRDs are updated; no duplicate ownership is introduced; existing tests remain green; action schemas are canonical.

#### Wave 1 implementation status

| Area | Status | Verification |
|---|---|---|
| Scene object listing and hierarchy | Implemented in addon runtime and dispatcher catalog | Blender 4.0.2 background smoke passed with bounded filtering and parent-child tree output |
| Undo/redo | Implemented with explicit context-aware result | UI/editor context may return `finished`; background context returns `unavailable` rather than fake success |
| Material authoring | Implemented for Principled BSDF create/update/local texture assignment | Blender background smoke passed for create, PBR update, assignment, and validation path |
| Render settings | Implemented with engine enum and dimension/sample/percentage bounds | Blender background smoke passed at 640×480, 50%, samples 8, transparent film |
| Job lifecycle | Implemented through shared JobOrchestrator and repository; no private store | Unit, persistence, dispatcher, and CLI contract tests passed |

### Wave 2 — Geometry and time domains

Create the first new core modules:

| New module | Core responsibility |
|---|---|
| `modules/geometry_nodes` | Inspect and mutate node groups, sockets, links, group interfaces, and Geometry Nodes modifier bindings. |
| `modules/animation` | Timeline, frame range, keyframes, F-curves, actions, constraints, and basic armature operations. |
| `modules/mesh` | Mesh statistics, topology inspection, normals, UV basics, edit-mode operations, and bounded mesh validation. |

These modules must not use direct MCP registration. Their actions are added to the canonical dispatcher and exposed through the existing five tools and CLI.

#### Wave 2 implementation status

| Module | Implemented actions | Verification |
|---|---|---|
| `modules/geometry_nodes` | `inspect_geometry_node_group`, `create_geometry_node_group`, `set_geometry_node_link`, `set_geometry_node_modifier` | AES executor tests and Blender 4.0.2 smoke: valid group interface, Group Input/Output link, and modifier binding |
| `modules/animation` | `get_animation_state`, `insert_object_keyframe`, `set_timeline_range`, `list_object_keyframes` | AES executor tests and Blender 4.0.2 smoke: timeline update, transform keyframes, F-curve inspection, and invalid-path error |
| `modules/mesh` | `get_mesh_statistics`, `validate_mesh`, `perform_mesh_edit_operation`, `ensure_mesh_uv_layer` | AES executor tests and Blender 4.0.2 smoke: cube topology, validation, UV layer creation, normals recalculation |

All Wave 2 actions remain behind the five-tool MCP surface and are routed through the canonical dispatcher catalog. The runtime handlers enforce bounded limits and explicit allow-lists; they do not create private job stores or direct transport connections.

### Wave 3 — Specialized internal Blender domains

Add only after Wave 2 contracts are stable:

| New module | Core responsibility |
|---|---|
| `modules/compositor` | Compositor node graph inspection, mutation, and render output routing. |
| `modules/vse` | Sequence strips, channels, media references, transitions, and sequence render coordination. |
| `modules/physics` | Rigid body, cloth, fluid, particle/force settings, simulation bake, progress, and cancellation. |

Long-running compositor, VSE, and physics operations must use `modules/job`; no domain may create a private job registry.

#### Wave 3 implementation status

| Module | Implemented actions | Verification |
|---|---|---|
| `modules/compositor` | `inspect_compositor_nodes`, `configure_compositor`, `create_compositor_node`, `set_compositor_link` | AES executor tests and Blender 4.0.2 smoke: node creation, dynamic socket discovery, exact link, bounded inspection |
| `modules/vse` | `inspect_sequence_editor`, `create_sequence_strip`, `remove_sequence_strip`, `render_sequence` | AES executor tests and Blender 4.0.2 smoke: COLOR strip lifecycle and invalid media path; render is a real handler with long-running metadata |
| `modules/physics` | `get_physics_state`, `configure_rigid_body`, `configure_cloth_simulation`, `bake_physics_simulation`, `clear_physics_bake` | AES executor tests and Blender 4.0.2 smoke: rigid body, cloth, state inspection, disable lifecycle; bake/clear use Blender cache operators |

Wave 3 keeps the five-tool MCP surface unchanged. Sequence rendering and physics baking carry explicit `background_eligibility_flag`, `long_running_flag`, bounded timeouts, and destructive/risk metadata so the shared dispatcher/job path can coordinate them without domain-specific registries. Fluid, particle, and force-field packs remain future scope rather than speculative actions.

### Wave 4 — Advanced simulation controls

Wave 4 extends the existing `modules/physics` contract instead of creating a second simulation module. The scope is limited to real Blender data and operator behavior:

| Capability | Canonical actions | Boundary |
|---|---|---|
| Simulation state and cache | `get_simulation_state`, `get_simulation_cache_status` | Read-only, bounded summaries; no private progress store |
| Particle systems | `configure_particle_system` | One object, bounded count/frame/lifetime, explicit physics type allow-list |
| Force fields | `configure_force_field` | Existing object or explicit Blender effector creation, bounded type/strength/noise |
| Fluid domain baseline | `configure_fluid_domain` | Domain modifier setup and bounded resolution/cache mode; full solver orchestration remains future work |

Wave 4 does not add a new MCP tool, external solver/provider integration, dashboard, or speculative fluid bake action. Every mutation remains a canonical action routed through the existing dispatcher and Blender gateway; any future long-running bake extension must reuse `modules/job`.

#### Wave 4 implementation status

| Capability | Implemented actions | Verification |
|---|---|---|
| Simulation state and cache | `get_simulation_state`, `get_simulation_cache_status` | Contract/unit tests and Blender 4.0.2 smoke: particle, force-field, fluid modifier, and cache summaries |
| Particle systems | `configure_particle_system` | Bounds and physics-type allow-list tests; Blender smoke: create, inspect, and disable a NEWTON system |
| Force fields | `configure_force_field` | Bounds and type tests; Blender smoke: create a WIND effector bound to a mesh and remove it safely |
| Fluid domain baseline | `configure_fluid_domain` | Bounds and enum tests; Blender smoke: configure LIQUID domain at resolution 32 and disable it |

Wave 4 preserves the five-tool MCP surface and adds no private simulation registry. Fluid bake, external solvers, and progress/cancellation orchestration remain intentionally outside this wave.

### Wave 5 — Rigging and deformation foundations (proposed)

The current catalog has no canonical armature, pose-bone, constraint, shape-key, or deformation-state actions. Wave 5 should close that core Blender gap with a focused `modules/rigging` aggregate rather than expanding unrelated object or animation handlers.

| Capability | Proposed canonical actions | Boundary |
|---|---|---|
| Armature inspection | `inspect_armature` | Bounded bones, parent relationships, deform flags, and pose summary |
| Pose control | `set_pose_bone_transform` | One named pose bone; bounded location, Euler rotation, or scale updates |
| Constraints | `configure_bone_constraint` | Allow-listed constraint types and validated target/subtarget references |
| Shape keys | `configure_shape_key` | Create/update one named shape key with bounded value and slider limits |
| Deformation inspection | `get_deformation_state` | Bounded armature modifiers, constraints, and shape-key summary |

Wave 5 non-goals are automatic weighting, weight-paint workflows, retargeting, driver graph authoring, full IK solving, B-Bone authoring, and external rig formats. The five-tool MCP surface remains unchanged, and every action requires a real Blender runtime handler plus contract and smoke coverage before it is accepted.

#### Wave 5 implementation status

| Capability | Implemented actions | Verification |
|---|---|---|
| Armature inspection | `inspect_armature` | Blender 4.0.2 smoke: two-bone hierarchy, parent/child relation, deform flags, and pose summary |
| Pose control | `set_pose_bone_transform` | Unit bounds and Blender smoke: Child bone Euler rotation plus invalid vector error |
| Constraints | `configure_bone_constraint` | Allow-list contract and Blender smoke: `COPY_ROTATION` with target object, then safe removal |
| Shape keys | `configure_shape_key` | Slider/value bounds and Blender smoke: create, inspect, and remove `Smile` key |
| Deformation inspection | `get_deformation_state` | Blender smoke: armature modifier, pose constraint, and shape-key summary |

Wave 5 preserves the five-tool MCP surface and does not add private rigging state. The accepted implementation is limited to explicit Blender data-block mutations and bounded inspection; automatic weighting, IK solving, retargeting, drivers, and external rig formats remain future scope.

### Wave 6 — Render and viewport completion (planned)

Wave 6 should complete the existing Render/Viewport FRD rather than create another broad feature pack. Camera configuration, frame rendering, and render settings already have canonical runtime coverage. The remaining audited gap is the unconnected viewport capture and HDRI lighting contract.

| Capability | Proposed canonical action | Boundary |
|---|---|---|
| Viewport capture | `get_viewport_screenshot` | Validated output path, bounded dimensions, shading mode, overlays, and optional focus object |
| HDRI lighting | `configure_hdri_lighting` | Asset-feature-resolved local HDRI, bounded strength/rotation, world-node setup, and lighting-only/visible policy |

Wave 6 acceptance requires a real Blender handler for both actions, security path validation, artifact references rather than raw image payloads, graceful background-context behavior, unit/contract tests, Blender smoke verification, and unchanged five-tool MCP surface. Existing `configure_camera`, `render`, and `set_render_settings` actions remain regression targets and are not duplicated.

Wave 6 non-goals are asset-provider implementation, arbitrary filesystem access, viewport UI automation, compositor redesign, external render farms, denoising algorithms, and new MCP tools. HDRI retrieval must reuse the existing asset/security boundary; the render action must reuse the existing job/capacity lifecycle for long-running work.

## Porting method

For each candidate implementation, maintain a small migration record containing the upstream URL, commit SHA, source file, license disposition, behavior being retained, Arwaky contract receiving it, and tests added. Porting proceeds in this order:

1. Extract behavior and invariants from the source.
2. Write or update the Arwaky FRD and shared protocol/VO/error/event contracts.
3. Implement through an AES capability and orchestrator.
4. Route Blender access only through gateway protocols.
5. Add the canonical dispatcher action schema and CLI mapping.
6. Add unit, contract, integration, security, and Blender smoke tests as appropriate.
7. Remove any competitor-specific surface assumptions, private globals, unbounded output, or duplicate configuration.
8. Record attribution and license notices when code is actually ported.

## Non-negotiable architecture gates

A migration is rejected when it:

- Adds a sixth MCP tool instead of a canonical action.
- Lets CLI or MCP call Blender or a feature implementation directly.
- Opens sockets, spawns Blender, or terminates Blender outside gateway/launcher ownership.
- Creates a domain-specific task store outside `modules/job`.
- Places business logic in `modules/shared`.
- Copies GPL implementation into the MIT core without an approved licensing decision.
- Introduces speculative actions without a real contract and runtime implementation.
- Exposes raw code, credentials, unrestricted filesystem paths, or oversized Blender payloads.
- Ports a full competitor surface merely to increase tool count.

## Quality gates and acceptance criteria

Every migrated wave must pass:

```bash
uv run pytest -q
uv run ruff check modules blender_mcp_addon scripts
uv run ruff format --check modules blender_mcp_addon scripts
git diff --check
uv run bandit -r modules blender_mcp_addon -x '*/tests/*' -ll -ii
```

The acceptance baseline is the current green suite of 1035 tests and at least 60% coverage. New capability work must add tests and must not introduce runtime artifacts such as `coverage.xml`, `registry.json`, or `launcher_state.json` into commits. Blender smoke tests must verify registration, runtime readiness, at least one successful mutation, structured error behavior, and clean shutdown for each new domain that touches Blender.

## Definition of done

A migrated capability is complete only when its FRD, contract taxonomy, implementation, root wiring, dispatcher schema, CLI/MCP help entry, tests, security review, source attribution, and changelog entry are complete. The feature must be reviewable as an Arwaky capability rather than as an embedded competitor subsystem.

## References

[1]: https://github.com/rakaarwaky/blender-arwaky/blob/develop/modules/shared/FRD.md "Shared layer boundary"
[2]: https://github.com/rakaarwaky/blender-arwaky/blob/develop/modules/gateway/FRD.md "Gateway transport boundary"
[3]: https://github.com/rakaarwaky/blender-arwaky/blob/develop/modules/job/FRD.md "Job lifecycle boundary"
[4]: https://github.com/rakaarwaky/blender-arwaky/blob/develop/modules/dispatcher/FRD.md "Dispatcher contract boundary"
