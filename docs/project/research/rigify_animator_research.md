# Research: Animator Tools untuk Karakter Native MPFB2–Rigify

> **Status:** Research selesai — rekomendasi arsitektur, belum implementasi.
>
> **Target:** Blender 5.2 LTS, karakter MPFB2, generated Rigify control rig.
>
> **Tanggal:** 16 Agustus 2026
>
> **Penulis:** Manus AI

## Kesimpulan Eksekutif

Ada beberapa plugin yang dapat mempermudah animasi karakter Rigify, tetapi tidak ada satu plugin yang sebaiknya langsung dijadikan dependency inti Arwaky. Untuk proyek ini, pilihan paling aman adalah membangun **Animator Provider native Blender 5.2** di atas animation data API, Pose Assets, Action, NLA, Graph Editor, dan generated Rigify control bones. Plugin eksternal cukup ditempatkan sebagai **optional adapter**.

Kandidat paling menarik untuk workflow retargeting open source saat ini adalah add-on **Retarget** yang terdistribusi melalui Blender Extensions. Listing resminya menyebut kompatibilitas Blender 5.0+, lisensi GPL-3.0-or-later, preset Mixamo/Unreal/VRoid/MMD/Daz, binding ke Rigify, baking action, root motion, mirror support, dan Action Manager.[1] Namun, kompatibilitas spesifik dengan native MPFB2 Rigify pada Blender 5.2 tetap harus dibuktikan melalui smoke test sebelum dipakai.

Untuk workflow animator sehari-hari, fondasi terbaik bukan plugin pihak ketiga melainkan **Pose Library native Blender 5.2**. Pose asset adalah action satu-frame yang dapat disimpan dalam `.asset.blend`, diterapkan pada armature, dan diblend secara interaktif. Ini cocok untuk hand pose, facial pose, expression, dan full-body pose Rigify.[2]

## Jawaban Langsung

| Pertanyaan | Jawaban |
|---|---|
| Apakah ada plugin untuk membuat animasi karakter Rigify lebih mudah? | Ada. Retarget, Mixaify, Rokoko, Auto-Rig Pro, AnimAide, dan Animation Layers menawarkan sebagian workflow yang relevan. |
| Apakah salah satu harus menjadi dependency inti Arwaky? | Tidak. Dependency inti sebaiknya native Blender 5.2 agar tidak bergantung pada maintenance, lisensi, atau API plugin lain. |
| Plugin paling relevan untuk retargeting? | **Retarget** dari Blender Extensions adalah kandidat terbaik untuk dievaluasi lebih lanjut; **Mixaify** adalah referensi kecil GPL-3.0 yang fokus pada Mixamo → Rigify. |
| Plugin paling relevan untuk pose animator? | **Pose Library native Blender 5.2**, bukan plugin eksternal. |
| Plugin paling lengkap sebagai benchmark UX? | **Auto-Rig Pro**, tetapi bersifat komersial/proprietary sehingga hanya layak menjadi benchmark, bukan dependency. |
| Apakah sudah siap diimplementasikan sekarang? | Belum langsung. Prioritas pertama adalah native Animator Provider dan smoke test Rigify control/action workflow. |

## Kriteria Evaluasi

Kandidat dievaluasi berdasarkan enam kriteria: dukungan Blender 5.x atau 5.2, kemampuan bekerja dengan generated Rigify control rig, kemampuan keyframe/pose/retargeting, lisensi dan batas redistribusi, status maintenance, serta kesesuaian dengan AES adapter boundary. Klaim kompatibilitas hanya dianggap valid jika berasal dari halaman resmi atau repository sumber yang dibuka dan dibaca, bukan dari snippet pencarian.

## Perbandingan Kandidat

