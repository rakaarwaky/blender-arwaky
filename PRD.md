# PRD — blender-arwaky (High-Level Overview)

> Version: 3.0.0 | Date: 2026-07-26

## Problem Statement

3D artists and developers waste hours manually controlling Blender through its UI when integrating with AI agents. There is no standard way for AI to control 3D scenes, manipulate objects, render images, or manage assets. This forces developers to build custom, fragile integrations for each AI platform.

**blender-arwaky** solves this by providing a standardized, secure interface between AI agents and the 3D application. It allows AI clients to discover capabilities, execute operations, import assets, and inspect system health through a unified, stable experience that mirrors direct command-line usage.

## Goals & Success Metrics

- **Goal 1: Rapid Setup:** Enable any compatible AI agent to connect and receive a successful system health check within 5 minutes of installation
- **Goal 2: Comprehensive Capability:** Support 15+ documented 3D actions through a unified, AI-readable command catalog.
- **Goal 3: Unified Asset Access:** Provide seamless search and import from  rexternal asset providers (e.g., Poly Haven, Sketchfab).
- **Goal 4: Absolute Safety:** Guarantee 0% application crashes from AI commands, and 100% blocking of unauthorized system/file access attempts.
- **Goal 5: Reliable Observability:** Ensure every operation has a tracking ID, structured responses, and clear, actionable error categorization.

## User Personas

- **3D Artist (AI-Augmented):** Wants to speed up repetitive scene composition and rendering using natural language, without manual UI scripting.
- **Developer (AI Integration):** Needs a stable, well-documented, and predictable interface to build custom AI tools without maintaining fragile, client-specific bridges.
- **Content Creator:** Needs automated, repeatable workflows to generate simple 3D scenes from text prompts, including asset search, placement, and rendering.

## Scope

- **In Scope:**
  - Standalone command-line interface for application lifecycle management.
  - AI integration interface exposing 5 universal tools (`execute_command`, `list_commands`, `read_skill_context`, `health_check`, `get_config`) with strict 1:1 behavioral parity to the command-line interface.
  - Core 3D operations: scene inspection/cleanup, object manipulation, viewport capture, rendering, and material/modifier management.
  - External asset discovery, secure downloading, caching, and importing.
  - Background task tracking for long-running operations.
  - Optional, privacy-focused usage analytics.
- **Out of Scope:**
  - Real-time multi-user collaboration, cloud rendering, non-Blender software support, custom AI model training, payment integrations, or advanced animation rigging.

## Feature  Overview

### P0 — Must Have (Core Foundation)

- **CLI Lifecycle Management:** Standalone commands to locate, launch, monitor, and gracefully shut down the 3D application with integration components enabled.
- **AI Integration Interface (1:1 Parity):** Exposes `execute_command`, `list_commands`, `read_skill_context`, `health_check`, and `get_config`. Behaves identically to the CLI, ensuring AI requests face the exact same constraints, priorities, and outcomes as manual terminal usage.
- **Scene & Object Management:** Inspect scene state, safely clean up objects, create primitives, transform objects, apply materials/modifiers, and delete objects with strict safety and confirmation policies.
- **Rendering & Viewport:** Capture viewport screenshots with presets, render high-quality images to explicitly allowed directories, and configure cameras/HDRI lighting.
- **External Asset Integration:** Search, securely download, cache, and import 3D assets (models, HDRIs, textures) from multiple providers, with strict duplicate handling and scale normalization.
- **Basic Security Controls:** Treat all user-provided code as untrusted, block dangerous system commands, restrict file writes to allowed directories, and prevent arbitrary code execution.

### P1 — Should Have (Enhanced Reliability & Workflow)

- **Background Task Tracking:** Monitor, poll, and cancel long-running operations (like rendering or large imports) with clear progress reporting and automatic cleanup of old records.
- **Workflow Orchestration:** Support batch command execution with stop-on-error or continue-on-error modes, including rollback hints.
- **Usage Analytics (Telemetry):** Optional, privacy-focused collection of anonymous usage data (startup, action execution, errors) without impacting performance or collecting Personally Identifiable Information (PII).

### P2 — Nice to Have (Future Expansion)

- **Advanced Asset Features:** Local asset cache management (size limits, invalidation) and support for additional providers (e.g., AmbientCG, Quixel Megascans).
- **AI Guidance:** Pre-built prompt templates for common scene creation, asset import, and debugging workflows.

## Non-functional Requirements (High-level)

- **Performance:** Lightweight operations must respond within 5 seconds. Heavy operations must run in the background without freezing the user interface.
- **Security & Privacy:** Strict execution boundaries, localhost default for connections, mandatory sanitization of error messages, and zero collection of PII in analytics.
- **Reliability:** Graceful error handling, deterministic sequential processing of 3D commands to prevent application instability, and no silent failures.
- **Usability:** Minimal manual configuration, AI-readable command catalogs, and highly actionable error messages that suggest corrective steps.

## Open Questions / Risks

- **Application Version Compatibility:** *Risk:* API changes across versions may break commands. *Mitigation:* Support multiple versions seamlessly and report version status in health checks.
- **External Provider Rate Limiting:** *Risk:* API quotas may limit search/download reliability. *Mitigation:* Implement local caching, return explicit rate-limit errors, and gracefully degrade.
- **UI Responsiveness During Heavy Tasks:** *Risk:* Long renders or imports may freeze the interface. *Mitigation:* Enforce background task execution and expose busy states in health checks.
- **Safety of AI-Generated Code:** *Risk:* Unsafe operations attempted via custom scripts. *Mitigation:* Strict pre-execution validation, restricted file directories, and explicit trusted-mode requirements.
- **Provider Licensing:** *Risk:* AI agents importing assets without license awareness. *Mitigation:* Clearly expose license metadata and attribute usage responsibility to the end user.
