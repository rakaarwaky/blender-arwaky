# Wave 5 Plugin Framework Hardening Audit

## Scope

Wave 5 memperkuat generic plugin framework setelah MPFB2 menjadi provider pertama. Fokus tahap ini adalah contract consistency, lifecycle state normalization, provider registry safety, execution guards, capability declaration, dan idempotent legacy package operations. Wave ini tidak menambahkan provider kedua atau preset karakter.

## Lifecycle model

Provider capabilities are declarations, not runtime availability. A provider can declare a capability even when its external package is absent or inactive. Runtime health is normalized into one of four states:

| State | Meaning | Executable |
|---|---|---:|
| `unavailable` | Provider is not installed or not active | No |
| `installed` | Provider is installed but not enabled | No |
| `enabled` | Provider is installed, active, and compatible | Yes |
| `incompatible` | Provider is installed but does not support the requested Blender version | No |

The registry derives the state deterministically from `installed`, `active`, and `compatible` flags. Providers may still return their original boolean fields and status message; the registry owns normalization at the aggregate boundary.

## Registry invariants

The registry now enforces the following invariants before mutating its indexes:

1. A provider identifier cannot be registered twice.
2. A single provider cannot declare the same capability more than once.
3. A capability cannot be claimed by more than one provider.
4. Capability and provider listings are returned in deterministic sorted order.
5. Provider discovery is delegated through the operation contract with an explicit Blender version.
6. Provider identity can be resolved by operation instance without importing provider-specific code.

A failed registration leaves both provider and capability indexes unchanged.

## Execution policy

The orchestrator resolves a declared capability, resolves its provider identity, reads normalized health, and permits execution only when the provider is `enabled`. Unknown capabilities produce a stable `plugin capability is not registered` result. A known capability owned by an unavailable, installed-only, or incompatible provider produces a stable lifecycle-state error and does not invoke provider code.

This guard is generic and applies equally to MPFB2 and future providers. Provider-specific execution remains behind the operation protocol and may not bypass the aggregate, CLI, MCP, confirmation, or response-envelope boundaries.

## Package lifecycle hardening

Legacy filesystem package installation is idempotent when the existing destination is a directory containing `__init__.py` or `blender_manifest.toml`. An invalid existing destination remains an error. Legacy removal is idempotent when the target directory is already absent, while symlinks, files, relative paths, and traversal paths remain rejected.

Blender Extension System operations continue to use fixed argument vectors and explicit extension identifiers. This Wave does not introduce shell interpretation, arbitrary Python execution, dynamic operator names, or unbounded package paths.

## Provider conformance

The MPFB2 provider now declares `character.create` independently of whether MPFB2 is currently installed or active. Runtime discovery and health determine availability. Existing provider behavior remains optional when MPFB2 is absent, while the generic orchestrator prevents execution until the provider is enabled and compatible.

## Validation status

| Check | Result |
|---|---:|
| Wave 5 branch based on `origin/develop` | Passed |
| Lifecycle state normalization | Passed |
| Explicit provider discovery contract | Passed |
| Duplicate provider rejection | Passed |
| Duplicate capability rejection | Passed |
| Capability collision rejection | Passed |
| Disabled/incompatible execution guard | Passed |
| Legacy install/remove idempotency tests | Passed |
| MPFB2 static capability declaration | Passed |
| Focused Ruff and pytest validation | Passed |

The remaining Wave 5 work is full repository CI, Blender 5.2 regression smoke validation, final documentation review, commit, and pull request creation.
