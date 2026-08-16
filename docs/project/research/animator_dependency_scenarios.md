# Animator Dependency Scenarios untuk Arwaky

> **Status:** Architecture planning
>
> **Target runtime:** Blender 5.2 LTS
>
> **Target character:** MPFB2 character dengan generated native Rigify control rig
>
> **Dependency policy:** Native Blender atau provider open source yang dapat diaudit saja
>
> **Tanggal:** 16 Agustus 2026

## Tujuan

Dokumen ini memetakan dependency untuk seluruh kebutuhan animator yang dianggap penting: animasi tubuh, ekspresi wajah, gestur tangan dan jari, instruksi bahasa alami, retargeting, serta editing dan layering. Tujuannya bukan memilih satu plugin besar, melainkan membangun **Animator Provider** yang memiliki native core dan sejumlah optional open-source adapters.

> **Prinsip utama:** pengguna meminta hasil animasi; dependency harus mengikuti hasil tersebut, bukan sebaliknya.

MPFB2 tetap dibatasi untuk character generation. Rigify tetap menjadi provider rigging dan pose foundation. Animator Provider hanya mengoperasikan generated Rigify control rig, animation actions, pose assets, constraints, F-curves, dan NLA data.

## Model Dependency Umum

```text
User intent
    │
    ▼
External AI harness (Claude Code, agent, or user automation)
    │  chooses action sequence and supplies structured parameters
    ▼
Animator Provider AES
    ├── Native Rigify control mapper
    ├── Pose Asset service
    ├── Keyframe and Action service
    ├── Expression and shape-key service
    ├── Retargeting service
    ├── NLA and layer service
    └── Validation and visual-evidence service
    │
    ▼
Blender 5.2 animation data + generated Rigify rig
```

Setiap capability harus mengembalikan evidence yang dapat diperiksa: target armature, action, frame range, key count, affected control bones, constraints, dan hasil visual. Kegagalan dependency harus menghasilkan error yang menjelaskan dependency mana yang tidak tersedia.

## Dependency Classes

| Kelas | Contoh | Boleh menjadi core? | Penjelasan |
|---|---|---:|---|
| Native Blender | Pose Asset, Action, F-Curve, NLA, Graph Editor data, constraints, shape keys | **Ya** | Tersedia di Blender 5.2 dan tidak menambah dependency eksternal |
| Native Rigify | Generated control rig, FK/IK controls, face controls, rig UI metadata | **Ya** | Provider rigging yang sudah dipilih Arwaky |
| Arwaky internal | Canonical action schemas, control mapping, validation, evidence renderer | **Ya** | Diimplementasikan mengikuti AES |
| Open-source adapter | Blender Extensions Retarget, Mixaify, open-source Mixamo/FBX/BVH tools | **Optional** | Harus lolos audit source, license, maintenance, dan Blender 5.2 smoke test |
| External AI harness | Memilih dan mengurutkan canonical animation tools dari instruksi pengguna | **Di luar scope Arwaky** | Claude Code, agent, atau automation caller mengirim structured tool calls; Arwaky tidak melakukan planning |
| Proprietary plugin | Auto-Rig Pro, Rokoko closed workflow | **Tidak** | Tidak boleh dibuatkan provider adapter Arwaky |

## Scenario 1 — Animasi Tubuh

### User intent

Contoh perintah: “Buat karakter berjalan selama empat detik, lalu melompat pada frame 80 dan mendarat pada frame 110.”

### Dependency scenario

| Layer | Dependency | Required | Fallback |
|---|---|---:|---|
| Target | Generated Rigify control rig | Ya | Fail jika armature bukan generated Rigify atau mapping tidak dapat ditemukan |
| Motion source | Native keyframes, pose assets, procedural keyframe templates, atau open-source retarget input | Ya, salah satu | Gunakan procedural body motion sederhana |
| Rig controls | `root`, `torso`, `upper_arm_ik`, `hand_ik`, `foot_ik`, pole controls, FK/IK switches | Ya | Fail dengan daftar control yang hilang |
| Timeline | Scene frame range dan current frame | Ya | Gunakan frame range scene |
| Physics | Tidak diperlukan untuk basic walk/jump | Tidak | Gunakan keyframe arc dan planted-foot validation |
| Validation | Foot contact, hip arc, root trajectory, no broken constraints | Ya | Render diagnostic dan warning |

