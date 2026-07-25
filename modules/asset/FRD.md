
# FRD — Asset Feature Module

## System Overview

The asset module handles multi-provider asset discovery, download, caching, and import for **blender-arwaky**. It provides a multi-provider asset search contract, a provider adapter contract for provider-specific implementations, and capability adapters for external asset libraries and downloadable model marketplaces.

This module is responsible for querying multiple asset sources, aggregating search results, normalizing asset metadata, downloading assets safely, and importing downloaded assets into Blender through the appropriate server-side execution path. It isolates provider-specific behavior behind a common provider abstraction so that new providers can be added without modifying core application logic.

The module covers:

- searching assets across multiple providers
- aggregating and normalizing provider search results
- downloading provider assets
- importing downloaded assets into Blender
- caching downloaded assets locally
- exposing license and availability metadata
- handling provider failures, rate limits, and pagination
- supporting asynchronous download and import for large assets

The module does not handle:

- direct Blender object manipulation beyond import handoff
- viewport capture or rendering
- network transport implementation, which is delegated to server or provider gateway mechanisms
- final licensing compliance decisions for end users
- paid asset purchase or marketplace checkout flows

## Functional Requirements

### FR-AST-001: Search Assets Across Providers

- **Description**: Query multiple asset providers and aggregate results
- **Input**: Text query, optional provider filter, optional asset type filter, optional category filter, optional result limit, optional pagination cursor
- **Output**: Aggregated asset metadata list, provider status summary, pagination metadata, warnings
- **Business Rules**:
  - Each enabled provider is queried independently
  - Provider failures must not block other providers
  - Provider results are normalized into a common asset metadata concept
  - Asset metadata should include at least:
    - asset identifier
    - provider identifier
    - asset name
    - asset type
    - categories
    - preview or thumbnail reference when available
    - license summary when available
    - download availability flag
    - source provider reference
  - Search should support provider filter to limit query to selected providers
  - Empty query may return curated, trending, or default results when provider supports it
  - If query is invalid or empty and no fallback exists, return request validation error or empty result based on configuration
  - Provider timeouts must be enforced independently
  - Failed providers are logged and skipped, with provider error category included in provider status summary
  - Partial results must be returned when at least one provider succeeds
  - If all providers fail, return empty result with aggregated provider error summary
  - Pagination may be provider-specific; aggregated search should preserve provider pagination metadata when available
  - Duplicate assets from different providers may be deduplicated when identity equivalence can be safely determined
  - Search results should preserve relevance ordering per provider unless global ranking policy is configured
  - Rate limit responses from providers should be surfaced as provider warnings or provider errors depending on severity
- **Edge Cases**: All providers fail, empty query, provider not registered, provider disabled, provider timeout, rate limit exceeded, malformed provider response, no results, partial pagination cursor, oversized result set, duplicate assets, missing license metadata
- **Error Handling**: Provider error logged per provider; partial results returned; aggregated error summary included when all providers fail; request validation error for invalid query parameters

### FR-AST-002: Fetch and Import Asset

- **Description**: Download an asset from a specific provider and import into Blender
- **Input**: Provider identifier, asset identifier, asset type, optional destination policy, optional import options, optional target collection, optional scale normalization policy, optional duplicate handling policy
- **Output**: Imported asset result containing success indicator, asset metadata, local artifact reference, Blender object reference, imported object references, and message
- **Business Rules**:
  - Provider must be registered and enabled
  - Asset identifier must be valid and resolvable by provider
  - Asset must be downloadable according to provider metadata
  - Downloaded asset must be stored in allowed cache or download location
  - Downloaded artifact should be validated for existence, size limit, and basic integrity when supported
  - Archive extraction must prevent path traversal and unsafe file writes
  - Import operation must be delegated to Blender through server module or appropriate import capability
  - Imported object should be added to active scene and target collection when specified
  - Scale normalization policy may normalize imported model to unit scale
  - Duplicate handling policy may be one of:
    - rename imported object
    - reuse existing imported asset
    - replace existing asset
    - reject duplicate import
  - Asset license metadata should be preserved in result when available
  - Temporary download artifacts should be cleaned up according to cache policy
  - Large download or import operations may be submitted as asynchronous jobs when supported
  - Operation should return final Blender object reference or imported object references after successful import
  - Operation should distinguish download failure from import failure in error category
