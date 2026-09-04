# Native Blender + Rigify Animation Action Catalog

> **Scope:** canonical tools untuk Blender 5.2 LTS dan generated Rigify control rig.
>
> **Out of scope:** natural-language planning, plugin proprietary, dan generator high-level seperti `create-walk-cycle`.
>
> **Caller:** Claude Code, AI harness, MCP client, CLI user, atau automation lain.
>
> **Executor:** Blender Arwaky Animator Provider.

## Boundary

AI harness menentukan bahwa pengguna menginginkan karakter berjalan, melompat, tertawa, atau menangis. AI harness kemudian memilih dan mengurutkan canonical actions di bawah. Arwaky tidak memahami natural language dan tidak menciptakan motion dari nama perintah. Arwaky mengimpor, menginspeksi, menghubungkan, menerapkan, meretarget, mengedit, membake, dan memvalidasi animation data.

```text
AI harness plan
  → canonical MCP/CLI actions
  → Animator Provider Arwaky
  → Blender 5.2 animation data + generated Rigify controls
```

## Catalog Summary

| No. | Category | CLI action | Native/Rigify responsibility | Priority |
|---:|---|---|---|---|
| 1 | Inspection | `inspect-animation-state` | Inspect frame, action, curves, NLA, and selection | P0 |
| 2 | Inspection | `inspect-armature-animation` | Inspect armature animation data and slots | P0 |
| 3 | Inspection | `list-animation-actions` | List actions available for an armature | P0 |
| 4 | Inspection | `inspect-action-curves` | Inspect F-curves, channels, keyframes, and ranges | P0 |
| 5 | Inspection | `inspect-rigify-controls` | Discover generated Rigify controls and FK/IK metadata | P0 |
| 6 | Inspection | `inspect-face-animation-channels` | Discover face controls, custom properties, and shape keys | P0 |
| 7 | Inspection | `inspect-hand-animation-controls` | Discover hand, finger, and side-mapped controls | P0 |
| 8 | Import | `import-animation-file` | Import an animation-bearing file using Blender importer | P0 |
| 9 | Import | `import-motion-capture` | Import BVH/FBX motion-capture source through Blender import path | P1 |
| 10 | Import | `import-pose-asset` | Load a pose asset from Asset Library or `.asset.blend` | P0 |
| 11 | Import | `link-action-to-armature` | Link or assign an imported Action to the target armature | P0 |
| 12 | Pose | `apply-pose-asset` | Apply or blend an imported pose asset to Rigify | P0 |
| 13 | Pose | `mirror-pose` | Mirror selected pose channels using Rigify side mapping | P1 |
| 14 | Pose | `set-rigify-fk-ik-mode` | Set or inspect Rigify FK/IK mode properties | P1 |
| 15 | Keying | `set-animation-frame` | Set current scene frame | P0 |
| 16 | Keying | `set-animation-range` | Set or validate scene/action frame range | P0 |
| 17 | Keying | `edit-action-keyframes` | Insert, update, move, or delete selected keyframes | P0 |
| 18 | Keying | `insert-pose-keyframe` | Insert keyframes for selected Rigify controls/channels | P0 |
| 19 | Keying | `clear-action-keyframes` | Remove keys by channel, bone set, or frame range | P1 |
| 20 | Facial | `set-shape-key-keyframe` | Keyframe MPFB2 facial shape keys | P0 |
| 21 | Facial | `edit-face-control-animation` | Edit Rigify face controls/custom-property animation | P1 |
| 22 | Retarget | `build-bone-mapping` | Build explicit source-to-target map | P1 |
| 23 | Retarget | `validate-rest-pose` | Validate or report source/target rest-pose compatibility | P1 |
| 24 | Retarget | `retarget-animation` | Transfer source Action to target Rigify controls | P1 |
| 25 | Retarget | `set-root-motion` | Configure root translation and root-motion policy | P1 |
| 26 | Retarget | `bake-retarget-action` | Bake retargeted constrained result to an editable Action | P1 |
| 27 | NLA | `list-nla-tracks` | Inspect NLA tracks, strips, blend, and extrapolation | P1 |
| 28 | NLA | `add-action-strip` | Add an Action to an NLA track | P1 |
| 29 | NLA | `set-animation-mask` | Restrict an Action/strip to selected Rigify control channels | P1 |
| 30 | NLA | `blend-action-strips` | Configure strip blend, influence, timing, and extrapolation | P1 |
| 31 | NLA | `mute-action-strip` | Mute or unmute a strip without deleting its data | P1 |
| 32 | NLA | `bake-animation-action` | Bake constraints/NLA result to an Action | P1 |
| 33 | Validation | `compare-action-channels` | Compare source/result channel and keyframe changes | P1 |
| 34 | Validation | `validate-animation-result` | Validate postconditions after any animation mutation | P0 |
| 35 | Validation | `validate-rigify-deformation` | Confirm mesh deformation follows target animation | P0 |
| 36 | Validation | `validate-foot-contact` | Check planted foot/root contact over a frame range | P1 |
| 37 | Validation | `validate-face-animation` | Check facial channels and visible expression response | P1 |
| 38 | Validation | `validate-finger-animation` | Check finger chain continuity and control alignment | P1 |
| 39 | Evidence | `render-animation-preview` | Render a diagnostic preview for visual verification | P1 |

## Action Contracts

### Import Animation

