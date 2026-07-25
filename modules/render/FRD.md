# FRD — render (Render Feature Module)

## System Overview

The render module handles viewport capture, image rendering, camera setup, and HDRI environment lighting. It provides the render operate protocol and viewport capture capabilities. Asset search and orchestration are handled by separate modules (asset, shared).

## Functional Requirements

### FR-RND-001: Get Viewport Screenshot

- **Description**: Capture current viewport as image with configurable presets
- **Input**: GetScreenshotRequestVO (max_size, view_angle, shading, show_overlays, focus_object, format)
- **Output**: ScreenshotResponseVO (success, image_data: bytes, format, width, height)
- **Business Rules**: View angle must be PERSPECTIVE/ORTHO; shading must be WIREFRAME/SOLID/MATERIAL/RENDERED
- **Edge Cases**: Empty viewport, focused object not found, unsupported format
- **Error Handling**: ExecutionError for Blender rendering failures

### FR-RND-002: Render Image

- **Description**: Render scene to image file with specified settings
- **Input**: RenderRequestVO (output_path, resolution_x, resolution_y, samples, use_denoising)
- **Output**: RenderResponseVO (success, image_path, render_time, message)
- **Business Rules**: Output path must be writable; resolution 1-8192; samples 1-4096
- **Edge Cases**: Invalid output path, render timeout, denoising not supported
- **Error Handling**: ExecutionError for render failures

### FR-RND-003: Setup Camera

- **Description**: Position and configure camera for rendering
- **Input**: Camera setup parameters (position, rotation, lens, focal_length)
- **Output**: Camera configuration applied
- **Business Rules**: Camera must be created if not exists; lens values in valid range
- **Edge Cases**: Multiple cameras, locked camera, invalid lens values
- **Error Handling**: SceneValidationError for invalid camera parameters

### FR-RND-004: Setup HDRI Lighting

- **Description**: Configure environment lighting from HDRI asset
- **Input**: HDRI ID, strength, rotation
- **Output**: HDRI applied to scene environment
- **Business Rules**: HDRI must be downloaded first via asset module; strength 0.0-10.0
- **Edge Cases**: HDRI not found, download failed, existing environment
- **Error Handling**: AssetNotFoundError, ProviderError (delegated to asset module)

## API Contract

| Operation | Input | Output | Description |
|-----------|-------|--------|-------------|
| `get_viewport_screenshot` | GetScreenshotRequestVO | ScreenshotResponseVO | Capture viewport |
| `render` | RenderRequestVO | RenderResponseVO | Render to file |
| `setup_camera` | Camera params | Camera config | Position camera |
| `setup_hdri` | HDRI params | Environment applied | Configure lighting |

## Integration Points

- **Internal**: shared (taxonomy VOs, contracts), server (Blender connection), asset (HDRI download)
- **External**: Blender Python API (bpy) — via server module

## Non-functional Requirements

- Performance: Screenshot capture within 3 seconds; render within 60 seconds for standard scenes
- Reliability: Graceful fallback on render failures

## Test Scenarios / QA Checklist

- [ ] Screenshot with valid params returns image bytes
- [ ] Screenshot with invalid view angle returns ValidationError
- [ ] Render with valid params produces image file
- [ ] Render with invalid path returns ValidationError
- [ ] Camera setup creates camera if not exists
- [ ] HDRI setup applies environment lighting

## Assumptions & Constraints

- Blender must be running for viewport/render operations
- HDRI download handled by asset module
- Internet connection required for HDRI download only

## Glossary

- **HDRI**: High Dynamic Range Image for environment lighting
- **Viewport**: The 3D view in Blender's UI

## Reference

- PRD: [../../PRD.md](../../PRD.md)
- FRD shared: [../shared/FRD.md](../shared/FRD.md)
- FRD asset: [../asset/FRD.md](../asset/FRD.md)
