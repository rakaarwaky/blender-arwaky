# Module: render (v1.7.0)

This document contains the source code for module `render` along with related and imported definitions from the `shared` module.

## File List

- [ARCHITECTURE.md](<ARCHITECTURE.md>)
- [modules/render/FRD.md](<modules/render/FRD.md>)
- [modules/render/pyproject.toml](<modules/render/pyproject.toml>)
- [modules/render/src/__init__.py](<modules/render/src/__init__.py>)
- [modules/render/src/agent_render_orchestrator.py](<modules/render/src/agent_render_orchestrator.py>)
- [modules/render/src/capabilities_camera_config.py](<modules/render/src/capabilities_camera_config.py>)
- [modules/render/src/capabilities_hdri_config.py](<modules/render/src/capabilities_hdri_config.py>)
- [modules/render/src/capabilities_render_operate_executor.py](<modules/render/src/capabilities_render_operate_executor.py>)
- [modules/render/src/root_render_container.py](<modules/render/src/root_render_container.py>)
- [modules/shared/src/common/__init__.py](<modules/shared/src/common/__init__.py>)
- [modules/shared/src/common/taxonomy_core_vo.py](<modules/shared/src/common/taxonomy_core_vo.py>)
- [modules/shared/src/render/__init__.py](<modules/shared/src/render/__init__.py>)
- [modules/shared/src/render/contract_camera_config_protocol.py](<modules/shared/src/render/contract_camera_config_protocol.py>)
- [modules/shared/src/render/contract_hdri_config_protocol.py](<modules/shared/src/render/contract_hdri_config_protocol.py>)
- [modules/shared/src/render/contract_render_aggregate.py](<modules/shared/src/render/contract_render_aggregate.py>)
- [modules/shared/src/render/contract_render_operate_protocol.py](<modules/shared/src/render/contract_render_operate_protocol.py>)
- [modules/shared/src/render/taxonomy_render_vo.py](<modules/shared/src/render/taxonomy_render_vo.py>)
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

## File: modules/render/FRD.md

