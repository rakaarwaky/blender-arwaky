# Research Notes — Rigify Animator Tools

> **Current scope decision (17 August 2026):** This is historical research only. Rigify-specific animation, retargeting, semantic controls, and procedural gait are deferred to external providers/plugins. The Arwaky core exposes native Blender animation primitives only. Earlier capability proposals in this historical ledger are superseded by `modules/animation/FRD.md`.

## Scope
Research awal untuk memilih capability animator bagi karakter MPFB2 yang sudah menggunakan generated Rigify rig pada Blender 5.2 LTS.

## Initial findings

- Blender manual 5.2 LTS is live at `https://docs.blender.org/manual/en/5.2/`, but the older search-result paths `en/latest/addons/rigging/rigify.html` and `en/latest/addons/rigging/rigify/index.html` returned 404 on 2026-08-16. This means source URLs must be validated before citation.
- Search results identify Rigify AnimBox as an older Rigify-specific animation helper, but available references indicate Blender 2.8/2.9-era compatibility and no clearly maintained Blender 5.2 source was found yet.
- Search results identify Rokoko's Blender integration and retargeting documentation as relevant for motion-capture import/retargeting, but it is a workflow/integration tool rather than a complete keyframe animator.
- Search results identify Auto-Rig Pro as a popular third-party rigging/animation workflow, but it is proprietary and would not be a direct provider for the existing native MPFB2 Rigify control rig without an adapter or retargeting boundary.

## Candidate categories to validate

1. Native Blender animation tools: Dope Sheet, Graph Editor, NLA, Pose Library/Asset Browser, constraints, motion paths, and animation data APIs.
2. Rigify-specific helpers: Rigify AnimBox or maintained successors.
3. Motion capture and retargeting: Rokoko, Mixamo/Rigify retargeting tools, and open-source retargeting add-ons.
4. Animation productivity tools: AnimBot/AnimAide-like workflows, pose mirroring, tweening, breakdowns, selection sets, and keying utilities.
5. Retargeting libraries and standards: HumanIK-like mapping, Rokoko/Mixamo/FBX source mapping, and Blender 5.2 Python APIs.

## Research rule

Do not recommend a dependency for Arwaky until its official source, maintenance status, license, Blender compatibility, and whether it operates on generated Rigify control bones are verified.

## Sources visited

- Blender Manual landing/404 pages: `https://docs.blender.org/manual/en/latest/addons/rigging/rigify/index.html` and `https://docs.blender.org/manual/en/latest/addons/rigging/rigify.html`
- Search result candidates: Blender Rigify manual, Rigify AnimBox BlenderArtists thread, Rokoko Blender integration, Rokoko retargeting support, cessen/Rigify GitHub.

## Status

Research is incomplete. This file is an interim ledger, not the final recommendation.

<!-- Sources will be expanded with validated official URLs and citations. -->

## References

[1]: https://docs.blender.org/manual/en/5.2/ "Blender 5.2 LTS Manual"
[2]: https://blenderartists.org/t/rigify-animbox-animation/1248691 "Rigify AnimBox discussion"
[3]: https://www.rokoko.com/integrations/blender "Rokoko Blender integration"
[4]: https://support.rokoko.com/hc/en-us/articles/4410463481489-Retarget-an-animation-in-Blender "Rokoko retargeting support"
[5]: https://github.com/cessen/rigify "Rigify source repository"

## Author

Manus AI

## Date

2026-08-16

## Version

0.1.0

## Next step

Validate the official Blender 5.2 manual path and inspect maintained repositories for Rigify animation, retargeting, pose libraries, and animation productivity tools.

## Notes

The user requested research first; no implementation decision has been made.

## Terminology

- **Generated Rigify rig**: The final control armature produced from a Rigify metarig.
- **Animator provider**: An Arwaky provider exposing canonical animation actions without owning character generation or rig generation.
- **Retargeting**: Mapping animation data from a source skeleton or control scheme to the target Rigify control rig.

## Acceptance criteria for final report

- At least one official Blender source and one official source per recommended third-party tool.
- Explicit license and compatibility status.
- Clear distinction between native Blender capabilities, add-ons, and external services.
- Concrete AES adapter boundary and prioritized implementation waves.
- Honest limitations where Blender 5.2 compatibility cannot be verified.

## Caveat

Search snippets are discovery aids only and will not be treated as evidence in the final recommendation without opening the underlying source URL.

## End

This ledger is intentionally concise and will be superseded by a final research document after source validation.

## Additional candidate names

- Blender Asset Shelf / Pose Library
- NLA strips and action management
- Animation Layers add-ons
- AnimAide
- Auto-Rig Pro
- Rokoko Studio Live / Retargeting
- Mixamo-to-Rigify retargeting tools
- Rigify AnimBox
- Blender Motion Capture Tools