`import-animation-file` accepts a source file path, importer format/options, whether to import armature or animation only, scale policy, rest-pose policy, and source object selection. It returns imported objects, Actions, armatures, warnings, and the source-to-data mapping. It must not assume that an imported Action is automatically linked; the caller should use `link-action-to-armature` after inspection. Blender's FBX documentation explicitly warns that imported animations/actions may require manual reassignment.[1]

`import-motion-capture` is a semantic Arwaky action over Blender's import path for motion-capture data. It does not claim a separate Blender operator named `import-motion-capture`; the implementation maps the request to the supported importer, such as BVH or FBX, and reports the actual importer used.

### Import and Apply Pose

`import-pose-asset` accepts an Asset Library path, `.asset.blend` path, asset identifier, target armature, selected control policy, and blend factor. `apply-pose-asset` accepts the resolved pose asset, target Rigify armature, bone selection policy, blend factor, and target frame. Blender's Pose Library is based on Asset Browser and stores pose assets as one-frame Actions.[2]

### Retarget

`build-bone-mapping` accepts source armature, target generated Rigify armature, explicit mapping overrides, naming preset, side mapping, and unmapped-bone policy. `validate-rest-pose` returns pose mismatch, scale mismatch, orientation warnings, and approval requirements. `retarget-animation` accepts the approved mapping, source Action, target armature, FK/IK policy, scale policy, frame range, and output Action name. `bake-retarget-action` creates an editable target Action and records which constraints or temporary objects were removed.

### Keyframe and Action Editing

`edit-action-keyframes` accepts Action, frame range, channel filters, transform channel policy, interpolation policy, and operation (`insert`, `move`, `delete`, `scale`, or `replace`). `insert-pose-keyframe` is a focused operation for selected Rigify control bones and must never silently key all DEF bones. `set-shape-key-keyframe` targets MPFB2 facial shape keys when the mesh exposes them.

### NLA and Layering

`add-action-strip` accepts Action, NLA track, frame start, scale, repeat, blend-in, blend-out, extrapolation, and influence. `set-animation-mask` accepts selected Rigify control bones or channel groups. `bake-animation-action` accepts frame range, source layers/constraints, channel policy, and output Action policy. These are action-data operations, not high-level “make a walk cycle” generators.

### Validation and Evidence

Every mutating action should optionally run `validate-animation-result`. The result must include target armature, target Action, affected bones/shape keys, frame range, key count before/after, warnings, and whether a diagnostic render was produced. For Rigify character work, visual evidence should include full-body, face, and hand close-ups when the action affects those areas.

## Dependency Matrix

| Action group | Blender 5.2 native data | Generated Rigify | MPFB2 | External plugin |
|---|---:|---:|---:|---:|
| Inspection | Required | Required for control discovery | Not required after character exists | None |
| Import animation | Required | Target optional at import | Not required | None |
| Import/apply pose | Required | Required for Rigify pose mapping | Not required | None |
| Facial animation | Required | Conditional | Shape keys may be provided by MPFB2 | None |
| Hand/finger animation | Required | Required | Not required after rig binding | None |
| Retarget | Required | Required as target | Not required | Optional open-source only |
| NLA/layering | Required | Recommended for control masks | Not required | None |
| Validation/evidence | Required | Required for Rigify deformation checks | Optional mesh source | None |

## Implementation Order

### P0 — Native inspection and import

Implement `inspect-animation-state`, `inspect-armature-animation`, `list-animation-actions`, `inspect-action-curves`, `inspect-rigify-controls`, `import-animation-file`, `import-pose-asset`, `link-action-to-armature`, `apply-pose-asset`, `set-animation-frame`, `set-animation-range`, `edit-action-keyframes`, and `validate-animation-result`.

### P1 — Rigify pose, face, fingers, retarget, and NLA

Implement `inspect-face-animation-channels`, `inspect-hand-animation-controls`, `mirror-pose`, `set-rigify-fk-ik-mode`, `set-shape-key-keyframe`, `edit-face-control-animation`, `import-motion-capture`, `build-bone-mapping`, `validate-rest-pose`, `retarget-animation`, `set-root-motion`, `bake-retarget-action`, and NLA operations.

### P1 — Visual and deformation evidence

Implement `validate-rigify-deformation`, `validate-foot-contact`, `validate-face-animation`, `validate-finger-animation`, `compare-action-channels`, and `render-animation-preview`.

### Later — Optional open-source adapters

Only after the native catalog is stable should Arwaky evaluate an open-source adapter such as Blender Extensions Retarget or Mixaify. No proprietary provider adapter is allowed.

## Explicit Non-Actions

The following are intentionally **not** canonical Blender actions:

```text
create-walk-cycle
create-run-cycle
create-jump-action
create-expression-action
animate-wave-gesture
parse-animation-intent
plan-animation-sequence
```

The AI harness may use these phrases in its private reasoning, but it must translate them into real canonical operations such as import, apply, retarget, edit, bake, and validate before calling Arwaky.

## References

[1]: https://docs.blender.org/manual/en/latest/files/import_export/fbx_legacy.html "FBX (Legacy) — Blender 5.2 LTS Manual"
[2]: https://docs.blender.org/manual/en/latest/animation/armatures/posing/editing/pose_library.html "Pose Library — Blender 5.2 LTS Manual"
[3]: https://github.com/blender/blender-addons/blob/main/rigify/rig_ui_template.py "Rigify source mirror — Blender add-ons"
