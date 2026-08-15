# FRD — Video Sequence Editor Feature

## Purpose

Provide bounded VSE strip inspection, validated local media strip creation, strip removal, and sequence rendering through canonical dispatcher actions.

## Canonical actions

| Action | Type | Contract |
|---|---|---|
| `inspect_sequence_editor` | Read-only | Bounded strip names, types, channels, and frame ranges |
| `create_sequence_strip` | Mutation | Create `COLOR`, `IMAGE`, `MOVIE`, or `SOUND` strip with validated inputs |
| `remove_sequence_strip` | Destructive mutation | Remove one exact strip name and require dispatcher confirmation |
| `render_sequence` | Long-running mutation | Render bounded frame range to a validated local output path; eligible for shared job lifecycle |

## Invariants

Channel numbers and frame ranges are bounded. `IMAGE`, `MOVIE`, and `SOUND` strips require an existing local file; `COLOR` strips do not. Output paths are resolved and restricted to regular local files by the server's path policy. Sequence rendering uses the shared `job` metadata path for background-capable dispatch and never creates a VSE-specific job registry.

## Verification

Unit tests cover strip type and range validation. Blender smoke tests cover color strip creation, bounded inspection, exact removal, and structured invalid-input errors. Media rendering is verified as a real handler but remains job-eligible for long-running dispatch.
