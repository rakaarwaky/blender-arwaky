
# PRD — blender-arwaky

> Version: 1.7.0 | Date: 2026-07-25

## Problem Statement

3D artists and developers waste hours manually controlling Blender through its UI when integrating with AI agents. There is no standard protocol for AI to control Blender scenes, manipulate objects, render images, or manage assets. This forces developers to build custom integrations for each AI platform, duplicating effort and creating fragile, unmaintainable solutions.

**blender-arwaky** solves this by providing a standardized MCP-compatible integration layer between AI agents and Blender. It allows AI clients such as Claude Desktop, Cursor, or other MCP-compatible tools to discover Blender capabilities, execute scene operations, import assets, trigger renders, and inspect system health through a unified, stable interface.

Without blender-arwaky:

- AI agents cannot reliably control Blender in a standardized way
- Developers must build and maintain custom Blender bridges per AI client
- 3D artists lose time translating AI intent into manual Blender operations
- Asset discovery and import workflows remain fragmented and manual
- Long-running Blender operations are hard to track and debug

With blender-arwaky:

- AI agents gain structured access to Blender operations
- Users can control Blender through natural language or programmatic MCP tools
- Asset providers can be integrated through a common provider interface
- Developers get a stable command catalog and clear integration contract
- Blender operations become inspectable, testable, and extensible

## Goals & Success Metrics

- **Goal 1: Enable any MCP-compatible AI agent to control Blender within 5 minutes of setup**

  - Success Metric:
    - A new user can install the addon, start the MCP server, connect a client, and receive a successful `health_check` response in under 5 minutes
    - At least 90% of first-time setup attempts succeed without manual debugging
    - Connection failure messages clearly indicate root cause: Blender not running, addon not enabled, port mismatch, auth failure, or protocol mismatch
- **Goal 2: Support 15+ Blender operations through a unified command catalog**

  - Success Metric:
    - At least 15 documented commands are available through `execute_command`
    - Each command has:
      - name
      - description
      - parameter schema
      - example usage
      - timeout behavior
      - error modes
    - All catalog commands pass automated integration tests against a running Blender instance
- **Goal 3: Provide 2+ asset providers for AI-driven asset discovery and import**

  - Success Metric:
    - Poly Haven and Sketchfab providers are available
    - AI agent can search assets by keyword and category
    - Supported asset results include:
      - asset ID
      - name
      - provider
      - thumbnail or preview URL when available
      - download/import metadata
      - license information when available
    - Asset import flow works end-to-end for at least one supported asset type per provider
- **Goal 4: Maintain clean AES 7-layer architecture for long-term maintainability**

  - Success Metric:
    - No direct dependency violations between layers
    - Core domain logic does not depend on transport details
    - Command handlers are independently testable
    - Provider integrations are pluggable via adapter interfaces
    - Unit and integration test coverage for core command execution flow is at least 80%
- **Goal 5: Provide reliable and debuggable operation lifecycle**

  - Success Metric:
    - Every MCP tool call returns structured success or error response
    - Every operation has a request ID for tracing
    - Long-running operations can be tracked or polled
    - Connection state is observable through `health_check`
    - Errors are actionable and categorized: connection error, timeout, validation error, provider error, execution error, security error

## User Personas

- **3D Artist (AI-Augmented)**

  - Description:
    - Uses AI agents such as Claude or Cursor to speed up scene composition, asset import, and rendering
    - Prefers natural language control over Blender instead of manual repetitive UI actions
  - Pain Points:
    - Repetitive scene setup tasks take too long
    - Searching and importing assets manually is slow
    - AI suggestions are hard to execute directly inside Blender
    - Rendering and viewport capture require manual configuration
  - Needs:
    - Simple natural-language-to-Blender workflow
    - Reliable object placement, scene cleanup, environment setup, and rendering
    - Clear feedback when an operation fails
  - Success Criteria:
    - Can ask AI to create primitives, place assets, setup lighting/environment, and render without manually scripting Blender
    - Can complete common scene composition tasks faster than manual UI workflow
- **Developer (MCP Integration)**

  - Description:
    - Builds custom AI tools or agents that need programmatic access to Blender
    - Needs a stable, well-documented API and predictable command behavior
  - Pain Points:
    - Custom Blender integrations are fragile and client-specific
    - Lack of standard schema for Blender operations
    - Hard to debug connection, execution, and provider failures
  - Needs:
    - Stable MCP tools
    - Command catalog with schemas and examples
    - Clear error taxonomy
    - Health and status endpoints
    - Extensible provider and command architecture
  - Success Criteria:
    - Can integrate a new MCP client with blender-arwaky in under one day
    - Can add a new Blender command or asset provider without modifying core transport logic
