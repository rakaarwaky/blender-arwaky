# Native Animation Core Cleanup Report

## Summary

The animation core was reduced to native Blender animation primitives. Rigify-specific animation, facial and hand control workflows, motion-capture retargeting, root-motion policy, and procedural animation helpers were removed from the core public surface or deferred to external providers/plugins.

## Branch

The work was executed on `chore/native-animation-core-cleanup`.

## Retained native capabilities

The canonical animation catalog now contains 21 native actions covering animation state, object keyframes, generic pose-bone keyframes, timeline range, keyframe listing, Action listing/linking, FBX/BVH import, pose assets, shape-key keyframes, and NLA track/strip/layer/mask/bake/validation operations.

The new `insert_pose_bone_keyframe` action is intentionally generic. It accepts an armature name, pose-bone name, frame, and native transform data path. It has no Rigify naming assumptions, control mapping, FK/IK policy, or character semantics.

## Removed or deferred capabilities

The core no longer exposes Rigify control inspection, Rigify pose-buffer actions, Rigify pose keyframing, face-channel inspection, hand-control inspection, Rigify FK/IK switching, facial-control animation, motion-capture import as a separate custom workflow, bone mapping, rest-pose validation, retargeting, root-motion policy, retarget baking, or custom animation-result validation. The retarget executor and its native-retarget smoke script were removed from the animation core. The Rigify face/hand smoke script was removed because it tested a provider-specific animation surface.

These workflows remain eligible for future external plugins/providers. Their removal from core is a boundary decision, not a claim that the workflows are impossible in Blender.

## Source changes

| Area | Change |
|---|---|
| Canonical action catalog | Removed provider-specific and advanced animation actions; added generic pose-bone keyframe action |
| Animation executor | Removed custom orphan methods and added native pose-bone keyframe execution |
| Animation orchestrator | Exposed the generic pose-bone keyframe operation |
| Blender server | Removed custom handler registration and added generic pose-bone keyframe handler |
| Shared value objects | Removed unused Rigify, retargeting, root-motion, and face-control VOs; retained native Action, import, pose asset, shape-key, and NLA VOs |
| Smoke tests | Converted Wave 1 and Wave 2 smoke coverage to native operations; removed provider-specific animation smoke coverage |
| Documentation | Rewrote the animation FRD and dependency scenario; marked Rigify animator research as historical/superseded |
| CLI tests | Updated canonical action count from 122 to 108 exposed CLI actions after cleanup |

## Verification

| Gate | Result |
|---|---:|
| Full pytest suite | **1,160 passed** |
| Coverage | **62.07%**; repository threshold is 60% |
| Ruff check | **Passed** |
| Ruff format check | **Passed** |
| Python compile check | **Passed** |
| `git diff --check` | **Passed** |
| lint-arwaky-cli v3.6.1 scan | **0 violations** |

## Deliberate boundary

Arwaky core now provides the native animation building blocks. An AI harness may compose these operations, and external plugins may provide complex character-animation workflows. The core does not provide a monolithic walk-cycle action and does not require the AI agent to write Blender Python for native primitives.
