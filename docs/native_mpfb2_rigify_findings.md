# Native MPFB2 Rigify Findings

## Runtime verification

Blender 5.2.0 LTS with the installed MPFB2 extension successfully ran the native workflow:

1. `HumanService.create_human()` created a basemesh character.
2. `HumanService.add_builtin_rig(character, "rigify.human_toes", import_weights=True)` created a fitted MPFB2 Rigify metarig.
3. The native metarig contained 213 bones.
4. MPFB2 created two armature modifiers on the character: `Armature` and `Armature PV`, both initially targeting the native metarig.
5. The character contained 361 vertex groups, including helper groups and native weight groups.
6. `RigService.identify_rig(meta_rig)` returned `rigify.human_toes`.
7. `RigService.generate_rigify_rig(meta_rig, name="Native_MPFB2_Rigify_Control", meta_rig_action="hide")` succeeded.
8. The generated final Rigify control rig contained 1090 bones, including 209 deform bones.
9. MPFB2 automatically redirected both armature modifiers to `Native_MPFB2_Rigify_Control`.

This confirms the correct integration path is the native MPFB2 service API, not a generic Rigify human metarig followed by bounding-box or landmark heuristics.

## Installed native data

The Blender 5.2 MPFB2 extension contains:

- `/home/ubuntu/.config/blender/5.2/extensions/user_default/mpfb/data/rigs/rigify/rig.human.json`
- `/home/ubuntu/.config/blender/5.2/extensions/user_default/mpfb/data/rigs/rigify/rig.human_toes.json`
- `/home/ubuntu/.config/blender/5.2/extensions/user_default/mpfb/data/rigs/rigify/weights.human_toes.json`

The native `HumanService.add_builtin_rig` implementation loads the rig definition with `Rig.from_json_file_and_basemesh`, fits it to the basemesh using MPFB strategies, loads the corresponding weights with `RigService.load_weights`, and ensures the armature modifier. Native `RigService.generate_rigify_rig` validates the metarig through Rigify, calls `bpy.ops.pose.rigify_generate()`, and lets MPFB adjust generated-rig children and metadata.

## External sources

- MPFB rigging documentation: https://static.makehumancommunity.org/mpfb/docs/rigging_mesh_assets.html
- MPFB2 Rigify issue and native data references: https://github.com/makehumancommunity/mpfb2/issues/21
- Blender Rigify manual: https://docs.blender.org/manual/en/latest/addons/rigging/rigify/basics.html
