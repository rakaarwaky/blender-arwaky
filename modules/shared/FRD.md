# FRD — shared (Taxonomy + Contracts)

## System Overview

The shared module provides the domain foundation (taxonomy) and public interface definitions (contracts) used across all feature modules. Each feature's FR describes what it needs from shared.

## Functional Requirements

### FR-SHR-ASSET: Shared Types for Asset Feature

**Taxonomy needed:**
- VOs: AssetId, AssetName, AssetType, ProviderName, SearchQuery, StringList, TagList, ThumbnailUrl, FilePath, ObjectName, SuccessFlag, ErrorMessage, AssetCount, EnabledFlag, ImageBytes, ResultLimit, ScaleFactor, StatusString
- Errors: ProviderError
- Constants: (none — asset constants are in shared/src/asset/)

**Contracts needed:**
- `AssetProviderPort` — provider adapter interface
- `AssetSearchProtocol` — multi-provider search interface
- `ImportExportProtocol` — GLB/OBJ import/export interface
- `BlenderConnectionPort` — connection to Blender for asset operations

---

### FR-SHR-OBJECT: Shared Types for Object Feature

**Taxonomy needed:**
- VOs: ActionName, Details, Prompt, PythonCode, HdriId, SearchQuery, SuccessFlag, ObjectName, FilePath
- Errors: BlenderMCPError, SceneValidationError
- Constants: CommandCatalog, ALLOWED_OBJECT_TYPES, OBJECT_TYPE_*

**Contracts needed:**
- `ObjectOperateProtocol` — object manipulation interface
- `ExecuteActionProtocol` — universal action dispatch interface
- `WorkflowProtocol` — multi-step workflow interface
- `BlenderPort` — Blender adapter interface
- `SceneOperateProtocol` — scene operations (for import/place)

**Request/Response VOs (shared/src/object/):**
- PlaceAssetRequestVO, CreatePrimitiveRequestVO, SetObjectTransformRequestVO
- SetMaterialRequestVO, ApplyModifierRequestVO, DeleteObjectRequestVO, GetObjectInfoRequestVO

---

### FR-SHR-RENDER: Shared Types for Render Feature

**Taxonomy needed:**
- VOs: FilePath, ImageBytes, MaxSize, ResolutionX, ResolutionY, RenderSamples, UseDenoising, SuccessFlag

**Contracts needed:**
- `RenderOperateProtocol` — render operations interface
- `BlenderPort` — Blender adapter interface

**Request/Response VOs (shared/src/render/):**
- GetScreenshotRequestVO, RenderRequestVO, RenderResponseVO, ScreenshotResponseVO

---

### FR-SHR-SCENE: Shared Types for Scene Feature

**Taxonomy needed:**
- VOs: ActionName, Prompt, ObjectName, ObjectType, BlenderObject, BlenderObjectList, SceneInfo, Vector3D

**Contracts needed:**
- `SceneOperateProtocol` — scene operations interface
- `SceneInspectionPort` — scene inspection interface
- `BlenderConnectionPort` — connection to Blender
- `CodeExecutionPort` — code execution in Blender
- `BlenderPort` — Blender adapter interface

**Request/Response VOs (shared/src/scene/):**
- GetSceneInfoRequestVO, CleanupSceneRequestVO, SetupEnvironmentRequestVO

---

### FR-SHR-SERVER: Shared Types for Server Feature

**Taxonomy needed:**
- VOs: ActionName, Prompt, PythonCode, StatusString, ErrorMessage, ConfigPath, ConfigValue
- Errors: ValidationError, ExecutionError, BlenderConnectionFailure

**Contracts needed:**
- `BlenderConnectionPort` — TCP socket connection interface
- `BlenderConnectionFactoryPort` — connection factory interface
- `CodeExecutionPort` — code execution interface
- `BlenderPort` — Blender adapter interface

---

### FR-SHR-MCP: Shared Types for MCP Feature