| Kandidat | Fokus | Rigify | Blender 5.x | Lisensi/distribusi | Status maintenance yang terlihat | Posisi untuk Arwaky |
|---|---|---:|---:|---|---|---|
| Blender Pose Library | Pose asset, apply/blend pose | Ya, karena bekerja pada armature | **Ya, native 5.2** | Native Blender; tidak ada dependency eksternal | Bagian dari workflow Blender 5.2 | **Fondasi utama** |
| Blender Extensions Retarget | Retarget, Rigify conversion, action tools, animation utilities | **Ya** | **Ya, listing menyebut 5.0+** | **GPL-3.0-or-later** | Listing aktif; versi 5.1.7 terlihat pada saat research | **Optional adapter / kandidat utama retargeting** |
| Mixaify | Mixamo → Rigify retargeting | **Ya** | **Ya, README menyebut Blender 5** | **GPL-3.0** | Repository kecil; 6 commits, 1 branch, tanpa release terlihat | Reference atau optional adapter sempit |
| Rokoko Blender plugin | Body/face mocap retargeting | Bisa ke custom target, mapping perlu diuji untuk Rigify | Belum dapat dipastikan spesifik 5.2 dari artikel | **Proprietary/vendor integration** | Dokumentasi resmi tersedia | **Out of scope — no adapter** |
| AnimAide | Curve tools, animation offset, key manager | Tidak Rigify-specific, tetapi bekerja pada F-curves/bones | Tidak aman diasumsikan 5.2; repo menyatakan development tidak lagi aktif | **Lisensi tidak diverifikasi pada repository** | **Tidak aktif menurut README** | **Reference only — no adapter** |
| Animation Layers for Blender | Layered animation berbasis NLA | Secara prinsip bisa untuk action Rigify | Belum terverifikasi 5.2 | **GPL-3.0** | Repository kecil; 3 commits dan tanpa release terlihat | Reference only; no adapter until validated |
| Auto-Rig Pro | Rigging, retargeting, IK, export | Remap mendukung Rigify/custom rigs | Versi harus mengikuti produk | **Komersial/proprietary** | Product page aktif dan mendukung paid updates/support | **Rejected — no provider adapter** |
| Rigify AnimBox | Helper animasi khusus Rigify | Ya | Referensi lama; kompatibilitas modern belum terbukti | Distribusi komunitas | Referensi yang ditemukan berorientasi Blender 2.8/2.9 | Tidak direkomendasikan sebagai dependency |

### Dasar Bukti Utama

Blender 5.2 mendokumentasikan Pose Library sebagai sistem berbasis Asset Browser. Pose asset berisi tepat satu frame animation data; pengguna dapat membuatnya dari bone yang dipilih, menyimpannya dalam library, menerapkannya, atau membblendnya ke pose aktif.[2]

Retarget dari Blender Extensions mencantumkan preset berbagai skeleton, binding ke active armature/metarig, mirror support, conversion ke Rigify, baking constrained action, root motion, dan Action Manager. Listing tersebut menyebut kompatibilitas Blender 5.0+ dan lisensi GPL-3.0-or-later.[1] Karena source dan lisensinya terbuka, tool ini tetap menjadi kandidat optional adapter setelah smoke test Blender 5.2; source code tidak akan disalin ke Arwaky.

Mixaify mendokumentasikan workflow Mixamo FBX ke Rigify FK, baking FK, serta keterbatasan bahwa mapping mengasumsikan nama bone default dan tidak menghasilkan kecocokan pose sempurna karena perbedaan joint positions. README juga memperingatkan bahwa konversi FK ke IK setiap frame dapat menghasilkan jitter dan rotasi yang buruk.[3]

Rokoko mendokumentasikan proses memilih source armature dan target armature, membangun bone list, memperbaiki mapping, menyamakan pose, mengatur scale, lalu menekan Retarget Animation. Fitur retargeting pada artikel tersebut dinyatakan tidak memerlukan akun premium.[4] Namun karena ini adalah vendor plugin/integration proprietary, Rokoko dicatat sebagai workflow eksternal saja dan tidak masuk scope provider adapter Arwaky.

AnimAide menyediakan curveTools, animOffset, dan KeyManager, tetapi halaman repository menyatakan development tidak lagi aktif dan project sedang menuju modul animasi yang lebih robust. Karena itu, fitur-fitur tersebut lebih tepat dijadikan inspirasi API daripada dependency.[5]

Auto-Rig Pro mendukung remap antar armature dengan nama/orientasi bone berbeda, IK feet/hands, offset proporsi, dan export game engine. Namun halaman resminya menampilkan product variants berbayar, sehingga Arwaky secara eksplisit tidak akan membuat provider adapter, runtime integration, atau source dependency untuk Auto-Rig Pro.[6]

## Rekomendasi Arsitektur AES

Natural-language planning berada di luar boundary Arwaky. Claude Code atau AI harness lain bertugas memahami instruksi pengguna, memilih canonical tools, mengisi parameter, dan menentukan urutan eksekusi. Arwaky hanya menyediakan MCP/CLI tools yang dapat dieksekusi secara langsung maupun dipanggil sebagai hasil planning eksternal.

```text
user language → AI harness planning → Arwaky MCP/CLI tools → Blender/Rigify mutation
```

Tidak ada `natural-language provider` atau LLM runtime yang perlu dibuat di dalam Blender Arwaky.

Arwaky sebaiknya menambahkan provider baru di luar boundary MPFB2:

```text
MPFB2 plugin
  └── character generation only

Rigify plugin
  └── metarig, generated rig, binding, pose bone transforms

Animator provider
  ├── native Blender 5.2 animation data
  ├── Rigify control-bone mapping
  ├── pose assets and action management
  ├── keyframe and timeline operations
  ├── constraints, bake, and NLA operations
  └── optional retarget adapters
```

