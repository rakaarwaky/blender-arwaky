# Documentation Map

This directory separates the **official Blender Python API snapshot** from documentation authored for Blender Arwaky. The separation prevents upstream reference material from being mixed with project decisions, implementation plans, audits, and evidence.

## Directory taxonomy

| Path | Scope | Intended reader |
| --- | --- | --- |
| [`reference/blender-python/`](reference/blender-python/) | Offline Blender 5.2 Python API snapshot, including `bpy`, `bmesh`, `gpu`, `mathutils`, and the upstream guides and index pages | Developers who need exact Blender Python API details |
| [`project/architecture/`](project/architecture/) | AES rules and architectural constraints | Developers and maintainers |
| [`project/plans/`](project/plans/) | Active and historical delivery plans, action items, and TODO records | Maintainers and project leads |
| [`project/audits/`](project/audits/) | Compliance, business-analysis, and hardening audit records | Maintainers and reviewers |
| [`project/research/`](project/research/) | Competitor, provider, runtime, and external-source research | Maintainers and feature owners |
| [`project/testing/`](project/testing/) | End-to-end and integration test reports | Developers and CI reviewers |
| [`project/migrations/`](project/migrations/) | Migration guidance for AES and supported implementation languages | Developers contributing to the codebase |
| [`project/plugins/`](project/plugins/) | MPFB2 plugin framework plans and provider-specific audits | Plugin and integration developers |
| [`project/rigging/`](project/rigging/) | Native MPFB2–Rigify findings, deformation validation, and visual evidence references | Rigging and character-integration developers |
| [`project/reference/`](project/reference/) | Arwaky-authored technical indexes that point into the official Blender snapshot | Developers who need a project-oriented entry point |

## Source boundary

The contents of `reference/blender-python/` are treated as an upstream documentation snapshot. They are grouped in one folder but are not rewritten as part of normal Arwaky feature work. Project-specific interpretation, examples, validation, and implementation decisions belong under `project/`.

The project reference [`project/reference/bpy_master_reference.md`](project/reference/bpy_master_reference.md) is not an upstream Blender document. It is an Arwaky-authored navigation and usage guide that links to the official snapshot and therefore remains in the project category.

## Maintenance rules

New Blender API snapshots belong under `reference/blender-python/<version-or-source>/` when more than one upstream version is retained. New Arwaky documentation must be placed in the narrowest applicable `project/` category. Temporary PR bodies, generated reports, and one-off terminal output must not be committed under `docs/`.
