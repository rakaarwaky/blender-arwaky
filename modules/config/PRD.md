# PRD — Config Feature Module

> Version: 1.0.0 | Date: 2026-07-25

## Problem Statement

The application needs a centralized, thread-safe configuration system that loads settings from YAML files and provides dot-notation access. Without a dedicated config module, configuration logic is scattered across entry points, making it difficult to test, override, or extend.

## Goals & Success Metrics

- Goal 1: Load application configuration from `config.yaml` with fallback resolution
- Goal 2: Provide dot-notation access (e.g., `server.port`) for nested config values
- Goal 3: Support environment variable overrides for deployment flexibility
- Goal 4: Thread-safe singleton access for concurrent operations

## User Personas

- **Developer**: Configures server ports, Blender paths, and API keys via YAML
- **DevOps**: Overrides config values via environment variables in CI/CD
- **AI Agent**: Reads config to discover available providers and capabilities

## Scope

- In scope:
  - YAML config file loading with project root detection
  - Dot-notation path access for nested values
  - Environment variable override (`BLENDERMCP_CONFIG_PATH`, `BLENDER_MCP_ROOT`)
  - Thread-safe singleton pattern
  - `ConfigPort` contract for dependency inversion
- Out of scope:
  - Config file editing or watching for changes
  - Multiple config file formats (JSON, TOML)
  - Config validation schemas

## Feature Requirements (Prioritized)

### P0 — Must Have

- [ ] Load `config.yaml` from project root
- [ ] Dot-notation access: `get_config("server.port")`
- [ ] Project root detection (env vars, file proximity, XDG, CWD fallback)
- [ ] Thread-safe singleton access
- [ ] `ConfigPort` contract for DI

### P1 — Should Have

- [ ] Default values for missing config keys
- [ ] Environment variable `BLENDERMCP_CONFIG_PATH` for explicit config path
- [ ] Environment variable `BLENDER_MCP_ROOT` for project root override

### P2 — Nice to Have

- [ ] Config caching with manual invalidation
- [ ] Config schema validation on load

## Non-functional Requirements

- Performance: Config access within 1ms (cached)
- Reliability: Returns empty dict if config file missing or malformed
- Thread Safety: `threading.Lock` protects singleton initialization

## Open Questions / Risks

- Config migration: How to handle config schema changes across versions?

## Reference

- PRD root: [../../PRD.md](../../PRD.md)
- FRD shared: [../shared/FRD.md](../shared/FRD.md)
