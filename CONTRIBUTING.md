# Contributing to Blender Arwaky

Thank you for contributing. This document is for developers and maintainers. User installation and usage belong in [README.md](README.md); internal architecture, source layout, tests, quality gates, and pull-request rules belong here.

## Prerequisites

Use the following development environment:

- Python 3.10 or newer.
- Blender 4.2 or newer for live addon or Blender smoke tests.
- [`uv`](https://docs.astral.sh/uv/).
- Git.
- `pre-commit` when working with local hooks.

## Development setup

```bash
git clone https://github.com/rakaarwaky/blender-arwaky.git
cd blender-arwaky
uv sync --dev
pre-commit install
uv run pytest -q
```

Create a feature branch from `develop`:

```bash
git switch develop
git pull --ff-only origin develop
git switch -c feat/short-description
```

## Architecture rules

Blender Arwaky follows **Agents → Executors → Services (AES)**. Keep dependencies directed toward shared contracts and taxonomy. Do not introduce shortcuts from surface code directly into unrelated feature implementations, and do not add duplicate access paths for an existing action.

The canonical dispatcher catalog defines the public action contract. A new action must be represented once in the catalog, routed through the dispatcher, exposed through the generated CLI, and callable through `execute_command`. The public naming rules are:

| Surface | Naming rule | Example |
|---|---|---|
| CLI | `kebab-case` | `create-primitive` |
| MCP/API | `snake_case` | `create_primitive` |
| MCP registry | Five stable tools only | `execute_command` |

Do not add a universal `run` fallback, feature shortcut, legacy alias, or parallel handler for an action already present in the catalog. Preserve validation, redaction, response envelopes, tracking metadata, and destructive-action confirmation at the shared boundaries.

### Source conventions

Feature code lives under `modules/<feature>/`. Follow the repository's AES naming convention for Python files and keep the `modules/` source tree compliant with `lint-arwaky-cli scan .`. Test directories are an approved naming exception.

Keep public boundaries typed and explicit. Use focused modules for taxonomy, contracts, capabilities, agents, composition, and surfaces. Avoid adding business logic to taxonomy constants or surface registration code.

## Adding or changing an action

Before implementation, determine whether the capability belongs to an existing category. Update the canonical action schema, executor/service implementation, dispatcher routing, CLI generation, MCP action handling, and tests as one change. Update user-facing README content only when the capability changes what users can install or do; update this document or the relevant technical document for internal workflow changes.

For a new action, verify all of the following:

1. The action has one canonical `snake_case` name.
2. Its CLI command is generated as the corresponding `kebab-case` name.
3. Parameters have explicit types, requiredness, defaults, and validation.
4. Mutating or destructive behavior is classified and guarded.
5. The MCP `execute_command` path and CLI path use the same dispatcher contract.
6. Unit, integration, and contract tests cover the new behavior.
7. Help output, catalog discovery, and error envelopes remain consistent.

## Testing and quality gates

Run focused tests during development:

```bash
uv run pytest modules/<feature>/tests -q
uv run pytest -m unit -q
uv run pytest -m integration -q
```

Run the full local gate before opening a pull request:

```bash
uv run pytest -q
uv run ruff check modules blender_mcp_addon scripts
uv run ruff format --check modules blender_mcp_addon scripts
python -m compileall -q modules blender_mcp_addon
uv run bandit -r modules blender_mcp_addon -x '*/tests/*' -ll -ii
lint-arwaky-cli scan .
bash scripts/ci.sh
```

The blocking CI workflow verifies lint and syntax, Python 3.10–3.13 tests, Bandit, AES architecture scanning, integration contracts, Codacy, and distributable artifacts. Do not open or merge a pull request with a known failing gate. Clean generated files such as coverage reports, build directories, and caches before committing.

For live Blender validation, install the generated addon package, start Blender with the addon enabled, and verify the relevant MCP or CLI action against a disposable scene. Record environment-specific limitations in the owning test or technical document rather than in the user README.

## Documentation policy

Documentation is split by audience:

| Audience | Document | Content |
|---|---|---|
| Users | `README.md` | Installation, client setup, commands, capabilities, limitations, and high-level comparison |
| Developers | `CONTRIBUTING.md` | Setup, architecture, source conventions, tests, quality gates, and PR workflow |
| Maintainers | `ARCHITECTURE.md`, `PRD.md`, `TEST.md`, `CHANGELOG.md` | Detailed design, requirements, verification, and release history |

Do not place internal Python module names, source tree diagrams, test commands, or CI implementation details in the user README. When a user-visible action changes, update the catalog documentation and a concise README entry. When only internal behavior changes, update developer or maintainer documentation instead.

## Commit and pull request workflow

Use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git add .
git commit -m "feat: add a canonical Blender action"
git commit -m "fix: correct dispatcher validation"
git commit -m "docs: clarify user installation"
```

Push the feature branch and open a pull request against `develop`:

```bash
git push -u origin feat/short-description
```

A pull request should explain the user or developer impact, identify changed contracts, describe tests performed, and call out any Blender-version or runtime limitations. Reviewers should confirm that the change preserves AES boundaries, catalog uniqueness, CLI/MCP parity, naming compliance, and backward-compatibility policy. Legacy aliases should be removed through an explicit migration rather than silently retained.

## Repository map

| Area | Purpose |
|---|---|
| `modules/shared/` | Shared taxonomy, contracts, schemas, security, and dispatcher data |
| `modules/<feature>/` | Feature-specific taxonomy, contracts, capabilities, agents, composition, and tests |
| `modules/cli/` | CLI surface and CLI contract tests |
| `modules/mcp/` | Five-tool MCP surface and protocol tests |
| `modules/root_cli_main_entry.py` | CLI composition and generated action parser |
| `blender_mcp_addon/` | Blender runtime addon and addon tests |
| `scripts/` | Build, CI, installation, and runtime helpers |
| `.github/` | Continuous integration and repository automation |

## Questions and support

For design questions, open a [GitHub Discussion](https://github.com/rakaarwaky/blender-arwaky/discussions). For bugs, provide a minimal reproduction, Blender version, Python version, command or MCP action, expected behavior, actual behavior, and the relevant test or log output.
