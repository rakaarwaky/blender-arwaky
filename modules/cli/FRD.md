# FRD — CLI Surface

## Purpose

Terminal interface for blender-arwaky. Parses user input, routes to owning feature aggregate, renders result. Surface only — zero business logic.

## Scope

- Command parsing with surface-level arg validation
- Terminal output formatting (text/JSON)
- Error display with category + actionable message
- Masking of sensitive values in all output
- Mapping CLI commands → owning feature aggregates
- Deterministic exit codes per outcome class
- Progress hints for long-running foreground ops
- Non-interactive output adaptation

## Out of Scope

Business logic, process lifecycle, connection logic, command validation, settings loading, health computation, task lifecycle, path/code safety decisions, interactive wizards, shell completion.

## Depends On

dispatcher (action execution + catalog), launcher (process control), diagnostics (health + status), config (settings), job (task status), plugin (optional provider package lifecycle), security policy (redaction).

## Provides To

Users via terminal.

## Functional Requirements

### FR-CLI-001: Parse and Route Commands

Parse terminal input, validate arg shape at surface, route to owning feature aggregate.

- **Input**: Raw CLI tokens: command, positional args, flags, options
- **Output**: Aggregate call dispatched + exit code
- **Business Rules**:
  - 1 CLI command → exactly 1 owning feature aggregate
  - Surface validates shape only: command recognized, required args present, flags well-formed, arg count in bounds
  - Semantic validation belongs to owning feature — CLI never judges action validity, path safety, or state
  - Unknown command → validation error with closest known commands suggested
  - Every command supports `--help` with usage, args, flags, examples
  - Root command without args → overview + help pointer
  - Exit codes: success, surface validation failure, upstream categorized failure, unexpected failure
  - No retry, reorder, or reinterpretation of aggregate results
  - Non-interactive input accepted for scripts/pipelines
  - Long-running ops may show non-blocking progress hints
- **Edge Cases**: Unknown command, missing required arg, conflicting flags, malformed flag value, extra positional arg, help at any level, empty input, piped/non-interactive invocation, aggregate unavailable at route time
- **Error Handling**: Surface validation error before any aggregate call; upstream errors passed through unchanged; unexpected failure → generic error with diagnostic ref, never raw stack

### FR-CLI-002: Render Terminal Output

Render aggregate results for human reading (default) or machine consumption (JSON flag).

- **Input**: Aggregate result, format preference, terminal capability
- **Output**: Rendered output + exit code
- **Business Rules**:
  - Human-readable text default; JSON via `--json` flag or config
  - JSON output: machine-stable shape, no color codes, errors as structured objects
  - Text output adapts to terminal: color only when supported, decoration suppressed for non-interactive, wide tables condensed
  - List-shaped results → tables with stable column ordering
  - Large payloads truncated in text mode with continuation hint; JSON emits complete data
  - Sensitive values masked via security policy in all output paths
  - Success, partial success with warnings, and failure visually distinguishable
  - Rendering never throws on unexpected data — unknown shapes fall back to safe generic display
  - Progress hints clear on completion/failure without corrupting output
- **Edge Cases**: Non-TTY, narrow terminal, no unicode support, huge result set, binary data in result, JSON + error simultaneously, color policy conflict, piped output, result with unknown fields
- **Error Handling**: Rendering failure → minimal safe display of raw result summary; masking failure → suppress affected value entirely

### FR-CLI-003: Display Errors

Present failures as categorized, actionable guidance. Never display secrets.

- **Input**: Error concept (category, message, optional field detail, optional upstream context)
- **Output**: Rendered error (category label, actionable message, remediation hint, exit code)
- **Business Rules**:
  - Every error shows stable category + actionable message + remediation hint
  - Secrets/tokens/credentials/code/paths masked via security policy before display
  - Upstream categories pass through unchanged — CLI renames nothing
  - Field-level validation detail rendered when present
  - Stack traces hidden by default; verbose flag may reveal structural detail (still masked)
  - Errors distinguish user-correctable from internal failures
  - JSON mode: errors as structured objects with category, message, hint, detail
  - Exit code maps to error category class for deterministic script branching
- **Edge Cases**: Error without category, message containing embedded secret, nested upstream errors, verbose mode, JSON error output, hint unavailable, field detail referencing masked value, multiple errors from one aggregate
- **Error Handling**: Display failure → generic categorized message; masking failure → suppress affected fragment; hint absence → degrade to category + message

