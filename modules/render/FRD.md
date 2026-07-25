
# FRD — render (Render Feature Module)

## System Overview

The render module handles viewport capture, image rendering, camera setup, and HDRI environment lighting for **blender-arwaky**. It provides a render operation contract and viewport capture capabilities. 

This module translates high-level rendering intents into validated Blender-side operations. It validates capture and render parameters, resolves camera and environment targets, enforces output safety policies, and delegates execution to the Blender scripting interface through the server module.

The module covers:

- capturing viewport images with configurable presets
- rendering scene images to output artifacts
- configuring active or target camera
- applying HDRI-based environment lighting
- supporting long-running render operations through asynchronous job awareness
- returning structured render results and diagnostic metadata

The module does not handle:

- asset discovery or asset download
- network communication with Blender
- object creation or scene composition beyond camera and environment setup
- multi-user collaboration
- cloud rendering services

## Functional Requirements

### FR-RND-001: Get Viewport Screenshot

- **Description**: Capture current viewport as image with configurable presets
- **Input**: Screenshot request concept containing maximum size, view angle, shading mode, overlay visibility, focus object reference, image format, and optional source view context
- **Output**: Screenshot result concept containing success indicator, image payload or artifact reference, image format, width, height, and message
- **Business Rules**:
  - View angle must be one of the supported conceptual modes:
    - perspective
    - orthographic
    - active camera view
  - Shading mode must be one of the supported conceptual modes:
    - wireframe
    - solid
    - material preview
    - rendered
  - Overlay visibility must be configurable
  - Maximum image size must be enforced while preserving aspect ratio
  - Image format must be supported by the Blender runtime and allowed by configuration
  - Focus object reference, if provided, must be resolved deterministically
  - If focus object is not found, behavior must follow configured policy:
    - return scene validation error
    - ignore focus and continue capture
  - If active viewport context is unavailable, implementation may fall back to offscreen capture or active camera capture when supported
  - Screenshot operation should be read-only and should not mutate scene state except temporary view adjustments required for capture
  - Returned image payload should be size-limited and safe for transport to MCP clients
  - If image payload exceeds transport-friendly size, return artifact reference instead of raw payload when supported
  - Operation should include capture metadata such as resolved width, height, format, shading mode, and capture duration
- **Edge Cases**: Empty viewport, focused object not found, unsupported image format, oversized viewport, no active 3D view context, headless runtime limitation, hidden focus object, locked view, unsupported shading mode, memory limit, capture timeout
- **Error Handling**: Execution error for Blender rendering failures; request validation error for invalid parameters; scene validation error for missing focus object when strict policy is enabled; timeout error when capture exceeds configured limit

### FR-RND-002: Render Image

- **Description**: Render scene to image artifact with specified settings
- **Input**: Render request concept containing output destination, resolution width, resolution height, sample count, denoising flag, render engine preference, color mode, transparency flag, camera reference, overwrite policy, timeout, and asynchronous execution policy
- **Output**: Render result concept containing success indicator, artifact reference, render time, render statistics, final resolution, and message
- **Business Rules**:
  - Output destination must be writable and located inside allowed output directories
  - Resolution width and height must be within configured minimum and maximum bounds, default conceptual range 1 to 8192
  - Sample count must be within configured minimum and maximum bounds, default conceptual range 1 to 4096
  - Denoising is optional and must gracefully degrade when unsupported by active render engine
  - Render engine preference may be specified but must fall back to available engine when requested engine is unavailable
  - Active camera must exist or be resolvable through camera setup policy
  - If no active camera exists, operation may trigger camera setup when policy allows
  - Existing output artifact must be handled according to overwrite policy:
    - overwrite
    - reject
    - create unique variant
  - Render operation should write to temporary artifact first and finalize only after successful render when supported
  - Long-running render operations should support asynchronous job submission when duration is expected to exceed standard timeout
  - Asynchronous render result should expose job status, progress when available, and final artifact reference
  - Render cancellation is best-effort due to Blender main-thread execution constraints
  - Render operation should return final render statistics when available:
    - render time
    - resolution
    - sample count
    - engine used
    - denoising applied
  - Output artifact must not expose sensitive filesystem information beyond allowed diagnostic metadata
- **Edge Cases**: Invalid output destination, permission denied, output directory missing, render timeout, denoising not supported, no active camera, empty scene, unsupported render engine, out of memory, existing artifact conflict, very high resolution, transparent background unsupported, canceled render, stale camera reference
- **Error Handling**: Request validation error for invalid render parameters; scene validation error for missing camera or invalid scene state; execution error for render failures; timeout error for exceeded render duration; delegated server error for communication failure

### FR-RND-003: Setup Camera