- **Edge Cases**: Provider not found, provider disabled, asset not downloadable, asset not found, download timeout, invalid artifact, unsupported import format, archive extraction failure, import fails, target collection missing, cache full, duplicate asset, license missing, rate limit exceeded, oversized asset
- **Error Handling**: Provider error for missing provider or download failure; asset not found error when asset identifier cannot be resolved; request validation error for invalid parameters; import error for Blender import failure; delegated server error for communication failure

### FR-AST-003: Search External Asset Library Assets

- **Description**: Search an external asset library for HDRIs, textures, or models
- **Input**: Asset search concept containing query, asset type, categories, result limit, and pagination cursor
- **Output**: Asset search result concept containing assets, total estimate, pagination cursor, provider identifier, and warnings
- **Business Rules**:
  - Asset type must be specified when provider requires it
  - Supported asset types include at least:
    - HDRIs
    - textures
    - models
  - Search request is dispatched through Blender bridge command channel or provider gateway depending on deployment configuration
  - Provider response must be parsed and normalized into common asset metadata concept
  - Search should support category filtering when provider supports categories
  - Search should support pagination when provider supports cursor or offset pagination
  - Default result limit should be configurable
  - Provider availability can be toggled through configuration
  - If provider is disabled, return provider disabled warning or empty result depending on configuration
  - License and preview metadata should be included when available
  - Search operation should be read-only and should not download asset files
- **Edge Cases**: Blender bridge not connected, invalid response format, provider disabled, asset type unsupported, category mismatch, rate limit exceeded, timeout, empty query, missing preview metadata, pagination cursor invalid
- **Error Handling**: Provider error wrapping bridge connection errors or provider response errors; request validation error for invalid asset type or parameters; timeout error when provider exceeds configured limit

### FR-AST-004: Download External Asset Library Asset

- **Description**: Download an asset from an external asset library by asset identifier and asset type
- **Input**: Asset download concept containing asset identifier, asset type, destination policy, resolution preference, and overwrite policy
- **Output**: Asset download result concept containing success indicator, local artifact reference, downloaded size, cache status, and message
- **Business Rules**:
  - Asset type must be specified
  - Supported asset types include at least:
    - models
    - textures
    - HDRIs
  - Download destination must be inside allowed cache or download directory
  - Existing local artifact must be handled according to overwrite policy:
    - reuse cached artifact
    - overwrite existing artifact
    - create unique variant
  - Download operation should support resolution or quality preference when provider supports multiple asset resolutions
  - Downloaded artifact should be validated for existence and non-empty size
  - If checksum or integrity metadata is available, validation should be performed
  - Download operation may return cached artifact without network access when cache policy allows
  - Download progress should be reported when asynchronous mode is enabled
  - Download operation should not import asset unless explicitly requested by higher-level fetch and import operation
- **Edge Cases**: Asset not found, download timeout, invalid local destination, permission denied, unsupported asset type, unsupported resolution, cache full, corrupted cached artifact, provider rate limit, network failure, oversized asset
- **Error Handling**: Provider error with descriptive message; asset not found error when identifier invalid; request validation error for invalid asset type or destination policy; timeout error for download timeout; cache error when local artifact cannot be read or written

### FR-AST-005: Search Downloadable Model Marketplace Models

- **Description**: Search a downloadable model marketplace for 3D models
- **Input**: Asset search concept containing query, result limit, category filter, downloadable-only flag, and pagination cursor
- **Output**: Asset search result concept containing assets, total estimate, pagination cursor, provider identifier, and warnings
- **Business Rules**:
  - Default result limit is configurable, with default conceptual value of 20
  - Downloadable-only filter should be enabled by default
  - Search should exclude non-downloadable models unless explicitly overridden
  - Search request may require provider authentication token when configured
  - Provider response must be normalized into common asset metadata concept
  - Asset metadata should include model identifier, name, provider, preview reference, license or usage summary when available, and downloadable status
  - Search should support pagination when provider supports it
  - Rate limit status should be surfaced as warning or error depending on provider response
  - Search operation should be read-only and should not download model files
- **Edge Cases**: Provider disabled, rate limit exceeded, authentication missing, invalid authentication token, malformed response, empty query, no downloadable results, unsupported category, pagination cursor invalid, network timeout
- **Error Handling**: Provider error with marketplace-specific message category; authentication error when credentials invalid or missing; request validation error for invalid search parameters; timeout error when search exceeds configured limit

### FR-AST-006: Download Marketplace Model

