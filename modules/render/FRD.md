# FRD — Rendering & Viewport Feature

## System Overview
The Render module is the single authority for image production and camera optics. It captures viewports, renders scenes to validated output locations, configures camera-specific behavior, and applies HDRI environment lighting using files from the Asset module.

## Functional Requirements

### FR-001: Viewport Screenshot and Scene Render
- **Description**: Capture viewport as image artifact and render scene to output artifact.
- **Input**: `filepath`, `max_size`, `view_angle`, `output_path`, `resolution_x`, `samples`, `engine`.
- **Output**: `UnifiedEnvelope` with artifact file ref, dimensions, render time, or task reference for background.
- **Business Rules**: Output location validated by `security`. Max size enforced. Long-running renders routed to `job`. Overwrite policy respected.
- **Edge Cases**: Empty viewport; missing active camera; OOM; invalid destination; capacity full.
- **Error Handling**: `render_output_error`; `security_violation`; `capacity_error`; `scene_state_error`.

### FR-002: Camera and HDRI Lighting Configuration
- **Description**: Configure camera optics (lens, framing, DoF) and apply HDRI environment lighting.
- **Input**: `camera_ref`, `focal_length`, `framing_target`, `hdri_id` (local path), `strength`.
- **Output**: `UnifiedEnvelope` with resolved camera/env refs and settings summary.
- **Business Rules**: Camera resolution deterministic (explicit → active → first). HDRI lighting uses local file ref from `asset`. Render never downloads HDRI directly. Generic transform belongs to `object`.
- **Edge Cases**: Multiple cameras; locked camera; HDRI not found locally; strength out of range.
- **Error Handling**: `camera_setup_error`; `asset_not_found` (delegated); `validation_error`.

### FR-003: Render Settings Management
- **Description**: Update bounded scene render settings without starting a render.
- **Input**: `engine`, `resolution_x`, `resolution_y`, `resolution_percentage`, `samples`.
- **Output**: `UnifiedEnvelope` with effective settings.
- **Business Rules**: Dimensions bounded 1–16384. Percentage 1–100. Samples 1–65536. Engine must exist in Blender runtime enum.
- **Edge Cases**: Unsupported engine; invalid bounds; engine without sample property.
- **Error Handling**: `validation_error` for invalid bounds/engine.

## API Contract

| Operation | Input | Output | Description |
|---|---|---|---|
| `get_viewport_screenshot` | `filepath`, `max_size`, `view_angle` | `UnifiedEnvelope` | AI-optimized viewport capture |
| `render` | `output_path`, `resolution_x`, `samples` | `UnifiedEnvelope` | Full frame render (job eligible) |
| `configure_camera` | `camera_ref`, `focal_length`, `framing_target`| `UnifiedEnvelope` | Setup camera optics/DoF |
| `setup_environment` | `hdri_id`, `strength` | `UnifiedEnvelope` | Apply HDRI lighting |
| `set_render_settings` | `engine`, `resolution_x`, `samples` | `UnifiedEnvelope` | Update scene render bounds |

## Integration Points

- **3rd Party**: No 3rd party integrations.
- **Internal**: `gateway` (transport), `security` (path validation), `job` (background tracking), `asset` (HDRI files), `config` (output dirs).

## Non-functional Requirements (Detailed)

- **Performance**: Synchronous renders bounded by `maximum_render_time` before auto-submitting to background.
- **Security**: Output paths strictly validated by `security` to prevent filesystem traversal.
- **Scalability**: Background renders respect `job` capacity limits. Temporary files finalized atomically.

## Test Scenarios / QA Checklist

- [ ] Verify viewport screenshot returns file ref, not raw image payload.
- [ ] Verify render output path is validated by `security` before render begins.
- [ ] Verify long-running renders auto-submit to `job` feature and return task ref.
- [ ] Verify HDRI lighting rejects provider IDs and requires local file path from `asset`.
- [ ] Verify `set_render_settings` enforces resolution and sample bounds.

## Assumptions & Constraints

- Render owns camera optics and HDRI lighting; Object owns generic positional transform.
- Asset owns HDRI file acquisition; Render never downloads files directly.

## Glossary

- **HDRI**: High Dynamic Range Image, used for environment lighting and reflections.
- **Artifact Ref**: Secure reference to a generated image file on the local filesystem.
- **UnifiedEnvelope**: The standardized JSON response wrapper containing success indicator, data payload, error category, tracking ID, and warnings.
- **WorkspacePath**: Absolute, normalized filesystem path derived from Config.

## Reference

- PRD: `./PRD.md`
- Depends On: `gateway`, `security`, `job`, `asset`, `config`, `dispatcher`