### Capability yang diperlukan

`import_animation_file`, `import_motion_capture`, `inspect_imported_action`, `link_action_to_armature`, `retarget_animation`, `bake_animation_action`, `edit_action_keyframes`, `set_root_motion`, `validate_foot_contact`, dan `inspect_animation_state`.

### Catatan implementasi

Wave pertama tidak perlu motion-capture plugin. Walk, run, idle, dan jump harus masuk melalui imported animation file, imported motion-capture action, imported pose asset, atau action yang sudah tersedia di library. Arwaky kemudian melakukan inspect, link/apply, retarget bila diperlukan, edit keyframes, dan bake. Procedural generation bukan dependency dasar Animator Provider.

## Scenario 2 — Ekspresi Wajah

### User intent

Contoh perintah: “Buat karakter tertawa selama dua detik, kemudian berubah menjadi menangis dengan transisi lambat.”

### Dependency scenario

| Layer | Dependency | Required | Fallback |
|---|---|---:|---|
| Face rig | Rigify face controls jika tersedia | Preferred | Gunakan shape keys MPFB2 yang tersedia |
| Shape keys | `key_blocks` pada mesh character | Conditional | Fail hanya jika intent meminta expression tetapi tidak ada target facial channel |
| Pose assets | Native Pose Library untuk expression poses | Preferred | Keyframe langsung pada face controls/shape keys |
| Timing | Actions, F-curves, interpolation, markers | Ya | Default timing berdasarkan frame range |
| Lip-sync | Phoneme/viseme mapping | Optional | Manual phoneme keys atau hold expression |
| Validation | Shape-key values, face control channels, visual render | Ya | Report affected channels dan render preview |

### Capability yang diperlukan

`inspect_face_controls`, `import_pose_asset`, `apply_pose_asset`, `set_shape_key_keyframe`, `edit_action_keyframes`, `import_viseme_animation`, dan `validate_face_animation`.

### Catatan implementasi

Ekspresi tidak boleh diasumsikan selalu berasal dari bone. MPFB2 character dapat memiliki shape keys, sedangkan Rigify face setup dapat menggunakan control bones, custom properties, atau kombinasi keduanya. Animator Provider harus lebih dahulu menginspeksi channel yang tersedia, kemudian memilih `bone_control`, `shape_key`, atau `hybrid_expression` strategy.

## Scenario 3 — Gestur Tangan dan Jari

### User intent

Contoh perintah: “Buat karakter melambaikan tangan kanan, lalu menunjuk ke depan sambil menggerakkan jari telunjuk.”

### Dependency scenario

| Layer | Dependency | Required | Fallback |
|---|---|---:|---|
| Hand rig | Rigify hand, palm, thumb, index, middle, ring, pinky controls | Ya untuk detailed gesture | Gunakan DEF/FK hand controls jika tersedia |
| Pose library | Native hand pose assets | Preferred | Keyframe per phalange |
| Side mapping | Left/right and finger naming map | Ya | Fail dengan unmapped bone list |
| Timing | Action/keyframe service | Ya | Default gesture timing |
| Mirror | Native transform mirror plus explicit Rigify mapping | Preferred | Manual opposite-side mapping |
| Validation | Finger chain continuity and no detached control | Ya | Close-up render evidence |

### Capability yang diperlukan

`inspect_hand_controls`, `import_pose_asset`, `apply_pose_asset`, `mirror_pose`, `edit_action_keyframes`, `add_action_strip`, dan `validate_finger_chain`.

### Catatan implementasi

Hand gesture harus menjadi capability kelas satu karena user membutuhkan detail jari. Control map tidak boleh hanya mencari prefix `DEF-`; sistem harus membedakan deformation bones dari animator controls. Evidence wajib menggunakan close-up tangan seperti evidence Rigify yang sudah dibuat.