## Command Mapping

The CLI exposes every canonical action exactly once using kebab-case. MCP keeps the same action names in snake_case. Both surfaces are generated from the shared dispatcher catalog; no duplicate fallback or shortcut alias is part of the public surface.

| CLI command | Parameters | MCP action | Owner |
|---|---|---|---|
| `execute-blender-code` | `--code` **required** | `execute_blender_code` | `gateway` |
| `get-scene-info` | — | `get_scene_info` | `scene` |
| `cleanup-scene` | `--mode` **required** | `cleanup_scene` | `scene` |
| `list-scene-objects` | `--include-hidden`, `--object-type`, `--limit` | `list_scene_objects` | `scene` |
| `get-object-hierarchy` | `--object-name`, `--include-hidden`, `--max-depth` | `get_object_hierarchy` | `scene` |
| `undo` | — | `undo` | `scene` |
| `redo` | — | `redo` | `scene` |
| `get-object-info` | `--object-name` **required** | `get_object_info` | `object` |
| `create-primitive` | `--primitive-type` **required**, `--location`, `--scale`, `--name` | `create_primitive` | `object` |
| `set-object-transform` | `--object-name` **required**, `--location`, `--rotation`, `--scale` | `set_object_transform` | `object` |
| `delete-object` | `--object-name` **required** | `delete_object` | `object` |
| `set-material` | `--object-name` **required**, `--material-name` **required** | `set_material` | `object` |
| `create-material` | `--material-name` **required**, `--base-color`, `--metallic`, `--roughness`, `--reuse-existing` | `create_material` | `object` |
| `set-material-properties` | `--material-name` **required**, `--base-color`, `--metallic`, `--roughness` | `set_material_properties` | `object` |
| `set-material-texture` | `--material-name` **required**, `--file-path` **required** | `set_material_texture` | `object` |
| `apply-modifier` | `--object-name` **required**, `--modifier-name` **required** | `apply_modifier` | `object` |
| `inspect-geometry-node-group` | `--node-group-name` **required** | `inspect_geometry_node_group` | `geometry_nodes` |
| `create-geometry-node-group` | `--node-group-name` **required**, `--object-name` | `create_geometry_node_group` | `geometry_nodes` |
| `set-geometry-node-link` | `--node-group-name` **required**, `--from-node` **required**, `--from-socket` **required**, `--to-node` **required**, `--to-socket` **required** | `set_geometry_node_link` | `geometry_nodes` |
| `set-geometry-node-modifier` | `--object-name` **required**, `--node-group-name` **required** | `set_geometry_node_modifier` | `geometry_nodes` |
| `get-animation-state` | `--object-name` **required**, `--limit` | `get_animation_state` | `animation` |
| `insert-object-keyframe` | `--object-name` **required**, `--frame` **required**, `--data-path` **required**, `--index` | `insert_object_keyframe` | `animation` |
| `set-timeline-range` | `--frame-start` **required**, `--frame-end` **required**, `--current-frame` | `set_timeline_range` | `animation` |
| `list-object-keyframes` | `--object-name` **required**, `--limit` | `list_object_keyframes` | `animation` |
| `get-mesh-statistics` | `--object-name` **required** | `get_mesh_statistics` | `mesh` |
| `validate-mesh` | `--object-name` **required**, `--limit` | `validate_mesh` | `mesh` |
| `perform-mesh-edit-operation` | `--object-name` **required**, `--operation` **required** | `perform_mesh_edit_operation` | `mesh` |
| `ensure-mesh-uv-layer` | `--object-name` **required**, `--uv-layer-name` | `ensure_mesh_uv_layer` | `mesh` |
| `configure-camera` | `--camera-ref`, `--focal-length`, `--sensor-fit`, `--framing-target`, `--set-active`, `--depth-of-field-enabled`, `--focus-distance`, `--focus-object`, `--aperture`, `--create-if-missing` | `configure_camera` | `render` |
| `setup-environment` | `--hdri-id` **required**, `--strength` | `setup_environment` | `render` |
| `get-viewport-screenshot` | `--filepath`, `--max-size`, `--view-angle`, `--shading-mode`, `--show-overlays`, `--focus-object` | `get_viewport_screenshot` | `render` |
| `render` | `--output-path` **required**, `--resolution-x`, `--resolution-y` | `render` | `render` |
| `set-render-settings` | `--engine`, `--resolution-x`, `--resolution-y`, `--resolution-percentage`, `--samples`, `--use-transparent` | `set_render_settings` | `render` |
| `inspect-compositor-nodes` | `--limit` | `inspect_compositor_nodes` | `compositor` |
| `configure-compositor` | `--use-nodes` **required** | `configure_compositor` | `compositor` |
| `create-compositor-node` | `--node-type` **required**, `--node-name` | `create_compositor_node` | `compositor` |
| `set-compositor-link` | `--from-node` **required**, `--from-socket` **required**, `--to-node` **required**, `--to-socket` **required** | `set_compositor_link` | `compositor` |
| `inspect-sequence-editor` | `--limit` | `inspect_sequence_editor` | `vse` |
| `create-sequence-strip` | `--strip-type` **required**, `--strip-name` **required**, `--filepath`, `--channel` **required**, `--frame-start` **required**, `--frame-end` | `create_sequence_strip` | `vse` |
| `remove-sequence-strip` | `--strip-name` **required** | `remove_sequence_strip` | `vse` |
| `render-sequence` | `--output-path` **required**, `--frame-start`, `--frame-end` | `render_sequence` | `vse` |
| `get-physics-state` | `--object-name` **required** | `get_physics_state` | `physics` |
| `configure-rigid-body` | `--object-name` **required**, `--enabled` **required**, `--body-type`, `--mass`, `--kinematic` | `configure_rigid_body` | `physics` |
| `configure-cloth-simulation` | `--object-name` **required**, `--enabled` **required**, `--quality`, `--pin-group` | `configure_cloth_simulation` | `physics` |
| `bake-physics-simulation` | `--frame-start`, `--frame-end` | `bake_physics_simulation` | `physics` |
| `clear-physics-bake` | — | `clear_physics_bake` | `physics` |
| `get-simulation-state` | `--object-name` **required** | `get_simulation_state` | `physics` |
| `get-simulation-cache-status` | — | `get_simulation_cache_status` | `physics` |
| `configure-particle-system` | `--object-name` **required**, `--enabled` **required**, `--count`, `--frame-start`, `--frame-end`, `--lifetime`, `--physics-type` | `configure_particle_system` | `physics` |
| `configure-force-field` | `--object-name` **required**, `--enabled` **required**, `--field-type`, `--strength`, `--noise` | `configure_force_field` | `physics` |
| `configure-fluid-domain` | `--object-name` **required**, `--enabled` **required**, `--domain-type`, `--resolution`, `--cache-type` | `configure_fluid_domain` | `physics` |
| `inspect-armature` | `--object-name` **required**, `--limit` | `inspect_armature` | `rigging` |
| `set-pose-bone-transform` | `--armature-name` **required**, `--bone-name` **required**, `--location`, `--rotation-euler`, `--scale` | `set_pose_bone_transform` | `rigging` |
| `configure-bone-constraint` | `--armature-name` **required**, `--bone-name` **required**, `--constraint-type` **required**, `--enabled` **required**, `--constraint-name`, `--target-object`, `--subtarget` | `configure_bone_constraint` | `rigging` |
| `configure-shape-key` | `--object-name` **required**, `--shape-key-name` **required**, `--enabled` **required**, `--value`, `--slider-min`, `--slider-max` | `configure_shape_key` | `rigging` |
| `get-deformation-state` | `--object-name` **required** | `get_deformation_state` | `rigging` |
| `search-assets` | `--query`, `--providers`, `--asset-type-filter`, `--limit`, `--page-token` | `search_assets` | `asset` |
| `get-provider-metadata` | `--provider` **required**, `--asset-id` **required** | `get_provider_metadata` | `asset` |
| `download-asset` | `--provider` **required**, `--asset-id` **required**, `--asset-type` **required**, `--cache-dir` **required**, `--resolution`, `--overwrite-policy`, `--max-size`, `--background` | `download_asset` | `asset` |
| `extract-asset` | `--artifact-path` **required**, `--destination` **required**, `--max-entries`, `--max-extracted-size`, `--allow-symlinks` | `extract_asset` | `asset` |
| `import-asset` | `--file-path` **required**, `--asset-type` **required**, `--target-collection`, `--scale-normalization`, `--duplicate-policy`, `--format-hint` | `import_asset` | `asset` |
| `import-glb` | `--file-path` **required**, `--object-name` | `import_glb` | `asset` |
| `export-model` | `--object-name` **required**, `--file-path` **required**, `--export-format` | `export_model` | `asset` |
| `place-asset` | `--asset-id` **required**, `--location`, `--rotation`, `--scale` | `place_asset` | `asset` |
| `launch-blender` | `--filepath`, `--mode`, `--port` | `launch_blender` | `launcher` |
| `shutdown-blender` | `--force` | `shutdown_blender` | `launcher` |
| `get-runtime-status` | — | `get_runtime_status` | `launcher` |
| `register-executable` | `--path` | `register_executable` | `launcher` |
| `submit-task` | `--operation-type` **required**, `--correlation-id`, `--metadata` | `submit_task` | `job` |
| `list-tasks` | — | `list_tasks` | `job` |
| `get-capacity-status` | — | `get_capacity_status` | `job` |
| `get-task-status` | `--task-id` **required** | `get_task_status` | `job` |
| `cancel-task` | `--task-id` **required** | `cancel_task` | `job` |
| `get-config` | `--key` | `get_config` | `config` |
| `set-config` | `--key` **required**, `--value` **required** | `set_config` | `config` |
| `list-plugins` | — | `list_plugins` | `plugin` |
| `download-plugin` | `--plugin-id` **required**, `--source-url` **required**, `--sha256` **required**, `--cache-path` **required** | `download_plugin` | `plugin` |
| `verify-plugin` | `--plugin-id` **required**, `--sha256` **required**, `--cache-path` **required** | `verify_plugin` | `plugin` |
| `install-plugin` | `--plugin-id` **required**, `--sha256` **required**, `--cache-path` **required**, `--install-path` **required** | `install_plugin` | `plugin` |
| `remove-plugin` | `--plugin-id` **required**, `--install-path` **required**, `--confirm` | `remove_plugin` | `plugin` |