## Implementation lens

The preferred Arwaky design should call Blender's native animation data APIs and target generated Rigify control bones. External add-ons should be optional adapters, not hard dependencies, unless their license and maintenance are suitable.

## End of initial notes


## Validated findings — 2026-08-16

### Native Blender Pose Library

The Blender 5.2 LTS manual states that Pose Library is based on the Asset Browser and is intended for Pose Mode armature work. A pose asset is an action containing exactly one frame of animation data. Users can create pose assets from selected bones, apply them by clicking, and blend them interactively by dragging. Pose assets can be stored in the current file or in `.asset.blend` libraries. This is a strong native foundation for Rigify hand, facial, and full-body pose workflows. Source: `https://docs.blender.org/manual/en/latest/animation/armatures/posing/editing/pose_library.html`.

### AnimAide

The official GitHub repository `aresdevo/animaide` describes three main panels: `curveTools` for manipulating keys across multiple F-curves, `animOffset` for propagating animation changes across a range, and `KeyManager` for speeding up common key operations. The repository page states that development is no longer active and that the project is transitioning to a more robust animation module; the latest displayed release is v1.0.39 and the repository shows a Python add-on. AnimAide is therefore useful as feature inspiration, but it is not a safe primary dependency for a Blender 5.2 production adapter without a compatibility fork and test suite. Source: `https://github.com/aresdevo/animaide`.

### Implication for Arwaky

The first animator capability should be built on native Blender 5.2 animation data and Asset Browser/Pose Asset APIs, not on an abandoned third-party add-on. AnimAide-like features can be implemented as optional productivity operations later: key selection/filtering, tween/breakdown generation, curve offset, mirror, and key-manager operations.

## References added

[6]: https://docs.blender.org/manual/en/latest/animation/armatures/posing/editing/pose_library.html "Blender 5.2 Pose Library"
[7]: https://github.com/aresdevo/animaide "AnimAide official repository"

## Source validation note

The Blender 5.2 manual URL for Pose Library was opened successfully and reports Blender 5.2 LTS. The AnimAide GitHub page was opened successfully and reports the repository status, feature panels, commit activity, and release information. Search snippets were not used as final evidence for these claims.

## End validated findings


## Validated findings — retargeting candidates

### Rokoko Blender retargeting

Rokoko's official support article says its Blender plugin can retarget exported Rokoko Studio Body and Face animations to custom characters. The retargeting workflow selects a source armature with animation and a target armature, builds a bone list, checks/fixes mappings, optionally auto-scales, chooses a matching pose, and runs Retarget Animation. Rokoko states that this retargeting feature does not require a premium plan. The article also warns that source and target armatures should be in the same pose and that auto-scale/current-pose choices affect results. This is relevant as an optional external retargeting adapter, but the target Rigify control-bone mapping and plugin version compatibility must be tested against Blender 5.2. Source: `https://support.rokoko.com/hc/en-us/articles/4410463481489-Retarget-an-animation-in-Blender`.

### Mixaify

The `netherby/mixaify-retarget` repository describes a GPL-3.0 Blender 5 add-on for Mixamo-to-Rigify retargeting. Its workflow imports a Mixamo FBX, aligns rest pose and scale, selects source and target armatures, retargets to Rigify FK controls, and bakes the constrained action. It includes a Rigify mode selector and recommends converting FK to IK only at keyframes because full per-frame conversion may introduce rotation and jitter problems. The author explicitly says the script assumes default Mixamo and Rigify bone names, is a simple FK solver, and cannot perfectly match poses because joint positions differ. The repository displayed six commits, one branch, five stars, and no published release at the time of research. This is a promising Blender 5 reference or optional adapter, not yet a production dependency. Source: `https://github.com/netherby/mixaify-retarget`.

### Blender Extensions — Retarget

The official Blender Extensions listing identifies `Retarget` by KBS-DEV as version 5.1.7, compatible with Blender 5.0 and newer, licensed GPL-3.0-or-later. It combines retargeting, Rigify conversion, Action Manager, and animation utilities. Listed features include Mixamo/Unreal/VRoid/MMD/Daz/Auto Rig Pro presets, custom presets, binding/unbinding armatures, constraints, mirror support, binding to an active metarig, conversion to Rigify, FK/action baking, root-motion transfer, and action management. The listing also states that it incorporates or forks functionality from Expy-Kit and AnimAide. Because it is a Blender Extensions-distributed GPL add-on with explicit Blender 5 compatibility, it is the strongest candidate found so far for an optional external workflow reference; Arwaky should still validate its mapping and maintenance before depending on it. Source: `https://extensions.blender.org/add-ons/retarget/`.