```markdown
# FRD — Rendering & Viewport Feature

## Purpose

Manages screenshot, render, camera setup, and HDRI lighting for **blender-arwaky**.

This feature is the single authority for image production and camera optics. It captures the viewport, renders the scene to validated output locations, configures camera-specific behavior such as lens, framing, active camera selection, and depth of field, and applies HDRI-based environment lighting using files acquired through the asset feature.

Execution is delegated to Blender through the gateway feature. Output safety is delegated to the security policy feature. Long-running renders are tracked through the job feature. This feature owns rendering policy and camera optics only — never transport, download, or task lifecycle.

## Scope

- Viewport screenshot capture with configurable presets
- Scene render to output artifact
- Render settings management: resolution, samples, denoising, engine preference
- Camera configuration: lens, framing, active camera, depth of field
- HDRI environment lighting configuration
- Output file policy for render and screenshot artifacts
- Output path validation through security policy feature
- Background render submission through job feature
- Overwrite and uniqueness policy for output artifacts
- Render and capture observability events

## Out of Scope

- Asset download, owned by asset feature
- Generic object manipulation, owned by object feature
- Scene cleanup, owned by scene feature
- Background task lifecycle, owned by job feature
- Queue management, owned by gateway feature
- Path traversal protection, owned by security policy feature
- Object placement and transformation
- HDRI asset discovery and caching
- Cloud rendering services
- Video or animation sequence output

## Depends On

- gateway feature for Blender command transport and scene-mutating serialization
- security policy feature for output path validation and artifact safety
- job feature for long-running render tracking and capacity enforcement
- asset feature for HDRI file download and local availability
- config feature for output directory, format, timeout, and lighting defaults

## Provides To

- dispatcher feature

## Functional Requirements

### FR-RND-001: Capture Viewport Screenshot

Capture current viewport as image. Return file path.

- **Description**: Capture the current viewport as an image artifact, save it to a validated output location, and return the file reference
- **Input**: Screenshot request concept containing maximum size, view angle, shading mode, overlay visibility, optional focus object reference, image format, and output destination policy
- **Output**: Screenshot result concept containing success indicator, artifact file reference, image format, resolved dimensions, capture duration, and message
- **Business Rules**:
  - Output location must be validated through security policy feature before capture is written
  - Output location must reside inside allowed output directories
  - View angle must be one of the supported conceptual modes: perspective, orthographic, or active camera view
  - Shading mode must be one of the supported conceptual modes: wireframe, solid, material preview, or rendered
  - Overlay visibility must be configurable per request
  - Maximum image size must be enforced while preserving aspect ratio
  - Image format must be supported by the runtime and allowed by configuration
  - Focus object reference, when provided, must be resolved deterministically
  - Missing focus object follows configured policy: reject with scene validation indication, or ignore focus and continue capture
  - Capture is read-only with respect to scene content; temporary view adjustments required for capture must be restored afterward
  - If active viewport context is unavailable, capture may fall back to offscreen capture or active camera capture when supported, otherwise return clear limitation error
  - Existing artifact at destination follows configured overwrite policy: overwrite, reject, or create unique variant
  - Artifact should be written atomically where supported so partial files are not exposed as success
  - Result must return file reference rather than raw image payload
  - Capture metadata should include resolved width, height, format, shading mode, and duration
- **Edge Cases**: Empty viewport, focus object not found, unsupported image format, oversized viewport, no active 3D view context, headless runtime limitation, hidden focus object, locked view, unsupported shading mode, capture timeout, permission denied destination, existing artifact conflict, memory limit
- **Error Handling**: Render output error for invalid or unwritable destination; security violation error delegated from security policy feature for path validation failure; validation error for invalid capture parameters; timeout error when capture exceeds configured limit

### FR-RND-002: Render Scene Image

Render full scene image. Uses security for output path validation. Uses job for long-running renders. Uses diagnostics for metrics and logging.

- **Description**: Render the scene to an image artifact at a validated output location, submitting long-running renders through the job feature
- **Input**: Render request concept containing output destination, resolution width and height, sample count, denoising flag, render engine preference, color mode, transparency flag, optional camera reference, overwrite policy, timeout, and background execution policy
- **Output**: Render result concept containing success indicator, artifact file reference, render time, render statistics, final resolution, and message; or task reference when submitted as background render
- **Business Rules**:
  - Output destination must be validated through security policy feature before render begins
  - Output destination must reside inside allowed output directories
  - Resolution and sample count must fall within configured bounds
  - Denoising is optional and must degrade gracefully when unsupported by active engine
  - Render engine preference may be specified but must fall back to an available engine when the requested engine is unavailable
  - Active camera must exist or be resolvable; missing camera may trigger camera configuration when policy allows, otherwise return scene state indication
  - Expected long-running render must be submitted through job feature and return task reference instead of blocking
  - Capacity exhaustion from job feature propagates as capacity error without partial render side effects
  - Render should write to temporary artifact first and finalize only after successful completion where supported
  - Existing artifact at destination follows configured overwrite policy
  - Cancellation of background render is best-effort due to main-thread execution constraints
  - Render statistics should include render time, resolution, sample count, engine used, and denoising status
  - Render completion, failure, and background submission must emit observability events for diagnostics composition
  - Output artifact reference must not expose sensitive filesystem detail beyond allowed diagnostic metadata
- **Edge Cases**: Invalid output destination, permission denied, output directory missing, render timeout, denoising unsupported, no active camera, empty scene, unsupported render engine, out of memory, existing artifact conflict, very high resolution, transparent background unsupported, canceled render, background capacity full, connection lost during render
- **Error Handling**: Render output error for invalid destination or output failure; security violation error delegated from security policy feature; capacity error delegated from job feature; timeout error for exceeded render duration; scene state error for missing camera or invalid scene condition; execution error delegated from gateway for render failure

### FR-RND-003: Configure Camera

Set camera lens, framing, active camera, depth of field. Render owns camera-specific setup. Object owns generic transform.

- **Description**: Configure camera-specific optical and selection behavior: lens, framing, active camera designation, and depth of field
- **Input**: Camera setup concept containing camera reference or creation policy, lens or focal length, sensor fit, optional framing target, active camera policy, and optional depth of field settings
- **Output**: Camera configuration result concept containing success indicator, resolved camera reference, final camera settings summary, active camera status, and message
- **Business Rules**:
  - Camera must be created if it does not exist and creation policy allows
  - Camera resolution must be deterministic when multiple cameras exist:
    - prefer explicit camera reference
    - fall back to active scene camera
    - fall back to first available camera when policy allows
  - If no camera exists and creation is disallowed, return camera setup failure with scene state indication
  - Lens or focal length values must fall within configured valid range
  - Camera may be designated as active scene camera when policy requests
  - Locked or protected camera state must be respected unless explicit override is allowed
  - Depth of field settings may include enablement, focus distance or focus object reference, and aperture control
  - Framing target may adjust camera orientation while preserving requested lens settings
  - Camera configuration must not modify shared or linked camera data unless explicitly allowed
  - Generic positional transformation of camera objects belongs to object feature and must not be duplicated here
  - Result must return resolved camera reference and final configuration state
- **Edge Cases**: Multiple cameras, locked camera, invalid lens values, missing camera reference with creation disallowed, linked camera data, camera constraint overriding configuration, incompatible camera type, creation not permitted, focus object not found for depth of field, unsupported depth of field in current engine
- **Error Handling**: Camera setup error when configuration cannot be applied; validation error for invalid lens, sensor, or depth of field parameters; scene state error for missing camera when creation disallowed; protection or lock error when camera cannot be modified without override

### FR-RND-004: Configure HDRI Lighting

Set HDRI environment lighting. Render does not download HDRI itself — uses asset feature to get HDRI file.

- **Description**: Apply HDRI-based environment lighting to the scene using a locally available HDRI file acquired through the asset feature
- **Input**: HDRI setup concept containing HDRI asset reference, strength, rotation, background visibility policy, and environment overwrite policy
- **Output**: Environment result concept containing success indicator, resolved environment reference, applied strength, applied rotation, and message
- **Business Rules**:
  - Render feature must never download HDRI files itself
  - HDRI acquisition follows a two-step conceptual flow:
    - HDRI file acquisition is requested through the asset feature download operation, producing a local file reference
    - HDRI lighting configuration is then requested through this feature using the local file reference and lighting settings
  - If HDRI asset is not locally available, request must delegate acquisition to asset feature before lighting configuration proceeds
  - HDRI strength must fall within configured valid range, default conceptual range zero to ten
  - HDRI rotation must be normalized according to configured angle convention
  - Existing scene environment follows configured overwrite policy: replace environment, update existing environment, or reject if environment exists
  - Environment lighting should apply to scene world or equivalent environment concept
  - If scene world does not exist, one should be created when policy allows
  - Background visibility policy controls whether HDRI appears as visible background or contributes lighting only
  - Non-environment lighting objects must be preserved unless explicitly replaced
  - Local HDRI file reference must be validated through security policy feature before use
  - Result must return resolved environment reference and final applied settings
- **Edge Cases**: HDRI asset not found, download failed, unsupported HDRI format, existing environment conflict, strength out of range, rotation overflow, missing scene world, linked world data, provider failure, asset cache unavailable, local file outside allowed directory, environment node incompatibility
- **Error Handling**: Asset not found error delegated from asset feature; provider error delegated from asset feature; validation error for invalid strength or rotation; environment state error for incompatible scene environment; security violation error when local file reference fails path validation

## Boundary: Render vs Object

- Render feature owns camera-specific setup:

  - lens and focal length configuration
  - framing and targeting behavior
  - active camera designation
  - depth of field configuration
  - sensor fit and optical properties
- Object feature owns generic transform:

  - location updates
  - rotation updates
  - scale updates
  - applied uniformly to any object type, including camera objects

Conceptual separation:

- Camera optical workflow such as lens, framing, active selection, and depth of field is requested through the render feature camera configuration operation
- Direct positional adjustment of a camera object is requested through the object feature generic transform operation

When a workflow requires both, higher layers compose render camera configuration for optical setup and object transform for positional adjustment, without either feature duplicating the other's responsibility.

## Error Categories

- render output error — render or screenshot output destination invalid, unwritable, or failed during artifact production
- camera setup error — camera configuration could not be applied
- security violation error — output path or file reference validation failed, delegated through security policy feature
- capacity error — background render capacity exceeded, delegated through job feature
- timeout error — capture or render exceeded configured duration
- validation error — invalid capture, render, camera, or lighting parameters
- asset not found error — HDRI asset unavailable, delegated from asset feature
- environment state error — scene environment incompatible with HDRI configuration
- scene state error — scene condition blocks operation, such as missing active camera

## Events

- viewport captured event — screenshot captured with format, dimensions, and artifact reference indicator
- scene render completed event — render finished with duration, resolution, sample count, and engine metadata
- scene render failed event — render failed with categorized error and phase metadata
- render submitted to background event — long-running render handed to job feature with task reference
- camera configured event — camera setup applied with resolved reference and settings summary
- HDRI lighting configured event — environment lighting applied with strength and rotation metadata

Event payloads should include:

- event category
- operation summary such as format, resolution, or camera reference
- tracking identifier when available
- duration metadata
- error category when failed
- task reference for background submission

Event payloads must avoid:

- raw image payloads
- full filesystem paths beyond redacted form
- sensitive asset credentials
- oversized render statistics dumps

## Configuration Keys


| Configuration Concept           | Description                                                                        | Typical Default                      |
| --------------------------------- | ------------------------------------------------------------------------------------ | -------------------------------------- |
| Default render output directory | Default validated directory for render and screenshot artifacts                    | Application-managed output directory |
| Screenshot file format          | Default image format for viewport capture                                          | Lossless raster format               |
| Maximum render time             | Upper bound for synchronous render before background submission or timeout         | Conservative render limit            |
| Default HDRI strength           | Environment lighting strength applied when request omits it                        | Moderate strength value              |
| Screenshot maximum size         | Upper bound for capture dimensions preserving aspect ratio                         | Conservative dimension limit         |
| Output overwrite policy         | Handling of existing artifact at destination: overwrite, reject, or unique variant | Unique variant                       |
| Resolution and sample bounds    | Allowed ranges for render resolution and sample count                              | Bounded conservative ranges          |
| Default denoising               | Whether denoising applies when request omits it                                    | Enabled when engine supports         |
| Default HDRI rotation           | Environment rotation applied when request omits it                                 | Zero rotation                        |
| Background render eligibility   | Whether long-running renders submit through job feature automatically              | Enabled                              |

## QA Checklist

- [ ]  Viewport screenshot captured and saved to validated output location
- [ ]  Screenshot returns file reference rather than raw payload
- [ ]  Screenshot respects view angle and shading mode settings
- [ ]  Screenshot enforces maximum size while preserving aspect ratio
- [ ]  Screenshot overlay visibility configurable
- [ ]  Screenshot focus object resolved or handled according to policy
- [ ]  Screenshot falls back or fails clearly when viewport context unavailable
- [ ]  Existing screenshot artifact handled according to overwrite policy
- [ ]  Scene render uses security for output path validation before render begins
- [ ]  Scene render produces artifact at validated destination
- [ ]  Render resolution and sample bounds enforced
- [ ]  Denoising degrades gracefully when unsupported
- [ ]  Engine preference falls back to available engine
- [ ]  Missing active camera triggers configuration or returns scene state indication
- [ ]  Long-running render tracked via job feature with task reference returned
- [ ]  Background capacity exhaustion surfaces as capacity error without partial side effects
- [ ]  Temporary artifact strategy prevents partial output exposed as success
- [ ]  Canceled background render reports best-effort status
- [ ]  Render statistics include duration, resolution, samples, engine, and denoising status
- [ ]  Camera-specific setup applies lens, framing, active designation, and depth of field
- [ ]  Camera resolution deterministic across multiple cameras
- [ ]  Camera creation follows configured policy
- [ ]  Locked camera respected without explicit override
- [ ]  Generic camera positional transform not duplicated by render feature
- [ ]  HDRI lighting uses asset feature for file download, never direct download
- [ ]  HDRI strength and rotation validated and normalized
- [ ]  Existing environment handled according to overwrite policy
- [ ]  Scene world created when missing and policy allows
- [ ]  Background visibility policy controls lighting-only versus visible background
- [ ]  Local HDRI file reference validated through security policy feature
- [ ]  No overlap with object feature for generic transform
- [ ]  No overlap with asset feature for download
- [ ]  No overlap with job feature for task lifecycle
- [ ]  Capture, render, camera, and HDRI events emitted for diagnostics composition
```