- **Content Creator**

  - Description:
    - Uses AI to generate 3D scenes from text descriptions
    - Needs automated asset search, placement, and rendering for rapid content production
  - Pain Points:
    - Manual asset discovery is time-consuming
    - Scene composition from text requires many repetitive steps
    - Rendering outputs require manual camera and viewport setup
  - Needs:
    - AI-driven asset search and import
    - Scene composition commands
    - Screenshot and render presets
    - Repeatable workflows
  - Success Criteria:
    - Can generate a simple scene from a text prompt using AI + blender-arwaky
    - Can search, import, place, and render assets with minimal manual intervention

## Scope

- In scope:

  - MCP server with 4 universal tools:
    - `execute_command`
    - `list_commands`
    - `read_skill_context`
    - `health_check`
  - Command catalog with 15+ actions covering:
    - scene inspection and cleanup
    - object creation, transformation, and deletion
    - viewport screenshot and rendering
    - import/export operations
    - material and modifier operations
    - asset search and import
    - code execution through controlled Blender bridge
  - Asset provider integration:
    - Poly Haven
    - Sketchfab
  - Blender addon with TCP socket communication
  - Standalone CLI for Blender management and diagnostics
  - Basic authentication and connection safety:
    - localhost default
    - optional token authentication
    - protocol version validation
  - Structured error handling and health reporting
  - Documentation for:
    - installation
    - MCP client configuration
    - command catalog
    - provider setup
    - troubleshooting
  - AI-friendly command metadata through `list_commands`
  - Skill documentation exposure through `read_skill_context`
- Out of scope:

  - Real-time collaboration or multi-user editing
  - Cloud rendering services
  - Non-Blender 3D software support
  - Custom AI model training
  - Full asset marketplace or payment integration
  - Automatic licensing compliance for commercial usage beyond exposing available license metadata
  - Advanced animation rigging or simulation tooling in initial release
  - Multi-Blender-instance orchestration in initial release

## Feature Requirements (Prioritized)

### P0 — Must Have

- [ ]  MCP server starts and accepts connections from Claude Desktop, Cursor, or any MCP client

  - Supports standard MCP client configuration
  - Provides clear startup logs
  - Reports fatal startup errors with actionable messages
  - Supports local-first usage by default
- [ ]  `execute_command` tool dispatches 15+ actions via command catalog

  - Accepts command name and structured arguments
  - Validates arguments against schema before execution
  - Returns structured success or error response
  - Includes request ID for tracing
  - Supports timeout configuration per command
  - Rejects unknown commands with descriptive error
  - Rejects invalid arguments with validation error
- [ ]  `list_commands` tool returns available actions with descriptions and parameters

  - Returns command name
  - Human-readable description
  - Parameter schema
  - Example payload
  - Expected timeout class
  - Whether command is read-only or mutating
  - Whether command is long-running
  - Supported provider or category metadata when relevant
- [ ]  `health_check` tool reports system connectivity and subsystem status

  - Reports MCP server status
  - Reports Blender addon connection status
  - Reports protocol version compatibility
  - Reports active transport type
  - Reports last heartbeat time
  - Reports asset provider availability
  - Reports queue depth or execution busy state when available
  - Returns actionable error hints when subsystem is unhealthy
- [ ]  Blender addon connects via TCP socket and executes Python code

  - Addon listens on configurable port
  - Default binding is localhost
  - Supports protocol version handshake
  - Supports optional authentication token
  - Supports heartbeat/ping mechanism
  - Executes commands received from MCP server
  - Returns structured JSON responses
  - Handles Blender exceptions safely
  - Does not crash Blender on command failure
- [ ]  Scene operations:

  - `get_scene_info`
  - `cleanup_scene`
  - `setup_environment`
  - `get_scene_info` returns objects, cameras, lights, active camera, render settings, and unit settings when available
  - `cleanup_scene` supports safe cleanup modes:
    - remove orphan data
    - remove hidden objects
    - remove non-essential objects
    - preserve selected objects
  - `setup_environment` supports basic lighting, camera, and world environment setup
- [ ]  Object operations:

  - `place_asset`
  - `create_primitive`
  - `set_transform`
  - `delete_object`
  - `create_primitive` supports cube, sphere, cylinder, plane, cone, torus, empty, camera, light
  - `set_transform` supports location, rotation, scale
  - `delete_object` supports delete by name, by selection, or by filter
  - `place_asset` supports placement at origin, at specified transform, or relative to target object
