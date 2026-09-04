# Engineering Rules Index

This directory contains the repository's canonical engineering rule files. Rules are guidance for implementation and review; the repository source, tests, and CI configuration remain authoritative when a rule conflicts with executable behavior.

## Rule precedence

Apply rules in the following order:

1. Repository source contracts and tests.
2. CI and tool configuration in `pyproject.toml` and `.github/workflows/`.
3. The AES architecture rules in [`RULES_AES.md`](RULES_AES.md).
4. Language- and tool-specific rules listed below.

## Canonical rule files

| Area | Rule file | Scope |
| --- | --- | --- |
| Architecture | [`RULES_AES.md`](RULES_AES.md) | Agents–Executors–Services boundaries and dependency direction |
| Python linting | [`RULES_RUFF.md`](RULES_RUFF.md) | Ruff diagnostics and formatting expectations |
| Python typing | [`RULES_MYPY.md`](RULES_MYPY.md) | Static typing guidance |
| Python complexity | [`RULES_RADON.md`](RULES_RADON.md) | Complexity and maintainability checks |
| JavaScript/TypeScript | [`RULES_ESLINT.md`](RULES_ESLINT.md), [`RULES_TSC.md`](RULES_TSC.md) | Frontend linting and type checking when applicable |
| Rust | [`RULES_CLIPPY.md`](RULES_CLIPPY.md), [`RULES_RUSTFMT.md`](RULES_RUSTFMT.md), [`RULES_CARGO_AUDIT.md`](RULES_CARGO_AUDIT.md) | Rust lint, formatting, and dependency audit guidance when applicable |

A new rule file must be linked from this index and must state its scope, enforcement mechanism, and relationship to the executable repository contracts.