---

## File: modules/render/pyproject.toml

```toml
[project]
name = "blender-arwaky-render"
version = "1.6.5"
description = "BlenderArwaky render feature module"
requires-python = ">=3.10"
license = {text = "MIT"}

[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
packages = ["."]
```

---

## File: modules/render/src/__init__.py

```python
"""Render feature module — AES implementation.

Layers:
  - Taxonomy (shared/src/render/)   → Request/response VOs
  - Contract (shared/src/render/)   → RenderOperateProtocol, ViewportCapturePort
  - Capabilities                   → RenderOperateExecutor
  - Agent                          → RenderOrchestrator
  - Root                           → RenderContainer (DI wiring)

Surface layer is intentionally absent — MCP/CLI command handlers live in
their respective feature modules (modules/mcp, modules/cli).
"""

from . import root_render_container
from .root_render_container import RenderContainer, create_render_container

__all__ = [
    "RenderContainer",
    "create_render_container",
    "root_render_container",
]
```

---

## File: modules/render/src/agent_render_orchestrator.py

```python
"""Agent: Render feature orchestrator.

Coordinates viewport capture, image rendering, camera setup, and HDRI
configuration through the render capability protocols.
"""

from __future__ import annotations

import logging
from typing import Any

from modules.shared.src.render.contract_camera_config_protocol import CameraConfigProtocol
from modules.shared.src.render.contract_hdri_config_protocol import HdriConfigProtocol
from modules.shared.src.render.contract_render_aggregate import (
    ICameraConfigAggregate,
    IHdriConfigAggregate,
    IRenderOperateAggregate,
    IViewportCaptureAggregate,
)
from modules.shared.src.render.contract_render_operate_protocol import RenderOperateProtocol
from modules.shared.src.render.taxonomy_render_vo import (
    GetScreenshotVO,
    RenderVO,
)

logger = logging.getLogger("BlenderMCPServer")


class RenderOrchestrator(
    IRenderOperateAggregate,
    ICameraConfigAggregate,
    IHdriConfigAggregate,
    IViewportCaptureAggregate,
):
    """Orchestrates render operations via capability protocols."""

    def __init__(
        self,
        executor: RenderOperateProtocol,
        camera_config: CameraConfigProtocol | None = None,
        hdri_config: HdriConfigProtocol | None = None,
    ) -> None:
        self._executor = executor
        self._camera_config = camera_config
        self._hdri_config = hdri_config

    async def get_screenshot(self, request: GetScreenshotVO) -> GetScreenshotVO:
        return await self._executor.get_viewport_screenshot(request)

    async def render(self, request: RenderVO) -> RenderVO:
        return await self._executor.render(request)

    # ─── Camera Configuration (FR-RND-003) ──────────────────────────────

    async def configure_camera(
        self,
        camera_id: str | None = None,
        lens: float | None = None,
        framing_target: str | None = None,
        set_active: bool = False,
        depth_of_field: dict[str, Any] | None = None,
        create_if_missing: bool = True,
    ) -> dict[str, Any]:
        """FR-RND-003: Configure camera optical and selection behavior.

        Delegates to CameraConfigCapability when available.
        """
        if self._camera_config is None:
            return {
                "success": False,
                "message": "CameraConfigCapability not available",
            }
        return await self._camera_config.configure_camera(
            camera_id=camera_id,
            lens=lens,
            framing_target=framing_target,
            set_active=set_active,
            depth_of_field=depth_of_field,
            create_if_missing=create_if_missing,
        )

    # ─── HDRI Configuration (FR-RND-004) ────────────────────────────────

    async def configure_hdri(
        self,
        hdri_file_path: str,
        strength: float = 1.0,
        rotation: float = 0.0,
        background_visible: bool = True,
        overwrite_policy: str = "replace",
    ) -> dict[str, Any]:
        """FR-RND-004: Set up HDRI-based environment lighting.

        Delegates to HdriConfigCapability when available.
        """
        if self._hdri_config is None:
            return {
                "success": False,
                "message": "HdriConfigCapability not available",
            }
        return await self._hdri_config.configure_hdri(
            hdri_file_path=hdri_file_path,
            strength=strength,
            rotation=rotation,
            background_visible=background_visible,
            overwrite_policy=overwrite_policy,
        )
```

---

## File: modules/render/src/capabilities_camera_config.py

