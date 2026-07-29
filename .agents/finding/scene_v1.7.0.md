# Module: scene (v1.7.0)

This document contains the source code for module `scene` along with related and imported definitions from the `shared` module.

## File List

- [ARCHITECTURE.md](<ARCHITECTURE.md>)
- [modules/scene/FRD.md](<modules/scene/FRD.md>)
- [modules/scene/pyproject.toml](<modules/scene/pyproject.toml>)
- [modules/scene/src/__init__.py](<modules/scene/src/__init__.py>)
- [modules/scene/src/agent_scene_orchestrator.py](<modules/scene/src/agent_scene_orchestrator.py>)
- [modules/scene/src/capabilities_scene_operate_executor.py](<modules/scene/src/capabilities_scene_operate_executor.py>)
- [modules/scene/src/root_scene_container.py](<modules/scene/src/root_scene_container.py>)
- [modules/shared/src/common/__init__.py](<modules/shared/src/common/__init__.py>)
- [modules/shared/src/common/taxonomy_core_vo.py](<modules/shared/src/common/taxonomy_core_vo.py>)
- [modules/shared/src/scene/__init__.py](<modules/shared/src/scene/__init__.py>)
- [modules/shared/src/scene/contract_scene_aggregate.py](<modules/shared/src/scene/contract_scene_aggregate.py>)
- [modules/shared/src/scene/contract_scene_inspection.py](<modules/shared/src/scene/contract_scene_inspection.py>)
- [modules/shared/src/scene/contract_scene_operate_protocol.py](<modules/shared/src/scene/contract_scene_operate_protocol.py>)
- [modules/shared/src/scene/taxonomy_scene_command_vo.py](<modules/shared/src/scene/taxonomy_scene_command_vo.py>)
- [pyproject.toml](<pyproject.toml>)
- [README.md](<README.md>)

---

## File: ARCHITECTURE.md

````markdown
# Agentic Engineering System Architecture

## 1. Purpose

The Agentic Engineering System is a layered, AI-native architecture pattern. It keeps domain models stable, business logic readable, technical detail isolated, and layer boundaries explicit enough for both humans and AI agents to modify the system safely.

---

## 2. Workspace Organization

The architecture supports multi-language workspaces.

| Term               | Meaning                                                           |
| ------------------ | ----------------------------------------------------------------- |
| Project Workspaces | Project root containing all configuration and language members    |
| Workspace Member   | One self-contained crate, package, or module inside the workspace |
| Crates directory   | Rust workspace members                                            |
| Packages directory | TypeScript or JavaScript packages                                 |
| Modules directory  | Python modules or sub-projects                                    |

---

## 3. Naming Convention

File names must communicate three parts:

1. Layer as prefix
2. Concern as middle name
3. Role as suffix

The parts are joined by underscores, followed by the normal file extension for the language.

`layer_concern_role.rs/py/ts`

---

## 4. Vertical Slicing Folder Structure

The recommended folder structure follows this order:

#### Features member

_Example feature crate `crates|packages|modules/<name-features>/`_

```text
surface_<concern>_<role>.rs/py/ts                ← surface layer
capabilities_<concern>_<role>.rs/py/ts           ← capabilities layer
agent_<concern>_orchestrator.rs/py/ts            ← agent layer
```

Exceptions: `main.rs`, `lib.rs`, `mod.rs`, `__init__.py`, `index.ts`, `index.js`.

#### Shared member

`crates|packages|modules/shared/<common>or<domain-folder>`

```text
contract_<concern>_protocol.rs/py/ts             ← contract layer
contract_<concern>_aggregate.rs/py/ts            ← contract layer
taxonomy_<concern>_vo.rs/py/ts                   ← taxonomy layer
taxonomy_<concern>_event.rs/py/ts                ← taxonomy layer
taxonomy_<concern>_entity.rs/py/ts               ← taxonomy layer
taxonomy_<concern>_constant.rs/py/ts             ← taxonomy layer
utility_<concern>_<role>.rs/py/ts                ← utility layer
```

`shared` folder groups by domain. Use `shared/common/` for generic files.

---

## 5. Taxonomy Layer

### Purpose

Taxonomy is the domain foundation layer. It defines the stable language of the domain and must remain free from technical or behavioral concerns.

### Components

| Role         | Meaning                               |
| ------------ | ------------------------------------- |
| Value object | Immutable data concept                |
| Entity       | Stateful domain concept with identity |
| Event        | Immutable domain fact                 |
| Error        | Domain-level error                    |
| Constant     | Compile-time literal value            |

### Dependencies

Taxonomy depends on nothing.

### Special Rules

- Value objects and Constants may use all primitive types.
- Entities, Events, and Errors must use Value objects/Constants instead of primitive types (bool/str is an exception).
- Constants must be compile-time values.
- Taxonomy must not contain business rules, infrastructure, or imports from other layers.

---

## 6. Contract Layer

### Purpose

Contract defines the public behavior of the system without exposing implementation. It allows callers to depend on stable interfaces instead of concrete logic.

### Components

| Role      | Meaning                                                                                           |
| --------- | ------------------------------------------------------------------------------------------------- |
| Protocol  | Interface defining inbound behavior. It is implemented by Capabilities and consumed by the Agent. |
| Aggregate | Facade definition implemented by Agent, used by Surface to access feature behavior.               |

### Dependencies

Contract may depend on Taxonomy only.

### Special Rules

- Protocol defines behavior only without implementation.
- Aggregate hides Capabilities from Surface.

---

## 7. Utility Layer

### Purpose

Utility contains low-level technical mechanics. It exists so that Capabilities can remain clean and expressive.

### Role Naming

Utility role suffixes are unlimited. The role name is chosen based on demand and must describe the technical responsibility and concern of the file.

parser
splitter
trimmer
slugifier
sanitizer
normalizer
extractor
replacer
converter
counter
resolver
detector
builder
joiner
serializer
deserializer
encoder
decoder
hasher
generator
formatter
comparator
differ
matcher
checker
calculator
mapper
merger
grouper
sorter
deduplicator
printer

### Dependencies

Utility may depend only on Taxonomy.

### Technical Concern Examples

| Concern                 | Responsibility                                      |
| ----------------------- | --------------------------------------------------- |
| File discovery          | Walk directories, detect files, apply ignore        |
| External tool execution | Run linters, compilers, formatters, analyzers       |
| Parsing and matching    | Parse text, match patterns, extract structured data |
| Path normalization      | Normalize paths across platforms                    |
| System operations       | Handle process or environment mechanics             |

### Special Rules

- Utility must use stateless standalone functions only.
- Utility must not contain stateful objects, behavior definitions, or contract implementations.
- Utility must not make business decisions.
- Utility may perform technical operations if needed.
- Utility must not implement any contract.
- Utility role names may expand freely, but the layer must remain technical and standalone.
- Utility must use stateless standalone functions only.

---

## 8. Capabilities Layer

### Purpose

Capabilities contain the concrete implementation of the system's behavior. This layer encapsulates both **pure business logic** (computations, validations) and **external adaptations** (database access, third-party API calls, infrastructure mechanics). By hiding these implementations behind Contracts, the system keeps its behavior modular, swappable, and fully isolated from orchestration.

### Role Naming

#### Internal Examples

validator
assessor
calculator
resolver
classifier
selector
mapper
transformer
policy
enricher
evaluator
analyzer
scorer
grader
ranker
filter
checker
reviewer
approver
rejector

#### External Examples

repository
gateway
client
provider
fetcher
reader
writer
scanner
executor
publisher
subscriber
adapter
connector
uploader
downloader
sender
receiver
dispatcher
watcher
monitor

### Dependencies

- Capabilities may depend on Taxonomy, Contract, and Utility.
- Capabilities must not depend on or import other Capabilities.

### Concern Examples

Capabilities generally handle two types of concerns:

| Category                | Concern        | Responsibility                                 |
| ----------------------- | -------------- | ---------------------------------------------- |
| **Business Logic**      | Validation     | Check domain conditions or input correctness   |
|                         | Computation    | Calculate scores, totals, or derived values    |
|                         | Transformation | Map, filter, reduce, or reshape data           |
|                         | Resolution     | Apply rules and decide outcomes                |
|                         | Assessment     | Judge severity, compliance, grade, or quality  |
| **External Adaptation** | Repository     | Fetch or persist domain entities to a database |
|                         | Integration    | Communicate with third-party services or APIs  |
|                         | Provider       | Generate data from external systems            |

### Special Rules

