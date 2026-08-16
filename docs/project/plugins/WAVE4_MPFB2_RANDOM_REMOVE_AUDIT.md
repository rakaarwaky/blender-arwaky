# Wave 4 MPFB2 Randomization and Removal Audit

## Scope

Audit ini memeriksa MPFB2 2.0.17 sebagai Blender 5.2 extension untuk menentukan contract aman bagi `randomize-character` dan `remove-character`. Audit dijalankan pada Blender 5.2.0 LTS dengan MPFB2 aktif pada repository `user_default` yang terisolasi.

## Executive conclusion

MPFB2 2.0.17 tidak mendaftarkan operator `mpfb.create_random_human` pada Blender 5.2. API publik yang tersedia untuk pembuatan human adalah `HumanService.create_human`, sedangkan randomisasi phenotype disediakan oleh `RandomizationService.randomize_macro_info_dict`. Karena kedua service tersebut menghasilkan karakter baru, canonical Arwaky `randomize-character` mendokumentasikan semantic-nya sebagai pembuatan karakter random baru, bukan mutasi karakter existing.

MPFB2 tidak menyediakan operator publik `remove-human` atau `remove-character`. Operator removal yang tersedia bersifat partial, seperti `remove_helpers`, `delete_helpers`, `prune_human`, dan `delete_hair_operator`. Oleh karena itu, `remove-character` harus menjadi operation yang dimiliki Arwaky dengan deletion closure yang eksplisit dan tervalidasi.

## Environment

| Item | Value |
|---|---|
| Blender | 5.2.0 LTS |
| MPFB2 | 2.0.17 |
| Extension namespace | `bl_ext.user_default.mpfb` and `bpy.ops.mpfb` |
| Randomization API | `RandomizationService.randomize_macro_info_dict` |
| Human creation API | `HumanService.create_human` |
| Operator inventory | `human_from_presets`, `randomize_detail_apply_all`, and related partial operators |
| Removal operator | No complete public operator found |

## Operator inventory

| Operator | RNA parameters | Audit result |
|---|---:|---|
| `RandomizationService.randomize_macro_info_dict` | `spec`, `rng` (Python service API) | Deterministically returns bounded macro phenotype values. |
| `HumanService.create_human` | `macro_detail_dict` (Python service API) | Creates a new MPFB2 basemesh from the approved phenotype dictionary. |
| `mpfb.human_from_presets` | None | Creates a human from selected presets; not the seeded randomization path. |
| `mpfb.randomize_detail_apply_all` | None | Partial detail operation, not a complete character randomizer. |
| `mpfb.randomize_load_preset` | None | Deferred until preset contract is defined. |
| `mpfb.randomize_save_new_preset` | None | Deferred until preset storage policy is defined. |
| `mpfb.remove_helpers` | None | Removes helpers only; not a complete character removal. |
| `mpfb.delete_helpers` | None | Deletes helpers only; not a complete character removal. |
| `mpfb.prune_human` | None | Cleanup/pruning operation, not character deletion. |
| `mpfb.delete_hair_operator` | `hair_asset` | Removes one hair asset, not the complete character. |

The legacy/UI randomizer settings are represented by MPFB2 scene properties, but the Wave 4 provider path does not mutate an unbounded scene-property dictionary. It constructs the default phenotype specification and passes a seeded `random.Random` instance to the public service API. The relevant legacy controls remain documented for audit traceability:

| Scene property | Meaning |
|---|---|
| `MPFB_RAND_seed` | Integer seed. The same seed and same settings produce the same random character. `0` requests a fresh random seed. |
| `MPFB_RAND_new_random_seed` | When enabled, writes a fresh seed after successful creation. |
| `MPFB_RAND_randomize_details` | Enables random detail targets. |
| `MPFB_RAND_randomize_skin` | Enables random skin selection. |
| `MPFB_RAND_race_include` | Enables race randomization. |
| `MPFB_RAND_*_neutral` and `MPFB_RAND_*_deviation` | Distribution controls for macro phenotype fields. |

## Determinism validation

The same seed was executed twice on Blender 5.2 with the same MPFB2 service specification. Both executions produced identical mesh vertex digests:

