# FRD — External Asset Management

## System Overview
The Asset module is the single authority for everything entering blender-arwaky from outside: searching providers, downloading to local cache, extracting archives under security supervision, and importing into Blender. It isolates provider-specific behavior behind internal adapters.

## Functional Requirements

### FR-001: Search Assets Across Providers
- **Description**: Query enabled providers through one unified search and return normalized aggregated results.
- **Input**: `query` (text), `provider_filter`, `asset_type_filter`, `limit`, `page_token`.
- **Output**: `UnifiedEnvelope` containing normalized asset metadata list, provider status summary, and pagination metadata.
- **Business Rules**: 1 search operation regardless of provider count. Provider failure is non-blocking; partial results returned when ≥1 provider succeeds. Duplicate assets deduplicated. Credentials never in results.
- **Edge Cases**: All providers fail; empty query; rate limits surfaced as warnings; oversized result sets.
- **Error Handling**: `provider_error` aggregated when all fail; `validation_error` for malformed params; `authentication_error` for missing credentials.

### FR-002: Download Asset to Cache
- **Description**: Acquire asset file from provider into local cache with integrity verification.
- **Input**: `provider_id`, `asset_id`, `type`, `resolution_preference`, `overwrite_policy`, `background_execution_policy`.
- **Output**: `UnifiedEnvelope` with local artifact ref, size, cache status, or task reference for background.
- **Business Rules**: Cache location validated by `security`. Overwrite policy: reuse/overwrite/create_unique. Atomic write (temp → final). Large downloads routed to `job` feature.
- **Edge Cases**: Asset not found; cache full; corrupted artifact; checksum mismatch; concurrent download of same asset.
- **Error Handling**: `asset_not_found`; `security_violation` (delegated); `capacity_error` (delegated); `cache_error`.

### FR-003: Extract Asset Archive
- **Description**: Extract downloaded archives under security policy supervision.
- **Input**: `artifact_ref`, `destination`, `options` (max entries, max size, allow symlinks).
- **Output**: `UnifiedEnvelope` with extracted file refs and rejected entry summary.
- **Business Rules**: All archive safety decisions delegated to `security`. Asset never implements own traversal protection. Rejected entries reported without exposing unsafe paths.
- **Edge Cases**: Entry outside destination; nested archive; archive bomb; excessive count/size; symlink/hardlink.
- **Error Handling**: `archive_safety_error` (delegated); `security_violation` (delegated); `validation_error`.

### FR-004: Import Asset into Blender
- **Description**: Import locally available asset file into Blender and return object references.
- **Input**: `file_path`, `asset_type`, `target_collection`, `scale_normalization`, `duplicate_policy`, `format_hint`.
- **Output**: `UnifiedEnvelope` with object refs and metadata summary including license attribution.
- **Business Rules**: File must exist locally. Import via `gateway`. Duplicate handling: rename/reuse/replace/reject. Feature responsibility ends at object ref handoff.
- **Edge Cases**: Unsupported format; missing local file; missing target collection; missing texture dependencies.
- **Error Handling**: `asset_import_error` (Blender-side); `asset_not_found` with download guidance; `validation_error`.

## API Contract
| Operation | Input | Output | Description |
|---|---|---|---|
| `search_assets` | `query`, `providers`, `limit`, `page_token` | `AssetSearchResult[]` | Unified provider search with normalized, deduplicated results and pagination metadata; partial results on provider failure; raises `provider_error` when all providers fail, `validation_error` on malformed params, `authentication_error` on missing credentials |
| `get_provider_metadata` | `provider`, `asset_id` | `ProviderAssetMetadata` | Raw provider asset description; raises `asset_not_found`, `authentication_error` |
| `download_asset` | `provider`, `asset_id`, `cache_dir`, `background` | `ArtifactRef | TaskRef` | Download to local cache with atomic write (temp → final); large downloads routed to Job and return `TaskRef`; raises `asset_not_found`, `security_violation`, `capacity_error`, `cache_error` |
| `extract_asset` | `artifact_path`, `destination`, `max_entries` | `ExtractedFileRef[]` | Safe archive extraction under Security supervision; rejected entries reported without exposing unsafe paths; raises `archive_safety_error`, `security_violation`, `validation_error` |
| `import_asset` | `file_path`, `asset_type`, `target_collection` | `AssetImportReport` | Import local file to Blender; returns object refs and metadata including license attribution; raises `asset_import_error`, `asset_not_found` with download guidance, `validation_error` |
| `import_glb` | `file_path`, `object_name` | `BlenderObjectRef` | Specific GLB/GLTF import; raises `asset_not_found`, `validation_error` for unsupported format, `execution_error` on Blender-side failure |
| `export_model` | `object_name`, `file_path`, `export_format` | `ArtifactRef` | Export scene object to validated file path; raises `not_found`, `security_violation` on unsafe path, `execution_error` |
| `place_asset` | `asset_id`, `location`, `rotation`, `scale` | `BlenderObjectRef` | Position existing asset in scene; raises `not_found`, `validation_error` on non-finite coordinates |
## Integration Points

- **3rd Party**: External Asset Providers (Polyhaven, Sketchfab, etc.) via HTTPS APIs.
- **Internal**: `config` (cache location), `security` (path/archive validation), `job` (large download tracking), `gateway` (import transport).

## Non-functional Requirements (Detailed)

- **Performance**: Provider timeouts bounded by `provider_timeout` config. Single search operation parallelizes provider requests.
- **Security**: Path traversal and archive bomb protection strictly delegated to `security`. Credentials never logged or exposed in events.
- **Scalability**: Concurrent same-asset downloads resolve to one transfer. Background downloads managed by `job` capacity limits.

## Test Scenarios / QA Checklist

- [ ] Verify single search operation returns normalized results from all enabled providers.
- [ ] Verify single provider failure yields partial results from remaining providers.
- [ ] Verify atomic write (temp → final) during cache downloads.
- [ ] Verify archive extraction rejects entries outside destination without exposing unsafe paths.
- [ ] Verify import failure is distinguished from download/extraction failure.

## Assumptions & Constraints

- Asset feature owns acquisition and import; Object feature owns post-import manipulation.
- HDRI file acquisition belongs to Asset; HDRI lighting configuration belongs to Render.
- Marketplace purchase flows and licensing compliance decisions are out of scope.

## Glossary

- **Artifact Ref**: A secure, local filesystem reference to a downloaded and verified asset.
- **Provider Adapter**: Internal component encapsulating provider-specific request shaping, auth, and parsing.
- **WorkspacePath**: Absolute, normalized filesystem path derived from Config.
- **UnifiedEnvelope**: The standardized JSON response wrapper containing success indicator, data payload, error category, tracking ID, and warnings.

## Reference

- PRD: `./PRD.md`
- Depends On: `config`, `security`, `job`, `gateway`
