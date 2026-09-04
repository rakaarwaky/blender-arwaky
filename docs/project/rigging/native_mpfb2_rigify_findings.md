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

## Visual detail evidence

The native scene was rendered again with deterministic diagnostic curves generated from the final Rigify pose-bone coordinates. This evidence is intended to verify local bone placement on the character mesh, complementing the runtime deformation measurements in `native_mpfb2_rigify_validation.md`.

| Evidence | Resolution | Native overlay content | Purpose |
| --- | ---: | --- | --- |
| `native_mpfb2_rigify_full_skeleton.png` | 900 × 1100 | 1,090 pose bones; 260 controls; 22 IK targets | Full-body structural inspection |
| `native_mpfb2_rigify_face_closeup.png` | 1,000 × 1,000 | 97 DEF facial bones; 72 face controls | Inspection of brow, eye, nose, cheek, lip, jaw, ear, and neck mapping |
| `native_mpfb2_rigify_hand_closeup.png` | 1,100 × 900 | 16 DEF left-hand/finger bones; 27 controls; 2 IK-related bones | Inspection of wrist, palm, thumb, index, middle, ring, and pinky chains |

The face close-up shows the facial chains tracking the corresponding mesh regions. The hand close-up uses the front-side camera because the character pose brings the fingers close together; overlapping silhouettes are therefore a property of the current pose, not a missing finger chain. IK targets and animator controls can extend outside the mesh by design and must not be interpreted as deform-bone misalignment.

The editable scene retains `show_in_front=True` and `display_type="OCTAHEDRAL"` on the generated Rigify armature, so the same native armature can also be inspected directly in Blender's 3D Viewport.

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