## Scenario 4 — Instruksi Bahasa Alami

### User intent

Contoh perintah: “Buat orang berjalan santai selama empat detik, melihat ke kiri, lalu melompat sambil tersenyum.”

### Dependency scenario

| Layer | Dependency | Required | Fallback |
|---|---|---:|---|
| Caller | AI harness seperti Claude Code atau automation pengguna | Di luar scope Arwaky | Mengirim canonical MCP/CLI tool calls |
| Canonical actions | Action names, target types, timing, emotion/gesture parameters | Ya | Tolak action atau parameter yang tidak dikenal |
| Executor | Animator Provider Arwaky | Ya | Partial execution dengan report |
| Blender state | Scene, armature, action, frame range inspection | Ya | Fail sebelum mutation |
| Validation | Schema, dependency preflight, postcondition checks | Ya | Rollback atau no-op |
| LLM/model provider | Dimiliki dan dikelola oleh AI harness | Tidak | Pengguna tetap dapat memanggil MCP/CLI secara langsung |

### Capability yang diperlukan

`inspect_animation_state`, `import_animation_file`, `import_pose_asset`, `apply_pose_asset`, `retarget_animation`, `add_action_strip`, `edit_action_keyframes`, dan `validate_animation_result`. Arwaky tidak menyediakan parser atau planner natural-language.

### Boundary keamanan

Natural-language interpretation dan planning adalah tanggung jawab AI harness seperti Claude Code, bukan Blender Arwaky. Arwaky hanya menerima canonical MCP/CLI calls dan mengubah scene Blender secara tervalidasi.

```text
natural language
  → AI harness planning (di luar Arwaky)
  → canonical MCP/CLI tool calls
  → Arwaky validation
  → Blender mutation
  → postcondition validation
```

Jika AI harness tidak tersedia, pengguna tetap dapat menjalankan tools yang sama secara langsung melalui MCP atau CLI. Tidak ada LLM runtime yang perlu dipasang di Blender atau dijadikan dependency Animator Provider.

## Scenario 5 — Retargeting

### User intent

Contoh perintah: “Ambil animasi Mixamo ini dan terapkan ke karakter MPFB2 Rigify, lalu bake ke action baru.”

### Dependency scenario

| Layer | Dependency | Required | Fallback |
|---|---|---:|---|
| Input | FBX, BVH, action, atau source armature | Ya | Fail dengan format yang didukung |
| Source mapping | Explicit source bone map | Ya | Preset open-source mapping |
| Target mapping | Rigify control map | Ya | Generate mapping candidate untuk approval |
| Rest pose | Source/target rest-pose normalization | Ya | Stop jika pose mismatch tidak dapat diperbaiki |
| Scale | Scale policy dan root offset | Ya | Manual scale override |
| Solver | Native constraints/FK bake atau audited open-source adapter | Ya | Native FK transfer |
| IK policy | FK-first, optional IK conversion at keyframes | Conditional | Simpan FK action jika IK conversion tidak aman |
| Bake | Action bake dan cleanup constraints | Ya | Keep constraints with warning |
| Validation | Foot/hand contact, root motion, rotation continuity | Ya | Reject bad bake |

### Open-source options

Blender Extensions **Retarget** adalah kandidat open-source adapter pertama karena listing resminya menyebut GPL-3.0-or-later dan Blender 5.0+.[1] **Mixaify** adalah kandidat GPL-3.0 yang lebih sempit untuk Mixamo → Rigify dan secara eksplisit mendokumentasikan keterbatasan default bone names serta FK/IK conversion.[2]

Rokoko dan Auto-Rig Pro tidak masuk dependency scenario Arwaky karena keduanya berada di luar open-source-only policy. Arwaky tidak membuat adapter untuk keduanya.

### Capability yang diperlukan

`inspect_retarget_source`, `build_bone_mapping`, `validate_rest_pose`, `preview_retarget_plan`, `retarget_animation`, `bake_retarget_action`, `apply_root_motion`, dan `validate_retarget_result`.