```python
"""Capability: Camera configuration (FR-RND-003).

Implements CameraConfigProtocol for configuring scene cameras.
Returns resolved camera reference and final settings.
"""

from __future__ import annotations

import logging
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import ObjectId
from modules.shared.src.render.contract_camera_config_protocol import CameraConfigProtocol

logger = logging.getLogger("BlenderMCPServer")


class CameraConfigCapability(CameraConfigProtocol):
    """Camera configuration capability.

    FR-RND-003: Configures camera optical properties including lens, framing,
    active designation, and depth of field. Returns resolved camera reference
    and final settings. Object feature handles positional transform only.
    """

    def __init__(
        self,
        gateway_client: Any | None = None,
        security_validator: Any | None = None,
        config_getter: Any | None = None,
    ) -> None:
        """Initialize with dependencies.

        Args:
            gateway_client: Gateway feature for Blender command transport.
            security_validator: Security policy for path validation.
            config_getter: Config feature for settings and policies.
        """
        self.gateway_client = gateway_client
        self.security_validator = security_validator
        self.config_getter = config_getter

    async def configure_camera(
        self,
        camera_id: ObjectId | None = None,
        lens: float | None = None,
        framing_target: ObjectId | None = None,
        set_active: bool = False,
        depth_of_field: dict[str, Any] | None = None,
        create_if_missing: bool = True,
    ) -> dict[str, Any]:
        """Configure camera optical and selection behavior.

        FR-RND-003: Creates camera if none exists (when policy allows).
        Resolves multiple cameras deterministically. Lens within valid range.
        Depth of field settings include enablement, focus distance/object, aperture.
        Framing target adjusts camera orientation preserving lens settings.
        Positional transform belongs to object feature, not here.

        Args:
            camera_id: Optional existing camera reference.
            lens: Focal length in millimeters.
            framing_target: Optional object to frame.
            set_active: Whether to designate as active scene camera.
            depth_of_field: Dict with dof settings (enable, focus_distance, aperture).
            create_if_missing: Whether to create camera if none exists.

        Returns:
            Dict with success, camera_reference, lens, active_status,
            depth_of_field_applied, and message.
        """
        # Validate lens range if provided
        if lens is not None:
            valid_range = (10.0, 300.0)  # Typical Blender range
            if lens < valid_range[0] or lens > valid_range[1]:
                return {
                    "success": False,
                    "camera_reference": None,
                    "lens": lens,
                    "active_status": False,
                    "depth_of_field_applied": False,
                    "message": f"Lens {lens}mm out of range ({valid_range[0]}-{valid_range[1]})",
                    "error": "invalid_parameter",
                }

        # Build camera configuration command
        config_command = self._build_camera_command(
            camera_id, lens, framing_target, set_active, depth_of_field, create_if_missing
        )

        # Validate gateway client is available
        if self.gateway_client is None:
            return {
                "success": False,
                "camera_reference": None,
                "lens": lens,
                "active_status": False,
                "depth_of_field_applied": False,
                "message": "Gateway client not configured",
                "error": "missing_dependency",
            }

        # Execute through gateway
        try:
            result = await self.gateway_client.execute_command(config_command)
            return {
                "success": True,
                "camera_reference": result.get("camera_id"),
                "lens": lens or result.get("current_lens", 50.0),
                "active_status": result.get("is_active", False),
                "depth_of_field_applied": result.get("dof_enabled", False),
                "message": f"Camera {str(camera_id or 'created')} configured successfully",
            }
        except Exception as e:
            logger.error("Camera configuration failed: %s", e)
            return {
                "success": False,
                "camera_reference": None,
                "lens": lens,
                "active_status": False,
                "depth_of_field_applied": False,
                "message": f"Camera configuration failed: {e}",
                "error": str(e),
            }

    def _build_camera_command(
        self,
        camera_id: ObjectId | None,
        lens: float | None,
        framing_target: ObjectId | None,
        set_active: bool,
        depth_of_field: dict[str, Any] | None,
        create_if_missing: bool,
    ) -> dict[str, Any]:
        """Build camera config command for gateway transport."""
        command = {
            "type": "camera_configure",
            "create_if_missing": create_if_missing,
            "set_active": set_active,
        }

        if camera_id:
            command["camera_id"] = str(camera_id)

        if lens is not None:
            command["lens"] = lens

        if framing_target:
            command["framing_target"] = str(framing_target)

        if depth_of_field:
            command["depth_of_field"] = depth_of_field

        return command
```

---

## File: modules/render/src/capabilities_hdri_config.py

```python
"""Capability: HDRI lighting configuration (FR-RND-004).

Implements HdriConfigProtocol for configuring HDRI environment lighting.
Never downloads HDRI itself — uses asset feature to get HDRI file.
"""

from __future__ import annotations

import logging
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import FilePath
from modules.shared.src.render.contract_hdri_config_protocol import HdriConfigProtocol

logger = logging.getLogger("BlenderMCPServer")


class HdriConfigCapability(HdriConfigProtocol):
    """HDRI lighting configuration capability.

    FR-RND-004: Applies HDRI-based environment lighting using locally available
    HDRI file acquired through asset feature. Resolves strength (0-10), rotation,
    overwrite policy, and background visibility. Never downloads HDRI itself.
    """

    def __init__(
        self,
        gateway_client: Any | None = None,
        security_validator: Any | None = None,
        asset_feature: Any | None = None,
        config_getter: Any | None = None,
    ) -> None:
        """Initialize with dependencies.

        Args:
            gateway_client: Gateway feature for Blender command transport.
            security_validator: Security policy for path validation.
            asset_feature: Asset feature for HDRI file acquisition.
            config_getter: Config feature for settings and policies.
        """
        self.gateway_client = gateway_client
        self.security_validator = security_validator
        self.asset_feature = asset_feature
        self.config_getter = config_getter

    async def configure_hdri(
        self,
        hdri_file_path: FilePath,
        strength: float = 1.0,
        rotation: float = 0.0,
        background_visible: bool = True,
        overwrite_policy: str = "replace",
    ) -> dict[str, Any]:
        """Set up HDRI-based environment lighting.

        FR-RND-004: HDRI file must be locally available (acquired via asset feature).
        Local file validated through security policy. Strength in valid range (0-10).
        Rotation normalized. Existing environment follows overwrite policy.
        Environment applies to scene world; world created if missing (when allowed).
        Background visibility controls HDRI appearance vs lighting-only contribution.

        Args:
            hdri_file_path: Path to local HDRI file (from asset feature).
            strength: Environment strength (0.0-10.0 range).
            rotation: HDRI rotation in degrees.
            background_visible: Whether HDRI appears as visible background.
            overwrite_policy: replace/update/reject for existing environment.

        Returns:
            Dict with success, environment_reference, strength, rotation,
            and message.
        """
        # Validate strength range
        if strength < 0.0 or strength > 10.0:
            return {
                "success": False,
                "environment_reference": None,
                "strength": strength,
                "rotation": rotation,
                "message": f"HDRI strength {strength} out of range (0.0-10.0)",
                "error": "invalid_parameter",
            }

        # Normalize rotation to [0, 360)
        rotation = rotation % 360.0

        # Validate HDRI file path through security policy
        if self.security_validator:
            try:
                await self.security_validator.validate_path(hdri_file_path, "read")
            except Exception as e:
                logger.warning("HDRI path validation failed: %s", e)
                return {
                    "success": False,
                    "environment_reference": None,
                    "strength": strength,
                    "rotation": rotation,
                    "message": f"HDRI path validation failed: {e}",
                    "error": "security_violation",
                }

        # Check if HDRI file exists locally
        import os
        if not os.path.exists(hdri_file_path):
            # Try to acquire through asset feature
            if self.asset_feature:
                try:
                    logger.info("HDRI file not found, attempting acquisition via asset feature")
                    download_result = await self.asset_feature.download_to_cache(
                        provider="polyhaven",  # Default provider
                        asset_id=hdri_file_path,  # Use path as ID for lookup
                        asset_type="hdri",
                        cache_dir=FilePath(""),
                    )
                    if not download_result.get("success"):
                        return {
                            "success": False,
                            "environment_reference": None,
                            "strength": strength,
                            "rotation": rotation,
                            "message": f"HDRI acquisition failed: {download_result.get('message', 'unknown error')}",
                            "error": "asset_not_found",
                        }
                    hdri_file_path = FilePath(download_result.get("file_path", ""))
                except Exception as e:
                    logger.error("HDRI acquisition failed: %s", e)
                    return {
                        "success": False,
                        "environment_reference": None,
                        "strength": strength,
                        "rotation": rotation,
                        "message": f"HDRI acquisition failed: {e}",
                        "error": "asset_not_found",
                    }

            # Still not found after attempt
            if not os.path.exists(hdri_file_path):
                return {
                    "success": False,
                    "environment_reference": None,
                    "strength": strength,
                    "rotation": rotation,
                    "message": f"HDRI file not found: {hdri_file_path}",
                    "error": "asset_not_found",
                }

        # Build HDRI configuration command
        hdri_command = self._build_hdri_command(
            hdri_file_path, strength, rotation, background_visible, overwrite_policy
        )

        # Execute through gateway
        try:
            result = await self.gateway_client.execute_command(hdri_command)
            return {
                "success": True,
                "environment_reference": result.get("environment_name"),
                "strength": strength,
                "rotation": rotation,
                "message": f"HDRI lighting configured with {hdri_file_path}",
            }
        except Exception as e:
            logger.error("HDRI configuration failed: %s", e)
            return {
                "success": False,
                "environment_reference": None,
                "strength": strength,
                "rotation": rotation,
                "message": f"HDRI configuration failed: {e}",
                "error": str(e),
            }

    def _build_hdri_command(
        self,
        hdri_path: str,
        strength: float,
        rotation: float,
        background_visible: bool,
        overwrite_policy: str,
    ) -> dict[str, Any]:
        """Build HDRI config command for gateway transport."""
        return {
            "type": "hdri_configure",
            "hdri_path": hdri_path,
            "strength": strength,
            "rotation": rotation,
            "background_visible": background_visible,
            "overwrite_policy": overwrite_policy,
        }
```