- **No Inter-Capability Dependency:** Capabilities must never import or call other Capabilities directly. They are standalone execution units.
- **Pipeline Aggregation:** Multiple Capabilities (e.g., Capability A for data fetching, Capability B for business calculation) are designed to be composed into a sequential pipeline by the **Agent Layer**, not by themselves.
- **Shared Logic Extraction (DRY):** If multiple Capabilities require the same technical mechanics or functions, that logic must be extracted into a reusable standalone function in the **Utility Layer**. Capabilities must not duplicate technical code (Don't Repeat Yourself).
- **Contract Implementation:** Capabilities must implement the `protocol_` defined in the Contract Layer.
- **State Ownership:** Capabilities are the owners of business and technical state within their execution scope.
- **Utility Delegation:** Capabilities must call Utility standalone functions when low-level technical operations are required, passing their state/data as arguments.
- **No Orchestration:** Capabilities must not contain flow control (looping across capabilities, branching between capabilities, or error escalation policy). They execute their single responsibility and return a result.
- **No Domain Definition:** Capabilities must not define domain models (Entities, Value Objects); they only consume and produce Taxonomy.

---

## 9. Agent Layer

### Purpose

Agent coordinates multiple capabilities into executable flows. It controls sequence and movement, not business calculation.

### Allowed Role

The only Agent role is orchestrator.

### Dependencies

Agent may depend only on Taxonomy, Contract, and Utility.

### Allowed Flow Control

| Flow Type               | Purpose                                |
| ----------------------- | -------------------------------------- |
| Sequential execution    | Run steps in order                     |
| Looping                 | Process multiple items or events       |
| Branching               | Choose path based on result            |
| Error handling          | Recover, abort, continue, or escalate  |
| Timeout or cancellation | Stop long-running or asynchronous work |

### Special Rules

- Agent must depend on Contract, not concrete implementations.
- Agent must not use and must be completely ignorant of Capabilities implementations.
- Agent must not calculate business results.
- Agent must not define domain models.

---

## 10. Surface Layer

### Purpose

Surface is the outer boundary of the system. It handles user-facing or external-facing interaction and translates it into architectural actions.

### Allowed Roles

Surface roles include:

- command
- controller
- page
- view
- component
- router
- layout
- hook
- store
- action
- screen

### Surface Groups

| Group            | Roles                             | Dependencies                          | Rule                                            |
| ---------------- | --------------------------------- | ------------------------------------- | ----------------------------------------------- |
| Smart surfaces   | command, controller, page, router | Taxonomy, Contract Aggregate, Utility | May initiate feature behavior through aggregate |
| Utility surfaces | hook, store, action, screen       | Taxonomy, Contract Aggregate, Utility | Support smart surfaces but must not import smart surfaces |
| Passive surfaces | component, view, layout           | Taxonomy only                         | Presentation-only, no logic or orchestration    |

### Special Rules

- Smart surfaces must consume Contract Aggregates.
- Surfaces must not import Capabilities, Utility, or Agent directly.
- Surfaces must not contain business calculation or orchestration.

---

## 11. Root Layer

### Purpose

Root is the composition layer. It assembles the system by connecting concrete implementations to contracts and starting the application.

### Components

| Role      | Meaning                                                                           |
| --------- | --------------------------------------------------------------------------------- |
| Container | Wires one feature by connecting Capabilities to Contract protocols and aggregates |
| Entry     | Bootstraps the application and composes feature containers                        |

### Dependencies

Root may depend on all layers.

### Special Rules

- Root may instantiate and wire components.
- Root must not contain business logic.
- Root must not contain orchestration policy.
- Root must not contain technical parsing or user interface behavior.
````

---

## File: modules/scene/FRD.md

```markdown

# FRD — Scene Management Feature

## Purpose

Manages scene-level inspection and bulk cleanup for **blender-arwaky**.

This feature owns scene-wide awareness and bulk operation policy. It is responsible for understanding the current state of the scene, summarizing scene contents, deciding which objects should be preserved during cleanup, and producing a cleanup report. Technical deletion of individual objects is delegated to the object feature.

The scene feature is policy-oriented and report-oriented, not a low-level object manipulation feature.

## Scope

- Inspect scene state
- Scene metadata summary
- Object summary by type and visibility
- Camera summary
- Light summary
- Active camera and active object awareness
- Render settings summary
- Collection summary
- Protected object awareness
- Bulk cleanup
- Preservation policy resolution
- Dry-run cleanup preview
- Cleanup reporting
- Deterministic filtering and ordering
- Event emission for inspection and cleanup completion
- Configuration-driven default preservation and dry-run behavior

## Out of Scope

- Single object create, read, update, or delete operations — owner: object feature
- Material detail management — owner: object feature
- Modifier detail management — owner: object feature
- Render execution — owner: render feature
- Asset import — owner: asset feature
- Queue management — owner: gateway feature
- Background task tracking — owner: job feature
- Long-running job polling — owner: job feature
- Network transport and Blender connectivity — owner: gateway feature
- Final licensing or usage compliance decisions — owner: higher-level product policy

## Depends On

- gateway feature for Blender command execution and connection state
- object feature for single-object deletion primitives and object reference resolution
- config feature for default preservation policy, dry-run default, inspection limits, and protection rules
- shared feature for common taxonomy, result envelope, and error category concepts

## Provides To

- dispatcher feature
- observability or diagnostics consumers when event and report data are exposed
- higher-level workflow or agent orchestration layers that need scene awareness

## Functional Requirements

### FR-SCN-001: Inspect Scene State

Scene returns an overview of current scene state.

- **Description**: Retrieve a structured summary of the active scene, including object count, camera list, light list, render settings summary, and scene metadata
- **Input**: Scene inspection request concept containing optional detail level, optional object filter, and optional inclusion flag for hidden objects
- **Output**: Scene inspection result concept containing success indicator, scene state summary, and message
- **Business Rules**:
  - Inspection is read-only and must not mutate scene state
  - Inspection must be idempotent
  - Scene state summary should include:
    - scene name or scene identifier
    - total object count
    - object count by type
    - visible object count
    - hidden object count when requested
    - camera list summary
    - light list summary
    - active camera reference
    - active object reference when available
    - render settings summary
    - resolution summary
    - render engine summary
    - frame range summary
    - unit system summary
    - collection summary
    - world or environment summary when available
    - protected object summary
  - Object list should be deterministic, ordered by stable object reference or object name
  - Hidden objects are excluded by default unless explicitly requested
  - Large scenes should support summarized detail level to avoid oversized response
  - Missing active camera or active object should be represented as empty reference, not as failure
  - Response should serialize safely and avoid cyclic references
  - Inspection may include capability flags indicating supported scene operations
- **Edge Cases**: Empty scene, no active object, no active camera, missing render engine information, large scene, hidden objects, linked objects, instanced objects, protected objects, stale object references, serialization limit, gateway not connected, inspection timeout
- **Error Handling**: Connection error when gateway is unavailable; timeout error when inspection exceeds configured limit; scene state error when scene cannot be safely inspected; delegated gateway error for Blender execution failure

### FR-SCN-002: Cleanup Scene Objects

Scene determines preservation policy and delegates actual deletion to object feature.

- **Description**: Remove objects from scene based on preservation policy, cleanup filter, and confirmation rules
- **Input**: Cleanup request concept containing cleanup mode, preservation list, optional object filter, dry-run flag, confirmation flag, child handling policy, dependent handling policy, and protected object policy
- **Output**: Cleanup report concept containing success indicator, removed object count, preserved object count, skipped object count, removed object references, preserved object references, skipped object references, dry-run indicator, and message
- **Business Rules**:
  - Scene feature owns policy resolution:
    - which objects are candidates for removal
    - which objects must be preserved
    - whether dry-run preview is active
    - whether confirmation is required
  - Object feature owns deletion execution:
    - resolving individual object reference
    - performing single-object deletion
    - handling low-level deletion constraints
    - reporting deletion outcome
  - Preservation policy may preserve:
    - camera objects
    - light objects
    - active camera
    - sole camera
    - objects marked protected
    - objects inside protected collections
  - Default preservation policy is resolved from configuration when request does not specify explicit policy
  - Dry-run mode must return cleanup preview without modifying scene
  - Dry-run report must use the same structure as actual cleanup report
  - Cleanup operation should be deterministic and repeatable for identical scene state and policy
  - Cleanup operation should return removed, preserved, and skipped object references
  - Cleanup operation should not remove world environment, render settings, or scene metadata unless explicitly extended by policy
  - Cleanup operation should support child handling policy:
    - delete hierarchy
    - detach children
    - reject cleanup when children exist
  - Cleanup operation should support dependent handling policy:
    - ignore dependents
    - reject cleanup when dependents exist
    - remove direct dependents when safe
  - Linked objects and instanced objects must be handled carefully to avoid unintended removal of shared data
  - Cleanup operation should be undo-aware when Blender undo capability is available
  - If undo capability is unavailable and operation is destructive, explicit confirmation is required
  - Cleanup operation may emit cleanup completion event after final report is produced
  - Partial failure must be reported clearly and should not be silently ignored
- **Edge Cases**: Scene already empty, only camera remaining, only light remaining, only protected objects remaining, linked objects, instanced objects, multi-user object data, active camera, locked objects, protected collections, hidden objects, objects with children, objects used as constraint targets, large scene, cleanup timeout, partial deletion failure, missing confirmation, dry-run with no removable objects
- **Error Handling**: Scene state error when scene is invalid for cleanup; protection error when protected object deletion is attempted without override; validation error for invalid cleanup mode or policy; confirmation error when destructive cleanup lacks required confirmation; delegated deletion error when object feature reports deletion failure

## Boundary: Scene vs Object

- Scene:

  - bulk operations
  - scene-wide inspection
  - preservation policy resolution
  - cleanup filtering
  - dry-run preview
  - cleanup reporting
  - protected object policy decisions
- Object:

  - single object technical operations
  - single object deletion execution
  - object reference resolution
  - low-level deletion constraints
  - object-level hierarchy handling as directed by scene policy
  - linked or instanced object safety at execution level

Conceptual separation:

- Scene cleanup request with preserve cameras enabled produces a preservation policy and cleanup report
- Object deletion request performs the actual removal of a single object reference

The scene feature decides what should happen.
The object feature executes the technical deletion safely.

## Error Categories

- scene state error — scene is in invalid state for requested operation
- protection error — attempted to delete protected object without valid override or confirmation
- validation error — invalid cleanup mode, invalid preservation policy, invalid filter, or invalid request concept
- confirmation error — destructive operation requires confirmation but confirmation was not provided
- delegated deletion error — object feature failed to delete one or more objects
- timeout error — scene inspection or cleanup exceeded configured time limit
- connection error — gateway or Blender execution channel is unavailable

## Events

- scene inspection completed event — emitted after scene inspection successfully produces scene state summary
- scene cleanup completed event — emitted after actual cleanup operation finishes and cleanup report is produced
- scene cleanup dry-run completed event — emitted after dry-run preview finishes and preview report is produced
- scene cleanup failed event — emitted when cleanup operation fails or partially fails

Event payloads should include:

- operation type
- success indicator
- summary counts
- dry-run indicator
- error category when failed
- correlation identifier when available

Event payloads should avoid full object dumps for large scenes and must avoid sensitive data.

## Configuration Keys


| Configuration Concept                | Description                                                                                            | Typical Default                                                           |
| -------------------------------------- | -------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| Default preservation list            | Default object categories preserved during cleanup when request does not specify explicit preservation | Preserve cameras and lights                                               |
| Default dry-run mode                 | Whether cleanup defaults to preview-only mode                                                          | Disabled                                                                  |
| Include hidden objects in inspection | Whether hidden objects are included in scene inspection by default                                     | Disabled                                                                  |
| Maximum inspection detail limit      | Limit for object detail returned during inspection to avoid oversized response                         | Configured safe limit                                                     |
| Protected object policy              | Rules for protecting active camera, sole camera, lights, and explicitly protected objects              | Active camera protected                                                   |
| Cleanup confirmation required        | Whether destructive cleanup requires explicit confirmation when undo is unavailable                    | Enabled                                                                   |
| Child handling default               | Default behavior for children of deleted objects                                                       | Detach children or reject when children exist, depending on safety policy |
| Dependent handling default           | Default behavior for dependents such as constraints or references                                      | Reject when dependents exist or handle only when safe                     |
| Cleanup timeout                      | Maximum allowed duration for cleanup operation before timeout category is returned                     | Configured timeout                                                        |

## QA Checklist

- [ ]  Scene inspection returns object summary
- [ ]  Scene inspection returns camera summary
- [ ]  Scene inspection returns light summary
- [ ]  Scene inspection returns render settings summary
- [ ]  Scene inspection returns active camera reference when available
- [ ]  Scene inspection handles empty scene gracefully
- [ ]  Scene inspection handles missing active camera gracefully
- [ ]  Scene inspection excludes hidden objects by default
- [ ]  Scene inspection includes hidden objects when explicitly requested
- [ ]  Scene inspection uses deterministic object ordering
- [ ]  Scene inspection supports summarized detail level for large scenes
- [ ]  Cleanup uses preservation policy
- [ ]  Cleanup preserves cameras when preservation policy requires it
- [ ]  Cleanup preserves lights when preservation policy requires it
- [ ]  Cleanup preserves active camera by default
- [ ]  Cleanup supports dry-run mode
- [ ]  Dry-run cleanup does not mutate scene
- [ ]  Dry-run cleanup returns same report structure as actual cleanup
- [ ]  Cleanup delegates actual deletion to object feature
- [ ]  Cleanup report includes removed object count
- [ ]  Cleanup report includes preserved object count
- [ ]  Cleanup report includes skipped object count
- [ ]  Cleanup report includes removed object references
- [ ]  Cleanup handles linked objects without removing shared data unintentionally
- [ ]  Cleanup handles instanced objects safely
- [ ]  Cleanup handles objects with children according to configured child policy
- [ ]  Cleanup handles protected objects according to configured protection policy
- [ ]  Cleanup without required confirmation returns confirmation error
- [ ]  Cleanup partial failure is reported clearly
- [ ]  No overlap with object feature for single-object technical operations
- [ ]  No overlap with render feature for render execution
- [ ]  No overlap with asset feature for asset import
- [ ]  No overlap with job feature for background task tracking
```

---

## File: modules/scene/pyproject.toml

```toml
[project]
name = "blender-arwaky-scene"
version = "1.6.5"
description = "BlenderArwaky scene feature module"
requires-python = ">=3.10"
license = {text = "MIT"}

[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
packages = ["."]
```

---

## File: modules/scene/src/__init__.py

```python
"""Scene feature module — AES implementation.

Layers:
  - Taxonomy (shared/src/scene/)   → SceneInfo, request/response VOs
  - Contract (shared/src/scene/)   → SceneOperateProtocol, SceneInspectionPort
  - Capabilities                   → SceneOperateExecutor, SceneInspectionAdapter
  - Agent                          → SceneOrchestrator
  - Root                           → SceneContainer (DI wiring)

Surface layer is intentionally absent — MCP/CLI command handlers live in
their respective feature modules (modules/mcp, modules/cli).
"""

from . import root_scene_container
from .root_scene_container import SceneContainer, create_scene_container

__all__ = [
    "SceneContainer",
    "create_scene_container",
    "root_scene_container",
]
```

---

## File: modules/scene/src/agent_scene_orchestrator.py

```python
"""Agent: Scene feature orchestrator.

Coordinates scene inspection and cleanup through the
SceneOperateProtocol capability layer.

FR-SCN-001, FR-SCN-002: Enhanced with preservation policy, dry-run, child/dependent handling.
Unified VO (merged request + response) — no split classes.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from modules.shared.src.scene.contract_scene_aggregate import ISceneAggregate
from modules.shared.src.scene.contract_scene_inspection import SceneInspectionPort
from modules.shared.src.scene.contract_scene_operate_protocol import SceneOperateProtocol
from modules.shared.src.scene.taxonomy_scene_command_vo import (
    SceneCleanupVO,
    SceneInspectionVO,
)

if TYPE_CHECKING:
    from modules.shared.src.scene.contract_scene_inspection import SceneInspectionPort

logger = logging.getLogger("BlenderMCPServer")


class SceneOrchestrator(ISceneAggregate):
    """Orchestrates scene operations via capability protocols.

    FR-SCN-001, FR-SCN-002: Enhanced with preservation policy, dry-run, child/dependent handling.
    Unified VO (merged request + response) — no split classes.
    """

    def __init__(
        self,
        executor: SceneOperateProtocol,
        inspector: SceneInspectionPort | None = None,
    ) -> None:
        self._executor = executor
        self._inspector = inspector

    async def get_scene_info(self, request: SceneInspectionVO) -> SceneInspectionVO:
        """Retrieve current scene metadata and object tree.

        FR-SCN-001: Supports detail level, hidden objects filter, object type filter.
        Returns unified VO with scene state summary (SceneStateSummaryVO).
        """
        return await self._executor.get_scene_info(request)

    async def cleanup_scene(self, request: SceneCleanupVO) -> SceneCleanupVO:
        """Execute cleanup of scene objects based on preservation policy.

        FR-SCN-002: Supports preservation modes (keep cameras, lights, both, remove all).
        Supports dry-run preview mode.
        Returns unified VO with removed/preserved/skipped counts and references.
        Same structure for actual cleanup and dry-run preview.
        """
        return await self._executor.cleanup_scene(request)

    async def get_scene_info_via_inspector(self, request: SceneInspectionVO) -> SceneInspectionVO:
        """Retrieve scene info via inspection port (fallback path).

        FR-SCN-001: Supports detail level, hidden objects filter.
        """
        if self._inspector is not None:
            return await self._inspector.get_scene_info(request)
        raise RuntimeError("No inspector available")

    async def cleanup_scene_via_inspector(self, request: SceneCleanupVO) -> SceneCleanupVO:
        """Execute cleanup via inspection port (fallback path).

        FR-SCN-002: Supports preservation modes (keep cameras, lights, both, remove all).
        """
        if self._inspector is not None:
            return await self._inspector.cleanup_scene(request)
        raise RuntimeError("No inspector available")
```

---

## File: modules/scene/src/capabilities_scene_operate_executor.py

```python
"""Capability: Scene operation executor.

Implements SceneOperateProtocol — handles scene inspection and cleanup
through the server module's code execution, with enhanced VOs, preservation
policy, dry-run preview, child/dependent handling, and protection rules.

FR-SCN-001: Enhanced inspection with detail level, hidden objects filter.
FR-SCN-002: Cleanup with preservation policy, dry-run, child/dependent handling.
Unified VO (merged request + response) — no split classes.
"""

from __future__ import annotations

import logging

from modules.shared.src.common.taxonomy_core_vo import (
    CoordinateList,
    ObjectCount,
    Prompt,
    ResolutionX,
    ResolutionY,
    RotationVector,
    ScaleVector,
    SuccessFlag,
)
from modules.shared.src.scene.contract_scene_operate_protocol import SceneOperateProtocol
from modules.shared.src.scene.taxonomy_scene_command_vo import (
    CameraInfoVO,
    CollectionSummaryVO,
    ObjectType,
    SceneCleanupVO,
    SceneInspectionVO,
    SceneStateSummaryVO,
)

logger = logging.getLogger("BlenderMCPServer")


class SceneOperateExecutor(SceneOperateProtocol):
    """Business logic for scene management (inspection, cleanup).

    FR-SCN-001: Enhanced inspection with detail level, hidden objects filter.
    FR-SCN-002: Cleanup with preservation policy, dry-run, child/dependent handling.
    """

    def __init__(self, code_executor: Prompt) -> None:
        """Initialize with a code executor capability from the server module.

        Args:
            code_executor: A callable or server capability that executes Python code.
        """
        if code_executor is None:
            raise ValueError("code_executor must be provided to SceneOperateExecutor")
        self._code_executor = code_executor

    async def cleanup_scene(self, request: SceneCleanupVO) -> SceneCleanupVO:
        """Execute cleanup of scene objects based on preservation policy.

        FR-SCN-002: Supports preservation modes (keep cameras, lights, both, remove all).
        Supports dry-run preview mode.
        Returns unified VO with removed/preserved/skipped counts and references.
        Same structure for actual cleanup and dry-run preview.
        """
        logger.info("Cleaning up scene (mode=%s, dry_run=%s)...", request.mode, request.dry_run)

        # Validation
        if not self._validate_request(request):
            return SceneCleanupVO(
                mode=request.mode,
                preservation_list=request.preservation_list,
                dry_run=request.dry_run,
                confirmation=request.confirmation,
                child_handling_policy=request.child_handling_policy,
                dependent_handling_policy=request.dependent_handling_policy,
                include_hidden_objects=request.include_hidden_objects,
                correlation_id=request.correlation_id,
                success=SuccessFlag(False),
                message=Prompt("Validation error: invalid cleanup mode"),
            )

        # Confirmation check for destructive operations
        if not request.dry_run and not request.confirmation:
            return SceneCleanupVO(
                mode=request.mode,
                preservation_list=request.preservation_list,
                dry_run=False,
                confirmation=False,
                child_handling_policy=request.child_handling_policy,
                dependent_handling_policy=request.dependent_handling_policy,
                include_hidden_objects=request.include_hidden_objects,
                correlation_id=request.correlation_id,
                success=SuccessFlag(False),
                message=Prompt("Confirmation error: destructive operation requires explicit confirmation"),
            )

        # Execute cleanup code
        try:
            if request.dry_run:
                result = await self._execute_dry_run(request)
            else:
                result = await self._execute_cleanup(request)
            return result
        except Exception as e:
            logger.error("Cleanup failed: %s", e)
            return SceneCleanupVO(
                mode=request.mode,
                preservation_list=request.preservation_list,
                dry_run=request.dry_run,
                confirmation=request.confirmation,
                child_handling_policy=request.child_handling_policy,
                dependent_handling_policy=request.dependent_handling_policy,
                include_hidden_objects=request.include_hidden_objects,
                correlation_id=request.correlation_id,
                success=SuccessFlag(False),
                message=Prompt(f"Cleanup failed: {e}"),
            )

    async def get_scene_info(self, request: SceneInspectionVO) -> SceneInspectionVO:
        """Retrieve current scene metadata and object tree.

        FR-SCN-001: Supports detail level, hidden objects filter, object type filter.
        Returns unified VO with scene state summary (SceneStateSummaryVO).
        """
        logger.info("Retrieving scene info (detail=%s)...", request.detail_level)

        try:
            code = self._build_inspection_code(request)
            result = await self._execute_code(code)

            # Parse the result into SceneStateSummaryVO
            scene_summary = self._parse_scene_info(result)

            return SceneInspectionVO(
                detail_level=request.detail_level,
                include_hidden_objects=request.include_hidden_objects,
                object_type_filter=request.object_type_filter,
                correlation_id=request.correlation_id,
                success=SuccessFlag(True),
                scene_state_summary=scene_summary,
                message=Prompt("Scene info retrieved successfully"),
            )
        except Exception as e:
            logger.error("get_scene_info failed: %s", e)
            return SceneInspectionVO(
                detail_level=request.detail_level,
                include_hidden_objects=request.include_hidden_objects,
                object_type_filter=request.object_type_filter,
                correlation_id=request.correlation_id,
                success=SuccessFlag(False),
                scene_state_summary=None,
                message=Prompt(f"Failed to get scene info: {e}"),
            )

    # ─── Helpers ────────────────────────────────────────────────

    def _validate_request(self, request: SceneCleanupVO) -> bool:
        """Validate cleanup request parameters."""
        valid_modes = {"all", "objects", "meshes"}
        if str(request.mode).lower() not in valid_modes:
            return False
        valid_child_policies = {"delete", "detach", "reject"}
        if request.child_handling_policy not in valid_child_policies:
            return False
        valid_dependent_policies = {"ignore", "reject", "remove_safe"}
        return request.dependent_handling_policy in valid_dependent_policies

    def _build_inspection_code(self, _request: SceneInspectionVO) -> str:
        """Build Blender Python code for scene inspection."""
        lines = [
            "import bpy",
            "scene = bpy.context.scene",
            "",
            "# Build object summary",
            "objects_by_type = {}",
            "visible_count = 0",
            "hidden_count = 0",
            "cameras = []",
            "lights = []",
            "active_camera_name = ''",
            "active_object_name = ''",
            "",
        ]

        # Object type counts and camera/light detection
        lines.append(
            "for obj in scene.objects:\n"
            "    obj_type = obj.type\n"
            "    objects_by_type[obj_type] = objects_by_type.get(obj_type, 0) + 1\n"
            "    if obj.hide_viewport:\n"
            "        hidden_count += 1\n"
            "    else:\n"
            "        visible_count += 1\n"
            "    if obj.type == 'CAMERA':\n"
            "        cameras.append({'name': obj.name, 'type': obj.data.type if hasattr(obj.data, 'type') else ''})\n"
            "    elif obj.type == 'LIGHT':\n"
            "        lights.append({'name': obj.name, 'light_type': obj.data.type if hasattr(obj.data, 'type') else ''})\n"
        )

        # Active camera and active object
        lines.append(
            "if scene.camera:\n"
            "    active_camera_name = scene.camera.name\n"
            "if scene.objects.active:\n"
            "    active_object_name = scene.objects.active.name\n"
        )

        # Render settings
        lines.extend(
            [
                "render_engine = ''",
                "res_x = 0",
                "res_y = 0",
                "frame_start = 1",
                "frame_end = 250",
                "unit_system = 'METRIC'",
                "",
                "if scene.render:\n"
                "    render_engine = scene.render.engine if hasattr(scene.render, 'engine') else ''\n"
                "    res_x = scene.render.resolution_x\n"
                "    res_y = scene.render.resolution_y\n"
                "if scene.frame_start is not None:\n"
                "    frame_start = scene.frame_start\n"
                "if scene.frame_end is not None:\n"
                "    frame_end = scene.frame_end\n",
            ]
        )

        # Collections
        lines.extend(
            [
                "collections = []",
                "for col in scene.collection.children_recursive:\n"
                "    collections.append({'name': col.name, 'object_count': len(col.objects)})\n",
            ]
        )

        # Output as JSON-compatible dict
        lines.extend(
            [
                "result = {",
                '    "scene_name": scene.name,',
                '    "total_object_count": len(scene.objects),',
                '    "visible_object_count": visible_count,',
                '    "hidden_object_count": hidden_count,',
                '    "object_type_counts": objects_by_type,',
                '    "cameras": cameras,',
                '    "lights": lights,',
                '    "active_camera_name": active_camera_name,',
                '    "active_object_name": active_object_name,',
                '    "render_engine": render_engine,',
                '    "resolution_x": res_x,',
                '    "resolution_y": res_y,',
                '    "frame_start": frame_start,',
                '    "frame_end": frame_end,',
                '    "unit_system": unit_system,',
                '    "collections": collections,',
                "}",
            ]
        )

        code = "\n".join(lines) + "\nprint(result)"
        return code

    def _parse_scene_info(self, result: str) -> SceneStateSummaryVO:
        """Parse inspection result into SceneStateSummaryVO.

        Guards against None or non-string result types before JSON parsing.
        """
        # Type guard — Blender code execution may return unexpected types
        if result is None:
            logger.warning("Scene info result is None; returning empty state")
            return SceneStateSummaryVO(
                scene_name="",
                total_object_count=ObjectCount(0),
                visible_object_count=ObjectCount(0),
                hidden_object_count=ObjectCount(0),
            )

        if not isinstance(result, str):
            logger.warning("Scene info result is non-string type %s; returning empty state", type(result).__name__)
            return SceneStateSummaryVO(
                scene_name="",
                total_object_count=ObjectCount(0),
                visible_object_count=ObjectCount(0),
                hidden_object_count=ObjectCount(0),
            )

        try:
            import json

            data = json.loads(result)

            # Parse cameras
            cameras = []
            for c in data.get("cameras", []):
                cameras.append(
                    CameraInfoVO(
                        name=c.get("name", ""),
                        type=ObjectType("CAMERA"),
                        location=CoordinateList([0.0, 0.0, 0.0]),
                        rotation=RotationVector([0.0, 0.0, 0.0]),
                        scale=ScaleVector([1.0, 1.0, 1.0]),
                        data_type=c.get("type", ""),
                    )
                )

            # Parse collections
            collections = []
            for c in data.get("collections", []):
                collections.append(
                    CollectionSummaryVO(
                        name=c.get("name", ""),
                        object_count=ObjectCount(c.get("object_count", 0)),
                    )
                )

            return SceneStateSummaryVO(
                scene_name=data.get("scene_name", ""),
                total_object_count=ObjectCount(data.get("total_object_count", 0)),
                visible_object_count=ObjectCount(data.get("visible_object_count", 0)),
                hidden_object_count=ObjectCount(data.get("hidden_object_count", 0)),
                object_type_counts={k: ObjectCount(v) for k, v in data.get("object_type_counts", {}).items()},
                cameras=cameras,
                active_camera_name=data.get("active_camera_name", ""),
                active_object_name=data.get("active_object_name", ""),
                render_engine=data.get("render_engine", "CYCLES"),
                resolution_x=ResolutionX(data.get("resolution_x", 1920)),
                resolution_y=ResolutionY(data.get("resolution_y", 1080)),
                frame_start=data.get("frame_start", 1),
                frame_end=data.get("frame_end", 250),
                unit_system=data.get("unit_system", "METRIC"),
                collections=collections,
            )
        except Exception as e:
            logger.warning("Failed to parse scene info: %s", e)
            return SceneStateSummaryVO(
                scene_name="",
                total_object_count=ObjectCount(0),
                visible_object_count=ObjectCount(0),
                hidden_object_count=ObjectCount(0),
            )

    async def _execute_dry_run(self, request: SceneCleanupVO) -> SceneCleanupVO:
        """Execute dry-run cleanup preview without modifying scene."""
        logger.info("Dry-run cleanup (mode=%s)...", request.mode)

        # Generate code to count removable objects (without deleting)
        code = self._build_dry_run_code(request)

        try:
            result = await self._execute_code(code)
            data = self._parse_cleanup_result(result, dry_run=True)
            return SceneCleanupVO(
                mode=request.mode,
                preservation_list=request.preservation_list,
                dry_run=True,
                confirmation=False,
                child_handling_policy=request.child_handling_policy,
                dependent_handling_policy=request.dependent_handling_policy,
                include_hidden_objects=request.include_hidden_objects,
                correlation_id=request.correlation_id,
                success=SuccessFlag(True),
                removed_count=data["removed_count"],
                preserved_count=data["preserved_count"],
                skipped_count=data["skipped_count"],
                removed_object_references=data["removed_refs"],
                preserved_object_references=data["preserved_refs"],
                skipped_object_references=data["skipped_refs"],
                message=Prompt(f"Dry-run cleanup complete (mode={request.mode}): {data['removed_count']} removable"),
            )
        except Exception as e:
            logger.error("Dry-run failed: %s", e)
            return SceneCleanupVO(
                mode=request.mode,
                preservation_list=request.preservation_list,
                dry_run=True,
                confirmation=False,
                child_handling_policy=request.child_handling_policy,
                dependent_handling_policy=request.dependent_handling_policy,
                include_hidden_objects=request.include_hidden_objects,
                correlation_id=request.correlation_id,
                success=SuccessFlag(False),
                message=Prompt(f"Dry-run failed: {e}"),
            )

    async def _execute_cleanup(self, request: SceneCleanupVO) -> SceneCleanupVO:
        """Execute actual cleanup with preservation policy."""
        logger.info("Actual cleanup (mode=%s)...", request.mode)

        code = self._build_cleanup_code(request)

        try:
            result = await self._execute_code(code)
            data = self._parse_cleanup_result(result, dry_run=False)
            return SceneCleanupVO(
                mode=request.mode,
                preservation_list=request.preservation_list,
                dry_run=False,
                confirmation=True,
                child_handling_policy=request.child_handling_policy,
                dependent_handling_policy=request.dependent_handling_policy,
                include_hidden_objects=request.include_hidden_objects,
                correlation_id=request.correlation_id,
                success=SuccessFlag(True),
                removed_count=data["removed_count"],
                preserved_count=data["preserved_count"],
                skipped_count=data["skipped_count"],
                removed_object_references=data["removed_refs"],
                preserved_object_references=data["preserved_refs"],
                skipped_object_references=data["skipped_refs"],
                message=Prompt(f"Scene cleaned up successfully (mode={request.mode}): {data['removed_count']} removed"),
            )
        except Exception as e:
            logger.error("Actual cleanup failed: %s", e)
            return SceneCleanupVO(
                mode=request.mode,
                preservation_list=request.preservation_list,
                dry_run=False,
                confirmation=True,
                child_handling_policy=request.child_handling_policy,
                dependent_handling_policy=request.dependent_handling_policy,
                include_hidden_objects=request.include_hidden_objects,
                correlation_id=request.correlation_id,
                success=SuccessFlag(False),
                message=Prompt(f"Actual cleanup failed: {e}"),
            )

    def _build_dry_run_code(self, request: SceneCleanupVO) -> str:
        """Build dry-run code to count removable objects without deleting."""
        mode = str(request.mode).lower()
        preservation = list(request.preservation_list) if request.preservation_list else ["camera", "light"]

        lines = [
            "import bpy",
            "scene = bpy.context.scene",
            "",
            "removable = []",
            "preserved = []",
            "skipped = []",
            "",
        ]

        # Build preservation check
        if "camera" in preservation:
            lines.append("# Preserve cameras")
            lines.append("cameras = [o for o in scene.objects if o.type == 'CAMERA']")
            lines.append("for cam in cameras:")
            lines.append("    preserved.append(cam.name)")
            lines.append("")

        if "light" in preservation:
            lines.append("# Preserve lights")
            lines.append("lights = [o for o in scene.objects if o.type == 'LIGHT']")
            lines.append("for light in lights:")
            lines.append("    preserved.append(light.name)")
            lines.append("")

        # Count removable objects
        if mode == "all":
            lines.append(
                "for obj in scene.objects:\n"
                "    if obj.type not in ('CAMERA', 'LIGHT'):\n"
                "        removable.append(obj.name)\n"
                "    else:\n"
                "        preserved.append(obj.name)\n"
            )
        elif mode == "objects":
            lines.append(
                "for obj in scene.objects:\n"
                "    if obj.type not in ('CAMERA', 'LIGHT'):\n"
                "        removable.append(obj.name)\n"
            )
        else:  # meshes
            lines.append("for obj in scene.objects:\n    if obj.type == 'MESH':\n        removable.append(obj.name)\n")

        lines.extend(
            [
                "result = {",
                '    "removed_count": len(removable),',
                '    "preserved_count": len(preserved),',
                '    "skipped_count": 0,',
                '    "removed_refs": removable,',
                '    "preserved_refs": preserved,',
                '    "skipped_refs": [],}',
            ]
        )

        code = "\n".join(lines) + "\nprint(result)"
        return code

    def _build_cleanup_code(self, request: SceneCleanupVO) -> str:
        """Build actual cleanup code with preservation policy."""
        mode = str(request.mode).lower()

        lines = [
            "import bpy",
            "scene = bpy.context.scene",
            "",
            "removed_count = 0",
            "preserved_count = 0",
            "skipped_count = 0",
            "removed_refs = []",
            "preserved_refs = []",
            "skipped_refs = []",
            "",
        ]

        # Preserve cameras
        lines.extend(
            [
                "# Preserve cameras",
                "for obj in list(scene.objects):",
                "    if obj.type == 'CAMERA':",
                "        preserved_count += 1",
                "        preserved_refs.append(obj.name)",
            ]
        )

        # Preserve lights
        lines.extend(
            [
                "",
                "# Preserve lights",
                "for obj in list(scene.objects):",
                "    if obj.type == 'LIGHT':",
                "        preserved_count += 1",
                "        preserved_refs.append(obj.name)",
            ]
        )

        # Delete removable objects
        if mode == "all" or mode == "objects":
            lines.extend(
                [
                    "",
                    "# Remove non-preserved objects",
                    "for obj in list(scene.objects):",
                    "    if obj.type not in ('CAMERA', 'LIGHT'):",
                    "        bpy.data.objects.remove(obj, do_unlink=True)",
                    "        removed_count += 1",
                    "        removed_refs.append(obj.name)",
                ]
            )
        else:  # meshes
            lines.extend(
                [
                    "",
                    "# Remove mesh objects only",
                    "for obj in list(scene.objects):",
                    "    if obj.type == 'MESH':",
                    "        bpy.data.objects.remove(obj, do_unlink=True)",
                    "        removed_count += 1",
                    "        removed_refs.append(obj.name)",
                ]
            )

        lines.extend(
            [
                "",
                "result = {",
                '    "removed_count": removed_count,',
                '    "preserved_count": preserved_count,',
                '    "skipped_count": skipped_count,',
                '    "removed_refs": removed_refs,',
                '    "preserved_refs": preserved_refs,',
                '    "skipped_refs": skipped_refs,',
                "}",
            ]
        )

        code = "\n".join(lines) + "\nprint(result)"
        return code

    def _parse_cleanup_result(self, result: str, dry_run: bool) -> dict:  # noqa: ARG002 (unused, but called with keyword arg)
        """Parse cleanup result JSON into structured data."""
        try:
            import json

            data = json.loads(result)
            return {
                "removed_count": ObjectCount(data.get("removed_count", 0)),
                "preserved_count": ObjectCount(data.get("preserved_count", 0)),
                "skipped_count": ObjectCount(data.get("skipped_count", 0)),
                "removed_refs": data.get("removed_refs", []),
                "preserved_refs": data.get("preserved_refs", []),
                "skipped_refs": data.get("skipped_refs", []),
            }
        except Exception as e:
            logger.warning("Failed to parse cleanup result: %s", e)
            return {
                "removed_count": ObjectCount(0),
                "preserved_count": ObjectCount(0),
                "skipped_count": ObjectCount(0),
                "removed_refs": [],
                "preserved_refs": [],
                "skipped_refs": [],
            }

    async def _execute_code(self, code: str) -> str:
        """Execute Python code through the server module's code execution capability.

        Args:
            code: Python code string to execute in Blender.

        Returns:
            Result string from code execution.

        Raises:
            RuntimeError: If code execution fails.
        """
        if callable(self._code_executor):
            result = await self._code_executor(Prompt(code))
            if isinstance(result, str):
                logger.info("Code execution result: %s", result[:200])
                return result
            raise RuntimeError(f"Unexpected code_executor result type: {type(self._code_executor)}")
        else:
            raise RuntimeError(f"Unexpected code_executor type: {type(self._code_executor)}")

    def __repr__(self) -> str:
        return "SceneOperateExecutor()"
```

---

## File: modules/scene/src/root_scene_container.py

```python
"""Root layer: Dependency injection container for the scene feature.

Wires scene capabilities to the agent orchestrator and bootstraps the system.
Provides a single entry point to obtain a fully configured SceneOrchestrator.

FR-SCN-001, FR-SCN-002: Enhanced with preservation policy, dry-run, child/dependent handling.
"""

from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .agent_scene_orchestrator import SceneOrchestrator

logger = logging.getLogger("BlenderMCPServer")


class SceneContainer:
    """DI container that wires scene capabilities to the agent orchestrator.

    Thread-safe singleton pattern for shared scene management.
    All components are lazy-instantiated on first access.

    FR-SCN-001, FR-SCN-002: Enhanced with preservation policy, dry-run, child/dependent handling.
    """

    def __init__(self, code_executor: object) -> None:
        """Initialize with a code executor from the server module.

        Args:
            code_executor: A callable or server capability that executes Python code.
        """
        self._code_executor = code_executor
        self._lock = threading.Lock()
        self._orchestrator: SceneOrchestrator | None = None

    def get_orchestrator(self) -> SceneOrchestrator:
        """Return a fully wired SceneOrchestrator (singleton).

        Lazy-initializes all dependencies on first call.
        Subsequent calls return the same orchestrator instance.

        FR-SCN-001, FR-SCN-002: Enhanced with preservation policy, dry-run, child/dependent handling.
        """
        if self._orchestrator is not None:
            return self._orchestrator

        with self._lock:
            if self._orchestrator is not None:
                return self._orchestrator

            from .agent_scene_orchestrator import SceneOrchestrator
            from .capabilities_scene_operate_executor import SceneOperateExecutor

            executor = SceneOperateExecutor(self._code_executor)
            self._orchestrator = SceneOrchestrator(executor=executor)

        logger.info("Scene container fully wired")
        return self._orchestrator

    def shutdown(self) -> None:
        """Shut down scene components."""
        with self._lock:
            self._orchestrator = None

    def __repr__(self) -> str:
        return "SceneContainer()"


def create_scene_container(code_executor: object) -> SceneContainer:
    """Factory function to create a new scene container.

    Args:
        code_executor: A callable or server capability that executes Python code.

    Returns:
        Configured SceneContainer instance.
    """
    return SceneContainer(code_executor=code_executor)
```

---

## File: modules/shared/src/common/__init__.py

```python
"""Common domain — taxonomy types and contracts (cross-cutting).

Note: Contract modules are imported by the main src/__init__.py to avoid
circular dependencies between domain folders.
"""

from . import (
    taxonomy_app_config_vo,
    taxonomy_bounding_box_vo,
    taxonomy_command_catalog_constant,
    taxonomy_core_vo,
    taxonomy_domain_error,
    taxonomy_vector3d_vo,
)

__all__ = [
    "taxonomy_app_config_vo",
    "taxonomy_bounding_box_vo",
    "taxonomy_command_catalog_constant",
    "taxonomy_core_vo",
    "taxonomy_domain_error",
    "taxonomy_vector3d_vo",
]
```

---

## File: modules/shared/src/common/taxonomy_core_vo.py

```python
"""Core branded primitive types (NewType aliases) — taxonomy value objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, NewType
from uuid import UUID

# ============================================================
# ID TYPES
# ============================================================

UserId = NewType("UserId", str)
SceneId = NewType("SceneId", str)
AssetId = NewType("AssetId", str)
JobId = NewType("JobId", str)
HdriId = NewType("HdriId", str)
ObjectId = NewType("ObjectId", UUID)
ParentId = NewType("ParentId", str)

# ============================================================
# NAME TYPES
# ============================================================

ObjectName = NewType("ObjectName", str)
AssetName = NewType("AssetName", str)
ProviderName = NewType("ProviderName", str)
MaterialName = NewType("MaterialName", str)
ModifierName = NewType("ModifierName", str)
ActionName = NewType("ActionName", str)
WorkflowName = NewType("WorkflowName", str)
RuleName = NewType("RuleName", str)
SceneRuleSetName = NewType("SceneRuleSetName", str)

# ============================================================
# TYPE & ENUM TYPES
# ============================================================

ObjectType = NewType("ObjectType", str)
AssetType = NewType("AssetType", str)
RenderEngine = NewType("RenderEngine", str)
ImageFormat = NewType("ImageFormat", str)
PrimitiveType = NewType("PrimitiveType", str)
ExportFormat = NewType("ExportFormat", str)
JobState = NewType("JobState", str)
CleanupMode = NewType("CleanupMode", str)
AssetTypeFilter = NewType("AssetTypeFilter", str)

# ============================================================
# TEXT, URLS & MESSAGES
# ============================================================

Prompt = NewType("Prompt", str)
ErrorString = NewType("ErrorString", str)
SearchQuery = NewType("SearchQuery", str)
NextPageToken = NewType("NextPageToken", str)
ResultUrl = NewType("ResultUrl", str)
ThumbnailUrl = NewType("ThumbnailUrl", str)

# ============================================================
# NUMERIC LIMITS & METRICS
# ============================================================

MaxSize = NewType("MaxSize", int)
IterationCount = NewType("IterationCount", int)
PortNumber = NewType("PortNumber", int)
Host = NewType("Host", str)
SampleCount = NewType("SampleCount", int)
ResolutionX = NewType("ResolutionX", int)
ResolutionY = NewType("ResolutionY", int)
ObjectCount = NewType("ObjectCount", int)
AssetCount = NewType("AssetCount", int)
RenderSamples = NewType("RenderSamples", int)
MaxImageSize = NewType("MaxImageSize", int)
ResultLimit = NewType("ResultLimit", int)
LightStrength = NewType("LightStrength", float)
RenderTime = NewType("RenderTime", float)
Progress = NewType("Progress", float)

# ============================================================
# FLAGS
# ============================================================

EnabledFlag = NewType("EnabledFlag", bool)
SuccessFlag = NewType("SuccessFlag", bool)
UseDenoising = NewType("UseDenoising", bool)

# ============================================================
# COLLECTIONS & VECTORS
# ============================================================

StringList = NewType("StringList", list[str])
TagList = NewType("TagList", list[str])
AssetIdList = NewType("AssetIdList", list[str])
CoordinateList = NewType("CoordinateList", list[float])
ScaleVector = NewType("ScaleVector", list[float])
RotationVector = NewType("RotationVector", list[float])
ObjectIdList = NewType("ObjectIdList", list[UUID])
ChildrenIds = NewType("ChildrenIds", list[str])

# Surface-typed primitives (for handler param annotations)
SkillName = NewType("SkillName", str)
SectionRef = NewType("SectionRef", str)
ServerName = NewType("ServerName", str)
DomainRef = NewType("DomainRef", str)
FormatRef = NewType("FormatRef", str)
CapabilityRef = NewType("CapabilityRef", str)

# Exit code for CLI main() return codes
ExitCode = NewType("ExitCode", int)

# Pathing
FilePath = NewType("FilePath", str)
DirectoryPath = NewType("DirectoryPath", str)

# Config types (no raw primitives in contracts)
ConfigPath = NewType("ConfigPath", str)

# Additional VOs for AES006 compliance
CustomerUuid = NewType("CustomerUuid", str)
SessionId = NewType("SessionId", str)
Timestamp = NewType("Timestamp", float)
VersionString = NewType("VersionString", str)
PlatformName = NewType("PlatformName", str)
ToolName = NewType("ToolName", str)
DurationMs = NewType("DurationMs", float)
BlenderVersion = NewType("BlenderVersion", str)
StatusString = NewType("StatusString", str)
PythonCode = NewType("PythonCode", str)
TaskUuid = NewType("TaskUuid", str)
ScaleFactor = NewType("ScaleFactor", float)
ImageBytes = NewType("ImageBytes", bytes)
BBoxIntegers = NewType("BBoxIntegers", list[int])

# Server-specific VOs for request correlation
RequestId = NewType("RequestId", str)
QueueWaitMs = NewType("QueueWaitMs", float)
ProtocolVersion = NewType("ProtocolVersion", str)
AuthToken = NewType("AuthToken", str)

# Job retention types
MaxTasksCount = NewType("MaxTasksCount", int)

# Details type alias (used in error handling)
Details = dict[str, Any]

# ErrorMessage is an alias for ErrorString, used by capability layers
ErrorMessage = ErrorString

# BlenderObjectList placeholder (resolved at runtime)
BlenderObjectList = NewType("BlenderObjectList", list[Any])

# ============================================================
# CONFIGURATION METADATA (FR-CFG-001, FR-CFG-005)
# ============================================================

SourceLocation = NewType("SourceLocation", str | None)
ParseWarning = NewType("ParseWarning", str)
ValidationWarning = NewType("ValidationWarning", str)
OverrideCount = NewType("OverrideCount", int)


@dataclass(frozen=True)
class ConfigMetadata:
    """Immutable metadata about configuration loading (FR-CFG-001, FR-CFG-005).

    Frozen (hashable). Carries structural counts + source path only —
    never raw settings values or secrets.
    """

    source: SourceLocation | None = None
    exists: bool = False
    overrides: OverrideCount = 0
    parse_warnings: tuple[ParseWarning, ...] = field(default_factory=tuple)
    validation_warnings: tuple[ValidationWarning, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        # Normalize list inputs to immutable tuples.
        if isinstance(self.parse_warnings, list):
            object.__setattr__(self, "parse_warnings", tuple(self.parse_warnings))
        if isinstance(self.validation_warnings, list):
            object.__setattr__(self, "validation_warnings", tuple(self.validation_warnings))

    def to_dict(self) -> dict[str, Any]:
        """Serialize metadata for diagnostics (secrets excluded)."""
        return {
            "source": self.source,
            "exists": self.exists,
            "overrides": self.overrides,
            "parse_warnings": list(self.parse_warnings),
            "validation_warnings": list(self.validation_warnings),
        }
```

---

## File: modules/shared/src/scene/__init__.py

```python
"""Scene domain shared taxonomy constants and contracts."""

from .contract_scene_aggregate import ISceneAggregate
from .contract_scene_inspection import SceneInspectionPort
from .contract_scene_operate_protocol import SceneOperateProtocol
from .taxonomy_scene_constant import (
    CLEANUP_CONFIRMATION_REQUIRED,
    CLEANUP_TIMEOUT_SECONDS,
    DEFAULT_CHILD_HANDLING_POLICY,
    DEFAULT_DEPENDENT_HANDLING_POLICY,
    DEFAULT_DRY_RUN_MODE,
    DEFAULT_INCLUDE_HIDDEN_OBJECTS,
    DEFAULT_PRESERVATION_LIST,
    INSPECTION_TIMEOUT_SECONDS,
    MAX_INSPECTION_DETAIL_LIMIT,
    PROTECTED_OBJECT_POLICY_ACTIVE_CAMERA,
    PROTECTED_OBJECT_POLICY_LIGHTS,
    PROTECTED_OBJECT_POLICY_PROTECTED,
    PROTECTED_OBJECT_POLICY_SOLE_CAMERA,
)

__all__ = [
    "SceneInspectionPort",
    "SceneOperateProtocol",
    "ISceneAggregate",
    "CLEANUP_CONFIRMATION_REQUIRED",
    "CLEANUP_TIMEOUT_SECONDS",
    "DEFAULT_CHILD_HANDLING_POLICY",
    "DEFAULT_DEPENDENT_HANDLING_POLICY",
    "DEFAULT_DRY_RUN_MODE",
    "DEFAULT_INCLUDE_HIDDEN_OBJECTS",
    "DEFAULT_PRESERVATION_LIST",
    "INSPECTION_TIMEOUT_SECONDS",
    "MAX_INSPECTION_DETAIL_LIMIT",
    "PROTECTED_OBJECT_POLICY_ACTIVE_CAMERA",
    "PROTECTED_OBJECT_POLICY_LIGHTS",
    "PROTECTED_OBJECT_POLICY_PROTECTED",
    "PROTECTED_OBJECT_POLICY_SOLE_CAMERA",
]
```

---

## File: modules/shared/src/scene/contract_scene_aggregate.py

```python
"""Scene domain contract: scene aggregate (ABC).

Agent implements this aggregate. Surface layers depend on it.
Facade for scene operations: inspect, cleanup.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_scene_command_vo import SceneCleanupVO, SceneInspectionVO


class ISceneAggregate(ABC):
    @abstractmethod
    async def get_scene_info(self, request: SceneInspectionVO) -> SceneInspectionVO:
        ...

    @abstractmethod
    async def cleanup_scene(self, request: SceneCleanupVO) -> SceneCleanupVO:
        ...
```

---

## File: modules/shared/src/scene/contract_scene_inspection.py

```python
"""Scene domain contract: scene inspection port interface.

FR-SCN-001: Scene inspection with detail level, hidden objects filter, summary mode.
FR-SCN-002: Cleanup delegation to object feature.
Contract layer — pure ABC definitions, no implementation.
Unified VO (merged request + response) — no split classes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import ObjectName, Prompt
from .taxonomy_scene_command_vo import SceneCleanupVO, SceneInspectionVO


class SceneInspectionPort(ABC):
    """Port interface for inspecting the Blender scene.

    FR-SCN-001: Supports detail levels (minimal, standard, detailed, summary),
    hidden objects filter, object type filter.
    Returns unified VO with scene state summary.
    """

    @abstractmethod
    async def get_scene_info(self, request: SceneInspectionVO) -> SceneInspectionVO:
        """Get detailed information about the current Blender scene.

        FR-SCN-001: Supports detail level, hidden objects filter, object type filter.
        Returns unified VO with scene state summary (SceneStateSummaryVO).
        """
        pass

    @abstractmethod
    async def get_object_info(
        self, object_name: ObjectName
    ) -> Prompt:
        """Get detailed information about a specific object by name."""
        pass

    @abstractmethod
    async def cleanup_scene(self, request: SceneCleanupVO) -> SceneCleanupVO:
        """Remove objects from scene based on preservation policy.

        FR-SCN-002: Supports preservation modes (keep cameras, lights, both, remove all).
        Supports dry-run preview mode.
        Returns unified VO with removed/preserved/skipped counts and references.
        Same structure for actual cleanup and dry-run preview.
        """
        pass
```

---

## File: modules/shared/src/scene/contract_scene_operate_protocol.py

```python
"""Scene domain contract: scene operations protocol (ABC based).

FR-SCN-001, FR-SCN-002: Scene-level management with unified VOs.
Contract layer — pure ABC definitions, no implementation.
Unified VO (merged request + response) — no split classes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_scene_command_vo import (
    SceneCleanupVO,
    SceneInspectionVO,
)


class SceneOperateProtocol(ABC):
    """Protocol interface for scene-level management (cleanup, environment, metadata).

    FR-SCN-001: Enhanced inspection with detail level, hidden objects filter.
    FR-SCN-002: Cleanup with preservation policy, dry-run, child/dependent handling.
    Unified VO (merged request + response) — no split classes.
    """

    @abstractmethod
    async def cleanup_scene(
        self, request: SceneCleanupVO
    ) -> SceneCleanupVO:
        """Remove objects from scene based on preservation policy.

        FR-SCN-002: Supports preservation modes (keep cameras, lights, both, remove all).
        Supports dry-run preview mode.
        Returns unified VO with removed/preserved/skipped counts and references.
        Same structure for actual cleanup and dry-run preview.
        """
        pass

    @abstractmethod
    async def get_scene_info(
        self, request: SceneInspectionVO
    ) -> SceneInspectionVO:
        """Retrieve current scene metadata and object tree.

        FR-SCN-001: Supports detail level, hidden objects filter, object type filter.
        Returns unified VO with scene state summary (SceneStateSummaryVO).
        """
        pass
```

---

## File: modules/shared/src/scene/taxonomy_scene_command_vo.py

```python
"""Scene operation value objects — unified input/output per operation.

Each VO merges request (input) and response (output) into a single frozen dataclass.
Caller sets input fields; callee sets output fields. No split Request/Response classes.

Enhanced VOs per FRD:
- SceneCleanupVO: cleanup with preservation policy, dry-run, child/dependent handling → success/message
- SceneInspectionVO: inspection with detail level, hidden objects filter → scene state summary/message
- SceneStateSummaryVO: comprehensive scene state (used as output in SceneInspectionVO)

Each VO is immutable and self-contained; no separate Request/Response classes.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..common.taxonomy_core_vo import (
    CleanupMode,
    CoordinateList,
    ObjectCount,
    ObjectType,
    Prompt,
    ResolutionX,
    ResolutionY,
    RotationVector,
    ScaleVector,
    SuccessFlag,
)

# ─── Unified Operation VOs (merged request + response) ────────


@dataclass(frozen=True)
class SceneCleanupVO:
    """Scene cleanup — input and output in one VO.

    Input: mode, preservation_list, dry_run, confirmation, child_handling_policy,
           dependent_handling_policy, include_hidden_objects, correlation_id.
    Output: success, removed/preserved/skipped counts and references, message.
    Same structure for actual cleanup and dry-run preview.
    """
    # Input fields
    mode: CleanupMode = field(default=CleanupMode("all"))
    preservation_list: tuple[str, ...] = ()
    dry_run: bool = False
    confirmation: bool = False
    child_handling_policy: str = "detach"  # "delete", "detach", "reject"
    dependent_handling_policy: str = "reject"  # "ignore", "reject", "remove_safe"
    include_hidden_objects: bool = False
    correlation_id: str = ""

    # Output fields (set by capability)
    success: SuccessFlag = field(default=SuccessFlag(False))
    removed_count: ObjectCount = 0
    preserved_count: ObjectCount = 0
    skipped_count: ObjectCount = 0
    removed_object_references: list[str] = field(default_factory=list)
    preserved_object_references: list[str] = field(default_factory=list)
    skipped_object_references: list[str] = field(default_factory=list)
    message: Prompt = field(default_factory=lambda: Prompt(""))


@dataclass(frozen=True)
class SceneInspectionVO:
    """Scene inspection — input and output in one VO.

    Input: detail_level, include_hidden_objects, object_type_filter, correlation_id.
    Output: success, scene_state_summary (SceneStateSummaryVO), message.
    """
    # Input fields
    detail_level: str = "standard"  # "minimal", "standard", "detailed", "summary"
    include_hidden_objects: bool = False
    object_type_filter: tuple[str, ...] = ()
    correlation_id: str = ""

    # Output fields (set by capability)
    success: SuccessFlag = field(default=SuccessFlag(False))
    scene_state_summary: SceneStateSummaryVO | None = None
    message: Prompt = field(default_factory=lambda: Prompt(""))


# ─── Scene State Summary VOs ──────────────────────────────────


@dataclass(frozen=True)
class CameraInfoVO:
    """Camera object information.

    Output: object name, type, location, rotation, scale, data properties.
    """
    name: str = ""
    type: ObjectType = field(default_factory=lambda: ObjectType("CAMERA"))
    location: CoordinateList = field(default_factory=lambda: CoordinateList([0.0, 0.0, 0.0]))
    rotation: RotationVector = field(default_factory=lambda: RotationVector([0.0, 0.0, 0.0]))
    scale: ScaleVector = field(default_factory=lambda: ScaleVector([1.0, 1.0, 1.0]))
    data_type: str = ""  # e.g., "perspective", "orthographic"
    sensor_width: float = 36.0
    focal_length: float = 50.0


@dataclass(frozen=True)
class LightInfoVO:
    """Light object information.

    Output: object name, type, location, rotation, scale, data properties.
    """
    name: str = ""
    type: ObjectType = field(default_factory=lambda: ObjectType("LIGHT"))
    location: CoordinateList = field(default_factory=lambda: CoordinateList([0.0, 0.0, 0.0]))
    rotation: RotationVector = field(default_factory=lambda: RotationVector([0.0, 0.0, 0.0]))
    scale: ScaleVector = field(default_factory=lambda: ScaleVector([1.0, 1.0, 1.0]))
    light_type: str = ""  # e.g., "point", "spot", "area", "sun"
    strength: float = 1.0
    color: CoordinateList = field(default_factory=lambda: CoordinateList([1.0, 1.0, 1.0]))


@dataclass(frozen=True)
class CollectionSummaryVO:
    """Collection summary with object counts and structure.

    Output: collection name, object count, child collections.
    """
    name: str = ""
    object_count: ObjectCount = 0
    child_collection_count: ObjectCount = 0
    child_collections: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ProtectedObjectSummaryVO:
    """Protected object summary with protection reasons.

    Output: protected objects and their protection categories.
    """
    active_camera_name: str = ""
    sole_camera_name: str = ""
    light_count: ObjectCount = 0
    protected_objects: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SceneStateSummaryVO:
    """Comprehensive scene state summary.

    FR-SCN-001: Scene state summary includes object count, camera list,
    light list, render settings, collection summary, protected object summary.
    Object list is deterministic, ordered by stable object reference.
    """
    # Scene metadata
    scene_name: str = ""
    scene_identifier: str = ""

    # Object counts
    total_object_count: ObjectCount = 0
    visible_object_count: ObjectCount = 0
    hidden_object_count: ObjectCount = 0
    object_type_counts: dict[str, ObjectCount] = field(default_factory=dict)

    # Camera and light summaries
    cameras: list[CameraInfoVO] = field(default_factory=list)
    lights: list[LightInfoVO] = field(default_factory=list)

    # Active references
    active_camera_name: str = ""
    active_object_name: str = ""

    # Render settings
    render_engine: str = "CYCLES"
    resolution_x: ResolutionX = ResolutionX(1920)
    resolution_y: ResolutionY = ResolutionY(1080)
    frame_start: int = 1
    frame_end: int = 250
    frame_step: int = 1
    unit_system: str = "METRIC"

    # Collections
    collection_count: ObjectCount = 0
    collections: list[CollectionSummaryVO] = field(default_factory=list)

    # Protected objects
    protected_object_summary: ProtectedObjectSummaryVO = field(default_factory=ProtectedObjectSummaryVO)

    # Capability flags
    capability_flags: dict[str, bool] = field(default_factory=dict)

    # Message
    message: str = ""


```

---

## File: pyproject.toml

```toml
[project]
name = "blender-arwaky"
version = "1.7.0"
description = "Blender integration through the Model Context Protocol"
readme = "README.md"
requires-python = ">=3.10"
authors = [
    {name = "rakaarwaky", email = "arwaky90@gmail.com"}
]
license = {text = "MIT"}
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
dependencies = [
    "mcp[cli]>=1.3.0",
    "tomli>=2.0.0",
    "python-dotenv>=1.0.0",
    "pyyaml>=6.0.3",
    "pillow>=12.2.0",
]

[project.optional-dependencies]
test = [
    "pytest>=9.0.3",
    "pytest-asyncio>=1.3.0",
    "pytest-cov>=7.1.0",
    "pytest-mock>=3.15.1",
    "requests>=2.31.0",  # Used by blender_mcp_addon modules (bundled with Blender at runtime)
]
lint = [
    "ruff>=0.11.0",
    "mypy>=1.15.0",
    "bandit>=1.8.0",
]
dev = [
    "blender-arwaky[test]",
    "blender-arwaky[lint]",
]

[dependency-groups]
test = ["blender-arwaky[test]"]
lint = ["blender-arwaky[lint]"]
dev = ["blender-arwaky[dev]"]

[project.scripts]
blender-arwaky = "modules.cli.src.surface_cli_main:main"
blender-mcp = "modules.root_mcp_entry:main"

[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["."]
include = ["modules*", "blender_mcp_addon*"]
exclude = ["*.tests", "tests*", "log*", "plugin*"]

[project.urls]
"Homepage" = "https://github.com/rakaarwaky/blender-arwaky"
"Bug Tracker" = "https://github.com/rakaarwaky/blender-arwaky/issues"

[tool.ruff]
line-length = 120
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "SIM", "ARG", "RUF100"]
ignore = ["E501"]

# Blender API contracts: class names (N801), argument names (N803/ARG001/ARG002),
# and Hunyuan API field names (N806) are dictated by external APIs.
[tool.ruff.lint.per-file-ignores]
"blender_mcp_addon/__init__.py"   = ["N801"]  # bl_info keys
"blender_mcp_addon/operators.py"  = ["N801"]  # Operator.bl_idname convention
"blender_mcp_addon/ui.py"         = ["N801", "ARG002"]  # Panel/AddonPreferences + context arg required by bpy
"blender_mcp_addon/polyhaven.py"  = ["B007"]  # `dirs` is required by os.walk contract
"blender_mcp_addon/sketchfab.py"  = ["B007"]  # `dirs` is required by os.walk contract
"blender_mcp_addon/properties.py" = []  # noqa already used inline

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "auto"

# ─── Pytest configuration ───────────────────────────────────────────────────
[tool.pytest.ini_options]
minversion = "9.0"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--tb=short",
    "--cov=src",
    "--cov=modules",
    "--cov=blender_mcp_addon",
    "--cov-report=term-missing",
    "--cov-report=html:htmlcov",
    "--cov-report=xml:coverage.xml",
]
markers = [
    "unit: Pure logic tests, no external dependencies",
    "integration: Layer interaction tests with real DI, mocked I/O",
    "functional: End-to-end command flows within project boundaries",
    "addon: Blender addon tests using bpy mock (tests/addon/)",
    "slow: Tests that take >1s to run",
    "asyncio: Async test marker (pytest-asyncio)",
]
asyncio_mode = "auto"

# ─── Coverage configuration ────────────────────────────────────────────────
[tool.coverage.run]
source = ["src", "modules", "blender_mcp_addon"]
branch = true
parallel = true
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/.*",
    "*/dist/*",
    "*/build/*",
    # Exclude external-API clients from global threshold.
    # They require recorded HTTP fixtures (vcrpy) to test meaningfully.
    "blender_mcp_addon/polyhaven.py",
    "blender_mcp_addon/sketchfab.py",
]

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
# Realistic current threshold — increase as tests mature.
# Excludes external-API modules (polyhaven, sketchfab)
# that require live network mocking to test.
fail_under = 60
exclude_lines = [
    "pragma: no cover",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.:",
    "\\.\\.\\.",
    "pass",
]
exclude_also = [
    "raise ImportError",
    "except ImportError",
    "@overload",
    "@abstractmethod",
]

```

---

## File: README.md

````markdown
# BlenderArwaky

> Connect Blender to AI agents through the Model Context Protocol.

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Blender 3.0+](https://img.shields.io/badge/Blender-3.0%2B-orange.svg)](https://www.blender.org/)

BlenderArwaky bridges [Blender 3D](https://www.blender.org/) with any MCP-compatible client — Claude Desktop, Cursor, Continue.dev, or custom agents. Control scenes, import assets, render, and execute Blender Python through 4 universal MCP tools.

## Prerequisites

- **Blender 3.0+** (tested on 5.1)
- **Python 3.10+**

## Quick Start

```bash
git clone https://github.com/rakaarwaky/blender-arwaky.git
cd blender-arwaky
uv sync
```

### Install Blender Addon

1. Blender → Edit → Preferences → Add-ons
2. Install `blender_mcp_addon/` directory
3. Enable **"Interface: Blender Arwaky"**

### Start MCP Server

```bash
uv run blender-mcp
```

### Configure MCP Client

```json
{
  "mcpServers": {
    "blender-arwaky": {
      "command": "uv",
      "args": ["--directory", "/path/to/blender-arwaky", "run", "blender-mcp"]
    }
  }
}
```

## Architecture

AES 7-layer architecture with full dependency inversion:

```
taxonomy → contract → capabilities → agent → surface → entry
                ↑
            infrastructure
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for full specification.

## Project Structure

```
modules/
├── shared/         ← Taxonomy + Contracts (FRD: modules/shared/FRD.md)
├── object/         ← Object operations (FRD: modules/object/FRD.md)
├── scene/          ← Scene management (FRD: modules/scene/FRD.md)
├── render/         ← Rendering + assets (FRD: modules/render/FRD.md)
├── telemetry/      ← Usage analytics (FRD: modules/telemetry/FRD.md)
├── job/            ← Job tracking (FRD: modules/job/FRD.md)
├── cli/            ← Standalone CLI (FRD: modules/cli/FRD.md)
├── root_mcp_entry.py
└── root_cli_entry.py
```

## Available Scripts

| Command | Description |
|---------|-------------|
| `uv run blender-mcp` | Start MCP server |
| `uv run blender-arwaky` | Run standalone CLI |
| `uv run pytest` | Run tests (455+) |
| `uv run pytest -m unit` | Unit tests only |
| `uv run ruff check .` | Lint code |
| `lint-arwaky-cli scan .` | AES architecture compliance |

## Configuration

```yaml
blender:
  executable_path: "/path/to/blender"
  host: "localhost"
  port: 9876

server:
  transport: "stdio"
  log_dir: "log"
```

| Env Var | Description |
|---------|-------------|
| `BLENDERMCP_CONFIG_PATH` | Override config.yaml path |
| `BLENDERMCP_BLENDER.HOST` | Override Blender host |
| `BLENDERMCP_BLENDER.PORT` | Override Blender port |
| `BLENDERMCP_STRICT` | Enable v1.7.0 new enforcement (schema validation, 1 MiB size limit, `\` path escaping, strict ConfigTypeError, runtime overrides). Default OFF; flips ON in v1.8.0. |

## Testing

```bash
uv run pytest              # Full suite
uv run pytest -m unit      # Unit tests
uv run pytest -m integration  # Integration tests
```

## Documentation

- [PRD.md](PRD.md) — Product requirements (stakeholders)
- [ARCHITECTURE.md](ARCHITECTURE.md) — System architecture
- [SKILL.md](SKILL.md) — Agent usage reference
- [AGENT.md](AGENT.md) — Developer reference
- [TEST.md](TEST.md) — Testing guide
- [modules/\*/FRD.md](modules/shared/FRD.md) — Feature specs (engineers)

## License

[MIT License](LICENSE) — Originally by Siddharth Ahuja, extended by Raka Arwaky.
````

---

