# FRD — Rendering & Viewport Feature

## Purpose

Single authority for image production and camera optics. Captures viewport, renders scene to validated output locations, configures camera-specific behavior (lens, framing, active camera, depth of field), applies HDRI environment lighting using files from asset feature. Execution via gateway; output safety via security policy; long-running renders via job feature.

## Scope

- Viewport screenshot capture with configurable presets
- Scene render to output artifact
- Render settings management (resolution, samples, denoising, engine preference)
- Camera configuration (lens, framing, active camera, depth of field)
- HDRI environment lighting configuration
- Output file policy for render/screenshot artifacts
- Output path validation through security policy
- Background render submission through job feature
- Overwrite and uniqueness policy for output artifacts
- Render and capture observability events

## Out of Scope

Asset download, generic object manipulation, scene cleanup, background task lifecycle, queue management, path traversal protection, object placement/transformation, HDRI asset discovery/caching, cloud rendering, video/animation output.

## Depends On

gateway (Blender command transport + mutation serialization), security policy (output path validation, artifact safety), job (long-running render tracking + capacity), asset (HDRI file download + local availability), config (output directory, format, timeout, lighting defaults).

## Provides To

dispatcher.

## Functional Requirements

### FR-RND-001: Capture Viewport Screenshot

- **Description**: Capture current viewport as image artifact, save to validated output location, return file reference
- **Input**: Screenshot request (max size, view angle, shading mode, overlay visibility, focus object ref, image format, output destination policy)
- **Output**: Screenshot result (success, artifact file ref, format, dimensions, duration)
- **Rules**: Output location validated through security policy; must be inside allowed directories. View angle: perspective/orthographic/active camera. Shading: wireframe/solid/material preview/rendered. Overlay visibility configurable. Max size enforced with aspect ratio preservation. Format must be supported by runtime + config. Focus object resolved deterministically; missing → reject or ignore per policy. Read-only on scene content — temporary view adjustments restored after. Fallback to offscreen/active camera capture if viewport context unavailable; else clear limitation error. Existing artifact → configured overwrite policy (overwrite/reject/unique variant). Atomic write where supported. Returns file ref, not raw payload. Metadata: dimensions, format, shading mode, duration.
- **Edge Cases**: Empty viewport, focus object not found, unsupported format, oversized viewport, no active 3D view, headless limitation, hidden focus object, locked view, unsupported shading, timeout, permission denied, existing artifact conflict, memory limit
- **Error Handling**: Render output error (invalid/unwritable destination); security violation (delegated); validation error (invalid params); timeout error

### FR-RND-002: Render Scene Image

- **Description**: Render scene to image artifact at validated output location; long-running → job feature
- **Input**: Render request (output destination, resolution, samples, denoising, engine, color mode, transparency, camera ref, overwrite policy, timeout, background execution policy)
- **Output**: Render result (success, artifact ref, render time, stats, resolution) or task reference for background
- **Rules**: Output destination validated through security before render begins. Resolution + samples within configured bounds. Denoising optional, degrades gracefully if unsupported by active engine. Engine preference → falls back to available if requested unavailable. Active camera must exist/resolvable; missing → configuration if policy allows, else scene state indication. Long-running → job feature + task reference. Capacity exhaustion → capacity error, no partial side effects. Temporary file → finalize atomically on success. Overwrite policy for existing artifact. Cancellation of background render = best-effort (main-thread constraints). Stats: render time, resolution, samples, engine, denoising status. Events emitted for completion/failure/submission. Output artifact ref never exposes sensitive filesystem beyond allowed diagnostic metadata.
- **Edge Cases**: Invalid destination, permission denied, missing dir, timeout, denoising unsupported, no active camera, empty scene, unsupported engine, OOM, existing artifact conflict, very high resolution, transparency unsupported, canceled, capacity full, connection loss during render
- **Error Handling**: Render output error; security violation (delegated); capacity error (delegated); timeout error; scene state error (missing camera); execution error (gateway)

### FR-RND-003: Configure Camera

- **Description**: Camera-specific optical/selection setup (lens, framing, active camera, depth of field). Generic positional transform belongs to object feature.
- **Input**: Camera setup (camera ref or creation policy, lens/focal length, sensor fit, framing target, active camera policy, depth of field settings)
- **Output**: Camera configuration result (success, resolved camera ref, settings summary, active camera status)
- **Rules**: Camera created if not exist + creation policy allows. Resolution deterministic: explicit ref → active scene camera → first available (if policy allows). No camera + creation disallowed → camera setup failure with scene state indication. Lens/focal length within valid range. May designate as active scene camera. Locked/protected state respected unless override. Depth of field: enablement, focus distance/ref, aperture control. Framing target may adjust orientation while preserving lens. Doesn't modify shared/linked camera data unless allowed. Generic transform belongs to object feature — not duplicated here. Returns resolved ref + final config.
- **Edge Cases**: Multiple cameras, locked, invalid lens values, missing ref with creation disallowed, linked data, constraint overriding config, incompatible type, creation not permitted, focus object not found for DoF, unsupported DoF in engine
- **Error Handling**: Camera setup error; validation error; scene state error; protection/lock error

### FR-RND-004: Configure HDRI Lighting