---

## File: modules/render/src/capabilities_render_operate_executor.py

```python
"""Capability: Render operation executor.

Implements RenderOperateProtocol — handles viewport capture, camera setup,
render configuration, composition rules, and frame rendering through
the server module's code execution capability.
"""

from __future__ import annotations

import json
import logging
import time

from modules.shared.src.common.taxonomy_core_vo import (
    CoordinateList,
    Prompt,
    RenderEngine,
    RenderSamples,
    RotationVector,
    RuleName,
    SuccessFlag,
    UseDenoising,
)
from modules.shared.src.render.contract_render_operate_protocol import RenderOperateProtocol
from modules.shared.src.render.taxonomy_render_vo import (
    GetScreenshotVO,
    RenderVO,
)

logger = logging.getLogger("BlenderMCPServer")


def _py_str(value: object) -> str:
    """Safely escape a value for inclusion in generated Python code."""
    return json.dumps(str(value))


def _format_coord(coord: object) -> str:
    """Safely format a coordinate value as a float for Python code."""
    return str(float(coord))


class RenderOperateExecutor(RenderOperateProtocol):
    """Business logic for rendering and visualization."""

    def __init__(self, code_executor: Prompt) -> None:
        """Initialize with a code executor from the server module.

        Args:
            code_executor: A callable or server capability that executes Python code.
        """
        self._code_executor = code_executor

    async def get_viewport_screenshot(self, request: GetScreenshotVO) -> GetScreenshotVO:
        """Capture viewport screenshot via generated Blender Python code.

        FR-RND-001: Captures the current viewport as an image, saves to validated output,
        and returns the file reference. Delegates execution through code executor.
        """
        logger.info(
            "Capturing viewport screenshot: max_size=%s, view=%s, shading=%s, overlays=%s, focus=%s",
            request.max_size,
            request.view_angle,
            request.shading,
            request.show_overlays,
            request.focus_object,
        )

        # Build screenshot capture code for Blender
        safe_path = _py_str(str(request.output_path))
        code = (
            "import bpy\n"
            "scene = bpy.context.scene\n"
            "engine = scene.render.engine\n"
            "scene.use_lock_interface = False\n"
            f"scene.render.filepath = {safe_path}\n"
            "bpy.ops.render.render(write_still=True)\n"
            "result_path = bpy.path.abspath(scene.render.filepath)\n"
            "print(result_path)\n"
        )

        try:
            start_time = time.perf_counter()
            result = await self._execute_code(code)
            duration_ms = round((time.perf_counter() - start_time) * 1000, 1)
            image_path = str(result) if isinstance(result, str) else str(request.output_path)
            return GetScreenshotVO(
                success=True,
                image_path=image_path,
                duration_ms=duration_ms,
                message="Screenshot captured successfully",
            )
        except Exception as e:
            logger.error("Viewport screenshot failed: %s", e)
            raise RuntimeError(f"Failed to capture viewport screenshot: {e}") from e

    async def setup_camera(
        self,
        location: CoordinateList,
        rotation: RotationVector,
        target: CoordinateList | None = None,
    ) -> Prompt:
        logger.info("Setting up camera at %s", location)

        loc = f"({_format_coord(location[0])}, {_format_coord(location[1])}, {_format_coord(location[2])})"
        rot = f"({_format_coord(rotation[0])}, {_format_coord(rotation[1])}, {_format_coord(rotation[2])})"

        code = (
            "import bpy\n"
            "camera = bpy.data.objects.get('Camera')\n"
            "if not camera:\n"
            "    bpy.ops.object.camera_add()\n"
            "    camera = bpy.context.active_object\n"
            f"camera.location = {loc}\n"
            f"camera.rotation_euler = {rot}\n"
        )
        if target is not None:
            tgt = f"({_format_coord(target[0])}, {_format_coord(target[1])}, {_format_coord(target[2])})"
            code += (
                "target_name = 'MCP_CameraTarget'\n"
                "target_obj = bpy.data.objects.get(target_name)\n"
                "if not target_obj:\n"
                "    bpy.ops.object.empty_add(type='PLAIN_AXES')\n"
                "    target_obj = bpy.context.active_object\n"
                "    target_obj.name = target_name\n"
                f"target_obj.location = {tgt}\n"
                "constraint = camera.constraints.get('Track To')\n"
                "if not constraint:\n"
                "    constraint = camera.constraints.new(type='TRACK_TO')\n"
                "constraint.target = target_obj\n"
                "constraint.track_axis = 'TRACK_NEGATIVE_Z'\n"
                "constraint.up_axis = 'UP_Y'\n"
            )
        try:
            await self._execute_code(code)
            return Prompt("Camera setup successful")
        except Exception as e:
            logger.error("setup_camera failed: %s", e)
            raise RuntimeError(f"Failed to setup camera: {e}") from e

    async def setup_render(
        self,
        engine: RenderEngine | None = None,
        samples: RenderSamples | None = None,
        resolution: CoordinateList | None = None,
        use_denoising: UseDenoising | None = None,
    ) -> Prompt:
        engine = engine or RenderEngine("CYCLES")
        samples = samples or RenderSamples(128)
        use_denoising = use_denoising or UseDenoising(True)
        engine_str = str(engine).upper()
        logger.info("Setting up render engine: %s", engine_str)

        safe_engine = _py_str(engine_str)
        code = f"import bpy\nbpy.context.scene.render.engine = {safe_engine}\n"

        if engine_str == "CYCLES":
            denoise = "True" if use_denoising else "False"
            code += (
                f"bpy.context.scene.cycles.samples = {int(samples)}\n"
                f"bpy.context.scene.cycles.use_denoising = {denoise}\n"
            )
        if resolution is not None:
            code += (
                f"bpy.context.scene.render.resolution_x = {int(resolution[0])}\n"
                f"bpy.context.scene.render.resolution_y = {int(resolution[1])}\n"
            )
        try:
            await self._execute_code(code)
            return Prompt(f"Render configured for {engine_str}")
        except Exception as e:
            logger.error("setup_render failed: %s", e)
            raise RuntimeError(f"Failed to configure render: {e}") from e

    async def apply_composition(self, rule: RuleName | None = None) -> Prompt:
        rule = rule or RuleName("thirds")
        logger.info("Applying composition rule: %s", rule)

        rule_val = str(rule).lower()
        guide_set = "{'THIRDS'}" if rule_val == "thirds" else "{'GOLDEN'}" if rule_val == "golden" else "set()"
        if rule_val not in ("thirds", "golden"):
            logger.warning("Unknown composition rule '%s', applying empty guide set.", rule_val)

        code = (
            "import bpy\n"
            "camera = bpy.data.objects.get('Camera')\n"
            "if camera and camera.type == 'CAMERA':\n"
            f"    camera.data.show_guide = {guide_set}\n"
        )

        try:
            await self._execute_code(code)
            return Prompt(f"Composition rule {rule} applied")
        except Exception as e:
            logger.error("apply_composition failed: %s", e)
            raise RuntimeError(f"Failed to apply composition: {e}") from e

    # FR-RND-002: Render Scene Image
    async def render(self, request: RenderVO) -> RenderVO:
        """Render scene to image at validated output destination.

        FR-RND-002: Renders the scene to an image artifact at a validated output location.
        Long-running renders are submitted through job feature (deferred until job integration).
        """
        logger.info("Rendering frame to %s", request.output_path)

        safe_path = _py_str(str(request.output_path))
        code = f"import bpy\nbpy.context.scene.render.filepath = {safe_path}\nbpy.ops.render.render(write_still=True)\n"
        try:
            start_time = time.perf_counter()
            await self._execute_code(code)
            render_time = round(time.perf_counter() - start_time, 2)
            return RenderVO(
                output_path=request.output_path,
                resolution_x=request.resolution_x,
                resolution_y=request.resolution_y,
                samples=request.samples,
                use_denoising=request.use_denoising,
                success=SuccessFlag(True),
                image_path=request.output_path,
                render_time=render_time,
                message="Render complete",
            )
        except Exception as e:
            logger.error("Render failed: %s", e)
            raise RuntimeError(f"Render failed: {e}") from e

    async def _execute_code(self, code: str) -> None:
        """Execute Python code through the server module's code execution capability.

        Args:
            code: Python code string to execute in Blender.

        Raises:
            RuntimeError: If code execution fails.
        """
        if callable(self._code_executor):
            result = await self._code_executor(code)
            if isinstance(result, str):
                logger.info("Code execution result: %s", result[:200])
        else:
            raise RuntimeError(f"Unexpected code_executor type: {type(self._code_executor)}")
```

