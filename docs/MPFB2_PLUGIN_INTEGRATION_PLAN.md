# Rencana Integrasi MPFB 2 sebagai Plugin Pertama

## 1. Tujuan

Dokumen ini mendefinisikan rencana untuk menjadikan **MPFB 2** sebagai plugin pertama dalam ekosistem plugin Blender Arwaky. Integrasi ini tidak menyalin source code MPFB 2 ke dalam core repository. Blender Arwaky menyediakan framework plugin global, contract, discovery, lifecycle, capability registry, validation, dan result normalization; implementasi spesifik MPFB 2 ditempatkan di luar `modules/`, yaitu pada `plugin/mpfb2/`.

MPFB 2 diperlakukan sebagai **optional Blender add-on provider**. Core Blender Arwaky harus tetap dapat berjalan ketika MPFB 2 tidak terpasang, tidak aktif, atau tidak kompatibel. Hanya capability yang berhasil ditemukan dan divalidasi pada runtime yang boleh dipublikasikan sebagai available.

## 2. Prinsip arsitektur

Rencana ini mengikuti lima prinsip utama. Pertama, `modules/` adalah core source tree dan wajib mematuhi AES architecture, AES naming rules, dependency direction, serta `lint-arwaky-cli scan .`. Kedua, `plugin/` adalah extension boundary; struktur internalnya boleh mengikuti kebutuhan provider, tetapi entry point dan manifest-nya wajib memenuhi plugin contract global. Ketiga, MCP dan CLI tidak boleh memanggil MPFB 2 secara langsung. Keempat, tidak boleh ada universal arbitrary-plugin execution atau shortcut access path. Kelima, plugin tidak boleh menjadi dependency wajib bagi core runtime.

> `modules/plugin/` berisi framework dan adapter global. `plugin/<plugin-name>/` berisi implementasi konkret provider.

## 3. Boundary repository

Struktur target yang direncanakan adalah sebagai berikut:

```text
blender-arwaky/
├── modules/
│   └── plugin/
│       └── src/
│           ├── contract_plugin_protocol.py
│           ├── schema_plugin_manifest.py
│           ├── registry_plugin_catalog.py
│           ├── service_plugin_discovery.py
│           ├── service_plugin_runtime.py
│           ├── service_plugin_adapter.py
│           └── service_plugin_capability.py
│
├── plugin/
│   └── mpfb2/
│       ├── plugin_manifest.yaml
│       ├── plugin_entry.py
│       ├── mpfb2_discovery.py
│       ├── mpfb2_capabilities.py
│       ├── mpfb2_operations.py
│       └── README.md
│
├── modules/shared/
├── modules/dispatcher/
├── modules/mcp/
├── modules/cli/
└── docs/
```

Nama file pada contoh `modules/plugin/` mengikuti aturan penamaan AES yang berlaku pada source tree `modules/`. Struktur internal `plugin/mpfb2/` tidak dipaksa mengikuti konvensi internal `modules/`, tetapi tetap harus readable, teruji, dan memiliki entry point yang jelas.

| Boundary | Aturan |
|---|---|
| `modules/plugin/` | Strict AES architecture, strict AES naming, typed contracts, no provider-specific implementation |
| `plugin/mpfb2/` | Provider-specific implementation, optional dependency, flexible internal structure |
| `modules/shared/` | Shared schemas, result envelopes, validation, security, and common types |
| `modules/dispatcher/` | Single routing path for core and validated extension actions |
| `modules/mcp/` | Remains limited to five stable MCP tools |
| `modules/cli/` | Uses generated CLI commands and `kebab-case` naming |

## 4. Target plugin contract

Setiap plugin harus menyediakan contract yang sama. Framework global tidak boleh mengetahui detail internal MPFB 2, Rigify, VRM, atau provider lain.

```python
class PluginContract(Protocol):
    def get_manifest(self) -> PluginManifest: ...
    def discover(self, context: BlenderContext) -> DiscoveryResult: ...
    def get_capabilities(self) -> list[PluginCapability]: ...
    def execute(self, action: str, params: dict[str, object]) -> PluginResult: ...
    def health_check(self) -> PluginHealth: ...
```

Contract tersebut bukan arbitrary Python gateway. `action` harus berasal dari capability schema yang telah didaftarkan, memiliki parameter terdefinisi, dan melewati validation sebelum execution.

## 5. Manifest MPFB 2

Manifest memberikan metadata yang dibutuhkan framework untuk discovery dan compatibility check. Contoh konseptual:

```yaml
id: mpfb2
name: MPFB 2
provider_type: blender_addon
version: 2.0.17
blender_min_version: 4.2
entry_point: plugin_entry:register
capabilities:
  - id: character.create
    version: 1
  - id: character.configure
    version: 1
  - id: character.rig
    version: 1
  - id: character.export
    version: 1
```

Nilai versi pada contoh harus diverifikasi terhadap release MPFB 2 dan hasil pengujian nyata sebelum menjadi compatibility claim. Release MPFB 2 v2.0.17 tersedia pada repository resmi MakeHuman Community. [1]

## 6. Lifecycle plugin

Lifecycle plugin harus deterministic dan tidak boleh mengganggu startup core.

| Tahap | Perilaku |
|---|---|
| Discover | Cari plugin manifest dan entry point yang valid |
| Load | Muat metadata tanpa langsung menjalankan operasi Blender mutatif |
| Compatibility check | Periksa versi Blender, versi plugin, API contract, dan dependency |
| Activate | Hubungkan provider yang tersedia ke plugin runtime |
| Capability probe | Verifikasi capability yang benar-benar tersedia pada sesi Blender |
| Register | Tambahkan extension actions yang lolos validation ke runtime catalog |
| Execute | Jalankan action melalui contract dan adapter global |
| Health check | Laporkan installed, active, compatible, dan capability status |
| Deactivate | Lepaskan provider tanpa merusak core runtime |

Kegagalan satu plugin harus menghasilkan status plugin-level seperti `unavailable`, `incompatible`, atau `configuration_error`; kegagalan tersebut tidak boleh membuat seluruh MCP server atau CLI gagal startup.

## 7. Integrasi dengan catalog, CLI, dan MCP

Core catalog Blender Arwaky tetap menjadi catalog utama. Plugin menambahkan **extension actions** hanya setelah manifest, capability, schema, dan compatibility check berhasil.

| Surface | Contract |
|---|---|
| CLI | Extension action menggunakan `kebab-case`, misalnya `mpfb2-create-character` |
| MCP/API | Extension action menggunakan `snake_case`, misalnya `mpfb2_create_character` |
| MCP registry | Tetap lima stable tools; plugin tidak mendaftarkan MCP tool baru |
| Dispatcher | Satu routing path untuk core action dan validated extension action |
| Help/catalog | Plugin action hanya muncul apabila plugin terdeteksi dan capability tersedia |
| Error | Provider failure dipetakan ke standard error envelope |

Tidak boleh ditambahkan command generic seperti `run-plugin`, `invoke-plugin`, atau `plugin-execute-code` yang menerima arbitrary Python. Setiap capability plugin harus memiliki schema dan action name yang dapat ditemukan.

## 8. Scope capability MPFB 2

Implementasi pertama tidak perlu mengekspos seluruh MPFB 2. Capability dipilih secara bertahap berdasarkan API yang stabil dan dapat diuji.

| Tahap | Capability target |
|---|---|
| MVP | Detect MPFB 2, health status, capability discovery, create base character |
| Phase 2 | Update anthropometric parameters dan material/skin settings |
| Phase 3 | Rig generation, pose preparation, dan bounded deformation workflow |
| Phase 4 | Export character, asset placement, dan repeatable preset workflow |
| Deferred | Capability MPFB 2 yang tidak memiliki contract stabil, membutuhkan UI-only context, atau belum memiliki integration test |

Nama action final tidak boleh ditambahkan ke canonical catalog sebelum parameter, requiredness, output, error mapping, dan destructive behavior terdokumentasi.

## 9. Dependency dan packaging

MPFB 2 tidak dibundel ke dalam core package Blender Arwaky. Pengguna memasang MPFB 2 secara terpisah di Blender. Plugin `plugin/mpfb2/` hanya berisi integration code dan metadata yang diperlukan untuk berkomunikasi dengan add-on tersebut.

Dependency Python tambahan untuk plugin tidak boleh otomatis menjadi dependency core apabila tidak dibutuhkan oleh 75 core actions. Jika plugin membutuhkan dependency khusus, dependency tersebut harus diisolasi, didokumentasikan, dan diverifikasi dalam plugin-specific test environment.

Sebelum distribusi plugin, lakukan review license, attribution, asset terms, dan aturan redistribusi MPFB 2. Menjalankan MPFB 2 sebagai add-on eksternal berbeda dari menyalin source code atau asset MPFB 2 ke repository Arwaky.

## 10. Testing strategy

