# Animator Dependency Scenarios untuk Arwaky

> **Status:** Scope disederhanakan dan disetujui untuk native Blender animation only.
>
> **Target runtime:** Blender 5.2 LTS.
>
> **Tanggal pembaruan:** 17 Agustus 2026.

## Keputusan arsitektur

Arwaky core hanya menyediakan primitive animasi native Blender yang dapat dikendalikan AI agent melalui MCP atau CLI. Core tidak membuat procedural walk cycle, tidak melakukan natural-language animation planning, tidak memetakan Rigify controls secara semantic, dan tidak melakukan motion-capture retargeting.

> AI harness memilih dan mengurutkan primitive native. Plugin/provider eksternal menangani workflow kompleks apabila dipasang.

MPFB2 dan Rigify tetap berada di area plugin/provider. Core animation tidak bergantung pada nama bone, custom property, parent-chain, atau workflow provider tertentu.

## Native core capability

| Capability group | Native operation |
|---|---|
| Timeline | Scene frame start/end/current |
| Action | List, inspect, link, dan validate Action |
| Keyframe | Object transform keyframe dan F-curve inspection |
| Pose | Native pose asset create/apply/blend |
| Shape key | Native shape-key keyframe |
| Import | Native FBX/BVH import |
| NLA | Track, strip, blend, layer, mask, repeat, reverse, remove |
| Bake | Native NLA assembly bake |
| Validation | Action/NLA ownership, frame range, key count, and structure |

Core menerima structured parameters dan mengembalikan hasil yang dapat diaudit. Core tidak mengambil keputusan artistik seperti pose contact, stride, foot-lock, ekspresi, atau gait.

## External provider boundary

| Workflow | Owner sekarang |
|---|---|
| Rigify semantic controls dan FK/IK | External Rigify provider/plugin |
| MPFB2 character creation | MPFB2 provider/plugin |
| Motion capture mapping dan retargeting | External open-source provider/plugin |
| Procedural walk/run/jump | External provider atau AI harness yang menyusun native calls |
| Facial performance system | External provider/plugin |
| Natural-language planning | External AI harness |

## Recommended agent flow

AI agent dapat melakukan workflow berikut tanpa menulis Python Blender:

```text
inspect animation state
→ import or select existing Action
→ link Action to armature/object
→ apply or blend native pose asset
→ insert native object/shape-key keyframes
→ set timeline
→ assemble NLA tracks and strips
→ bake if required
→ validate Action/NLA result
```

Jika agent ingin membuat animasi karakter kompleks, agent menggunakan plugin/provider yang mengekspos capability tambahan. Core tidak berpura-pura memiliki kemampuan tersebut.

## Deferred capability policy

Retargeting, Rigify control mapping, semantic character pose, face/hand control systems, procedural gait, and custom root-motion policies tidak dihapus dari visi produk. Semuanya dipindahkan ke backlog provider/plugin dan tidak boleh dimasukkan kembali ke canonical core catalog tanpa keputusan scope baru.

## AES boundary

`modules/animation` hanya berisi native animation executor, NLA executor, orchestrator, canonical action schema, value objects, dan tests. Provider-specific code berada di `plugin/`. AI planning berada di luar Arwaky. Blender-side server hanya mendaftarkan canonical native commands yang benar-benar tersedia.
