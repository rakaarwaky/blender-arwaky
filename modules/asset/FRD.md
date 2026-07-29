# FRD — External Asset Feature

## Purpose

Single authority for everything entering blender-arwaky from outside: search providers, download to local cache, extract archives under security supervision, import into Blender. Provider-specific behavior isolated behind internal adapters. Does not manipulate imported objects, light scenes, or track work — those belong to object, render, job features.

## Scope

- Provider search (single unified operation)
- Provider authentication with safe credential handling
- Asset metadata normalization across providers
- Download to local cache with integrity verification
- Cache reuse and eviction policy
- Overwrite policy for cached artifacts
- Resolution preference for multi-resolution providers
- Safe archive extraction delegated to security policy
- Asset import into Blender with object reference handoff
- License and attribution metadata preservation
- Background download coordination through job feature
- Provider capability and health awareness

## Out of Scope

Object manipulation, scene cleanup, HDRI lighting setup, render output, path traversal protection, background task lifecycle, settings loading, marketplace purchase flows, licensing compliance decisions, cloud asset storage sync.

## Depends On

config (cache location, provider enablement, overwrite policy, size limits), security policy (path validation, archive extraction safety), job (large download tracking, capacity), gateway (import command transport to Blender).

## Provides To

dispatcher, render (local HDRI file references for lighting).

## Functional Requirements

### FR-AST-001: Search Assets Across Providers

- **Description**: Query enabled providers through one unified search, return normalized aggregated results
- **Input**: Search request (text query, optional provider/asset type/category filter, result limit, pagination cursor)
- **Output**: Search result (normalized asset metadata list, provider status summary, pagination metadata, warnings)
- **Rules**: 1 search operation regardless of provider count. Provider adapters encapsulate request shaping, auth, parsing. Each enabled provider queried independently with own timeout. Provider failure non-blocking; partial results returned when ≥1 provider succeeds. Results normalized to common shape before aggregation. Duplicate assets deduplicated when equivalence is safely determinable. Empty query returns curated/default results if provider supports. Disabled providers excluded with warning. Marketplace providers filter to downloadable by default. Rate limits surfaced as warning/error. Pagination provider-specific. Credentials never in results/logs/events.
- **Edge Cases**: All providers fail, empty query, no providers registered, provider disabled/timeout/rate-limited/malformed response, missing auth, no results, partial pagination cursor, oversized result set, duplicates across providers
- **Error Handling**: Per-provider error with aggregated summary when all fail; validation error for malformed params; auth error for missing/invalid credentials; partial results whenever possible

### FR-AST-002: Download Asset to Cache

- **Description**: Acquire asset file from provider into local cache with integrity verification, background coordination for large transfers
- **Input**: Download request (provider ID, asset ID, type, resolution preference, overwrite policy, background execution policy)
- **Output**: Download result (success, local artifact ref, size, cache status, integrity status) or task reference for background
- **Rules**: Cache location from config, validated by security. Overwrite policy: reuse/overwrite/create_unique. Valid cached artifact reused without network. Corrupted artifact → re-download or cache error. Integrity verification when checksum available. Atomic write (temp → final). Max download size enforced. Resolution preference when offered. Large downloads → job feature, task reference returned. Capacity exhaustion → capacity error, no partial cache side-effects. Credentials never logged. License/attribution recorded. Download ≠ import. Concurrent same-asset downloads resolve to one transfer.
- **Edge Cases**: Asset not found, provider unavailable, timeout, permission denied, cache full, corrupted artifact, checksum mismatch, rate limit, auth failure, oversized asset, network interruption, concurrent download of same asset, resolution unavailable
- **Error Handling**: Asset not found, provider error, security violation (delegated), capacity error (delegated), cache error, timeout error

### FR-AST-003: Extract Asset Archive

- **Description**: Extract downloaded archives under security policy supervision. Must not implement traversal protection locally.
- **Input**: Extraction request (artifact ref, destination, options)
- **Output**: Extraction result (success, extracted file refs, rejected entry summary)
- **Rules**: All archive safety decisions delegated to security: entry path validation, traversal/escape rejection, depth/size/entry count limits, symlink/hardlink policy. Asset never implements own traversal protection. Destination validated by security before any write. Plan-level approval. Rejected entries reported without exposing unsafe paths. Already-extracted valid artifact reused. Partial extraction cleaned up on failure. Unsupported format → validation error. Nested archives follow same supervision.
- **Edge Cases**: Entry outside destination, nested archive, archive bomb, excessive count/size, symlink/hardlink, invalid encoding, duplicate names, unsupported format, permission denied, partial extraction after failure, disk full
- **Error Handling**: Archive safety error (delegated), security violation (delegated), cache error, validation error

### FR-AST-004: Import Asset into Blender