Animator Provider tidak boleh mengubah batas MPFB2 menjadi provider rigging. MPFB2 tetap hanya menghasilkan karakter dan native Rigify tetap menangani rigging. Animator Provider menerima nama armature hasil generated Rigify, menemukan control bones yang valid, lalu bekerja pada action dan pose data.

Adapter eksternal harus bersifat opsional:

```text
native animator core
       │
       ├── pose asset adapter
       ├── action/NLA adapter
       ├── Mixamo/Mixaify adapter
       └── Blender Extensions Retarget adapter
```

Arwaky tidak boleh menyalin source code add-on mana pun ke dalam repository. Hanya native Blender atau provider open source yang source, lisensi, dan maintenance-nya dapat diaudit yang boleh dipertimbangkan sebagai adapter. Auto-Rig Pro dan Rokoko tidak boleh memiliki provider adapter. Untuk provider open source, integrasi tetap menggunakan adapter boundary, runtime detection, license metadata, dan canonical actions milik Arwaky.

## Roadmap Implementasi yang Disarankan

### Wave A — Native Animator Foundation

Wave pertama harus mengimplementasikan capability yang tidak membutuhkan plugin eksternal:

| Canonical action | Tujuan |
|---|---|
| `inspect_animation_state` | Membaca current frame, action aktif, F-curves, keyframe count, NLA tracks, dan selected control bones |
| `edit_action_keyframes` | Mengedit atau menyisipkan keyframe pada control bones terpilih dengan channel yang eksplisit |
| `set_animation_frame` | Memindahkan current frame dengan validasi scene range |
| `import_pose_asset` | Mengimpor pose asset dari Asset Library atau `.asset.blend` ke workflow armature |
| `apply_pose_asset` | Menerapkan atau blend pose asset pada Rigify armature |
| `mirror_rigify_pose` | Mirror pose kiri/kanan berdasarkan mapping control bone Rigify |
| `list_animation_actions` | Menampilkan action dan slot yang tersedia untuk armature |
| `bake_animation_action` | Bake constrained/IK result ke action dengan frame range dan channel policy |

Ini adalah capability dengan risiko paling rendah dan manfaat langsung terbesar untuk karakter MPFB2–Rigify.

### Wave B — Animator Productivity

Wave kedua dapat menambahkan pose selection sets, keying set, motion paths, breakdown/tween, curve filtering, action duplication, action rename, dan NLA strip management. Fitur-fitur ini mengambil inspirasi dari AnimAide dan Auto-Rig Pro tetapi harus diimplementasikan melalui native Blender API agar tidak bergantung pada keduanya.

### Wave C — Retargeting Core

Wave ketiga menambahkan retargeting contract yang memisahkan source armature, target Rigify armature, pose normalization, scale policy, bone mapping, FK/IK policy, bake policy, dan validation report. Mapping tidak boleh diasumsikan berdasarkan nama bone saja; mapping harus dapat dikonfigurasi dan diverifikasi.

### Wave D — Optional Open-Source Retarget Adapters

Wave keempat hanya mengevaluasi adapter untuk provider open source seperti Blender Extensions Retarget, Mixaify, atau format Mixamo/FBX/BVH yang dapat diproses melalui kode open source/auditable. Rokoko dan Auto-Rig Pro dikeluarkan dari scope. Setiap adapter harus memiliki runtime detection, version check, license metadata, graceful unavailable behavior, dan evidence test. Adapter tidak boleh menjadi syarat untuk native animator core.

### Wave E — Animation Layers dan Production Actions

Wave kelima dapat menambahkan NLA/action-layer workflow, additive animation, root motion, animation clips, and reusable animation assets. Fitur ini harus dibangun di atas native NLA dan action APIs terlebih dahulu. Add-on Animation Layers hanya dijadikan pembanding atau optional integration setelah validasi Blender 5.2 selesai.

## Keputusan Prioritas

Keputusan yang direkomendasikan adalah **tidak menginstal satu plugin eksternal sebagai solusi utama**. Implementasi berikutnya harus dimulai dari native Animator Provider untuk pose assets, keyframes, actions, baking, dan NLA. Setelah native provider lulus smoke test pada file `native_mpfb2_rigify_character.blend`, lakukan spike terisolasi terhadap Blender Extensions Retarget karena kombinasi fitur dan metadata kompatibilitasnya paling relevan.

Mixaify layak dipakai sebagai referensi implementasi retargeting FK yang kecil dan mudah diaudit, tetapi jangan dianggap sebagai solusi universal. Rokoko dan Auto-Rig Pro hanya dicatat sebagai pembanding eksternal dan **tidak memiliki adapter Arwaky**. AnimAide dan Animation Layers menjadi sumber inspirasi fitur; keduanya tidak menjadi dependency sampai lisensi, maintenance, dan Blender 5.2 compatibility dapat diverifikasi.

## Risiko dan Batasan

