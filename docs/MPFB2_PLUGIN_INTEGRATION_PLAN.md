# Plan: AES Plugin Framework with MPFB 2 as the First Provider

## 1. Decision

Blender Arwaky will add a generic `plugin` feature module under `modules/plugin/`. This is an ordinary AES feature module and must follow all repository architecture, naming, import, orphan, and quality rules.

MPFB 2 will be the first concrete provider under the project-root `plugin/` directory:

```text
modules/plugin/        # AES feature module; strict architecture
plugin/mpfb2/          # provider-specific extension; flexible internal layout
```

The project will not copy MPFB 2 source code into `modules/` or treat MPFB 2 as a core dependency. The core application must remain usable when MPFB 2 is absent.

> `modules/plugin/` owns stable Arwaky contracts and orchestration. `plugin/mpfb2/` owns provider-specific translation to the externally installed MPFB 2 add-on.

This plan replaces all earlier plugin plans. No implementation work may continue until this plan is approved.

## 2. Rules that are not negotiable

The `modules/plugin/` feature must obey the seven-layer architecture in `ARCHITECTURE.md` and the complete AES rule set in `docs/RULES_AES.md`.

| Rule | Requirement for this plan |
|---|---|
| AES101–102 | Every Python file in `modules/plugin/src/` uses a valid layer prefix, a three-part name, and a valid layer suffix. |
| AES201–205 | Imports follow the bottom-up dependency direction. Contract imports taxonomy only; capabilities import taxonomy, contract protocols, and utility; agent imports taxonomy, contract, and utility; root composes all layers. |
| AES301–305 | Files remain focused, contain real definitions, avoid bypass comments and stubs, and do not duplicate provider mechanics. |
| AES401 | Taxonomy contains only domain VOs, constants, entities, events, and errors appropriate to the taxonomy layer. |
| AES402 | Contract signatures use taxonomy value objects/constants, not raw domain primitives or unbounded `Any`. |
| AES403 | Each capability implements a contract protocol, contains no more than three type declarations, and does not import another capability. |
| AES404 | Utilities, if required, are stateless standalone functions and depend only on taxonomy. |
| AES405 | The orchestrator implements an aggregate, uses contract protocols, contains no `Any` annotations, and does not import concrete capabilities. |
| AES406 | No new surface is introduced until a user-facing action is approved; any future smart surface must use the aggregate. |
| AES501–506 | Every taxonomy, contract, capability, agent, and surface file is inbound-wired and reachable through a root container or approved entry point. |

The plugin directory is outside the AES `modules/` source tree and may use provider-specific filenames and structure. Nevertheless, every provider must implement the stable plugin contract and must not bypass the dispatcher, MCP surface, CLI surface, validation, redaction, response envelope, tracking metadata, or destructive-action confirmation.

## 3. Non-goals

This phase will not copy, vendor, or fork MPFB 2. It will not introduce a `modules/character/` feature. It will not expose arbitrary Blender Python through a plugin escape hatch. It will not add a generic `run` fallback, a provider shortcut, a second MCP tool, or a parallel CLI path.

This phase will not add public MPFB2 actions to the 75-action core catalog until the provider contract, parameter schemas, runtime behavior, and Blender integration tests are approved. A provider being installed is not sufficient evidence that a capability is safe or ready for the public catalog.

## 4. Target AES module layout

The initial target layout is deliberately limited to valid AES layer filenames. No `schema_`, `service_`, `registry_`, or `adapter_` layer prefixes may be introduced under `modules/plugin/src/`.

```text
modules/plugin/
├── src/
│   ├── __init__.py
│   ├── taxonomy_plugin_vo.py
│   ├── taxonomy_plugin_constant.py
│   ├── contract_plugin_registry_protocol.py
│   ├── contract_plugin_operation_protocol.py
│   ├── contract_plugin_aggregate.py
│   ├── capabilities_plugin_discovery.py
│   ├── capabilities_plugin_registry.py
│   ├── capabilities_plugin_operation.py
│   ├── agent_plugin_orchestrator.py
│   └── root_plugin_container.py
└── tests/
    ├── test_plugin_taxonomy.py
    ├── test_plugin_contract.py
    ├── test_plugin_capabilities.py
    ├── test_plugin_orchestrator.py
    └── test_plugin_container.py
```