- **Description**: Import locally available asset file into Blender, return object references. Object manipulation after handoff belongs to object feature.
- **Input**: Import request (file ref, asset type, target collection, scale normalization policy, duplicate handling policy, format hint)
- **Output**: Import result (success, object refs, metadata summary including license attribution)
- **Rules**: File must exist locally first → missing file directs caller to download. Import via gateway (never direct Blender talk). Scale normalization optional. Duplicate handling: rename/reuse/replace/reject. Object added to active scene + target collection if specified. Feature responsibility ends at object ref handoff. Long-running imports may use job feature. License/attribution preserved. Import failure distinguished from download/extraction failure. Missing texture dependencies → warnings when import succeeds.
- **Edge Cases**: Unsupported format, corrupted file, missing local file, import failure in Blender, missing target collection, duplicate asset, oversized scene, missing texture dependencies, format version mismatch, linked data conflict, timeout
- **Error Handling**: Import error (Blender-side), asset not found with download guidance, validation error, scene state error, timeout error (delegated)

### FR-AST-005: Manage Provider Metadata

- **Description**: Normalize provider-specific asset descriptions into one consistent metadata shape
- **Input**: Raw provider asset description
- **Output**: Normalized asset metadata
- **Rules**: Normalized shape: name, provider ID, asset ID, type, categories, preview/thumbnail ref, license summary, download availability flag. Missing optional fields → safe empty values, never absent. License info is informational only. Attribution preserved. Preview refs never embed credentials. Pagination cursors opaque. Provider capability metadata describes supported types/pagination/auth. Cache within freshness window. Stale metadata refreshed before download. Provider extra fields preserved in extension container without breaking common shape. No secrets exposed.
- **Edge Cases**: Missing required fields, unknown license, preview unavailable, provider-specific extras, conflicting metadata across providers, stale cache, schema changed
- **Error Handling**: Provider error on retrieval failure; validation error when normalization unsafe; stale metadata refreshed/flagged

## Boundary: Asset vs Object

Asset owns acquisition+import (search, download, cache, extraction, import → object refs). Object owns manipulation of existing objects (transform, material, modifier, deletion). Asset hands objects into scene; object takes over.

## Boundary: Asset vs Render

Asset owns HDRI file acquisition (search, download, cache, local file). Render owns HDRI lighting config (world env, strength, rotation, background visibility). Asset never touches scene lighting; render never downloads files.

## Error Categories

| Category | Description |
|---|---|
| asset not found | Not in any provider, or local file missing at import |
| asset import error | Blender import failed after successful acquisition |
| provider error | API failure, timeout, malformed response |
| security violation | Path/archive validation failed (delegated) |
| capacity error | Download capacity exceeded (delegated) |
| cache error | Unreadable, unwritable, corrupted, full |
| archive safety error | Extraction limits violated (delegated) |
| authentication error | Provider credentials missing/invalid |
| timeout error | Download/import exceeded configured duration |
| validation error | Malformed search/download/extraction/import params |

## Events

- asset searched (result count + provider status)
- asset downloaded (size, resolution, integrity)
- asset cache hit (reused without network)
- archive extracted (entry counts)
- asset imported (object ref count)
- provider degraded (failed/rate-limited while others continued)

Payloads include category, provider ID, asset ID, type, size, duration, cache status, tracking ID, error category. Never: credentials, signed locations, full paths, raw provider responses, license legal text.

## Configuration Keys

| Key | Description | Default |
|---|---|---|
| local_cache_directory | Where artifacts reside | App-managed cache dir |
| overwrite_policy | reuse/overwrite/create_unique | reuse |
| enabled_providers | Active for search+download | All supported |
| maximum_download_size | Single asset upper bound | Conservative |
| resolution_preference | Preferred when multiple offered | Highest within size limit |
| cache_eviction_policy | How excess entries removed | Oldest terminal first, size cap |
| default_result_limit | Search results per provider | Conservative count |
| provider_timeout | Max wait per provider request | Conservative |
| integrity_verification | Checksum/size check after download | Enabled when checksum available |
| extraction_destination_policy | Where extracted content may reside | Inside validated cache subtree |

## QA Checklist

- [ ] Search returns normalized results from all enabled providers
- [ ] Single search operation regardless of provider count
- [ ] Provider adapters encapsulate all provider-specific behavior
- [ ] Single provider failure → partial results from remaining providers
- [ ] All providers fail → empty result with aggregated error
- [ ] Credentials never in results/logs/events
- [ ] Traversal protection: download uses security for path validation
- [ ] Atomic write (temp → final)
- [ ] Valid cached artifact reused without network
- [ ] Corrupted artifact → re-download or error
- [ ] Integrity verified when checksum available
- [ ] Max download size enforced
- [ ] Large downloads tracked via job with task ref returned
- [ ] Capacity exhaustion → capacity error, no partial cache
- [ ] Archive extraction uses security, not own traversal
- [ ] Destination validated before any write
- [ ] Rejected entries reported without exposing unsafe paths
- [ ] Partial extraction cleaned up on failure
- [ ] Nested archives follow same supervision
- [ ] Import returns object refs
- [ ] Import failure distinguished from download/extraction failure
- [ ] Missing local file directs toward download
- [ ] Duplicate import handled per configured policy
- [ ] License/attribution preserved through download and import
- [ ] Post-import manipulation delegated to object feature
- [ ] HDRI download separate from render lighting setup
- [ ] All 6 events emitted