Every command supports `--help`, `--json`, `--quiet`, `--verbose`, `--color`, `--no-progress`, and `--confirm`. The `--confirm` flag is enforced by the action contract for destructive operations.

The command form is:

```text
blender-arwaky <action-name> [typed flags]
```

Action parameters are typed from the same schema consumed by MCP `list_commands`; CLI uses kebab-case flags while MCP uses snake_case object keys.

## Error Categories

- **Owned**: validation error (surface-level arg problems), configuration error (settings unavailable), blocked (contract not executable), unsupported (runtime mode/capability unavailable)
- Plugin package actions delegate HTTPS, digest, archive, and filesystem safety decisions to the plugin aggregate; CLI only validates flag shape and renders the normalized result.
- **Displayed but unowned**: not_found, capacity, timeout, security_violation, connection, state, task — pass through from owning features with CLI remediation hints attached (hints carry no logic authority)
- `not_found` must never be used for a known-but-blocked or known-but-unsupported command.

## Events

None. CLI does not emit domain events.

## Configuration Keys


| Key                   | Description                 | Default                 |
| ----------------------- | ----------------------------- | ------------------------- |
| default_output_format | text or json                | text                    |
| secret_masking        | always enabled              | enabled                 |
| color_policy          | auto/always/never           | auto                    |
| list_page_size        | row limit before truncation | conservative            |
| progress_hints        | show for long operations    | enabled for interactive |

## QA Checklist

- [ ]  Commands parse + route to correct aggregate
- [ ]  Unknown command → validation error with suggestions
- [ ]  Every command supports --help
- [ ]  Surface validation before routing
- [ ]  Semantic validation by owning feature only
- [ ]  Results rendered in clear text format
- [ ]  JSON output: machine-stable, no decoration
- [ ]  JSON errors: structured objects
- [ ]  Large payloads truncated in text, complete in JSON
- [ ]  Color suppressed for non-TTY
- [ ]  Errors: category + actionable message + remediation hint
- [ ]  Stack traces hidden by default
- [ ]  Secrets masked in all output paths
- [ ]  Exit codes deterministic per outcome class
- [ ]  Progress hints clear on completion/failure
- [ ]  No business logic in CLI layer
- [ ]  New capability reachable via mapping only, no CLI logic changes
