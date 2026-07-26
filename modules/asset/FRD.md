# FRD — External Asset Feature

## Purpose

Manages search, download, cache, extraction, and import of external assets for **blender-arwaky**.

This feature is the single authority for everything that enters the project from outside: discovering assets across providers, acquiring files safely into a local cache, extracting archives under security supervision, and importing acquired files into Blender as usable objects. Provider-specific behavior is isolated behind internal provider adapters so that the rest of the system sees one consistent asset surface.

The asset feature brings files in. It does not manipulate imported objects, light scenes with them, or track long-running work — those responsibilities belong to object, render, and job features respectively.

## Scope

- Provider search through one unified operation
- Provider authentication usage with safe credential handling
- Asset metadata normalization across providers
- Download to local cache with integrity verification
- Cache reuse and eviction policy
- Overwrite policy for cached artifacts
- Resolution preference for multi-resolution providers
- Safe archive extraction delegated to security policy feature
- Asset import into Blender with object reference handoff
- License and attribution metadata preservation
- Background download coordination through job feature
- Provider capability and health awareness

## Out of Scope

- Object manipulation after import, owned by object feature
- Scene cleanup, owned by scene feature
- HDRI lighting setup, owned by render feature
- Render output, owned by render feature
- Path traversal protection, owned by security policy feature
- Background task lifecycle, owned by job feature
- Settings loading, owned by config feature
- Asset marketplace purchase or checkout flows
- Final licensing compliance decisions
- Cloud asset storage synchronization

## Depends On

- config feature for cache location, provider enablement, overwrite policy, and size limits
- security policy feature for path validation and archive extraction safety
- job feature for large download tracking and capacity enforcement
- gateway feature for import command transport into Blender

## Provides To

- dispatcher feature
- render feature, which consumes local HDRI file references for lighting setup

## Functional Requirements

### FR-AST-001: Search Assets Across Providers

Asset provides one search operation. Provider-specific behavior handled by internal provider adapter.

- **Description**: Query enabled providers through one unified search operation and return normalized, aggregated results
- **Input**: Search request concept containing text query, optional provider filter, optional asset type filter, optional category filter, optional result limit, optional pagination cursor
- **Output**: Search result concept containing normalized asset metadata list, provider status summary, pagination metadata, and warnings
- **Business Rules**:
  - Callers see one search operation regardless of how many providers are enabled
  - Provider-specific request shaping, authentication, and response parsing live inside provider adapters, never in calling features
  - Each enabled provider is queried independently with its own timeout
  - Provider failure must not block other providers; failures are logged and skipped
  - Partial results must be returned when at least one provider succeeds
  - All provider results must be normalized into the common asset metadata shape before aggregation
  - Search should support provider filter, asset type filter, and category filter
  - Marketplace-style providers should filter to downloadable assets by default
  - Provider authentication uses stored credentials; credentials must never appear in results, logs, or events
  - Rate limit responses must be surfaced as provider warnings or provider errors depending on severity
  - Pagination remains provider-specific; aggregated results preserve provider pagination metadata when available
  - Duplicate assets from different providers may be deduplicated when identity equivalence can be safely determined
  - Empty query may return curated or default results when provider supports it, otherwise return empty result
  - Provider enablement comes from configuration; disabled providers are excluded with warning
- **Edge Cases**: All providers fail, empty query, no providers registered, provider disabled, provider timeout, rate limit exceeded, malformed provider response, missing authentication for provider, no results, partial pagination cursor, oversized result set, duplicate assets across providers
- **Error Handling**: Provider error recorded per failed provider with aggregated summary when all fail; validation error for malformed search parameters; authentication error when provider credentials missing or invalid; partial results returned whenever possible

### FR-AST-002: Download Asset to Cache

Asset downloads file to cache. Asset uses security for path validation. Asset uses job for large downloads.