The names above are targets, not permission to create all files indiscriminately. Each file must have a concrete inbound and outbound dependency reason before implementation.

## 5. Layer responsibilities and dependency direction

### 5.1 Taxonomy

`taxonomy_plugin_vo.py` will define stable value objects such as plugin identifier, provider type, semantic version, Blender version, capability identifier, action name, and compatibility status. `taxonomy_plugin_constant.py` will contain compile-time values such as provider categories and lifecycle states.

Taxonomy must not import contracts, capabilities, agents, roots, external provider code, Blender runtime modules, YAML parsers, filesystem code, or registry behavior.

### 5.2 Contract

Contract protocols will define behavior only. The initial contract split is:

| Contract | Responsibility |
|---|---|
| `contract_plugin_registry_protocol.py` | Register, unregister, list, and resolve provider capabilities using taxonomy types. |
| `contract_plugin_operation_protocol.py` | Discover, health-check, and execute one explicitly declared provider operation using taxonomy types. |
| `contract_plugin_aggregate.py` | Stable aggregate consumed by approved smart surfaces or the existing dispatcher composition. |

Contracts may import taxonomy only. They must not import MPFB 2, Blender `bpy`, concrete capability classes, filesystem readers, or runtime adapters.

### 5.3 Capabilities

Capabilities will implement the protocols and hold technical/provider state within their execution scope:

| Capability | Responsibility |
|---|---|
| `capabilities_plugin_discovery.py` | Discover provider manifests, check installation state, and evaluate Blender/provider compatibility. |
| `capabilities_plugin_registry.py` | Maintain the validated provider registry and expose only declared capabilities. |
| `capabilities_plugin_operation.py` | Invoke a declared provider operation through the contract and normalize success/error results. |

Capabilities must not import one another. Shared technical mechanics must become stateless utility functions only if the implementation proves they are reused. Concrete MPFB2 code must not be imported into this feature module.

### 5.4 Agent

`agent_plugin_orchestrator.py` will coordinate discovery, registry resolution, and operation execution through contract protocols. It will implement `contract_plugin_aggregate.py` and will not import concrete capability files.

The orchestrator will coordinate at least two subsystem concerns through contracts—provider resolution and operation execution—without implementing provider business logic, parsing manifest files, or calling Blender operators directly.

### 5.5 Root

`root_plugin_container.py` will be the composition boundary. It may instantiate concrete capabilities, connect them to protocols, construct the orchestrator aggregate, and expose the resulting aggregate to the existing application composition path.

The root must contain wiring only. It must not contain manifest parsing, compatibility policy, provider business rules, CLI parsing, or MCP registration logic.

### 5.6 Surface and dispatcher integration

No new MCP tool will be created. No direct CLI shortcut will be created. Public plugin actions may be added only through the existing canonical dispatcher and generated CLI/MCP mapping after a separate action-catalog decision.

Until that decision is approved, the plugin framework remains an internal capability registry and health/discovery component. This prevents an unreviewed dynamic plugin action from becoming a universal fallback.

## 6. Provider boundary: plugin/mpfb2

The first provider will live outside `modules/`:

```text
plugin/mpfb2/
├── plugin_manifest.yaml
├── plugin_entry.py
├── plugin_operations.py
└── README.md
```

The provider may use a structure appropriate to MPFB 2. It must implement the stable contract exposed by `modules/plugin`, declare its compatibility metadata, detect whether MPFB 2 is installed and enabled, and return normalized results. It may import provider-specific APIs and Blender runtime APIs only inside the provider boundary.

The provider must not:

1. import or register MCP tools directly;
2. create a CLI shortcut;
3. modify the core 75-action catalog without an approved schema change;
4. expose arbitrary Python execution;
5. make the core application fail when MPFB 2 is absent; or
6. copy MPFB 2 source code or assets into the Arwaky repository.

The provider must return explicit states for unavailable, inactive, incompatible, unsupported, failed, and successful operations. Missing MPFB 2 is a normal optional-provider state, not a startup exception.

## 7. Provider manifest and action boundary

The manifest is provider metadata, not a replacement for an AES taxonomy or contract. It must declare at least:

| Field | Meaning |
|---|---|
| Provider identifier | Stable provider identity used by the registry. |
| Provider version | Installed provider release. |
| Provider type | Blender add-on/provider category. |
| Blender compatibility | Minimum and, when known, maximum supported Blender version. |
| Entry point | Provider contract factory. |
| Capabilities | Explicit operation identifiers and schema versions. |

The first capability will be limited to a discovery-safe contract test. Character creation, rigging, parameter mutation, and export are future capabilities that require individual schemas and live Blender tests. They must not be represented as implemented merely because MPFB 2 can theoretically perform them.

## 8. Implementation waves

| Wave | Scope | Required outcome |
|---:|---|---|
| 0 | Plan and architecture review | This plan is approved; prior skeleton is removed or replaced; no code proceeds on the old structure. |
| 1 | Taxonomy and contracts | Valid AES taxonomy and protocols compile, use VO types, and have planned implementors. |
| 2 | Capabilities | Discovery, registry, and operation capabilities implement protocols without inter-capability imports. |
| 3 | Agent and root | Aggregate, orchestrator, and container are wired with correct dependency direction and no orphan findings. |
| 4 | MPFB2 provider | Provider manifest, discovery probe, compatibility handling, and bounded provider results work without MPFB2 installed. |
| 5 | Blender integration | With MPFB2 installed and enabled, a disposable Blender smoke test validates discovery and one approved operation. |
| 6 | Catalog decision | Only explicitly approved, fully schema-validated actions are added to the canonical catalog and generated surfaces. |
| 7 | Hardening | Documentation, packaging policy, license review, regression tests, and all AES/CI gates pass. |

## 9. Testing strategy

Tests must follow the same vertical slice as the architecture:

| Test class | Scope |
|---|---|
| Taxonomy tests | Value-object normalization and constant invariants. |
| Contract tests | Protocol signatures, aggregate behavior, and stable error/result types. |
| Capability tests | Discovery, duplicate registration, compatibility, allow-list enforcement, and normalized failures. |
| Agent tests | Orchestration through protocol doubles; no concrete capability imports. |
| Root/container tests | Wiring and aggregate reachability. |
| Provider tests | MPFB2 manifest and provider behavior without requiring MPFB2 installation. |
| Blender integration tests | Actual add-on discovery and one approved operation in a disposable Blender scene. |
| Surface parity tests | Only after catalog integration: CLI, MCP action, help, parameter validation, and error envelope parity. |

No test may satisfy a mandatory import through a dummy function or dead stub. No `NotImplementedError`, `TODO`, `FIXME`, `noqa`, `type: ignore`, or bypass comment may be used to silence a gate.

## 10. Acceptance criteria

Implementation may be considered complete only when all of the following are true:

1. `modules/plugin/` follows the seven-layer architecture and valid filename prefixes/suffixes.
2. `lint-arwaky-cli scan .` reports zero violations, including AES501–506 orphan checks.
3. Contract protocols use taxonomy VOs/constants and have real capability implementors.
4. Capabilities do not import one another and each is reachable through the root container.
5. The agent implements the aggregate, imports no concrete capability, uses no `Any`, and is wired by the root container.
6. The provider is outside `modules/`, optional, version-aware, and does not copy MPFB2 source or assets.
7. No MCP tool, CLI shortcut, universal fallback, or duplicate access path is introduced.
8. The existing 5-tool MCP surface and 75-action core catalog remain unchanged until a separate approved catalog change.
9. Focused tests, full tests, integration contracts, syntax, Ruff, Bandit, packaging, and AES gates pass.
10. A live Blender smoke test passes with MPFB2 installed and enabled, and the absent-provider path passes without MPFB2.
11. README remains user-facing; developer and architecture details stay in `CONTRIBUTING.md`, `ARCHITECTURE.md`, and this plan.
12. The implementation is reviewed against this plan before any merge to `develop`.

## 11. Review gate

The next action after approval is not to add character actions. It is to delete or replace the previously generated non-AES skeleton, implement Wave 1 taxonomy and contracts, run the focused architecture gate, and present the diff for review. No provider operation will be advertised as available until its contract, capability, wiring, and Blender integration evidence exist.