- [ ]  Render operations:

  - `get_viewport_screenshot`
  - `render`
  - `get_viewport_screenshot` supports resolution, view angle, shading mode, overlay visibility, and output path
  - `render` supports output path, resolution, file format, and render engine when available
  - Long-running render operations return job/task reference when async mode is enabled
- [ ]  Import/export:

  - `import_glb`
  - `export_model`
  - `import_glb` supports file path, target collection, transform options, and duplicate handling policy
  - `export_model` supports selected objects, export path, file format, and export options
  - Initial supported formats include GLB/GLTF for import and GLB/GLTF for export
- [ ]  Asset search from Poly Haven and Sketchfab providers

  - Supports keyword search
  - Supports category filter when provider supports it
  - Returns normalized asset metadata
  - Includes provider name and asset ID
  - Includes license information when available
  - Supports pagination or result limit
  - Handles provider API errors gracefully
  - Does not expose raw provider secrets in responses
- [ ]  Basic security controls for code execution

  - User-provided code is treated as untrusted or semi-trusted
  - Server performs static validation before sending code to Blender
  - Forbidden constructs include dangerous system calls, dynamic imports, and unsafe file access patterns
  - Blender addon enforces runtime restrictions where possible
  - File write operations are limited to configured allowed directories
  - Raw code payload is not logged by default

### P1 — Should Have

- [ ]  `read_skill_context` tool provides SKILL.md documentation to AI agents

  - Returns concise product capability summary
  - Returns recommended command usage patterns
  - Returns examples of common workflows
  - Returns known limitations and safety constraints
  - Supports versioned skill documentation
- [ ]  AI-optimized screenshot presets

  - Presets for common view angles:
    - front
    - top
    - side
    - perspective
    - camera view
    - selected object focus
  - Presets for shading modes:
    - solid
    - material preview
    - rendered
    - wireframe
  - Overlay control:
    - show/hide gizmos
    - show/hide grid
    - show/hide statistics
    - show/hide annotations
- [ ]  Material and modifier operations

  - `set_material`
  - `apply_modifier`
  - `set_material` supports base color, metallic, roughness, alpha, and material slot targeting
  - `apply_modifier` supports modifier name or modifier type
  - Operations return clear error when material or modifier does not exist
- [ ]  Workflow orchestration for multi-step scene creation

  - Supports batch command execution
  - Supports stop-on-error or continue-on-error mode
  - Returns per-step results
  - Supports rollback hints or undo recommendation where possible
  - Enables AI agent to compose scenes through multiple commands in one workflow
- [ ]  Job tracking for long-running operations

  - Supports async submission for render, export, and large import operations
  - Returns task ID
  - Supports polling task status
  - Task states include:
    - pending
    - running
    - success
    - error
    - timeout
    - cancelled
  - Task result retention is configurable
  - Unknown or expired task returns clear error
- [ ]  CLI diagnostics and management

  - CLI can check server status
  - CLI can check Blender addon connectivity
  - CLI can list available commands
  - CLI can run health check
  - CLI can validate configuration
  - CLI can print troubleshooting hints

### P2 — Nice to Have

- [ ]  HDRI environment setup via Poly Haven

  - Supports HDRI search
  - Supports HDRI download or cache usage
  - Supports world environment setup
  - Supports intensity and rotation configuration
- [ ]  Telemetry recording for usage analytics

  - Optional and privacy-conscious
  - Records command usage frequency
  - Records success/failure rates
  - Records latency metrics
  - Does not record raw user prompts or sensitive code payload by default
  - Can be disabled via configuration
- [ ]  MCP prompt templates for AI-guided workflows

  - Scene creation templates
  - Asset import templates
  - Render setup templates
  - Debugging templates
  - Best-practice command usage templates
- [ ]  Additional asset provider support

  - AmbientCG
  - Quixel Megascans
  - Local asset library
  - Custom provider adapter interface
- [ ]  Local asset cache management

  - Cache downloaded assets
  - Avoid duplicate downloads
  - Support cache invalidation
  - Support cache size limit

## Non-functional Requirements (High-level)

- **Performance:**

  - MCP tool responses within 5 seconds for standard lightweight operations
  - Command catalog listing and health check should respond within 1 second under normal conditions
  - Long-running operations such as render, export, or large import should use async job tracking
  - Queue wait time should be visible or estimable when operations are serialized
  - Server-side overhead should be minimal compared to Blender execution time
- **Security:**

  - No execution of untrusted code without user confirmation or explicit trusted mode
  - Default connection target is localhost
  - Remote connection requires explicit configuration and authentication
  - Authentication token support for TCP socket communication
  - Protocol version validation to prevent incompatible client/addon behavior
  - Static validation and runtime sandboxing for code execution
  - File write access restricted to configured allowed directories
  - Payload size limits for requests and responses
  - Secrets and API keys must not appear in logs or tool responses
  - Raw code payload is masked, hashed, or truncated in logs by default
