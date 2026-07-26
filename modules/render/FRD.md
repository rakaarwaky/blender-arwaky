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