---

## File: modules/render/src/root_render_container.py

```python
"""Root layer: Dependency injection container for the render feature.

Wires render capabilities to the agent orchestrator and bootstraps the system.
Provides a single entry point to obtain a fully configured RenderOrchestrator.
"""

from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .agent_render_orchestrator import RenderOrchestrator

logger = logging.getLogger("BlenderMCPServer")


class RenderContainer:
    """DI container that wires render capabilities to the agent orchestrator.

    Thread-safe singleton pattern for shared render management.
    All components are lazy-instantiated on first access.
    """

    def __init__(
        self,
        code_executor: object,
        gateway_client: Any | None = None,
        security_validator: Any | None = None,
        asset_feature: Any | None = None,
        config_getter: Any | None = None,
    ) -> None:
        """Initialize with dependencies for render capabilities.

        Args:
            code_executor: A callable or server capability that executes Python code.
            gateway_client: Gateway feature for Blender command transport.
            security_validator: Security policy for path validation.
            asset_feature: Asset feature for HDRI file acquisition.
            config_getter: Config feature for settings and policies.
        """
        self._code_executor = code_executor
        self._gateway_client = gateway_client
        self._security_validator = security_validator
        self._asset_feature = asset_feature
        self._config_getter = config_getter
        self._lock = threading.Lock()
        self._orchestrator: RenderOrchestrator | None = None

    def get_orchestrator(self) -> RenderOrchestrator:
        """Return a fully wired RenderOrchestrator (singleton).

        Lazy-initializes all dependencies on first call.
        Subsequent calls return the same orchestrator instance.
        """
        if self._orchestrator is not None:
            return self._orchestrator

        with self._lock:
            if self._orchestrator is not None:
                return self._orchestrator

            from .agent_render_orchestrator import RenderOrchestrator
            from .capabilities_camera_config import CameraConfigCapability
            from .capabilities_hdri_config import HdriConfigCapability
            from .capabilities_render_operate_executor import RenderOperateExecutor

            executor = RenderOperateExecutor(self._code_executor)
            camera_cap = CameraConfigCapability(
                gateway_client=self._gateway_client,
                security_validator=self._security_validator,
                config_getter=self._config_getter,
            )
            hdri_cap = HdriConfigCapability(
                gateway_client=self._gateway_client,
                security_validator=self._security_validator,
                asset_feature=self._asset_feature,
                config_getter=self._config_getter,
            )
            self._orchestrator = RenderOrchestrator(
                executor=executor,
                camera_config=camera_cap,
                hdri_config=hdri_cap,
            )

        logger.info("Render container fully wired")
        return self._orchestrator

    def shutdown(self) -> None:
        """Shut down render components."""
        with self._lock:
            self._orchestrator = None

    def __repr__(self) -> str:
        return "RenderContainer()"


def create_render_container(
    code_executor: object,
    gateway_client: Any | None = None,
    security_validator: Any | None = None,
    asset_feature: Any | None = None,
    config_getter: Any | None = None,
) -> RenderContainer:
    """Factory function to create a new render container.

    Args:
        code_executor: A callable or server capability that executes Python code.
        gateway_client: Gateway feature for Blender command transport.
        security_validator: Security policy for path validation.
        asset_feature: Asset feature for HDRI file acquisition.
        config_getter: Config feature for settings and policies.

    Returns:
        Configured RenderContainer instance.
    """
    return RenderContainer(
        code_executor=code_executor,
        gateway_client=gateway_client,
        security_validator=security_validator,
        asset_feature=asset_feature,
        config_getter=config_getter,
    )
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

## File: modules/shared/src/render/__init__.py

```python
"""Render domain — taxonomy types and contracts."""