- **Description**: Acquire an asset file from its provider into the local cache with integrity verification and background coordination for large transfers
- **Input**: Download request concept containing provider identifier, asset identifier, asset type, resolution preference, overwrite policy, and background execution policy
- **Output**: Download result concept containing success indicator, local artifact reference, downloaded size, cache status, integrity status, and message; or task reference when submitted as background download
- **Business Rules**:
  - Cache location must come from configuration; asset feature must never invent storage locations
  - Cache location and destination paths must be validated through security policy feature
  - Existing cached artifact follows configured overwrite policy:
    - reuse cached artifact
    - overwrite existing artifact
    - create unique variant
  - Valid cached artifact satisfying request must be reused without network access
  - Corrupted or integrity-failed cached artifact must trigger re-download or surface cache error according to policy
  - Downloaded artifact should be verified for existence, non-empty size, and checksum when provider supplies one
  - Download should write to temporary artifact first and finalize atomically so partial files are never served as valid cache entries
  - Maximum download size must be enforced from configuration
  - Resolution preference applies when provider offers multiple asset resolutions
  - Expected large downloads must be submitted through job feature and return task reference
  - Capacity exhaustion from job feature propagates as capacity error without partial cache side effects
  - Provider credentials must be handled safely and never logged or echoed in results
  - License and attribution metadata should be recorded alongside artifact when available
  - Download operation must not import asset; import is a separate operation
  - Concurrent downloads of the same asset should resolve to one transfer where detectable
- **Edge Cases**: Asset not found, provider download unavailable, download timeout, permission denied destination, cache full, corrupted cached artifact, integrity checksum mismatch, rate limit exceeded, authentication failure, oversized asset, network interruption, concurrent download of same asset, resolution unavailable falling back to nearest available
- **Error Handling**: Asset not found error when identifier cannot be resolved; provider error for remote failure; security violation error delegated from security policy feature; capacity error delegated from job feature; cache error for unreadable or unwritable cache state; timeout error for exceeded download duration

### FR-AST-003: Extract Asset Archive

Asset uses security for extraction. Asset must not implement path traversal protection itself.

- **Description**: Extract downloaded archive artifacts under security policy supervision, never implementing traversal protection locally
- **Input**: Extraction request concept containing local artifact reference, extraction destination within allowed directories, and extraction options
- **Output**: Extraction result concept containing success indicator, extracted file references, rejected entry summary, and message
- **Business Rules**:
  - All archive safety decisions are delegated to security policy feature:
    - entry path validation
    - traversal and escape rejection
    - depth, size, and entry count limits
    - symbolic link and hard link policy
  - Asset feature must not implement its own path traversal protection
  - Extraction destination must be validated through security policy feature before any entry is written
  - Extraction proceeds only after security approval of the extraction plan
  - Rejected entries must be reported in result without exposing unsafe target paths in raw form
  - Already-extracted and valid artifact may be reused without re-extraction when extraction cache policy allows
  - Partial extraction must be cleaned up on failure so corrupt or incomplete trees are not mistaken for valid cache content
  - Supported archive formats depend on runtime capability; unsupported formats produce clear validation error
  - Extracted file references must be returned for downstream import operations
  - Extraction of nested archives follows the same security supervision as top-level extraction
- **Edge Cases**: Archive entry outside destination, nested archive, archive bomb pattern, excessive entry count, excessive extracted size, symbolic link entry, hard link entry, invalid entry encoding, duplicate entry names, unsupported archive format, permission denied destination, partial extraction after failure, disk full
- **Error Handling**: Archive safety error delegated from security policy feature for depth, size, count, or link violations; security violation error delegated for path escape attempts; cache error for unwritable extraction destination; validation error for unsupported or malformed archive

### FR-AST-004: Import Asset into Blender

Asset imports file into Blender. Asset returns object reference. After import, object manipulation is responsibility of object feature.