Retargeting ke Rigify tidak identik dengan menyalin keyframe ke semua bone. Generated Rigify mempunyai control bones, DEF bones, IK/FK mechanism, constraints, pole vectors, dan layer policy. Karena itu, retargeting yang hanya mengisi DEF bones atau hanya menyalin transform FK dapat menghasilkan animasi visual yang tidak sesuai dengan control rig.

Mixaify sendiri mendokumentasikan keterbatasan pose matching dan jitter pada konversi FK-to-IK. Risiko tersebut harus menjadi acceptance criteria Arwaky: validasi rest pose, validasi frame range, max displacement, foot contact, hand contact, and no unexpected 360-degree rotation.

Compatibility Blender 5.2 harus diuji secara lokal. Pernyataan “Blender 5” atau “Blender 5.0+” dari plugin tidak otomatis membuktikan kompatibilitas dengan Blender 5.2 LTS, MPFB2 native weights, atau generated Rigify controls Arwaky.

## Open-Source Gate

Arwaky hanya menerima provider yang memenuhi seluruh syarat berikut: source code tersedia untuk audit, lisensi open source yang kompatibel dengan distribusi/integrasi, maintenance dan version history dapat diperiksa, Blender 5.2 runtime behavior dapat diuji, dan dependency tidak mengunci pengguna pada akun atau plugin proprietary. Jika salah satu syarat tidak terpenuhi, provider ditandai **out of scope** dan tidak boleh dibuatkan adapter.

Dengan gate ini, native Blender/Rigify, Blender Extensions Retarget, Mixaify, serta proyek open source lain yang lolos audit dapat dipertimbangkan. Auto-Rig Pro dan Rokoko tidak dapat dipertimbangkan sebagai provider adapter.

## Acceptance Criteria untuk Animator Tool

| Area | Kriteria lulus |
|---|---|
| Rig target | Generated Rigify control rig terdeteksi tanpa mengubah MPFB2 generation boundary |
| Pose | Hand, face, and full-body pose asset dapat dibuat, disimpan, diterapkan, dan diblend |
| Keyframe | Keyframe hanya ditulis pada control bones atau channels yang diminta |
| FK/IK | Policy FK/IK eksplisit; tidak ada konversi diam-diam yang menghasilkan jitter |
| Retarget | Source/target mapping dapat diinspeksi dan dikoreksi sebelum bake |
| Action | Action, slots, frame range, NLA tracks, dan bake result dapat diverifikasi |
| Safety | Hanya provider native/open-source; unavailable dependency menghasilkan error yang dapat dipahami |
| Visual evidence | Minimal satu pose animation dan satu retargeted clip diverifikasi melalui `.blend` dan render |
| Quality | AES, ruff, pytest, and `git diff --check` lulus |

## Rekomendasi Final

**Tool animator Arwaky harus dimulai sebagai native Blender 5.2 Animator Provider, dengan Pose Library sebagai workflow pose utama dan Retarget dari Blender Extensions sebagai kandidat adapter open-source pertama.** Mixaify dapat menjadi optional Mixamo adapter setelah audit dan smoke test. Rokoko serta Auto-Rig Pro berada di luar scope adapter karena proprietary. AnimAide dan Animation Layers hanya menjadi referensi fitur sampai status lisensi, maintenance, dan Blender 5.2 compatibility cukup kuat.

Keputusan ini menjaga arsitektur AES, mempertahankan MPFB2 sebagai character-generation boundary, menghindari dependency proprietary, dan tetap memberi jalan menuju workflow animasi yang mudah bagi pengguna Rigify.

## References

[1]: https://extensions.blender.org/add-ons/retarget/ "Retarget — Blender Extensions"
[2]: https://docs.blender.org/manual/en/latest/animation/armatures/posing/editing/pose_library.html "Pose Library — Blender 5.2 LTS Manual"
[3]: https://github.com/netherby/mixaify-retarget "Mixaify — Mixamo to Rigify animation retargeter"
[4]: https://support.rokoko.com/hc/en-us/articles/4410463481489-Retarget-an-animation-in-Blender "Retarget an animation in Blender — Rokoko Support"
[5]: https://github.com/aresdevo/animaide "AnimAide official repository"
[6]: https://superhivemarket.com/products/auto-rig-pro "Auto-Rig Pro — Superhive"
[7]: https://github.com/evilmushroom/Animation-Layers-for-Blender "Animation Layers for Blender"

## Related Files

- Interim research ledger: `docs/project/research/rigify_animator_research_notes.md`
- Existing native Rigify evidence: `docs/project/rigging/native_mpfb2_rigify_findings.md`
- Existing deformation validation: `docs/project/rigging/native_mpfb2_rigify_validation.md`

## Scope Boundary

This report is a research and architecture recommendation. It does not install third-party add-ons, modify Blender, or claim that every candidate has passed Blender 5.2 runtime testing.
