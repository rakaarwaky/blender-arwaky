# Wave 3 MPFB2 RNA Audit

## Scope

This audit targets MPFB2 2.0.17 installed as a Blender 5.2 extension. The goal is to identify stable, explicit surfaces for `inspect-character` and `configure-character` without importing arbitrary provider source into Arwaky or exposing arbitrary Python execution.

## Environment

The live audit ran with Blender 5.2.0 LTS and the MPFB2 extension installed in the isolated `user_default` repository. The public operator namespace `bpy.ops.mpfb` was available and `bpy.ops.mpfb.create_human()` returned `{'FINISHED'}`.

The generated character was a mesh object named `Human` with 19,158 vertices, one `MASK` modifier named `Hide helpers`, and 11 initial shape keys. The runtime probe must detect the modern extension through the public `bpy.ops.mpfb.create_human` operator; legacy `addon_utils.check("mpfb")` does not reliably represent modern Blender Extension System state.

## Operator inventory

The character-related operator inventory exposed by MPFB2 contained 19 operators. The primary relevant operators were:

| Operator | RNA parameters | Wave 3 status |
|---|---:|---|
| `mpfb.create_human` | None | Already mapped by Wave 2 as `create-character`. |
| `mpfb.create_random_human` | None | Candidate for a later `randomize-character` action. |
| `mpfb.create_random_human_batch` | None | Deferred; batch semantics require a separate bounded contract. |
| `mpfb.human_from_mhm` | `filepath`, `filter_glob` | Deferred; requires file import policy and asset validation. |
| `mpfb.human_from_presets` | None | Deferred; preset discovery and selection contract are not yet defined. |
| `mpfb.randomize_detail_apply_all` | None | Deferred; affects detail targets rather than core phenotype. |
| `mpfb.randomize_load_preset` | None | Deferred; requires allowlisted preset identity. |
| `mpfb.prune_human` | None | Candidate for a later optimization/cleanup action, not configuration. |
| `mpfb.refit_human` | None | Deferred; requires explicit rig/bodypart semantics. |

The relevant conclusion is that MPFB2 does not expose the first configuration operation as an operator with typed parameters. Configuration is represented by object properties and then applied through MPFB2's `TargetService.reapply_macro_details` service.

## Character RNA properties

The following properties were present on the generated base mesh and form the first safe configuration surface. MPFB2 metadata files define these values as normalized floats with defaults; Arwaky should enforce the `[0.0, 1.0]` range even though Blender's generated RNA hard limits are effectively unbounded.

| Canonical field | MPFB2 property | Type | Meaning |
|---|---|---:|---|
| `gender` | `MPFB_HUM_gender` | float | `0.0` female, `1.0` male. |
| `age` | `MPFB_HUM_age` | float | Baby `0.0`, child `0.1875`, young `0.5`, old `1.0`. |
| `weight` | `MPFB_HUM_weight` | float | Character weight phenotype. |
| `height` | `MPFB_HUM_height` | float | Character height phenotype. |
| `muscle` | `MPFB_HUM_muscle` | float | Character muscularity. |
| `proportions` | `MPFB_HUM_proportions` | float | `0.0` wide hips/narrow shoulders, `1.0` wide shoulders/narrow hips. |
| `race_african` | `MPFB_HUM_african` | float | African race target influence. |
| `race_asian` | `MPFB_HUM_asian` | float | Asian race target influence. |
| `race_caucasian` | `MPFB_HUM_caucasian` | float | Caucasian race target influence. |
| `cupsize` | `MPFB_HUM_cupsize` | float | Breast cup-size phenotype. |
| `firmness` | `MPFB_HUM_firmness` | float | Breast firmness phenotype. |

The core first implementation should expose the six general fields (`gender`, `age`, `weight`, `height`, `muscle`, and `proportions`) plus the three race fields. `cupsize` and `firmness` should be accepted only when explicitly requested because MPFB2 documents that non-default values can look strange on male characters.

The object also exposes general metadata properties such as `MPFB_GEN_object_type`, which returned `Basemesh`, `MPFB_GEN_uuid`, which was empty for the generated default human in this audit, and `MPFB_GEN_scale_factor`. Object name and active mesh identity are therefore more reliable initial identifiers than the optional UUID field.

## Safe configuration path

Writing `MPFB_HUM_*` values alone changes the RNA value but does not change the evaluated mesh. The live audit showed that direct property mutation produced no geometry change until MPFB2's target reapplication service was called.

The verified provider path is:

```text
resolve explicit mesh object
→ validate allowlisted MPFB_HUM fields and [0, 1] values
→ set MPFB_HUM_* properties
→ call TargetService.reapply_macro_details(mesh)
→ update Blender dependency graph
→ inspect evaluated result
```

`TargetService.reapply_macro_details` reads the phenotype dictionary using `get_macro_info_dict_from_basemesh`, recalculates macro target weights with `calculate_target_stack_from_macro_info_dict`, loads missing macro target shape keys, and updates the target values. The live test changed 18 shape-key values and changed the evaluated geometry after reapplication.

Arwaky should call this provider service through an explicit provider mapper. It must not accept a module path, Python expression, or arbitrary service name from CLI/MCP input. The mapper should contain one fixed MPFB2 operation such as `character.configure`.

## Recommended canonical contracts

### `inspect-character`

The request should contain a bounded character selector, initially `object_name` and optionally `plugin_id` defaulting to `mpfb2`. The result should include object name, object type, vertex count, material names, modifier summaries, shape-key count, current macro values, and provider health. The result should not dump every Blender RNA property by default; a bounded allowlist keeps the response stable and avoids leaking unrelated settings.

### `configure-character`

The request should contain `object_name`, `plugin_id`, and an optional patch containing only the allowlisted fields from the table above. The operation must reject unknown fields, non-numeric values, NaN/infinite values, values outside `[0.0, 1.0]`, missing target objects, non-mesh objects, and inactive MPFB2 provider state. It should return the normalized applied values and a compact evaluated summary.

A first schema can be represented as:

```text
configure-character
  --object-name OBJECT_NAME
  --gender 0..1
  --age 0..1
  --weight 0..1
  --height 0..1
  --muscle 0..1
  --proportions 0..1
  --race-african 0..1
  --race-asian 0..1
  --race-caucasian 0..1
  --cupsize 0..1
  --firmness 0..1
```

The action should require at least one patch field and should not silently normalize the three race values unless the contract explicitly documents that behavior. The safest initial behavior is to preserve supplied values and report them; optional sum validation can be introduced after more MPFB2 behavior is tested.

## Audit conclusion

The audit confirms that Wave 3 can be implemented without arbitrary Python. `inspect-character` can be built from bounded Blender object and MPFB2 property reads. `configure-character` should use direct allowlisted RNA writes followed by the explicit MPFB2 `TargetService.reapply_macro_details` service. The next implementation step is to add canonical schemas, provider mapping, Blender-side handler, and live tests for these two actions.
