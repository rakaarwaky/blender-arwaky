# Blender Arwaky — Pull Request

## Description

<!-- Briefly describe what this PR does. Link to any related issues. -->

Closes #(issue number)

## Type of Change

- [ ] 🐛 Bug fix (non-breaking change that fixes an issue)
- [ ] ✨ New feature (non-breaking change that adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to change)
- [ ] 📚 Documentation update
- [ ] 🔧 Refactor / code cleanup (no functional change)
- [ ] ⚡ Performance improvement
- [ ] ✅ Test addition / improvement
- [ ] 🏗️ Build / CI / dependency change

## Affected Layers

- [ ] `taxonomy/` (data structures, VOs)
- [ ] `contract/` (ports, protocols)
- [ ] `infrastructure/` (adapters, API clients)
- [ ] `capabilities/` (use cases)
- [ ] `agent/` (orchestrators)
- [ ] `surfaces/` (MCP tools, CLI)
- [ ] `blender_mcp_addon/` (Blender addon)
- [ ] Documentation only
- [ ] CI / build only

## Changes Made

<!-- List the key changes in this PR -->

-
-
-

## Testing

- [ ] I have added tests that prove my fix/feature works
- [ ] New and existing unit tests pass locally
- [ ] I have updated the test markers appropriately (`@pytest.mark.unit`, etc.)

```bash
# Commands run to verify
uv run pytest
uv run ruff check src/ blender_mcp_addon/
uv run mypy src/
```

## Documentation

- [ ] I have updated `README.md` (if user-facing change)
- [ ] I have updated `AGENT.md` (if architecture change)
- [ ] I have updated `SKILL.md` (if MCP tool/action change)
- [ ] I have updated `TEST.md` (if test pattern change)
- [ ] I have added an entry to `CHANGELOG.md` under `[Unreleased]`

## Checklist

- [ ] My code follows the project's AES 6-layer architecture (see [AGENT.md](AGENT.md))
- [ ] My code follows the 3-word file naming convention (`{domain}_{concern}_{suffix}.py`)
- [ ] I have added type hints to all new functions
- [ ] I have added docstrings to all new public functions/classes
- [ ] I have run `pre-commit run --all-files` and all checks pass
- [ ] My changes do not introduce new linting or type errors
- [ ] I have not committed any secrets, API keys, or hardcoded paths

## Screenshots / Recordings

If applicable, add screenshots or recordings to help reviewers.

## Additional Notes

Any additional context for the reviewers.
