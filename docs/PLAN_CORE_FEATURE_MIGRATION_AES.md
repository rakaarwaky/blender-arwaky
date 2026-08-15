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

### Wave 3 — Specialized internal Blender domains

Add only after Wave 2 contracts are stable:

| New module | Core responsibility |
|---|---|
| `modules/compositor` | Compositor node graph inspection, mutation, and render output routing. |
| `modules/vse` | Sequence strips, channels, media references, transitions, and sequence render coordination. |
| `modules/physics` | Rigid body, cloth, fluid, particle/force settings, simulation bake, progress, and cancellation. |

Long-running compositor, VSE, and physics operations must use `modules/job`; no domain may create a private job registry.

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