- **Description**: Download and prepare a marketplace model by unique model identifier
- **Input**: Asset download concept containing model identifier, destination policy, import policy, scale normalization policy, and overwrite policy
- **Output**: Asset download result concept containing success indicator, local artifact reference, prepared import reference, cache status, and message
- **Business Rules**:
  - Model identifier must be valid and resolvable
  - Model must be downloadable according to marketplace metadata
  - Download destination must be inside allowed cache or download directory
  - Downloaded model may be compressed archive and must be extracted safely
  - Archive extraction must prevent path traversal and unsafe file writes
  - Imported model may be normalized to unit scale when scale normalization policy enabled
  - Existing local artifact must be handled according to overwrite policy
  - Download operation may return cached artifact when cache policy allows
  - If import policy is enabled, downloaded model should be imported into Blender through server module
  - If import policy is disabled, operation should only return local artifact reference
  - Operation should distinguish marketplace download failure from Blender import failure
  - Operation should preserve marketplace attribution and license metadata when available
- **Edge Cases**: Model not downloadable, model identifier invalid, download timeout, archive extraction failure, unsupported model format, import failure, permission denied, cache full, rate limit exceeded, authentication failure, oversized model, missing texture dependencies
- **Error Handling**: Provider error with marketplace error details; asset not found error for invalid model identifier; authentication error for missing or invalid credentials; import error for Blender import failure; request validation error for invalid download parameters

## API Contract


| Operation                  | Input                                                                                   | Output                         | Description                      |
| ---------------------------- | ----------------------------------------------------------------------------------------- | -------------------------------- | ---------------------------------- |
| Search across providers    | Text query, optional provider filter, optional asset type filter, optional result limit | Aggregated asset metadata list | Multi-provider search            |
| Fetch and import asset     | Provider identifier, asset identifier, import options                                   | Imported asset result          | Download and import asset        |
| Provider-specific search   | Provider identifier, asset search concept                                               | Asset search result concept    | Search assets from one provider  |
| Provider-specific download | Provider identifier, asset identifier, download options                                 | Asset download result concept  | Download asset from one provider |

Common contract behavior:

- All operations return structured result containing success indicator, human-readable message, and error category when failed
- All operations may accept request correlation identifier for tracing
- Search operations are read-only and should not trigger downloads unless explicitly requested
- Download operations should report cache status when artifact is served from local cache
- Fetch and import operation should combine download and import status into a single result envelope
- Provider-specific operations should expose provider identifier and provider status metadata
- Long-running download or import operations may return asynchronous job reference when supported
- Errors should distinguish between:
  - request validation error
  - provider error
  - asset not found error
  - authentication error
  - timeout error
  - cache error
  - import error
  - delegated server error

## Integration Points

- **Internal**:
  - shared module: taxonomy concepts for asset metadata, provider identifier, asset identifier, asset type, result envelope, error categories, and pagination metadata
  - configuration module: provider enablement, authentication tokens, cache location, download limits, timeout settings, default result limits, and allowed output directories
  - server module: Blender command dispatch, import execution, queueing, timeout handling, and asynchronous job coordination
  - object module: post-import placement or object reference resolution when required
  - dependency injection mechanism: provider adapter registration and lifecycle management
- **External**:
  - External asset library services
  - Downloadable model marketplace services
  - Blender scripting interface through server module
  - Filesystem or local artifact cache
  - Network provider endpoints through configured gateway or bridge mechanism

## Non-functional Requirements

- **Performance**:

  - Search per provider within 3 seconds under normal network conditions
  - Aggregated search should return partial results as providers complete rather than waiting for all providers when supported
  - Download performance depends on provider network speed, but download initiation and validation should complete within configured timeout
  - Cached asset retrieval should avoid redundant network calls
- **Reliability**:

  - Failed provider does not block other providers
  - Partial search results are returned whenever at least one provider succeeds
  - Download failure and import failure are reported as distinct error categories
  - Cached artifacts should be validated before reuse
  - Temporary artifacts should be cleaned up after failure when safe
- **Extensibility**:

  - New providers implement provider adapter contract without modifying core search orchestration
  - Provider adapters can be enabled or disabled through configuration
  - Additional asset types can be added through provider capability metadata
  - Pagination, filtering, and sorting capabilities may vary by provider and should be exposed through capability metadata
- **Security**:

  - Provider credentials and authentication tokens must be redacted from logs
  - Downloaded files must be written only to allowed directories
  - Archive extraction must prevent path traversal
  - Downloaded artifact size limits must be enforced
  - Unsupported or unsafe file types should be rejected before import
  - License metadata should be exposed but final usage compliance remains user responsibility