## Comparative implication

For a native Arwaky animator provider, the safest foundation remains Blender 5.2 Pose Assets and animation data APIs. For retargeting, the Blender Extensions `Retarget` add-on is the most relevant current candidate, while Mixaify is a smaller GPL reference focused specifically on Mixamo-to-Rigify. Rokoko is useful when the user already has Rokoko capture data, but it introduces an external vendor workflow. Auto-Rig Pro remains proprietary and should not be a core dependency.

## References added

[8]: https://support.rokoko.com/hc/en-us/articles/4410463481489-Retarget-an-animation-in-Blender "Rokoko official Blender retargeting guide"
[9]: https://github.com/netherby/mixaify-retarget "Mixaify Mixamo-to-Rigify repository"
[10]: https://extensions.blender.org/add-ons/retarget/ "Blender Extensions Retarget listing"

## End retargeting findings


## Validated findings — animation layers and commercial comparison

### Auto-Rig Pro

The official Superhive product page describes Auto-Rig Pro as a Blender add-on for rigging characters, retargeting animations, and exporting FBX/GLTF. Its Remap tool transfers actions between armatures with different bone names and orientations, supports BVH/FBX sources, and includes IK feet/hands and proportion offsets. The page presents paid product variants and seat options. Auto-Rig Pro is therefore a strong commercial benchmark for retargeting UX, but its paid proprietary distribution makes it unsuitable as an Arwaky core dependency. Source: `https://superhivemarket.com/products/auto-rig-pro`.

### Animation Layers for Blender

The `evilmushroom/Animation-Layers-for-Blender` repository describes a GPL-3.0 add-on that adds a non-destructive animation-layering system on top of Blender's NLA editor. The repository page shows a small project with one branch, three commits, and no published releases at the time of research. It is useful as a conceptual reference for layered keyframe editing, but its maintenance and Blender 5.2 compatibility require validation before adoption. Source: `https://github.com/evilmushroom/Animation-Layers-for-Blender`.

## Product decision implication

Arwaky should not copy or embed third-party add-on source code. The recommended architecture is a native Blender 5.2 animator provider that exposes canonical actions over generated Rigify control bones, with optional adapters for external retargeting workflows. Commercial tools such as Auto-Rig Pro should serve as UX benchmarks only. GPL tools can be evaluated or invoked as optional user-installed integrations, but license boundaries and independent compatibility testing must be respected.

## References added

[11]: https://superhivemarket.com/products/auto-rig-pro "Auto-Rig Pro official marketplace page"
[12]: https://github.com/evilmushroom/Animation-Layers-for-Blender "Animation Layers for Blender repository"

## End layer findings


## Scope decision — open source only

User decision: Arwaky must not create provider adapters for proprietary or unauditable plugins.

### Included candidates

- Native Blender 5.2 animation and Pose Library APIs.
- Native Rigify source and control-rig workflow; the Blender add-ons mirror exposes Rigify source under GPL-2.0-or-later.
- Blender Extensions Retarget, subject to Blender 5.2 runtime testing and license/maintenance audit; listing states GPL-3.0-or-later.
- Mixaify, subject to runtime testing; repository states GPL-3.0.
- Other open-source candidates only after explicit source, license, maintenance, and Blender 5.2 validation.

### Excluded candidates

- Auto-Rig Pro: commercial/proprietary; no Arwaky provider adapter, runtime integration, or source dependency.
- Rokoko Blender integration: vendor/proprietary workflow; no Arwaky provider adapter.
- AnimAide: repository indicates development is no longer active and license was not verified in the repository page; reference only, no adapter.
- Any plugin that requires a proprietary account, closed runtime, or source code that cannot be audited.

### Source validation

The Blender add-ons mirror page identifies itself as an archived read-only repository and shows Rigify code with SPDX `GPL-2.0-or-later`. This validates the native Rigify source boundary as auditable/open source, while it does not by itself guarantee every historical snapshot is the exact Blender 5.2 runtime source. Source: `https://github.com/blender/blender-addons/blob/main/rigify/rig_ui_template.py`.

## References added

[13]: https://github.com/blender/blender-addons/blob/main/rigify/rig_ui_template.py "Blender add-ons Rigify source mirror"

## Final scope rule

No proprietary provider adapter will be implemented in Arwaky. Native/open-source-only is now a hard acceptance gate for the Animator Provider roadmap.

## Wave 3 Rigify Control Audit — 2026-08-16

