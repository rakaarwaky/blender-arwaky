# FRD — shared (Taxonomy + Contracts)

## System Overview

The shared module contains the domain foundation layer (taxonomy) and public interface definitions (contracts) used across all feature modules. It defines the stable language of the domain and the behavioral contracts that decouple layers.

```
modules/shared/src/
├── common/        ← Cross-cutting VOs, errors, constants, aggregates, protocols
├── config/        ← Application configuration port
├── scene/         ← Scene domain VOs and contracts
├── object/        ← Object domain VOs and contracts
├── render/        ← Render domain VOs and contracts
├── asset_io/      ← Import/export VOs and contracts
├── asset_provider/← Asset provider VOs and contracts
├── job/           ← Job tracking VOs
└── telemetry/     ← Telemetry VOs and contracts
```

## Functional Requirements

### FR-001: Core Value Objects

- **Description**: Define branded NewType primitives for type-safe domain modeling
- **Input**: None (definition only)
- **Output**: 93+ NewType wrappers (ActionName, ObjectId, AssetId, etc.)
- **Business Rules**: Each VO must be semantically distinct; no implicit conversion between VOs
- **Edge Cases**: Empty strings, max length violations, invalid characters
- **Error Handling**: Type errors caught at compile time via static analysis

### FR-002: Rich Value Objects

- **Description**: Immutable data structures with computed properties
- **Input**: Constructor parameters
- **Output**: Vector3D (arithmetic ops), BoundingBox (containment checks), SceneInfo, AssetMetadata
- **Business Rules**: VOs are frozen/immutable; computed properties are pure functions
- **Edge Cases**: Zero-vector division, empty bounding boxes, null optional fields
- **Error Handling**: ValueError for invalid构造 parameters

### FR-003: Domain Error Hierarchy

- **Description**: Typed exception hierarchy for domain-specific error handling
- **Input**: Error conditions
- **Output**: BlenderMCPError → DomainError → {SceneValidationError, AssetNotFoundError, ConnectionError, ...}
- **Business Errors**: Each error carries structured details for MCP error responses
- **Edge Cases**: Nested exceptions, error chaining
- **Error Handling**: All errors implement `to_mcp_format()` for client consumption

### FR-004: Command Catalog

- **Description**: Single source-of-truth mapping of action names to capability contracts
- **Input**: Action name string
- **Output**: CommandSpec with description, capability reference, parameters, domain, return type
- **Business Rules**: 15+ actions registered; action names are lowercase alphanumeric with underscores
- **Edge Cases**: Unknown action names, malformed capability references
- **Error Handling**: InvalidCommandError for unknown actions

### FR-005: Contract Protocols

- **Description**: ABC interfaces defining inbound behavior for capabilities
- **Input**: Method calls with typed parameters
- **Output**: Typed return values (RequestVO → ResponseVO)
- **Business Rules**: Protocols define behavior only; no implementation; depend on taxonomy only
- **Edge Cases**: Optional parameters, union return types
- **Error Handling**: AbstractMethodError if not implemented

### FR-006: Contract Aggregates

- **Description**: Facade interfaces for agent orchestrators, consumed by surfaces
- **Input**: Method calls via aggregate interface
- **Output**: Prompt (JSON string) responses
- **Business Rules**: Aggregates hide capabilities from surfaces; one aggregate per orchestrator
- **Edge Cases**: Missing aggregate implementations, circular dependencies
- **Error Handling**: Delegated to underlying capabilities

### FR-007: Contract Ports

- **Description**: Infrastructure-facing interfaces for external adapters
- **Input**: External system calls
- **Output**: Typed port responses
- **Business Rules**: Ports define adapter contracts; implemented by infrastructure layer
- **Edge Cases**: Connection timeouts, invalid responses
- **Error Handling**: ConnectionError, ProviderError for external failures

## API Contract

| Operation | Input | Output | Description |
|-----------|-------|--------|-------------|
| `BlenderPort.execute_code(PythonCode)` | Python code string | StatusString | Execute code in Blender |
| `BlenderPort.get_scene_info()` | None | SceneInfo | Get current scene state |
| `SceneOperateProtocol.cleanup_mode(CleanupSceneRequestVO)` | Cleanup mode | CleanupSceneResponseVO | Clean scene objects |
| `ObjectOperateProtocol.place_asset(PlaceAssetRequestVO)` | Asset placement params | PlaceAssetResponseVO | Place asset in scene |
| `RenderOperateProtocol.get_viewport_screenshot(GetScreenshotRequestVO)` | Screenshot params | ScreenshotResponseVO | Capture viewport |
| `ExecuteActionProtocol.execute(ActionName, Details)` | Action name + args | Prompt | Universal action dispatch |

## Integration Points

- **Internal**: All feature modules depend on shared taxonomy and contracts
- **External**: None (foundation layer)

## Non-functional Requirements (Detailed)

- Performance: Import time < 100ms for full barrel
- Type Safety: 100% type hint coverage on public APIs
- Stability: Backward-compatible changes only; breaking changes require major version

## Test Scenarios / QA Checklist

- [ ] All 93+ NewType VOs import correctly from barrel
- [ ] All contract ABCs raise TypeError if instantiated directly
- [ ] Command catalog contains all 15+ registered actions
- [ ] Error hierarchy serializes to MCP-compatible format
- [ ] Vector3D arithmetic operations produce correct results
- [ ] BoundingBox containment checks work for edge cases

## Assumptions & Constraints

- Python 3.10+ required (union types, match statements)
- No runtime dependencies beyond stdlib (pure domain definitions)
- Taxonomy must not import from any other layer

## Glossary

- **VO**: Value Object — immutable data concept with structural equality
- **Entity**: Stateful domain concept with identity
- **Protocol**: ABC interface defining inbound behavior
- **Aggregate**: Facade interface implemented by agent, consumed by surface
- **Port**: Infrastructure-facing interface for external adapters

## Reference

- PRD: [../../PRD.md](../../PRD.md)