- **Description**: Import a locally available asset file into Blender and return the resulting object references, stopping at the handoff boundary
- **Input**: Import request concept containing local file reference, asset type, optional target collection, scale normalization policy, duplicate handling policy, and format hint
- **Output**: Import result concept containing success indicator, imported object references, imported asset metadata summary including license attribution, and message
- **Business Rules**:
  - File must exist locally before import; missing local file must direct caller toward download operation rather than failing obscurely
  - Import command is transported through gateway feature; asset feature never talks to Blender directly
  - Supported import formats depend on runtime capability and asset type
  - Scale normalization policy may normalize imported model to expected scene units
  - Duplicate handling policy may be one of:
    - rename imported object
    - reuse existing imported asset
    - replace existing asset
    - reject duplicate import
  - Imported object should be added to active scene and target collection when specified
  - Result must return canonical object references after successful import
  - Asset feature responsibility ends at object reference handoff; all subsequent manipulation belongs to object feature
  - Expected long-running imports may be submitted through job feature when supported
  - License and attribution metadata must be preserved in import result when available
  - Import failure must be distinguished clearly from download or extraction failure
  - Missing texture or dependency files should be reported as warnings when import still succeeds
- **Edge Cases**: Unsupported format, corrupted file, missing local file, import failure inside Blender, target collection missing, duplicate asset, oversized scene content, missing texture dependencies, format version mismatch, linked asset data conflict, import timeout
- **Error Handling**: Asset import error for Blender-side import failure; asset not found error for missing local file with download guidance; validation error for unsupported format or invalid import parameters; scene state error for missing target collection; timeout error delegated from gateway for exceeded import duration

### FR-AST-005: Manage Provider Metadata

Asset normalizes metadata: name, provider, type, categories, preview, license, download availability.

- **Description**: Normalize provider-specific asset descriptions into one consistent metadata shape consumed across the system
- **Input**: Raw provider asset description concept
- **Output**: Normalized asset metadata concept
- **Business Rules**:
  - Normalized metadata must include at least:
    - asset name
    - provider identifier
    - asset identifier
    - asset type
    - categories when available
    - preview or thumbnail reference when available
    - license summary when available
    - download availability flag
  - Missing optional fields must fall back to safe empty values, never absent structure
  - License information is informational and does not constitute legal clearance
  - Attribution requirements from provider must be preserved when present
  - Preview references must not embed credentials or signed locations in results
  - Pagination cursors must remain opaque to callers
  - Provider capability metadata should describe supported asset types, pagination behavior, and authentication requirements
  - Cached metadata may be reused within configured freshness window to reduce provider load
  - Stale metadata affecting download availability should be refreshed before download when policy requires
  - Provider-specific extra fields may be preserved in extension container without breaking the common shape
  - Metadata handling must never expose provider secrets or user credentials
- **Edge Cases**: Missing required fields, unknown license, preview unavailable, provider-specific extra fields, conflicting metadata between providers for equivalent asset, stale cached metadata, metadata cache expired, provider changed schema
- **Error Handling**: Provider error when raw metadata cannot be retrieved; validation error when raw metadata cannot be normalized safely; stale metadata refreshed or flagged rather than silently served

## Boundary: Asset vs Object

- Asset feature owns acquisition and import:

  - provider search
  - download and caching
  - extraction
  - import producing object references
- Object feature owns manipulation of existing objects:

  - transform, material, modifier, deletion
  - single object operations after import is complete

Conceptual separation:

- Asset acquisition and import is requested through the asset feature import operation, which produces object references
- Subsequent positioning, material assignment, or modifier work is requested through the object feature operations using those object references

The asset feature hands objects into the scene. The object feature takes over from there.

## Boundary: Asset vs Render

- Asset feature owns HDRI file acquisition:

  - search, download, cache, and local file availability
- Render feature owns HDRI lighting configuration:

  - world environment setup, strength, rotation, background visibility

Conceptual separation:

- HDRI file acquisition is requested through the asset feature download operation, which produces a local file reference
- HDRI lighting configuration is then requested through the render feature lighting operation using that local file reference and lighting settings

The asset feature never touches scene lighting. The render feature never downloads files.

## Error Categories