Testing harus memisahkan core framework dari provider integration.

| Test layer | Target |
|---|---|
| Unit | Manifest parser, version comparison, capability registry, lifecycle state, error mapper |
| Contract | Setiap plugin memenuhi `PluginContract` dan schema rules |
| Mock provider | Core `modules/plugin/` berjalan tanpa Blender atau MPFB 2 |
| Blender integration | MPFB 2 terpasang, aktif, dan dapat menjalankan capability MVP |
| Negative integration | MPFB tidak terpasang, disabled, incompatible, API mismatch, dan operation failure |
| CLI/MCP parity | Extension action menghasilkan behavior dan error envelope yang sama |
| AES gate | Semua perubahan di `modules/` lulus `lint-arwaky-cli scan .` |
| Packaging | Core package tetap dapat dibangun tanpa MPFB 2 |

Plugin-specific tests boleh berada dekat dengan plugin di `plugin/mpfb2/` sesuai kebutuhan, sedangkan framework tests yang berada di `modules/plugin/` wajib mengikuti seluruh aturan test dan AES pada source tree `modules/`.

## 11. Security boundary

Plugin execution tetap menjalankan Blender Python dan bukan sandbox penuh. Framework harus menerapkan path validation, parameter validation, response redaction, bounded output, destructive-action confirmation, dan capability allow-listing. Plugin tidak boleh menyisipkan secret ke response atau menerima arbitrary code dari MCP/CLI sebagai pengganti action schema.

Jika plugin memiliki operasi yang menulis file, mengubah scene, menghapus data, atau menjalankan proses eksternal, operation tersebut harus diklasifikasikan dan menggunakan confirmation policy yang sesuai.

## 12. Implementasi bertahap

### Wave 1 — Framework skeleton

Buat contract global, manifest schema, plugin registry, discovery state, compatibility result, capability model, dan standard plugin error mapping. Belum mengimplementasikan capability MPFB 2.

### Wave 2 — MPFB 2 discovery

Tambahkan `plugin/mpfb2/`, manifest, detection terhadap add-on aktif, version probe, health status, dan negative path ketika MPFB 2 tidak tersedia.

### Wave 3 — First capability

Implementasikan satu capability MVP untuk membuat base character melalui contract global. Tambahkan CLI/MCP parity test dan Blender smoke test.

### Wave 4 — Capability expansion

Tambahkan parameter update, rig, dan export secara bertahap. Setiap capability harus memiliki schema, result mapping, error mapping, dan integration test sendiri.

### Wave 5 — Hardening

Uji compatibility matrix, failure recovery, plugin disable/remove, catalog refresh, package build tanpa MPFB 2, documentation, dan license notice.

## 13. Acceptance criteria

Rencana ini dianggap berhasil apabila:

1. `modules/plugin/` hanya berisi framework, contract, registry, discovery, runtime, adapter global, dan shared plugin services.
2. Tidak ada folder provider seperti `mpfb2/` di dalam `modules/plugin/`.
3. Implementasi MPFB 2 berada di `plugin/mpfb2/` dan dapat dihapus tanpa merusak core build.
4. Core Blender Arwaky dapat startup tanpa MPFB 2.
5. MCP tetap mengekspos lima stable tools.
6. Plugin actions memakai satu dispatcher, memiliki schema, dan tidak menggunakan generic arbitrary-code fallback.
7. Plugin unavailable menghasilkan status atau error terstruktur, bukan crash.
8. Semua perubahan pada `modules/` lulus AES architecture dan naming gates.
9. Plugin-specific tests mencakup provider available, unavailable, incompatible, dan execution failure.
10. Dokumentasi user tidak mengklaim capability MPFB 2 sebagai core capability tanpa plugin terpasang.

## 14. Keputusan yang belum ditetapkan

Beberapa hal perlu diputuskan sebelum implementasi dimulai: apakah extension actions digabungkan ke runtime catalog secara dinamis atau dibatasi pada catalog plugin manifest; apakah plugin discovery hanya memindai repository `plugin/` atau juga lokasi instalasi eksternal; bagaimana distribusi plugin dilakukan; dan compatibility matrix MPFB 2 versus versi Blender yang akan didukung.

Keputusan tersebut tidak boleh mengubah prinsip utama bahwa `modules/` adalah strict AES core dan `plugin/` adalah provider extension boundary.

## References

[1]: https://github.com/makehumancommunity/mpfb2/releases/tag/v2.0.17 "MPFB 2 v2.0.17 release"