- **Description**: Apply HDRI environment lighting using locally available file from asset feature. Render never downloads HDRI itself.
- **Input**: HDRI setup (local cached file reference resolved by Asset, strength, rotation, background visibility policy, environment overwrite policy). On the CLI surface, `hdri_id` is the local `.hdr`/`.exr` path returned by asset resolution; it is not a provider ID and it never triggers download.
- **Output**: Environment result (success, resolved environment ref, applied strength/rotation)
- **Rules**: Two-step flow: asset feature download → local file ref → this feature lighting config. Render never resolves provider IDs or downloads directly. Not locally available → delegate acquisition to asset before proceeding. Strength within valid range (default 0–10). Rotation normalized per angle convention. Existing environment: replace/update/reject per policy. Applies to scene world/equivalent; world created if missing + policy allows. Background visibility: visible background vs lighting-only. Non-environment lighting objects preserved unless explicitly replaced. Local HDRI file ref validated through security before use. Returns resolved env ref + final settings.
- **Edge Cases**: HDRI not found, download failed, unsupported format, existing environment conflict, strength out of range, rotation overflow, missing scene world, linked world data, provider failure, cache unavailable, file outside allowed directory, node incompatibility
- **Error Handling**: Asset not found (delegated); provider error (delegated); validation error; environment state error; security violation (file path validation)

### FR-RND-005: Configure Render Settings

- **Description**: Update bounded scene render settings without starting a render.
- **Input**: Optional engine, resolution width/height, resolution percentage, sample count, and transparent-film flag.
- **Output**: Effective engine, dimensions, percentage, transparency, and available engine-specific sample value.
- **Rules**: Dimensions are bounded to 1–16384 pixels, percentage to 1–100, and samples to 1–65536. Requested engine must exist in Blender's runtime enum. Omitted fields retain their current values except documented defaults supplied by the action schema. The action does not write an image and does not download assets. Engine-specific sample settings degrade gracefully when the active engine does not expose them.
- **Edge Cases**: Unsupported engine, invalid bounds, engine without sample property, background context, render settings changed concurrently.
- **Error Handling**: Validation error for invalid bounds or engine; render state error for unavailable scene settings.

## Boundary: Render vs Object

Render: camera-specific (lens, focal length, framing, active camera, depth of field, sensor fit). Object: generic transform (location, rotation, scale on any object type including cameras). Higher layers compose both without duplication.

## Error Categories

- render output error — destination invalid/unwritable or artifact production failed
- camera setup error — configuration could not be applied
- security violation — path/file validation failed (delegated)
- capacity error — background render capacity exceeded (delegated)
- timeout error — capture/render exceeded duration
- validation error — invalid capture/render/camera/lighting params
- asset not found — HDRI unavailable (delegated)
- environment state error — scene incompatible with HDRI config
- scene state error — condition blocks operation (missing camera)

## Events

- viewport captured (format, dimensions, artifact ref indicator)
- scene render completed (duration, resolution, samples, engine)
- scene render failed (categorized error + phase)
- render submitted to background (task ref)
- camera configured (settings summary)
- HDRI lighting configured (strength, rotation)

Payloads: category, operation summary, tracking ID, duration, error category, task ref. Never: raw image payloads, full filesystem paths, sensitive asset credentials, oversized stats.

## Configuration Keys

| Key | Description | Default |
|---|---|---|
| default_render_output_directory | Validated output root | App-managed output dir |
| screenshot_file_format | Default format | Lossless raster |
| maximum_render_time | Sync render bound before background | Conservative |
| default_hdri_strength | When request omits | Moderate |
| screenshot_maximum_size | Max dimensions + aspect ratio | Conservative |
| output_overwrite_policy | overwrite/reject/unique_variant | unique variant |
| resolution_and_sample_bounds | Allowed ranges | Bounded conservative |
| default_denoising | When request omits | Enabled if engine supports |
| default_hdri_rotation | When request omits | 0 |
| background_render_eligibility | Auto-submit long renders to job | Enabled |

## QA Checklist

- [ ] Screenshot captured to validated location; returns file ref, not raw payload
- [ ] View angle + shading mode respected; max size enforced
- [ ] Focus object resolved or handled per policy
- [ ] Fallback/fail gracefully when viewport context unavailable
- [ ] Overwrite policy respected; atomic write
- [ ] Render output via security path validation before start
- [ ] Resolution + sample bounds enforced
- [ ] Denoising degrades gracefully if unsupported
- [ ] Engine preference falls back to available
- [ ] Missing active camera → configuration or scene state indication
- [ ] Long-running → job feature + task ref
- [ ] Background capacity exhaustion → capacity error, no partial side effects
- [ ] Temporary file → atomic finalization
- [ ] Canceled background = best-effort
- [ ] Stats: duration, resolution, samples, engine, denoising
- [ ] Camera: lens, framing, active designation, DoF
- [ ] Render settings: engine validation, resolution/percentage/sample bounds, transparency
- [ ] Camera resolution deterministic (explicit → active → first)
- [ ] Locked camera respected; generic transform not duplicated
- [ ] HDRI lighting uses asset feature for download (never direct)
- [ ] Strength/rotation validated; existing env handled per policy
- [ ] World created if missing + policy allows
- [ ] Background visibility: lighting-only vs visible
- [ ] Local file ref validated via security
- [ ] No overlap with object (transform), asset (download), job (lifecycle)
- [ ] All 6 events emitted
