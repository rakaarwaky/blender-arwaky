# Contributing to Blender Arwaky

First off, thank you for considering contributing! 🎉

Blender Arwaky is a community-driven project, and every contribution —
whether it's a bug report, feature suggestion, documentation improvement,
or code change — is valuable.

## 📜 Code of Conduct

This project and everyone participating in it is governed by our
[Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected
to uphold this code.

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- Git
- Blender 3.0+ (only required for addon testing in real Blender)
- pre-commit (`pip install pre-commit`)

### Setup

```bash
# 1. Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/blender-arwaky.git
cd blender-arwaky

# 2. Install dependencies
uv sync --all-groups

# 3. Install pre-commit hooks
pre-commit install

# 4. Verify everything works
uv run pytest
```

## 🛠️ Development Workflow

### 1. Create a branch

```bash
git checkout -b feat/your-feature-name
# or
git checkout -b fix/issue-number-description
```

### 2. Make your changes

Follow the project's architecture and style:

- **AES layered architecture** — see [AGENT.md](AGENT.md)
- **3-word file naming**: `{domain}_{concern}_{suffix}.py`
- **Type hints everywhere** — mypy must pass
- **Docstrings** — public functions/classes
- **Tests required** — see [TEST.md](TEST.md)

### 3. Add tests

New code should be accompanied by tests:

| Layer | Test Directory | Marker |
|-------|---------------|--------|
| `taxonomy/` | `tests/unit/` | `@pytest.mark.unit` |
| `contract/` | `tests/unit/` or `tests/integration/` | unit/integration |
| `capabilities/` | `tests/unit/` or `tests/integration/` | unit/integration |
| `agent/` | `tests/integration/` | `@pytest.mark.integration` |
| `surfaces/` | `tests/functional/` | `@pytest.mark.functional` |
| `blender_mcp_addon/` | `tests/addon/` | `@pytest.mark.addon` |

### 4. Run the test suite

```bash
# Run all tests
uv run pytest

# Run by marker
uv run pytest -m unit
uv run pytest -m integration
uv run pytest -m functional
uv run pytest -m addon

# Run with coverage
uv run pytest --cov=src --cov=blender_mcp_addon

# Run a specific test
uv run pytest tests/unit/test_command_catalog.py -v
```

### 5. Run linters and type checks

```bash
# Ruff (lint + format)
uv run ruff check src/ blender_mcp_addon/
uv run ruff format --check src/ blender_mcp_addon/

# Mypy (type check)
uv run mypy src/

# Bandit (security scan)
uv run bandit -c bandit.yaml -r src/

# Or use pre-commit (runs all of the above)
pre-commit run --all-files
```

### 6. Update documentation

- Update `README.md` for user-facing changes
- Update `AGENT.md` for architecture changes
- Update `SKILL.md` for new MCP tools/actions
- Update `TEST.md` for new test patterns
- Add an entry to `CHANGELOG.md` under `[Unreleased]`

### 7. Commit and push

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git add .
git commit -m "feat: add new search command for Poly Haven"
# or
git commit -m "fix: resolve socket connection retry loop"
# or
git commit -m "docs: update README installation steps"
```

Pre-commit hooks will run automatically on commit.

### 8. Open a Pull Request

- Push your branch: `git push origin feat/your-feature-name`
- Open a PR against the `main` branch
- Fill out the PR template
- Wait for CI to pass
- Address review comments

## 📁 Project Structure

```
blender-arwaky/
├── modules/                # Feature modules (AES layered)
│   ├── shared/             # Taxonomy + contracts (cross-feature)
│   ├── {feature}/          # Per feature: taxonomy, contract, capabilities, agent, surface
│   │   ├── FRD.md
│   │   └── src/
│   │       ├── taxonomy_<domain>_<type>.py
│   │       ├── contract_<domain>_<concern>_protocol.py
│   │       ├── capabilities_<domain>_<concern>.py
│   │       ├── agent_<domain>_orchestrator.py
│   │       └── root_<domain>_container.py
│   ├── cli/src/            # CLI surface — direct command per action
│   └── mcp/src/            # MCP surface — 5 tools via execute_command
├── blender_mcp_addon/      # Blender addon (TCP server)
├── tests/                  # Test suite
│   ├── unit/               # @pytest.mark.unit
│   ├── integration/        # @pytest.mark.integration
│   ├── functional/         # @pytest.mark.functional
│   └── addon/              # @pytest.mark.addon (mock bpy)
├── scripts/                # Helper scripts (see scripts/README.md)
│   ├── build/              # CI/release: build_addon_package, bump_release_version
│   ├── blender/            # Runtime: run_server_headless, manage_blender_process, ...
│   └── install/            # User installers: install_cli_wrappers
├── config.yaml             # Server configuration
├── .github/workflows/      # CI/CD pipelines
└── docs/                   # Additional documentation
```

## 🎯 Contribution Areas

Looking for where to help? Here are some areas:

- 🐛 **Bug fixes** — check [open issues](https://github.com/rakaarwaky/blender-arwaky/issues)
- ✨ **New actions** — extend the command catalog (see [AGENT.md](AGENT.md#command-catalog))
- 🔌 **New asset providers** — add support for new 3D asset sources
- 📚 **Documentation** — improve READMEs, docstrings, examples
- 🧪 **Test coverage** — bring under-tested modules to 100%
- 🌍 **Translations** — translate SKILL.md and docs
- ⚡ **Performance** — optimize slow operations

## ❓ Questions?

- Open a [Discussion](https://github.com/rakaarwaky/blender-arwaky/discussions)
- Check the [docs](README.md)
- Read the [architecture guide](AGENT.md)

Thank you for contributing! 🙏