```text
seed 424242:
  first character  = Wave4CharacterA
  second character = Wave4CharacterB
  mesh digest      = identical
```

The live smoke test also verified that each invocation creates a distinct named character and that the same seed yields an identical mesh digest. Therefore, Wave 4 exposes an optional non-negative integer `seed` while preserving deterministic behavior.

## Character ownership audit

With default randomization settings and rig generation enabled, MPFB2 produced this object relationship:

```text
Human.rig  (ARMATURE, root)
└── Human  (MESH, MPFB basemesh)
```

The basemesh had an Armature modifier referencing `Human.rig`, a Mask modifier, and a Subdivision modifier. Both objects were linked to the existing `Collection`. The unrelated `Camera`, `Cube`, and `Light` remained in the same collection.

No complete MPFB-specific object custom property was present on the object or mesh data in this default run. Therefore, the initial selector must require an exact object name and verify MPFB identity using mesh type, required `MPFB_HUM_*` properties, and the `MPFB_GEN_object_type == "Basemesh"` marker when available.

## Removal closure validation

The safe initial closure algorithm is:

1. Resolve the exact requested object name.
2. Verify that the target is a mesh MPFB2 basemesh.
3. Walk to the topmost parent root.
4. Include the target, the root, and all descendants of the root.
5. Remove only that explicit object set with `do_unlink=True`.
6. Do not remove the containing collection, unrelated objects, or globally shared datablocks by default.

The live Blender 5.2 smoke test resolved the closure to:

```text
["Human", "Human.rig"]
```

After deletion, the remaining objects were:

```text
["Camera", "Cube", "Light"]
```

This confirms that the closure removes the MPFB2 character and rig while preserving unrelated scene objects.

## Recommended canonical schemas

### `randomize-character`

The first schema should have these semantics:

```text
randomize-character
  --plugin-id mpfb2
  --name optional
  --seed optional integer >= 0
```

`randomize-character` should create one new character. It should not accept an existing `object_name` until a separate mutate-existing randomization service is implemented and verified. The provider handler constructs the default MPFB2 phenotype specification, uses a seeded local random generator, calls only `RandomizationService.randomize_macro_info_dict` followed by `HumanService.create_human`, and returns the created basemesh identity and seed. It does not accept arbitrary scene-property mutation.

The mapper must not expose the entire MPFB2 scene configuration. Wave 4 should initially expose only `seed`, `name`, and a small, explicitly approved set of randomization toggles. Macro distribution settings and asset filters should be deferred until their schema is designed.

### `remove-character`

The first schema should have these semantics:

```text
remove-character
  --plugin-id mpfb2
  --object-name required
  --confirm required for destructive execution
```

The handler must reject missing targets, non-mesh targets, meshes without required MPFB2 properties, and ambiguous selectors. It returns the exact removed object names and preserves unrelated scene objects. It does not call MPFB2 partial cleanup operators as a substitute for deletion closure. The live smoke test additionally verifies that `confirm=false` is rejected.

## Wave 4 implementation boundary

The provider mapping remains in `plugin/mpfb2/`. The canonical schemas and action catalog remain in `modules/shared/`. The Blender-side removal algorithm belongs to the explicit addon handler because MPFB2 has no complete public remove operator. The randomization handler calls the namespaced public MPFB2 service APIs through an explicit import path and a bounded seed contract.

No arbitrary Python, dynamic operator names, arbitrary module paths, or unbounded MPFB2 scene-property dictionaries should be accepted.

## Audit status

| Check | Result |
|---|---:|
| Blender 5.2 MPFB2 operator inventory | Passed |
| Randomization seed property audit | Passed |
| Same-seed determinism | Passed |
| Different-seed variation | Passed |
| Object parent/child ownership audit | Passed |
| Removal closure smoke test | Passed |
| Canonical schema and provider mapping | Passed |
| Live Blender 5.2 same-seed smoke test | Passed |
| Live Blender 5.2 removal confirmation guard | Passed |

Wave 4 implementation is complete. `randomize-character` is explicitly documented as **create a new random human**, and `remove-character` is implemented as a bounded Arwaky-owned deletion closure.