## Scenario 6 — Editing dan Layering Animasi

### User intent

Contoh perintah: “Pertahankan walk cycle, tambahkan lambaian tangan pada frame 40–80, dan blend ekspresi tersenyum tanpa mengubah kaki.”

### Dependency scenario

| Layer | Dependency | Required | Fallback |
|---|---|---:|---|
| Base action | Blender Action dan frame range | Ya | Create new action |
| Layer model | Native NLA strips/tracks atau additive F-curves | Preferred | Duplicate action dengan channel filtering |
| Bone mask | Rigify control selection set | Ya | Explicit bone list |
| Blend | F-Curve/NLA blend and extrapolation | Ya | Bake combined action |
| Action manager | Native actions, slots, asset metadata | Ya | Name-based action listing |
| Undo safety | Transaction boundary and preflight snapshot | Ya | No mutation if preflight fails |
| Validation | Channel diff and visual preview | Ya | Report channels changed |

### Capability yang diperlukan

`list_nla_tracks`, `add_action_strip`, `set_animation_mask`, `blend_action_strips`, `mute_action_strip`, `bake_animation_action`, `compare_action_channels`, dan `validate_layer_result`.

Animation Layers for Blender dapat menjadi reference open-source untuk workflow NLA, tetapi tidak boleh menjadi dependency sebelum maintenance dan Blender 5.2 runtime compatibility diverifikasi.[3] Core Arwaky tetap harus memakai native NLA dan Action APIs.

## Dependency Scenarios menurut Kesiapan

| Capability group | Native Blender 5.2 | Native Rigify | Open-source adapter | LLM planner | Prioritas |
|---|---:|---:|---:|---:|---|
| Body motion templates | **Ya** | **Ya** | Tidak wajib | Tidak wajib | P0 |
| Face expressions | **Ya** | Conditional | Tidak wajib | Tidak wajib | P0 |
| Hand/finger gestures | **Ya** | **Ya** | Tidak wajib | Tidak wajib | P0 |
| Canonical tool execution dari AI harness | **Ya** | Ya | Tidak wajib | **External caller** | P1 |
| Retargeting | Partial native | **Ya** | **Ya, optional** | Optional | P1 |
| Layered editing | **Ya, NLA/Action** | Ya | Tidak wajib | Optional | P1 |
| Motion capture | Partial import/bake | Target mapping | Open-source only | Optional | P2 |
| Lip-sync | Shape-key/action APIs | Conditional | Open-source input optional | Optional | P2 |

## Fallback Design

Setiap capability harus memiliki fallback yang tetap menghasilkan output yang dapat diedit:

| Failure | Fallback |
|---|---|
| Rigify face controls tidak tersedia | Gunakan shape keys; jika tidak ada, laporkan channel yang hilang |
| Pose asset library tidak tersedia | Buat action satu-frame lokal |
| Retarget adapter tidak terpasang | Jalankan native FK mapping atau minta source mapping eksplisit |
| LLM tidak tersedia | Jalankan canonical action melalui MCP/CLI |
| NLA workflow gagal | Bake channel-filtered action baru |
| Bone map ambigu | Tampilkan preview mapping dan minta approval, jangan menebak diam-diam |
| IK conversion menghasilkan jitter | Simpan FK result dan laporkan conversion tidak dilakukan |
| Validation gagal | Jangan publish action sebagai final; simpan diagnostic evidence |

## Dependency Resolution Flow

```text
1. Inspect scene and generated Rigify rig
2. Inspect available face/hand/IK/FK/action channels
3. Parse user intent into structured plan
4. Resolve only native/open-source dependencies
5. Preview affected controls, frame range, and output action
6. Ask for approval when mapping is ambiguous or mutation is destructive
7. Execute canonical Animator actions
8. Bake or preserve editable layers
9. Validate keyframes, channels, contacts, and visual result
10. Return action/evidence summary
```

## AES Module Boundary

Modul `animator` di `modules/` hanya berisi taxonomy, contract, utility, capability, agent, surface, dan root yang diperlukan untuk Animator Provider. Integrasi plugin open source berada di `plugin/` sesuai boundary plugin project, bukan di dalam taxonomy internal animator.

