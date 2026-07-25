# FRD — Asset Feature Module

## System Overview

The asset module handles multi-provider asset discovery, download, and import. It provides the `AssetSearchProtocol` for searching across providers, `AssetProviderPort` for provider-specific implementations, and capability adapters for Poly Haven and Sketchfab.

## Functional Requirements

### FR-AST-001: Search Assets Across Providers

- **Description**: Query multiple asset providers and aggregate results
- **Input**: SearchQuery (text query), StringList (optional provider filter)
- **Output**: list[AssetMetadata] (aggregated results from all providers)
- **Business Rules**: Each provider is queried independently; failures are logged and skipped
- **Edge Cases**: All providers fail, empty query, provider not registered
- **Error Handling**: ProviderError logged per provider; partial results returned

### FR-AST-002: Fetch and Import Asset

- **Description**: Download an asset from a specific provider and import into Blender
- **Input**: ProviderName, AssetId
- **Output**: ImportedAsset (id, name, blender_id)
- **Business Rules**: Provider must be registered; download must return valid file path
- **Edge Cases**: Provider not found, download returns no file path, import fails
- **Error Handling**: ProviderError for missing provider or download failure

### FR-AST-003: Search Poly Haven Assets

- **Description**: Search Poly Haven for HDRIs, textures, or models
- **Input**: AssetSearchRequestVO (query, asset_type, categories)
- **Output**: AssetSearchResponseVO (assets, total, next_token, provider)
- **Business Rules**: Sends command to Blender addon via TCP; parses response
- **Edge Cases**: Blender not connected, invalid response format
- **Error Handling**: ProviderError wrapping Blender connection errors

### FR-AST-004: Download Poly Haven Asset

- **Description**: Download a Poly Haven asset by ID and type
- **Input**: AssetDownloadRequestVO (asset_id, destination_path)
- **Output**: AssetDownloadResponseVO (success, file_path, message)
- **Business Rules**: Asset type must be specified (models, textures, hdris)
- **Edge Cases**: Asset not found, download timeout, invalid file path
- **Error Handling**: ProviderError with descriptive message

### FR-AST-005: Search Sketchfab Models

- **Description**: Search Sketchfab for downloadable 3D models
- **Input**: AssetSearchRequestVO (query)
- **Output**: AssetSearchResponseVO (assets, total, provider)
- **Business Rules**: Default count=20, downloadable=True
- **Edge Cases**: Sketchfab disabled, rate limit exceeded
- **Error Handling**: ProviderError with Sketchfab-specific messages

### FR-AST-006: Download Sketchfab Model

- **Description**: Download and import a Sketchfab model by UID
- **Input**: AssetDownloadRequestVO (asset_id)
- **Output**: AssetDownloadResponseVO (success, file_path, message)
- **Business Rules**: Normalizes size to target_scale=1.0
- **Edge Cases**: Model not downloadable, UID invalid
- **Error Handling**: ProviderError with Sketchfab error details

## API Contract

| Operation | Input | Output | Description |
|-----------|-------|--------|-------------|
| `search_all` | SearchQuery, StringList? | list[AssetMetadata] | Multi-provider search |
| `fetch_and_import` | ProviderName, AssetId | ImportedAsset | Download and import |
| `search_assets` | AssetSearchRequestVO | AssetSearchResponseVO | Provider-specific search |
| `download_asset` | AssetDownloadRequestVO | AssetDownloadResponseVO | Provider-specific download |

## Integration Points

- **Internal**: shared (taxonomy VOs, contracts), config (configuration)
- **External**: Blender addon (TCP socket for Poly Haven/Sketchfab commands)

## Non-functional Requirements

- Performance: Search per provider within 3 seconds
- Reliability: Failed provider doesn't block other providers
- Extensibility: New providers implement `AssetProviderPort`

## Test Scenarios / QA Checklist

- [ ] Search across multiple providers returns aggregated results
- [ ] Single provider failure returns partial results from others
- [ ] Fetch and import creates valid Blender object
- [ ] Poly Haven search returns correct metadata format
- [ ] Sketchfab search filters downloadable models
- [ ] Download failure raises ProviderError with message

## Assumptions & Constraints

- Blender addon handles actual API calls to Poly Haven/Sketchfab
- TCP socket communication for Blender commands
- Providers are registered at startup via DI container

## Glossary

- **AssetProviderPort**: Contract for provider-specific search and download
- **AssetSearchProtocol**: Contract for multi-provider search orchestration
- **ImportedAsset**: Result VO with Blender object reference after import

## Reference

- PRD: [../PRD.md](../PRD.md)
- FRD shared: [../shared/FRD.md](../shared/FRD.md)