from .contract_render_aggregate import (
    CameraConfigProtocol,
    HdriConfigProtocol,
    RenderOperateProtocol,
)
from .taxonomy_render_vo import (
    CameraConfigVO,
    CameraSetupVO,
    GetScreenshotVO,
    HdriConfigVO,
    HdriSetupVO,
    RenderVO,
)

__all__ = [
    "CameraConfigProtocol",
    "HdriConfigProtocol",
    "RenderOperateProtocol",
    "CameraConfigVO",
    "CameraSetupVO",
    "GetScreenshotVO",
    "HdriConfigVO",
    "HdriSetupVO",
    "RenderVO",
]
```

---

## File: modules/shared/src/render/contract_camera_config_protocol.py

```python
"""Render domain contract: camera configuration protocol (ABC based).

Defines the protocol for configuring scene cameras.

FR-RND-003: Configure Camera
AES Contract layer — pure ABC definitions, no implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import (
    ObjectId,
)


class CameraConfigProtocol(ABC):
    """Protocol for configuring scene cameras.

    FR-RND-003: Configures camera optical properties including lens, framing,
    active designation, and depth of field. Returns resolved camera reference
    and final settings. Object feature handles positional transform only.
    """

    @abstractmethod
    async def configure_camera(
        self,
        camera_id: ObjectId | None = None,
        lens: float | None = None,
        framing_target: ObjectId | None = None,
        set_active: bool = False,
        depth_of_field: dict[str, Any] | None = None,
        create_if_missing: bool = True,
    ) -> dict[str, Any]:
        """Configure camera optical and selection behavior.

        FR-RND-003: Creates camera if none exists (when policy allows).
        Resolves multiple cameras deterministically. Lens within valid range.
        Depth of field settings include enablement, focus distance/object, aperture.
        Framing target adjusts camera orientation preserving lens settings.
        Positional transform belongs to object feature, not here.

        Args:
            camera_id: Optional existing camera reference.
            lens: Focal length in millimeters.
            framing_target: Optional object to frame.
            set_active: Whether to designate as active scene camera.
            depth_of_field: Dict with dof settings (enable, focus_distance, aperture).
            create_if_missing: Whether to create camera if none exists.

        Returns:
            Dict with success, camera_reference, lens, active_status,
            depth_of_field_applied, and message.
        """
        ...
```

---

## File: modules/shared/src/render/contract_hdri_config_protocol.py

```python
"""Render domain contract: HDRI configuration protocol (ABC based).

Defines the protocol for configuring HDRI environment lighting.

FR-RND-004: Configure HDRI Lighting
AES Contract layer — pure ABC definitions, no implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import (
    FilePath,
)


class HdriConfigProtocol(ABC):
    """Protocol for configuring HDRI environment lighting.

    FR-RND-004: Applies HDRI-based environment lighting using locally available
    HDRI file acquired through asset feature. Resolves strength (0-10), rotation,
    overwrite policy, and background visibility. Never downloads HDRI itself.
    """

    @abstractmethod
    async def configure_hdri(
        self,
        hdri_file_path: FilePath,
        strength: float = 1.0,
        rotation: float = 0.0,
        background_visible: bool = True,
        overwrite_policy: str = "replace",
    ) -> dict[str, Any]:
        """Set up HDRI-based environment lighting.

        FR-RND-004: HDRI file must be locally available (acquired via asset feature).
        Local file validated through security policy. Strength in valid range (0-10).
        Rotation normalized. Existing environment follows overwrite policy.
        Environment applies to scene world; world created if missing (when allowed).
        Background visibility controls HDRI appearance vs lighting-only contribution.

        Args:
            hdri_file_path: Path to local HDRI file (from asset feature).
            strength: Environment strength (0.0-10.0 range).
            rotation: HDRI rotation in degrees.
            background_visible: Whether HDRI appears as visible background.
            overwrite_policy: replace/update/reject for existing environment.

        Returns:
            Dict with success, environment_reference, strength, rotation,
            and message.
        """
        ...
```

---

## File: modules/shared/src/render/contract_render_aggregate.py

```python
"""Aggregate contract for the render feature.

Aggregates all protocol contracts into a single unified interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .contract_camera_config_protocol import CameraConfigProtocol
from .contract_hdri_config_protocol import HdriConfigProtocol
from .contract_render_operate_protocol import RenderOperateProtocol
from .taxonomy_render_vo import CameraConfigVO, GetScreenshotVO, HdriConfigVO, RenderVO

__all__ = [
    "CameraConfigProtocol",
    "GetScreenshotVO",
    "HdriConfigProtocol",
    "RenderOperateProtocol",
]


class ICameraConfigAggregate(ABC):
    """Aggregate facade for camera configuration operations.

    FR-RND-003: Configures camera optical properties including lens, framing,
    active designation, and depth of field. Returns resolved camera reference
    and final settings. The Agent orchestrator implements this interface.
    Surface layers call through this aggregate.
    """

    @abstractmethod
    async def configure_camera(self, request: CameraConfigVO) -> CameraConfigVO:
        """FR-RND-003: Configure camera optical and selection behavior.

        Creates camera if none exists (when policy allows). Resolves multiple
        cameras deterministically. Lens within valid range. Depth of field
        settings include enablement, focus distance/object, aperture. Framing
        target adjusts camera orientation preserving lens settings. Positional
        transform belongs to object feature, not here.

        Args:
            request: Camera config with camera_id, lens, framing_target,
                     set_active, depth_of_field, and create_if_missing.

        Returns:
            CameraConfigVO with success, camera_name, final_settings,
            and message.
        """
        ...


class IHdriConfigAggregate(ABC):
    """Aggregate facade for HDRI lighting configuration operations.

    FR-RND-004: Applies HDRI-based environment lighting using a locally
    available HDRI file acquired through the asset feature. Resolves strength
    (0-10), rotation, overwrite policy, and background visibility. Never
    downloads HDRI itself. The Agent orchestrator implements this interface.
    Surface layers call through this aggregate.
    """

    @abstractmethod
    async def configure_hdri(self, request: HdriConfigVO) -> HdriConfigVO:
        """FR-RND-004: Set up HDRI-based environment lighting.

        HDRI file must be locally available (acquired via asset feature).
        Local file validated through security policy. Strength in valid range
        (0-10). Rotation normalized. Existing environment follows overwrite
        policy. Environment applies to scene world; world created if missing
        (when allowed). Background visibility controls HDRI appearance vs
        lighting-only contribution.

        Args:
            request: HDRI config with hdri_path, strength, rotation,
                     background_visible, and overwrite_policy.

        Returns:
            HdriConfigVO with success, environment_ref, applied_strength,
            and message.
        """
        ...


class IRenderOperateAggregate(ABC):
    """Aggregate facade for scene render operations.

    FR-RND-002: Renders the scene to an image artifact at a validated output
    location. Long-running renders are submitted through the job feature.
    The Agent orchestrator implements this interface.
    Surface layers call through this aggregate.
    """

    @abstractmethod
    async def render_scene(self, request: RenderVO) -> RenderVO:
        """FR-RND-002: Render scene to image artifact.

        Output validated through security policy. Resolution and samples
        within configured bounds. Long-running renders submitted through
        job feature with task reference. Returns render statistics including
        duration, resolution, sample count, engine used, and denoising status.

        Args:
            request: Render request with output_path, resolution, samples,
                     use_denoising, render_engine, and camera_id.

        Returns:
            RenderVO with success, image_path, render_time, resolution,
            engine, denoising_status, and message; or task_ref when background.
        """
        ...


class IViewportCaptureAggregate(ABC):
    """Aggregate facade for viewport screenshot capture operations.

    FR-RND-001: Captures the current viewport as an image artifact at a
    validated output location. Returns file reference with capture metadata.
    The Agent orchestrator implements this interface.
    Surface layers call through this aggregate.
    """

    @abstractmethod
    async def capture_viewport(self, request: GetScreenshotVO) -> GetScreenshotVO:
        """FR-RND-001: Capture current viewport as image artifact.

        Output location validated through security policy. View angle must be
        perspective/orthographic/active_camera. Shading mode must be
        wireframe/solid/material_preview/rendered. Max size enforced while
        preserving aspect ratio. Result returns file reference with metadata.

        Args:
            request: Screenshot capture request with max_size, view_angle,
                     shading_mode, overlay_visibility, and focus_object.

        Returns:
            GetScreenshotVO with success, image_path, dimensions, format,
            duration_ms, and message.
        """
        ...
```

---

## File: modules/shared/src/render/contract_render_operate_protocol.py

```python
"""Render domain contract: scene render protocol (ABC based).

