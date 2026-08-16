# Native MPFB2 Rigify Validation

Blender 5.2.0 LTS successfully executed the native MPFB2 Rigify workflow through the Arwaky server handler.

The native path used `HumanService.add_builtin_rig(character, "rigify.human_toes", import_weights=True)`. It created a 213-bone MPFB2-fitted metarig, two armature modifiers (`Armature` and `Armature PV`), and native vertex weights. `RigService.generate_rigify_rig` then generated a 1090-bone final Rigify control rig containing 209 deform bones. Both armature modifiers target the final generated rig.

The initial pose test using `upper_arm_fk.L` was intentionally rejected because it produced zero vertex displacement. Diagnosis showed the correct generated Rigify control for this operation is `upper_arm_ik.L`. With `upper_arm_ik.L` rotated, 2,371 vertices changed and maximum evaluated displacement was 0.074709 Blender units. Resetting the pose returned the mesh to the rest state with maximum displacement 0.0.

The native beauty render was generated at `/home/ubuntu/mpfb_native_rigify_evidence/native_mpfb2_rigify_character.png` and the editable Blender scene is `/home/ubuntu/mpfb_native_rigify_evidence/native_mpfb2_rigify_character.blend`. The diagnostic DEF overlay is `/home/ubuntu/mpfb_native_rigify_evidence/native_mpfb2_rigify_def_overlay.png`.

The overlay intentionally displays only selected primary DEF bone names; the authoritative acceptance evidence is the native weight/modifier metadata and measured evaluated-mesh deformation, not the overlay alone.