- **Observability**:

  - Log provider name, operation type, duration, result status, and error category
  - Log search result count and provider status summary without logging full response payload by default
  - Log download cache hits, cache misses, and download size metadata
  - Log import success or failure with object reference metadata when available
  - Avoid logging authentication tokens, full download URLs with secrets, or sensitive user data
- **Portability**:

  - Provider behavior should remain consistent across supported platforms
  - Filesystem path handling should support common desktop operating systems
  - Cache location should respect platform-standard configuration or application-configured storage location

## Test Scenarios / QA Checklist

- [ ]  Search across multiple providers returns aggregated results
- [ ]  Search across providers normalizes asset metadata into common concept
- [ ]  Single provider failure returns partial results from other providers
- [ ]  All providers failure returns empty result with aggregated error summary
- [ ]  Provider filter limits search to selected providers
- [ ]  Empty query returns fallback results or empty result based on configuration
- [ ]  Search timeout for one provider does not block other providers
- [ ]  Rate limit response is surfaced as provider warning or provider error
- [ ]  Pagination metadata is preserved when provider supports pagination
- [ ]  Fetch and import creates valid Blender object reference
- [ ]  Fetch and import distinguishes download failure from import failure
- [ ]  Fetch and import respects duplicate handling policy
- [ ]  Fetch and import normalizes scale when policy enabled
- [ ]  Fetch and import preserves license metadata when available
- [ ]  Downloaded artifact is stored inside allowed cache directory
- [ ]  Cached artifact is reused when cache policy allows
- [ ]  Corrupted cached artifact triggers re-download or clear cache error
- [ ]  Archive extraction prevents unsafe path traversal
- [ ]  External asset library search returns correct normalized metadata
- [ ]  External asset library search supports asset type filter
- [ ]  External asset library search supports category filter when available
- [ ]  External asset library download requires valid asset type
- [ ]  External asset library download handles missing asset gracefully
- [ ]  Marketplace search filters downloadable models by default
- [ ]  Marketplace search excludes non-downloadable models unless overridden
- [ ]  Marketplace search handles missing authentication token gracefully
- [ ]  Marketplace download rejects invalid model identifier
- [ ]  Marketplace download handles non-downloadable model gracefully
- [ ]  Marketplace model import succeeds for supported format
- [ ]  Marketplace model import failure returns import error category
- [ ]  Download failure raises provider error with descriptive message
- [ ]  Provider timeout returns timeout error category
- [ ]  Provider disabled state returns clear warning or error based on configuration
- [ ]  Asset operations delegate Blender execution through server module
- [ ]  Asset operations respect server-side serialization constraints for import

## Assumptions & Constraints

- Blender bridge or addon handles actual provider command execution when provider integration is configured through Blender-side execution
- Provider communication may be performed through server command channel or provider gateway depending on deployment configuration
- Providers are registered at startup through dependency injection mechanism
- Provider enablement and credentials are managed through configuration module
- Internet connection is required for remote asset search and download
- Some providers may enforce rate limits, authentication, or download restrictions
- Asset licensing information is informational and does not constitute legal clearance
- Imported asset support depends on Blender runtime import capabilities
- Large assets may require asynchronous download and import handling
- Cache storage location must be writable and allowed by application configuration

## Glossary

- **Asset provider adapter contract**: Contract for provider-specific search and download behavior
- **Multi-provider asset search contract**: Contract for orchestrating search across multiple providers
- **Asset metadata**: Normalized description of an asset including identifier, provider, name, type, categories, preview reference, license summary, and availability
- **Imported asset result**: Result concept containing Blender object reference and imported artifact information after import
- **Provider identifier**: Conceptual name or key identifying an asset provider
- **Asset identifier**: Provider-specific identifier for a single asset
- **Asset type**: Category of asset such as HDRI, texture, or model
- **Pagination cursor**: Provider-specific token used to retrieve additional search results
- **Cache status**: Indicator whether downloaded artifact was retrieved from local cache or remote provider
- **Downloadable asset**: Asset that can be retrieved and imported according to provider rules
- **Scale normalization policy**: Rule for adjusting imported model scale to expected scene units
- **Duplicate handling policy**: Rule for handling repeated import of same asset

## Reference

- Product Requirements Document for blender-arwaky
- Shared feature requirements documentation
- Server feature requirements documentation
- Configuration feature requirements documentation