- **Reliability:**

  - Graceful error handling with descriptive error messages
  - Auto-reconnect on connection loss with limited retry attempts
  - Heartbeat mechanism to detect stale connections
  - Pending operations fail deterministically when connection is lost
  - Long-running operations should not block health check indefinitely
  - Blender addon must not crash Blender on command failure
  - Provider failures return categorized errors instead of generic failures
- **Maintainability:**

  - AES 7-layer architecture with full dependency inversion
  - Command handlers isolated from transport layer
  - Asset providers implemented through common adapter interface
  - Command catalog is declarative and extensible
  - Error types are standardized and categorized
  - Automated tests for command handlers, provider adapters, and connection lifecycle
  - Documentation kept in sync with command catalog
- **Compatibility:**

  - Initial target: Blender 4.x
  - Blender 3.6 LTS support considered where feasible
  - Addon should report Blender version and API compatibility status
  - Protocol versioning used to manage breaking changes
  - MCP server and Blender addon must negotiate compatible protocol version
- **Observability:**

  - Structured logs for connection, command execution, provider calls, and errors
  - Each operation includes request ID
  - Logs include duration, queue time, command name, and error type
  - Metrics include:
    - command success rate
    - command latency
    - queue depth
    - reconnect count
    - provider error rate
    - security violation count
  - Debug mode available without exposing sensitive payload by default
- **Usability:**

  - Setup should require minimal manual configuration
  - Error messages should suggest corrective action
  - Command catalog should be AI-readable and developer-readable
  - Documentation should include quickstart, troubleshooting, and examples
  - Health check should be sufficient to diagnose most setup failures

## Open Questions / Risks

- **Blender version compatibility:**

  - Risk: Blender API changes across versions may break addon commands
  - Question: Which Blender versions should be officially supported in v1?
  - Mitigation:
    - Implement compatibility layer inside addon
    - Report Blender version in health check
    - Use protocol versioning
    - Maintain version-specific command adapters where necessary
- **Asset provider rate limiting:**

  - Risk: Poly Haven/Sketchfab API quotas may limit search/download reliability
  - Question: How should quota exhaustion be surfaced to AI agents?
  - Mitigation:
    - Cache search results where appropriate
    - Cache downloaded assets locally
    - Return explicit provider rate-limit errors
    - Support configurable API keys where required
    - Gracefully degrade when provider is unavailable
- **Blender main-thread execution constraint:**

  - Risk: `bpy` is not thread-safe and long-running operations can block Blender UI
  - Question: How should queueing, cancellation, and progress reporting be standardized?
  - Mitigation:
    - Serialize all `bpy` operations through a single queue
    - Use async task model for long-running operations
    - Expose queue depth and busy state in health check
    - Define cancellation as best-effort for running operations
- **Security of code execution:**

  - Risk: AI-generated Python code may perform unsafe operations
  - Question: What level of sandboxing is acceptable for local Blender usage?
  - Mitigation:
    - Treat code as untrusted by default
    - Use AST-based static validation
    - Enforce runtime restrictions in addon
    - Restrict file write directories
    - Require explicit trusted mode for advanced execution
    - Avoid logging raw code payload
- **Authentication and local network exposure:**

  - Risk: TCP socket may be accessible to other processes or network clients
  - Question: Should authentication be mandatory for all modes or only remote mode?
  - Mitigation:
    - Default to localhost binding
    - Require token authentication for non-local binding
    - Document security implications clearly
    - Add protocol version handshake
- **Large asset and render output handling:**

  - Risk: Large files, slow downloads, or long renders may exceed MCP tool expectations
  - Question: Which operations should be synchronous vs asynchronous by default?
  - Mitigation:
    - Use async job tracking for render/export/large import
    - Return task ID for long-running operations
    - Provide polling mechanism
    - Define result retention period
- **Provider licensing and usage rights:**

  - Risk: AI agents may import assets without clear license awareness
  - Question: How much licensing responsibility should blender-arwaky handle?
  - Mitigation:
    - Expose license metadata when available
    - Include provider attribution in asset results
    - Document that users are responsible for final usage compliance
    - Avoid implying automatic commercial clearance
- **MCP client compatibility:**

  - Risk: Different MCP clients may handle tool responses, errors, or timeouts differently
  - Question: Which MCP clients should be officially validated?
  - Mitigation:
    - Validate against Claude Desktop and Cursor first
    - Keep tool responses structured and simple
    - Avoid overly large payloads
    - Provide compatibility matrix in documentation
