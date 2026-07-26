# FRD — External Asset Feature

## Purpose

Manages search, download, cache, extraction, and import of external assets.

## Scope

- Provider search
- Provider authentication usage
- Asset metadata normalization
- Download to cache
- Cache reuse
- Overwrite policy
- Resolution preference
- Safe archive extraction
- Asset import into Blender
- License/attribution metadata

## Out of Scope

- Object manipulation after import
- Scene cleanup
- HDRI lighting setup
- Render output
- Path traversal protection (owner: `security`)
- Background task lifecycle (owner: `job`)
- Settings loading (owner: `config`)

## Depends On

- `config`
- `security`
- `job`
- `gateway`

## Provides To

- `dispatcher`
- `render`

## Functional Requirements

### FR-AST-001: Search Assets Across Providers

Asset provides one search operation. Provider-specific behavior handled by internal provider adapter.

### FR-AST-002: Download Asset to Cache

Asset downloads file to cache. Asset uses security for path validation. Asset uses job for large downloads.

### FR-AST-003: Extract Asset Archive

Asset uses security for extraction. Asset must not implement path traversal protection itself.

### FR-AST-004: Import Asset into Blender

Asset imports file into Blender. Asset returns object reference. After import, object manipulation is responsibility of `object` feature.

### FR-AST-005: Manage Provider Metadata

Asset normalizes metadata: name, provider, type, categories, preview, license, download availability.

## Boundary: Asset vs Object

- Asset: download + import asset into object
- Object: manipulate existing object

```
asset.import_asset(model.glb) -> object refs
object.set_transform(object_ref, location) -> transform
```

## Boundary: Asset vs Render

- Asset: download HDRI file
- Render: setup HDRI lighting in scene

```
asset.download_asset(hdri_id) -> local file
render.configure_hdri(local_file, strength) -> world lighting
```

## Error Categories

- `AssetNotFoundError` — asset not found in any provider
- `AssetImportError` — import into Blender failed
- `ProviderError` — provider API failure
- `SecurityViolationError` — path validation failed (via security)
- `CapacityError` — download queue full (via job)

## Events

- `asset.searched` — search completed
- `asset.downloaded` — file downloaded to cache
- `asset.imported` — asset imported into Blender

## Configuration Keys

- `asset.cache_dir` — local cache directory
- `asset.overwrite_policy` — how to handle cached files
- `asset.providers` — enabled provider list

## QA Checklist

- [ ] Search returns normalized results from all providers
- [ ] Download uses security for path validation
- [ ] Archive extraction uses security (not own implementation)
- [ ] Import returns object references
- [ ] Large downloads tracked via job
- [ ] HDRI download separate from render lighting setup