Contoh struktur:

```text
modules/animator/
├── FRD.md
├── src/
│   ├── agent_animator_orchestrator.py
│   ├── capabilities_animation_intent.py
│   ├── capabilities_body_motion.py
│   ├── capabilities_face_expression.py
│   ├── capabilities_hand_gesture.py
│   ├── capabilities_retargeting.py
│   ├── capabilities_animation_layers.py
│   └── root_animator_container.py
└── tests/

plugin/animator-retarget/
├── plugin_manifest.yaml
├── plugin_entry.py
├── plugin_operations.py
└── test_plugin_animator_retarget.py
```

Naming and lint policy tetap mengikuti AES: `modules/` wajib patuh lint dan naming, sedangkan folder `plugin/` mengikuti kebutuhan adapter dan dikecualikan dari lint scope yang telah ditetapkan proyek.

## Roadmap Keseluruhan

### Wave 1 — Native animator inspection and keying

Bangun `inspect_animation_state`, `insert_rigify_keyframe`, `set_animation_frame`, `list_animation_actions`, dan `validate_animation_state`. Wave ini membuktikan bahwa Arwaky dapat membaca dan menulis animation data tanpa plugin eksternal.

### Wave 2 — Pose and gesture library

Bangun `import_pose_asset`, `apply_pose_asset`, `mirror_pose`, `edit_action_keyframes`, `set_shape_key_keyframe`, dan `validate_finger_chain`. Gunakan native Pose Library dan evidence close-up wajah/tangan.

### Wave 3 — Body motion primitives

Bangun import dan editing workflow untuk walk, run, idle, jump, look-at, wave, point, sit, stand, dan blend operations. Sumbernya berupa imported motion, imported pose assets, atau existing Actions; Arwaky menghubungkan, mengedit, meretarget, dan membake data tersebut.

### Wave 4 — Canonical Tool Surface for AI Harnesses

Bangun MCP/CLI surface dan schema canonical untuk seluruh animation tools. Claude Code atau AI harness lain dapat memilih dan mengurutkan tools tersebut. Arwaky hanya menyediakan validation, execution, result reporting, dan postcondition checks; Arwaky tidak membangun planner atau natural-language interpreter.

### Wave 5 — Native action layering

Bangun NLA/action manager, masks, additive layers, bake, channel diff, and rollback. Open-source Animation Layers hanya menjadi reference, bukan prerequisite.

### Wave 6 — Open-source retargeting

Audit dan smoke-test Blender Extensions Retarget dan Mixaify pada Blender 5.2 dengan native MPFB2 Rigify evidence. Hanya adapter yang lolos source/license/runtime gate yang boleh masuk plugin layer.

### Wave 7 — Production validation

Tambahkan motion quality metrics, foot/hand contact checks, face channel validation, action export, visual evidence, and regression fixtures.

## Keputusan

Semua enam kebutuhan penting dan akan didukung, tetapi dependency-nya tidak sama. Body motion, expressions, hand gestures, editing/layering, dan sebagian natural-language execution dapat dibangun di native core. Retargeting adalah satu-satunya area yang layak memakai optional open-source adapters setelah audit. Tidak ada provider proprietary yang akan diadaptasi.

## References

[1]: https://extensions.blender.org/add-ons/retarget/ "Retarget — Blender Extensions"
[2]: https://github.com/netherby/mixaify-retarget "Mixaify — Mixamo to Rigify animation retargeter"
[3]: https://github.com/evilmushroom/Animation-Layers-for-Blender "Animation Layers for Blender"
[4]: https://docs.blender.org/manual/en/latest/animation/armatures/posing/editing/pose_library.html "Pose Library — Blender 5.2 LTS Manual"
[5]: https://github.com/blender/blender-addons/blob/main/rigify/rig_ui_template.py "Rigify source mirror — Blender add-ons"

## Related Research

- `docs/project/research/rigify_animator_research.md`
- `docs/project/research/rigify_animator_research_notes.md`