- **Description**: Position and configure camera for rendering
- **Input**: Camera setup concept containing camera reference or creation policy, position, rotation, lens or focal length, sensor fit, depth of field options, active camera policy, and optional framing target
- **Output**: Camera configuration result concept containing success indicator, resolved camera reference, final camera settings, active camera status, and message
- **Business Rules**:
  - Camera must be created if it does not exist and creation policy allows
  - If multiple cameras exist, camera resolution must be deterministic:
    - prefer explicit camera reference
    - fall back to active scene camera
    - fall back to first available camera when policy allows
  - If no camera exists and creation policy disallows, return scene validation error
  - Lens or focal length values must be within configured valid range
  - Position and rotation values must be finite and valid three-component vectors
  - Camera may be set as active scene camera when policy requests
  - Locked camera or protected camera state must be respected unless explicit override is allowed
  - Camera setup should not modify shared or linked camera data unless explicitly allowed
  - Optional framing target may adjust camera orientation while preserving requested lens settings
  - Operation should return resolved camera reference and final configuration state
- **Edge Cases**: Multiple cameras, locked camera, invalid lens values, non-finite transform values, missing camera reference, linked camera data, protected camera, camera constraints overriding transform, no scene camera, creation not permitted, incompatible camera type
- **Error Handling**: Scene validation error for invalid camera state or missing camera when creation disallowed; request validation error for invalid camera parameters; protection or lock error when camera cannot be modified; delegated server error for Blender execution failure

### FR-RND-004: Setup HDRI Lighting

- **Description**: Configure environment lighting from HDRI asset
- **Input**: HDRI setup concept containing asset reference, strength, rotation, background visibility policy, and environment overwrite policy
- **Output**: Environment result concept containing success indicator, resolved environment reference, applied strength, applied rotation, and message
- **Business Rules**:
  - HDRI asset must be available locally before environment setup
  - If HDRI asset is not available, request must delegate download or resolution to asset module
  - HDRI strength must be within configured valid range, default conceptual range 0.0 to 10.0
  - HDRI rotation must be normalized according to configured angle convention
  - Existing scene environment must be handled according to overwrite policy:
    - replace environment
    - update existing environment
    - reject if environment exists
  - Environment setup should apply to scene world or equivalent environment lighting concept
  - If scene world does not exist, implementation should create one when policy allows
  - Background visibility policy may control whether HDRI appears as background or only contributes lighting
  - Operation should preserve non-environment lighting objects unless explicitly replaced
  - Operation should return resolved environment reference and final applied settings
- **Edge Cases**: HDRI asset not found, download failed, unsupported HDRI format, existing environment conflict, strength out of range, rotation overflow, missing scene world, linked world data, provider failure, asset cache unavailable, environment node incompatibility
- **Error Handling**: Asset not found error delegated to asset module; provider error delegated to asset module; request validation error for invalid strength or rotation; scene validation error for incompatible scene environment state; delegated server error for Blender execution failure

## API Contract


| Operation                   | Input                      | Output                              | Description                    |
| ----------------------------- | ---------------------------- | ------------------------------------- | -------------------------------- |
| Capture viewport screenshot | Screenshot request concept | Screenshot result concept           | Capture viewport as image      |
| Render image                | Render request concept     | Render result concept               | Render scene to artifact       |
| Setup camera                | Camera setup concept       | Camera configuration result concept | Position and configure camera  |
| Setup HDRI lighting         | HDRI setup concept         | Environment result concept          | Configure environment lighting |

Common contract behavior:

- All operations return structured result containing success indicator, human-readable message, and error category when failed
- All operations may accept request correlation identifier for tracing
- All mutating operations delegate execution to Blender through server module
- Render operation may return asynchronous job reference when long-running execution mode is selected
- Screenshot operation may return raw image payload or artifact reference depending on size policy and transport constraints
- Camera and HDRI operations should report resolved references after execution
- Destructive or overwrite operations must expose explicit policy flags
- Operations should avoid returning oversized binary payloads directly when artifact reference is supported

## Integration Points

- **Internal**:
  - shared module: taxonomy concepts for render settings, camera settings, environment settings, result envelope, error categories, and correlation identifiers
  - server module: Blender connection, operation dispatch, response parsing, queueing, timeout handling, and asynchronous job coordination
  - asset module: HDRI asset resolution, download, caching, and provider interaction
  - configuration module: allowed output directories, default resolution limits, timeout policy, supported image formats, and render defaults
- **External**:
  - Blender scripting interface — accessed via server module
  - Blender scene data: cameras, world environment, render settings, viewport context, and output artifact storage
  - Filesystem or artifact storage for rendered images
  - Asset provider ecosystem through asset module for HDRI acquisition

## Non-functional Requirements

- **Performance**:

  - Screenshot capture within 3 seconds for standard viewport settings
  - Render within 60 seconds for standard scenes under default resolution and sample settings
  - Long-running render operations should be submitted as asynchronous jobs when expected duration exceeds standard timeout
  - Render progress reporting should be provided when supported by Blender runtime