- asset not found error — asset not found in any provider, or local file missing when import expected
- asset import error — import into Blender failed after successful acquisition
- provider error — provider API failure, timeout, or malformed response
- security violation error — path validation or archive safety failed, delegated through security policy feature
- capacity error — download capacity exceeded, delegated through job feature
- cache error — cache unreadable, unwritable, corrupted, or full
- archive safety error — extraction limits violated, delegated from security policy feature
- authentication error — provider credentials missing or invalid
- timeout error — download or import exceeded configured duration
- validation error — malformed search, download, extraction, or import parameters

## Events

- asset searched event — search completed with result count and provider status summary
- asset downloaded event — file downloaded to cache with size, resolution, and integrity status
- asset cache hit event — valid cached artifact served without network access
- archive extracted event — extraction completed with extracted and rejected entry counts
- asset imported event — asset imported into Blender with object reference count
- provider degraded event — provider failed or rate-limited while others continued

Event payloads should include:

- event category
- provider identifier and asset identifier
- asset type
- size and duration metadata
- cache status where applicable
- tracking identifier when available
- error category when failed

Event payloads must avoid:

- provider credentials and signed locations
- full filesystem paths beyond redacted form
- raw provider response payloads
- license legal text beyond summary indicator

## Configuration Keys


| Configuration Concept         | Description                                                               | Typical Default                             |
| ------------------------------- | --------------------------------------------------------------------------- | --------------------------------------------- |
| Local cache directory         | Validated directory where downloaded and extracted artifacts reside       | Application-managed cache directory         |
| Overwrite policy              | Handling of existing cached artifact: reuse, overwrite, or unique variant | Reuse cached artifact                       |
| Enabled provider list         | Providers active for search and download                                  | All supported providers enabled             |
| Maximum download size         | Upper bound for single asset download                                     | Conservative size limit                     |
| Resolution preference         | Preferred asset resolution when provider offers multiple                  | Highest available within size limit         |
| Cache eviction policy         | How excess or stale cache entries are removed                             | Oldest terminal entries first with size cap |
| Default result limit          | Default number of search results per provider                             | Conservative result count                   |
| Provider timeout              | Maximum wait per provider request                                         | Conservative request limit                  |
| Integrity verification        | Whether checksum or size verification applies after download              | Enabled when provider supplies checksum     |
| Extraction destination policy | Where extracted content may reside relative to cache                      | Inside validated cache subtree              |

## QA Checklist

- [ ]  Search returns normalized results from all enabled providers in common shape
- [ ]  Single search operation used regardless of provider count
- [ ]  Provider-specific behavior contained inside provider adapters
- [ ]  Single provider failure returns partial results from remaining providers
- [ ]  All providers failure returns empty result with aggregated provider error summary
- [ ]  Provider credentials never appear in results, logs, or events
- [ ]  Marketplace-style providers filter to downloadable assets by default
- [ ]  Rate limit surfaced as provider warning or provider error
- [ ]  Download uses security for path validation before write
- [ ]  Download writes temporary artifact and finalizes atomically
- [ ]  Valid cached artifact reused without network access
- [ ]  Corrupted cached artifact triggers re-download or cache error
- [ ]  Integrity checksum verified when provider supplies one
- [ ]  Maximum download size enforced
- [ ]  Large downloads tracked via job feature with task reference returned
- [ ]  Capacity exhaustion surfaces as capacity error without partial cache entry
- [ ]  Archive extraction uses security policy feature, not own traversal implementation
- [ ]  Extraction destination validated before any entry written
- [ ]  Rejected archive entries reported without exposing unsafe paths
- [ ]  Partial extraction cleaned up on failure
- [ ]  Nested archives follow same security supervision
- [ ]  Import returns object references after successful import
- [ ]  Import distinguishes import failure from download and extraction failure
- [ ]  Missing local file at import directs caller toward download operation
- [ ]  Duplicate import handled according to configured policy
- [ ]  Scale normalization applied when policy enabled
- [ ]  License and attribution metadata preserved through download and import
- [ ]  Post-import manipulation delegated to object feature, not duplicated
- [ ]  HDRI download separate from render lighting setup
- [ ]  Search, download, cache hit, extraction, import, and provider degradation events emitted
