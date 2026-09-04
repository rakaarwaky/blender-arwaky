# FRD — Video Sequence Editor Feature

## System Overview
The VSE module provides bounded Video Sequence Editor strip inspection, validated local media strip creation, strip removal, and sequence rendering through canonical dispatcher actions.

## Functional Requirements

### FR-001: Strip Inspection and Creation
- **Description**: Inspect bounded strip metadata and create validated local media strips.
- **Input**: `strip_type` (COLOR, IMAGE, MOVIE, SOUND), `strip_name`, `filepath`, `channel`, `frame_start`, `frame_end`.
- **Output**: `UnifiedEnvelope` with bounded strip names/types or creation confirmation.
- **Business Rules**: Channel numbers and frame ranges bounded. `IMAGE`, `MOVIE`, `SOUND` require existing local file. `COLOR` does not. Output paths restricted to regular local files.
- **Edge Cases**: Channel overlap; missing local file; invalid frame range; unsupported strip type.
- **Error Handling**: `validation_error` for bad ranges/missing files; `security_violation` for unsafe paths.

### FR-002: Strip Removal and Sequence Rendering
- **Description**: Remove exact strip names and render bounded frame ranges to local output.
- **Input**: `strip_name`, `output_path`, `frame_start`, `frame_end`.
- **Output**: `UnifiedEnvelope` confirming removal or task reference for background render.
- **Business Rules**: Removal requires dispatcher confirmation. Sequence rendering uses shared `job` metadata path for background-capable dispatch. Never creates VSE-specific job registry.
- **Edge Cases**: Strip not found; output path unwritable; render frame range out of bounds.
- **Error Handling**: `not_found` for missing strips; `render_output_error` for bad paths; `capacity_error` if job queue full.

## API Contract
| Operation | Input | Output | Description |
|---|---|---|---|
| `inspect_sequence_editor` | `limit` | `SequenceStripInfo[]` | Read-only bounded strip metadata; raises `validation_error` on invalid limit |
| `create_sequence_strip` | `strip_type`, `strip_name`, `channel` | `sequence_strip_created` | Create media or color strip; IMAGE/MOVIE/SOUND require existing Security-validated local file; raises `validation_error` on bad ranges or missing file, `security_violation` on unsafe path |
| `remove_sequence_strip` | `strip_name`, `confirm` | `sequence_strip_removed` | Remove exact strip name; requires dispatcher confirmation; raises `not_found`, `confirmation_error` |
| `render_sequence` | `output_path`, `frame_start`, `frame_end` | `RenderArtifact | TaskRef` | Render bounded frame range via shared Job lifecycle (job-eligible); raises `render_output_error`, `capacity_error`, `security_violation` |
## Integration Points

- **3rd Party**: No 3rd party integrations.
- **Internal**: `gateway` (command transport), `dispatcher` (routing), `job` (background rendering), `security` (path validation).

## Non-functional Requirements (Detailed)

- **Performance**: Inspection bounded to prevent payload exhaustion.
- **Security**: Media file paths and output paths validated by `security`.
- **Scalability**: Long-running sequence renders offloaded to `job` feature.

## Test Scenarios / QA Checklist

- [ ] Verify `create_sequence_strip` rejects MOVIE strips without a valid local file path.
- [ ] Verify `remove_sequence_strip` requires confirmation flag.
- [ ] Verify `render_sequence` returns a task reference when submitted as background.
- [ ] Verify channel numbers and frame ranges enforce bounds.

## Assumptions & Constraints

- Sequence rendering uses the shared `job` lifecycle; no private VSE job registry.
- Complex video editing effects (transitions, color grading) are out of scope for the baseline.

## Glossary

- **Strip**: A discrete media or effect block on the VSE timeline.
- **Channel**: The vertical track on the VSE timeline where strips reside.
- **UnifiedEnvelope**: The standardized JSON response wrapper containing success indicator, data payload, error category, tracking ID, and warnings.

## Reference

- PRD: `./PRD.md`
- Depends On: `gateway`, `dispatcher`, `job`, `security`