Defines the protocol for rendering the scene to an image artifact.

FR-RND-002: Render Scene Image
AES Contract layer — pure ABC definitions, no implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import (
    FilePath,
    ObjectId,
    RenderEngine,
    RenderSamples,
    UseDenoising,
)


class RenderOperateProtocol(ABC):
    """Protocol for rendering scene images.

    FR-RND-002: Renders scene to image artifact at validated output location.
    Validates paths through security policy, submits long renders through job feature.
    Returns render statistics and artifact reference.
    """

    @abstractmethod
    async def render_scene(
        self,
        output_path: FilePath | None = None,
        resolution_width: int = 1920,
        resolution_height: int = 1080,
        samples: RenderSamples | None = None,
        use_denoising: UseDenoising = False,
        render_engine: RenderEngine | None = None,
        camera_id: ObjectId | None = None,
        background: bool = False,
        timeout_seconds: float | None = None,
        overwrite_policy: str = "overwrite",
    ) -> dict[str, Any]:
        """Render scene to image artifact.

        FR-RND-002: Output validated through security policy. Resolution and
        samples within configured bounds. Long-running renders submitted through
        job feature with task reference. Render statistics include duration,
        resolution, sample count, engine used, and denoising status.

        Args:
            output_path: Optional output file path.
            resolution_width: Render width in pixels.
            resolution_height: Render height in pixels.
            samples: Render sample count.
            use_denoising: Enable denoising.
            render_engine: Preferred render engine.
            camera_id: Optional camera reference.
            background: Submit as background job.
            timeout_seconds: Optional timeout limit.
            overwrite_policy: overwrite/reject/unique for existing files.

        Returns:
            Dict with success, file_path, render_time, resolution, engine,
            denoising_status, and message; or task_ref when background.
        """
        ...
```

---

## File: modules/shared/src/render/taxonomy_render_vo.py

```python
"""Render operation value objects — unified input/output per operation.

Each VO merges request (input) and response (output) into a single frozen dataclass.
Caller sets input fields; callee sets output fields.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..common.taxonomy_core_vo import (
    ImageBytes,
    ImageFormat,
    Prompt,
    RenderSamples,
    ResolutionX,
    ResolutionY,
    SuccessFlag,
    UseDenoising,
)


@dataclass(frozen=True)
class GetScreenshotVO:
    """Screenshot capture — input and output in one VO.

    Input: output_path, max_size, view_angle, shading, show_overlays, focus_object, format.
    Output: success, image_path, image_data, format, width, height, duration_ms, message.
    """
    # Input
    output_path: str = ""
    max_size: int = 800
    view_angle: str | None = None
    shading: str | None = None
    show_overlays: bool = False
    focus_object: str | None = None
    format: ImageFormat | None = None
    # Output
    success: SuccessFlag = field(default=SuccessFlag(False))
    image_path: str = ""
    image_data: ImageBytes = field(default_factory=lambda: ImageBytes(b""))
    width: ResolutionX = field(default_factory=lambda: ResolutionX(0))
    height: ResolutionY = field(default_factory=lambda: ResolutionY(0))
    duration_ms: float = 0.0
    message: Prompt = field(default_factory=lambda: Prompt(""))


@dataclass(frozen=True)
class RenderVO:
    """Render frame — input and output in one VO.

    Input: output_path, resolution_x, resolution_y, samples, use_denoising.
    Output: success, image_path, render_time, message.
    """
    # Input
    output_path: str
    resolution_x: int | None = None
    resolution_y: int | None = None
    samples: RenderSamples | None = None
    use_denoising: UseDenoising | None = None
    # Output
    success: SuccessFlag = field(default=SuccessFlag(False))
    image_path: str = ""
    render_time: float = 0.0
    message: Prompt = field(default_factory=lambda: Prompt(""))


@dataclass(frozen=True)
class CameraSetupVO:
    """Camera setup — input and output in one VO.

    Input: camera_name, location, rotation, focal_length, is_active, framing_target.
    Output: success, message.
    """
    # Input
    camera_name: str | None = None
    location_x: float = 0.0
    location_y: float = 0.0
    location_z: float = 0.0
    rotation_x: float = 0.0
    rotation_y: float = 0.0
    rotation_z: float = 0.0
    focal_length: float = 50.0
    is_active: bool = False
    framing_target: str | None = None
    # Output
    success: SuccessFlag = field(default=SuccessFlag(False))
    message: Prompt = field(default_factory=lambda: Prompt(""))


@dataclass(frozen=True)
class HdriSetupVO:
    """HDRI setup — input and output in one VO.

    Input: hdri_path, strength, rotation, is_visible, overwrite_policy.
    Output: success, environment_ref, applied_strength, message.
    """
    # Input
    hdri_path: str
    strength: float = 1.0
    rotation: float = 0.0
    is_visible: bool = True
    overwrite_policy: str = "replace"
    # Output
    success: SuccessFlag = field(default=SuccessFlag(False))
    environment_ref: str = ""
    applied_strength: float = 0.0
    message: Prompt = field(default_factory=lambda: Prompt(""))


@dataclass(frozen=True)
class CameraConfigVO:
    """Camera configuration result — output only (no separate request)."""
    success: SuccessFlag = field(default=SuccessFlag(False))
    camera_name: str = ""
    final_settings: dict = field(default_factory=dict)
    message: Prompt = field(default_factory=lambda: Prompt(""))


@dataclass(frozen=True)
class HdriConfigVO:
    """HDRI configuration result — output only (no separate request)."""
    success: SuccessFlag = field(default=SuccessFlag(False))
    environment_ref: str = ""
    applied_strength: float = 0.0
    message: Prompt = field(default_factory=lambda: Prompt(""))
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