- **Reliability**:

  - Graceful fallback on render failures
  - No partial output artifact should be exposed as successful when supported by temporary artifact strategy
  - Missing camera or environment states should be resolved deterministically or fail with clear error category
  - Asynchronous render failures should preserve final error state for polling
- **Safety**:

  - Output destination must be restricted to allowed directories
  - Overwrite behavior must be explicit
  - HDRI setup must not unintentionally destroy existing environment unless policy allows
  - Camera setup must respect locked or protected camera state unless override is explicitly allowed
- **Observability**:

  - Log operation type, target reference, result status, duration, and error category
  - Log render metadata such as resolution, sample count, engine used, and denoising status without exposing sensitive paths
  - Log screenshot metadata such as format, dimensions, shading mode, and capture duration
  - Avoid logging full image payload or sensitive asset credentials
- **Portability**:

  - Behavior should remain consistent across supported Blender versions where rendering and viewport capabilities are available
  - Headless runtime limitations should be detected and handled gracefully
  - Image format support should depend on Blender runtime capabilities
- **Extensibility**:

  - New shading presets, render presets, camera framing modes, and environment policies can be added without modifying core render contract
  - Additional render engines or denoising strategies can be supported through adapter-style extension when available

## Test Scenarios / QA Checklist

- [ ]  Screenshot with valid parameters returns image payload or artifact reference
- [ ]  Screenshot with invalid view angle returns request validation error
- [ ]  Screenshot with invalid shading mode returns request validation error
- [ ]  Screenshot with unsupported image format returns request validation error
- [ ]  Screenshot with missing focus object follows configured policy
- [ ]  Screenshot with maximum size limit preserves aspect ratio
- [ ]  Screenshot falls back gracefully when viewport context is unavailable
- [ ]  Screenshot in headless environment returns clear limitation error or supported fallback
- [ ]  Render with valid parameters produces output artifact
- [ ]  Render with invalid output destination returns request validation error
- [ ]  Render with permission-denied output destination returns execution or load error category
- [ ]  Render with resolution outside allowed range returns request validation error
- [ ]  Render with sample count outside allowed range returns request validation error
- [ ]  Render with missing active camera returns scene validation error or triggers camera setup when allowed
- [ ]  Render with denoising unsupported degrades gracefully
- [ ]  Render with existing artifact follows overwrite policy
- [ ]  Render timeout returns timeout error
- [ ]  Render asynchronous submission returns job reference
- [ ]  Render asynchronous polling returns progress and final result
- [ ]  Render cancellation is best-effort and returns clear status
- [ ]  Camera setup creates camera if none exists and creation policy allows
- [ ]  Camera setup uses active camera when no explicit reference is provided
- [ ]  Camera setup resolves multiple cameras deterministically
- [ ]  Camera setup with invalid lens values returns request validation error
- [ ]  Camera setup with locked camera returns protection or lock error unless override allowed
- [ ]  Camera setup sets active camera when policy requests
- [ ]  HDRI setup applies environment lighting when asset is available
- [ ]  HDRI setup delegates download when asset is unavailable
- [ ]  HDRI setup with missing asset returns asset not found error
- [ ]  HDRI setup with provider failure returns delegated provider error
- [ ]  HDRI setup with strength outside valid range returns request validation error
- [ ]  HDRI setup with rotation overflow normalizes value correctly
- [ ]  HDRI setup follows environment overwrite policy
- [ ]  HDRI setup creates scene world when missing and policy allows
- [ ]  Render operations delegate to server module and propagate server errors
- [ ]  Render and screenshot operations respect server-side serialization constraints

## Assumptions & Constraints

- Blender must be running for viewport and render operations
- Blender scripting interface must be enabled and reachable through server module
- HDRI download and asset caching are handled by asset module
- Internet connection is required only for HDRI download or remote asset resolution
- Viewport capture may depend on active viewport context and may require fallback in headless environments
- Render operations may be long-running and should use asynchronous execution when appropriate
- Blender main-thread constraint requires serialized execution for state-modifying operations
- Output artifacts must be written only to allowed output locations
- Some render features depend on active render engine capabilities
- Camera and environment setup may affect existing scene state and must follow explicit policies

## Glossary

- **HDRI**: High Dynamic Range Image used for environment lighting
- **Viewport**: The 3D view representation inside Blender user interface
- **Shading mode**: Conceptual viewport display mode such as wireframe, solid, material preview, or rendered
- **Overlay**: Viewport helper elements such as grid, gizmos, statistics, or annotations
- **Render artifact**: Output image result produced by render operation
- **Active camera**: Camera currently used by the scene for rendering
- **Environment lighting**: Scene-wide lighting contribution from background or world environment
- **Render job**: Asynchronous execution unit for long-running render operations
- **Allowed output location**: Configured directory or storage area where render artifacts may be written
- **Overwrite policy**: Rule describing how existing output artifact or existing environment should be handled

## Reference

- Product Requirements Document for blender-arwaky
- Shared feature requirements documentation
- Asset feature requirements documentation
- Server feature requirements documentation