**Taxonomy needed:**
- VOs: ActionName, Details, Prompt, FilePath, ObjectName, ServerName, DomainRef, FormatRef, CapabilityRef, SectionRef, SkillName, StringList
- Constants: CommandCatalog, CommandSpec, ACTION_NAMES

**Contracts needed:**
- `CommandCatalogPort` — command catalog interface

---

### FR-SHR-TELEMETRY: Shared Types for Telemetry Feature

**Taxonomy needed:**
- Events: EventType, TelemetryEvent
- Constants: EVENT_TYPE_STARTUP, EVENT_TYPE_TOOL_EXECUTION, EVENT_TYPE_PROMPT_SENT, EVENT_TYPE_CONNECTION, EVENT_TYPE_ERROR

**Contracts needed:**
- `TelemetryRecordingPort` — event recording interface

---

### FR-SHR-CONFIG: Shared Types for Config Feature

**Taxonomy needed:**
- VOs: ConfigPath, ConfigValue, FilePath

**Contracts needed:**
- `ConfigPort` — configuration access interface

---

### FR-SHR-JOB: Shared Types for Job Feature

**Taxonomy needed:**
- Entity: JobStatus
- Constants: JOB_STATE_PENDING, JOB_STATE_RUNNING, JOB_STATE_COMPLETED, JOB_STATE_FAILED

**Contracts needed:**
- (none — job is self-contained)

---

### FR-SHR-CLI: Shared Types for CLI Feature

**Taxonomy needed:**
- (minimal — CLI is standalone)

**Contracts needed:**
- (none — CLI is standalone)

---

### FR-SHR-COMMON: Common Taxonomy

**Core VOs (shared/src/common/taxonomy_core_vo.py):**
- 93+ NewType wrappers used across all features
- Organized by domain: identity, name, type, path, numeric, flag, string, config

**Domain Errors (shared/src/common/taxonomy_domain_error.py):**
- BlenderMCPError → DomainError → specific errors
- Used by: asset, object, scene, server, render, config, mcp

**Command Catalog (shared/src/common/taxonomy_command_catalog_constant.py):**
- CommandCatalog, CommandSpec, ACTION_NAMES
- Used by: mcp, object

**Rich VOs (shared/src/common/):**
- Vector3D, BoundingBox — used by object, scene
- ApplicationConfig — used by config

## API Contract

| Feature | Taxonomy Types | Contract Types | Total |
|---------|---------------|----------------|-------|
| asset | 12 VOs, 1 error | 4 contracts | 17 |
| object | 9 VOs, 2 errors, 3 constants | 5 contracts | 19 |
| render | 7 VOs | 2 contracts | 9 |
| scene | 6 VOs | 5 contracts | 11 |
| server | 6 VOs, 3 errors | 4 contracts | 13 |
| mcp | 10 VOs, 3 constants | 1 contract | 14 |
| telemetry | 2 events, 5 constants | 1 contract | 8 |
| config | 3 VOs | 1 contract | 4 |
| job | 1 entity, 4 constants | 0 | 5 |
| cli | 0 | 0 | 0 |

## Integration Points

- **Internal**: All feature modules depend on shared taxonomy and contracts
- **External**: None

## Non-functional Requirements

- Performance: Import time < 100ms for full barrel
- Type Safety: 100% type hint coverage on public APIs
- Stability: Backward-compatible changes only

## Test Scenarios

- [ ] Each feature can import its required shared types
- [ ] All NewType VOs are distinct (no implicit conversion)
- [ ] All contract ABCs raise TypeError if instantiated directly
- [ ] Command catalog contains all registered actions
- [ ] Error hierarchy serializes to MCP-compatible format

## Assumptions & Constraints

- Python 3.10+ required
- No runtime dependencies beyond stdlib
- Taxonomy must not import from any other layer

## Glossary

- **taxonomy_**: Domain foundation layer (VOs, entities, errors, constants)
- **contract_**: Public interface definitions (protocols, ports)
- **_protocol**: ABC implemented by capabilities, consumed by agent
- **_port**: ABC implemented by infrastructure, consumed by capabilities

## Reference

- PRD: [../../PRD.md](../../PRD.md)
