# Blender Arwaky — Pull Request

## Description

<!-- Briefly describe what this PR does. Link to any related issues. -->

Closes #(issue number)

## Type of Change

- [ ]  🐛 Bug fix
- [ ]  ✨ New feature
- [ ]  💥 Breaking change
- [ ]  📚 Documentation update
- [ ]  🔧 Refactor / code cleanup
- [ ]  ⚡ Performance improvement
- [ ]  ✅ Test addition / improvement
- [ ]  🏗️ Build / CI / dependency change

## Affected Modules

- [ ]  modules/asset
- [ ]  modules/cli
- [ ]  modules/config
- [ ]  modules/diagnostics
- [ ]  modules/dispatcher
- [ ]  modules/gateway
- [ ]  modules/job
- [ ]  modules/launcher
- [ ]  modules/mcp
- [ ]  modules/object
- [ ]  modules/render
- [ ]  modules/scene
- [ ]  modules/security
- [ ]  modules/shared
- [ ]  modules/telemetry
- [ ]  `blender_mcp_addon/`
- [ ]  Documentation only
- [ ]  CI / build only

## Changes Made

<!-- List the key changes in this PR -->

## Testing

- [ ]  I have added tests that prove my fix/feature works
- [ ]  New and existing unit tests pass locally
- [ ]  I have updated the test markers appropriately (`@pytest.mark.unit`, etc.)

```bash
# Commands run to verify
uv run pytest
uv run ruff check src/ blender_mcp_addon/
uv run mypy src/
```

## Documentation

- [ ]  I have updated `README.md` (if user-facing change)
- [ ]  I have updated `AGENT.md` (if agent command change)
- [ ]  I have updated `SKILL.md` (if MCP / CLI tool change)
- [ ]  I have updated `TEST.md` (if test pattern change)
- [ ]  I have added an entry to `CHANGELOG.md` under `[Unreleased]`

## Checklist

- [ ]  My code follows the project's AES 7-layer architecture ARCHITECTURE.md
- [ ]  My code follows the 3-word file naming convention (`{domain}_{concern}_{suffix}.py`)
- [ ]  I have added docstrings to all new public functions/classes
- [ ]  My changes do not introduce new linting errors
- [ ]  I have not committed any secrets, API keys, or hardcoded paths
