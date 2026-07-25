# PRD — BlenderArwaky

> Version: 1.6.5 | Date: 2026-07-25

## Problem Statement

3D artists and developers waste hours manually controlling Blender through its UI when integrating with AI agents. There is no standard protocol for AI to control Blender scenes, manipulate objects, render images, or manage assets. This forces developers to build custom integrations for each AI platform, duplicating effort and creating fragile, unmaintainable solutions.

## Goals & Success Metrics

- Goal 1: Enable any MCP-compatible AI agent to control Blender within 5 minutes of setup
- Goal 2: Support 15+ Blender operations through a unified command catalog
- Goal 3: Provide 2+ asset providers (Poly Haven, Sketchfab) for AI-driven asset discovery and import
- Goal 4: Maintain clean AES 7-layer architecture for long-term maintainability

## User Personas

- **3D Artist (AI-Augmented)**: Uses AI agents (Claude, Cursor) to speed up scene composition, asset import, and rendering. Needs natural language control over Blender.
- **Developer (MCP Integration)**: Builds custom AI tools that need programmatic access to Blender. Needs a stable, well-documented API.
- **Content Creator**: Uses AI to generate 3D scenes from text descriptions. Needs automated asset search, placement, and rendering.

## Scope

- In scope:

  - MCP server with 4 universal tools (execute_command, list_commands, read_skill_context, health_check)
  - Command catalog with 15+ actions (scene, object, render, import/export, code execution)
  - Asset provider integration (Poly Haven, Sketchfab)
  - Blender addon with TCP socket communication
  - Standalone CLI for Blender  management
- Out of scope:

  - Real-time collaboration (multi-user editing)
  - Cloud rendering services
  - Non-Blender 3D software support
  - Custom AI model training

## Feature Requirements (Prioritized)

### P0 — Must Have

- [ ]  MCP server starts and accepts connections from Claude Desktop, Cursor, or any MCP client
- [ ]  `execute_command` tool dispatches 15+ actions via command catalog
- [ ]  `list_commands` tool returns available actions with descriptions and parameters
- [ ]  Blender addon connects via TCP socket and executes Python code
- [ ]  Scene operations: get_scene_info, cleanup_scene, setup_environment
- [ ]  Object operations: place_asset, create_primitive, set_transform, delete_object
- [ ]  Render operations: get_viewport_screenshot, render
- [ ]  Import/export: import_glb, export_model
- [ ]  Asset search from Poly Haven and Sketchfab providers

### P1 — Should Have

- [ ]  `read_skill_context` tool provides SKILL.md documentation to AI agents
- [ ]  `health_check` tool reports system connectivity and subsystem status
- [ ]  AI-optimized screenshot presets (view angles, shading modes, overlay control)
- [ ]  Material and modifier operations (set_material, apply_modifier)
- [ ]  Workflow orchestration for multi-step scene creation

### P2 — Nice to Have

- [ ]  HDRI environment setup via Poly Haven
- [ ]  Telemetry recording for usage analytics
- [ ]  Job tracking for long-running operations
- [ ]  MCP prompt templates for AI-guided workflows

## Non-functional Requirements (High-level)

- Performance: MCP tool responses within 5 seconds for standard operations
- Security: No execution of untrusted code without user confirmation
- Reliability: Graceful error handling with descriptive error messages
- Maintainability: AES 7-layer architecture with full dependency inversion

## Open Questions / Risks

- Blender version compatibility: How to handle API changes across Blender versions?
- Asset provider rate limiting: How to handle API quotas from Poly Haven/Sketchfab?