The native MPFB2-Rigify evidence character uses a 1,090-bone generated control armature. The canonical limb parent controls `upper_arm_parent.L` and `upper_arm_parent.R` expose the custom properties `FK_limb_follow`, `IK_FK`, `IK_Stretch`, `pole_vector`, `IK_parent`, and `pole_parent`; these are the native Rigify FK/IK switching controls for the generated limbs. The visible hand controls `hand_ik.L` and `hand_ik.R` exist as pose bones without custom properties.

The generated rig contains explicit facial controls and mechanisms, including `jaw_master`, `jaw_master_mouth`, `jaw`, eye controls, lip controls, brow controls, cheek controls, forehead controls, and nose controls. Wave 3 therefore scopes bounded domain inspection for face and hand/finger controls, plus allowlisted FK/IK property mutation on explicit limb-parent controls, instead of exposing all 1,090 bones indiscriminately.


## Wave 4 Retargeting API Findings — 2026-08-16

The official Blender Python API documents `bpy.ops.nla.bake` with `frame_start`, `frame_end`, `step`, `only_selected`, `visual_keying`, `clear_constraints`, `clear_parents`, `use_current_action`, `clean_curves`, `bake_types`, and `channel_types`. It bakes selected object or pose animation into an Action. Wave 4 will use this native operator only after explicit source-to-target mapping and temporary constraint setup, with `visual_keying=True`, `bake_types={"POSE"}`, and controlled frame ranges. The smoke test must verify the resulting target Action and preserve the source Action.

Source: `https://docs.blender.org/api/current/bpy.ops.nla.html`.

## Import workflow correction — 2026-08-16

The official Blender 5.2 FBX manual confirms that FBX is used to exchange animated characters and that Blender imports animation data as actions/curves. It explicitly warns that imported animations/actions may not be linked to the object automatically and may need manual reassignment. It also documents that import orientation and baked animation behavior require validation. Therefore Arwaky's canonical workflow must expose import, inspect, link/apply action, retarget, and bake operations rather than pretend Blender has high-level `create_walk_cycle` or `create_jump_action` operators. Source: `https://docs.blender.org/manual/en/latest/files/import_export/fbx_legacy.html`.

The attempted official URL `https://docs.blender.org/manual/en/latest/files/import_export/mocap.html` returned 404 on 2026-08-16. This URL should not be cited as evidence until the correct Blender 5.2 Motion Capture (BVH) manual path is located. The search result did confirm that Motion Capture (BVH) is a section in the Blender manual navigation, but the result snippet is not treated as final evidence.

## Canonical naming correction

Do not use fictional high-level actions such as `create_walk_cycle`, `create_jump_action`, or `create_run_cycle` as if they were official Blender operations. Prefer explicit operations such as `import_animation_file`, `import_motion_capture`, `inspect_imported_action`, `link_action_to_armature`, `retarget_animation`, `bake_animation_action`, `import_pose_asset`, `apply_pose_asset`, `edit_action_keyframes`, and `validate_animation_result`.

## End import correction


## Wave 2 Pose Asset Findings

The official Blender 5.2 LTS manual states that the Pose Library is based on the Asset Browser and is intended for Pose Mode armatures. A pose asset is an Action marked as an asset containing exactly one frame of animation data. Pose assets can use slots, and applying a pose chooses the best matching slot for the active armature. The documented operations include Apply Pose, Apply Pose Flipped, Blend Pose, and Select/Deselect Pose Bones.

The official Copy/Paste Pose manual documents Pose > Copy Pose, Paste Pose, and Paste Pose Flipped. Copying uses selected bones, while pasting applies by bone name and operates on each bone's local position, rotation, and scale. The paste buffer is session-only and is not saved, so Wave 2 should prefer persistent pose assets for reusable workflows and expose copy/paste only as an explicitly ephemeral operation.

Sources:
- https://docs.blender.org/manual/en/latest/animation/armatures/posing/editing/pose_library.html
- https://docs.blender.org/manual/en/latest/animation/armatures/posing/editing/copy_paste.html
- https://docs.blender.org/api/current/bpy.ops.poselib.html


## Wave 5 — Blender 5.2 NLA API findings

Wave 5 uses Blender native `AnimData.nla_tracks`, `NlaTrack.strips`, and `NlaStrip` properties. The implementation treats track mute/solo, strip Action linkage, frame start, scale, repeat, blend in/out, influence, blend type, extrapolation, and reverse playback as native NLA state. Rigify bone masks are represented as explicit bounded metadata on each strip because Blender's NLA strip RNA does not expose a general per-strip bone-mask collection; the executor validates that mask names are animator control bones and excludes `DEF-`, `MCH-`, and `ORG-` bones. Assembly baking uses Blender's native NLA bake operator with explicit frame range and output Action policy.

Official references: Blender Python API NlaStrip, NlaTrack, and AnimData pages retrieved during Wave 5 planning.
