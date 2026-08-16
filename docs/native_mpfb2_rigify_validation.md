# Native MPFB2 Rigify Validation

Blender 5.2.0 LTS successfully executed the native MPFB2 Rigify workflow through the Arwaky server handler.

The native path used `HumanService.add_builtin_rig(character, "rigify.human_toes", import_weights=True)`. It created a 213-bone MPFB2-fitted metarig, two armature modifiers (`Armature` and `Armature PV`), and native vertex weights. `RigService.generate_rigify_rig` then generated a 1090-bone final Rigify control rig containing 209 deform bones. Both armature modifiers target the final generated rig.

The initial pose test using `upper_arm_fk.L` was intentionally rejected because it produced zero vertex displacement. Diagnosis showed the correct generated Rigify control for this operation is `upper_arm_ik.L`. With `upper_arm_ik.L` rotated, 2,371 vertices changed and maximum evaluated displacement was 0.074709 Blender units. Resetting the pose returned the mesh to the rest state with maximum displacement 0.0.

The native beauty render was generated at `/home/ubuntu/mpfb_native_rigify_evidence/native_mpfb2_rigify_character.png` and the editable Blender scene is `/home/ubuntu/mpfb_native_rigify_evidence/native_mpfb2_rigify_character.blend`. The visual evidence set now also includes `/home/ubuntu/mpfb_native_rigify_evidence/native_mpfb2_rigify_full_skeleton.png`, `/home/ubuntu/mpfb_native_rigify_evidence/native_mpfb2_rigify_face_closeup.png`, and `/home/ubuntu/mpfb_native_rigify_evidence/native_mpfb2_rigify_hand_closeup.png`.

The full-skeleton renderer projects all 1,090 final Rigify pose bones into deterministic curve overlays. The face close-up contains 97 DEF facial bones and 72 face controls. The hand close-up contains 16 DEF left-hand/finger bones, 27 controls, and 2 IK-related bones. These overlays are visual diagnostics; the authoritative acceptance evidence remains the native weight/modifier metadata and measured evaluated-mesh deformation, not the overlay alone.
