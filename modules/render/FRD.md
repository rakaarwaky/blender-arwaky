# FRD — Rendering & Viewport Feature

## Purpose

Manages screenshot, render, camera setup, and HDRI lighting.

## Scope

- Viewport screenshot
- Scene render
- Render settings
- Camera configuration
- HDRI environment lighting
- Output file policy for render

## Out of Scope

- Asset download (owner: `asset`)
- Generic object manipulation (owner: `object`)
- Scene cleanup (owner: `scene`)
- Background task lifecycle (owner: `job`)
- Queue (owner: `gateway`)
- Path traversal protection (owner: `security`)

## Depends On

- `gateway`
- `security`
- `job`
- `asset` (HDRI file download)
- `config`

## Provides To

- `dispatcher`

## Functional Requirements

### FR-RND-001: Capture Viewport Screenshot

Capture current viewport as image. Return file path.

### FR-RND-002: Render Scene Image

Render full scene image. Uses security for output path validation. Uses job for long-running renders. Uses diagnostics for metrics/logging.

### FR-RND-003: Configure Camera

Set camera lens, framing, active camera, depth of field. Render owns camera-specific setup. Object owns generic transform.

### FR-RND-004: Configure HDRI Lighting

Set HDRI environment lighting. Render does not download HDRI itself — uses `asset` feature to get HDRI file.

```
asset.download_asset(hdri_id) -> local file
render.configure_hdri(local_file, strength) -> world lighting
```

## Boundary: Render vs Object

- Render: camera-specific setup (lens, framing, DOF, active camera)
- Object: generic transform (location, rotation, scale)

## Error Categories

- `RenderOutputError` — render output path invalid
- `CameraSetupError` — camera configuration failed
- `SecurityViolationError` — output path validation failed (via security)
- `CapacityError` — background render queue full (via job)

## Events

- `render.screenshot` — viewport captured
- `render.completed` — scene render completed
- `render.camera_configured` — camera setup applied
- `render.hdri_configured` — HDRI lighting applied

## Configuration Keys

- `render.output_dir` — default render output directory
- `render.screenshot_format` — screenshot file format
- `render.render_timeout` — max render time
- `render.hdri_strength` — default HDRI strength

## QA Checklist

- [ ] Viewport screenshot captured and saved
- [ ] Scene render uses security for output path
- [ ] Long-running render tracked via job
- [ ] Camera-specific setup (lens, framing, DOF)
- [ ] HDRI lighting uses asset for file download
- [ ] No overlap with `object` (generic transform) or `asset` (download)
