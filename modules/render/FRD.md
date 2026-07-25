# FRD — render (Render Feature Module)

## System Overview

The render module handles viewport capture, image rendering, camera setup, and asset provider integrations. It contains the render protocol, viewport capture port, and asset search capabilities.

```
modules/render/
├── render_operate_protocol.py   ← RenderOperateProtocol ABC
├── viewport_capture_port.py     ← ViewportCapturePort ABC
├── polyhaven_adapter.py         ← AssetProviderPort for Poly Haven
├── sketchfab_adapter.py         ← AssetProviderPort for Sketchfab
├── capabilities_render_operate_executor.py  ← Rendering logic
├── capabilities_asset_search_collector.py   ← Multi-provider search
├── agent_search_expert_orchestrator.py      ← Asset search orchestrator
├── agent_refinement_expert_orchestrator.py  ← Iterative refinement
└── __init__.py
```

## Functional Requirements

### FR-001: Get Viewport Screenshot

- **Description**: Capture current viewport as image with configurable presets
- **Input**: GetScreenshotRequestVO (max_size, view_angle, shading, show_overlays, focus_object, format)
- **Output**: ScreenshotResponseVO (success, image_data: bytes, format, width, height)
- **Business Rules**: View angle must be PERSPECTIVE/ORTHO; shading must be WIREFRAME/SOLID/MATERIAL/RENDERED
- **Edge Cases**: Empty viewport, focused object not found, unsupported format
- **Error Handling**: ExecutionError for Blender rendering failures

### FR-002: Render Image

- **Description**: Render scene to image file with specified settings
- **Input**: RenderRequestVO (output_path, resolution_x, resolution_y, samples, use_denoising)
- **Output**: RenderResponseVO (success, image_path, render_time, message)
- **Business Rules**: Output path must be writable; resolution 1-8192; samples 1-4096
- **Edge Cases**: Invalid output path, render timeout, denoising not supported
- **Error Handling**: ExecutionError for render failures

### FR-003: Setup Camera

- **Description**: Position and configure camera for rendering
- **Input**: Camera setup parameters (position, rotation, lens, focal_length)
- **Output**: Camera configuration applied
- **Business Rules**: Camera must be created if not exists; lens values in valid range
- **Edge Cases**: Multiple cameras, locked camera, invalid lens values
- **Error Handling**: SceneValidationError for invalid camera parameters

### FR-004: Setup HDRI Lighting

- **Description**: Configure environment lighting from HDRI asset
- **Input**: HDRI ID, strength, rotation
- **Output**: HDRI applied to scene environment
- **Business Rules**: HDRI must be downloaded first; strength 0.0-10.0
- **Edge Cases**: HDRI not found, download failed, existing environment
- **Error Handling**: AssetNotFoundError, ProviderError

### FR-005: Multi-Provider Asset Search

- **Description**: Search assets across Poly Haven and Sketchfab simultaneously
- **Input**: Search query, asset type filter, result limit
- **Output**: Aggregated search results from all providers
- **Business Rules**: Parallel search; deduplicate by name; respect result limits
- **Edge Cases**: One provider unavailable, empty results, rate limiting
- **Error Handling**: ProviderError for individual provider failures; partial results on degradation

### FR-006: Poly Haven Integration

- **Description**: Search and download assets from Poly Haven
- **Input**: Search query, asset type (HDRI/texture/model)
- **Output**: Asset metadata and download URLs
- **Business Rules**: Use Poly Haven API; respect attribution requirements
- **Edge Cases**: API rate limit, asset not available, download timeout
- **Error Handling**: ProviderError with retry logic

### FR-007: Sketchfab Integration

- **Description**: Search and download models from Sketchfab
- **Input**: Search query, format filter (GLB/FBX/OBJ)
- **Output**: Asset metadata and download URLs
- **Business Rules**: Use Sketchfab API; respect license terms
- **Edge Cases**: API rate limit, format not available, download timeout
- **Error Handling**: ProviderError with retry logic

### FR-008: Search Expert Orchestrator

- **Description**: Multi-step asset search with AI fallback
- **Input**: Search parameters
- **Output**: Found and imported assets
- **Business Rules**: Try providers in order; fallback to AI-guided search
- **Edge Cases**: All providers fail, ambiguous results, import failure
- **Error Handling**: Escalates to caller

## API Contract

| Operation | Input | Output | Description |
|-----------|-------|--------|-------------|
| `get_viewport_screenshot` | GetScreenshotRequestVO | ScreenshotResponseVO | Capture viewport |
| `render` | RenderRequestVO | RenderResponseVO | Render to file |
| `search_assets` | SearchQuery | AssetSearchResponseVO | Multi-provider search |
| `download_asset` | AssetDownloadRequestVO | AssetDownloadResponseVO | Download asset |

## Integration Points

- **3rd Party**: Poly Haven API (HDRI/textures/models), Sketchfab API (3D models)
- **Internal**: shared (taxonomy VOs, contracts), scene (environment setup)

## Non-functional Requirements (Detailed)

- Performance: Screenshot capture within 3 seconds; render within 60 seconds for standard scenes
- Reliability: Partial results on provider failure; retry with exponential backoff
- Security: Downloaded assets validated before import

## Test Scenarios / QA Checklist

- [ ] Screenshot with valid params returns image bytes
- [ ] Screenshot with invalid view angle returns ValidationError
- [ ] Render with valid params produces image file
- [ ] Render with invalid path returns ValidationError
- [ ] Search across both providers returns aggregated results
- [ ] Search with one provider down returns partial results
- [ ] Download from Poly Haven succeeds
- [ ] Download from Sketchfab succeeds
- [ ] Search expert orchestrator handles all-provider failure

## Assumptions & Constraints

- Blender must be running for viewport/render operations
- Internet connection required for asset provider APIs
- Asset downloads cached locally to avoid re-download

## Glossary

- **HDRI**: High Dynamic Range Image for environment lighting
- **Viewport**: The 3D view in Blender's UI
- **Provider**: External asset service (Poly Haven, Sketchfab)

## Reference

- PRD: [../../PRD.md](../../PRD.md)
- FRD shared: [../shared/FRD.md](../shared/FRD.md)
