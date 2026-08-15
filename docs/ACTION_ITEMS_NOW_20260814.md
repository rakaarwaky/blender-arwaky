# Action Items yang Dapat Dilakukan Sekarang

## Tujuan

Dokumen ini adalah execution gate setelah revalidation seluruh plan business-analyst. Isinya hanya pekerjaan yang dapat dimulai dengan aman berdasarkan bukti current source dan revised plans. Plan lama 2026-08-08 tidak boleh digunakan langsung. Setiap item yang masih ambigu ditempatkan di bagian klarifikasi dan tidak boleh diimplementasikan sebelum kontraknya dipastikan.

## Aturan Eksekusi

| Status | Makna | Perlakuan |
|---|---|---|
| `READY` | Scope dan acceptance criterion cukup jelas untuk dikerjakan. | Dapat dimulai sekarang. |
| `CLARIFY_FIRST` | Ada ketidakpastian tentang kontrak, path, atau perilaku yang diharapkan. | Lakukan investigasi dan tulis keputusan sebelum coding. |
| `BLOCKED` | Bergantung pada keputusan desain atau module lain. | Jangan implementasi sampai dependensi selesai. |
| `DONE_CRITERION` | Bukan pekerjaan baru; dipakai untuk regression verification. | Jadikan acceptance test, bukan refactor ulang. |

## Prioritas P0 — Keamanan dan Integritas Data

| ID | Module | Action | Status | Acceptance criteria |
|---|---|---|---|---|
| SEC-001 | Security | Tambahkan test path traversal untuk `../`, absolute path, encoded traversal seperti `%2e%2e%2f`, dan variasi separator. | `READY` | Semua input berbahaya ditolak; path valid tetap diterima; hasil error tidak membocorkan path sensitif. |
| SEC-002 | Security | Tambahkan test symlink escape dari allowed directory. | `READY` | Symlink yang resolve ke luar allowed root ditolak; symlink aman tetap mengikuti kebijakan yang ditetapkan. |
| SEC-003 | Security | Tambahkan test archive bomb berdasarkan jumlah entry, ukuran total, dan rasio ekstraksi. | `READY` | Archive yang melampaui batas ditolak sebelum ekstraksi; alasan penolakan terstruktur. |
| SEC-004 | Security | Tambahkan test nested archive extraction. | `READY` | Archive bertingkat tidak dapat melewati batas destination atau traversal policy. |
| SEC-005 | Security | Tambahkan test multiline secret redaction dan false-positive cases. | `READY` untuk test; implementasi redactor tetap `CLARIFY_FIRST` bila hasil test menemukan masalah | Secret multiline tersamarkan; data normal yang bukan secret tidak terhapus berlebihan. |
| SEC-006 | Security/Gateway | Pertahankan regression test bahwa code validation terjadi sebelum gateway transport. | `READY` | Code yang melanggar policy tidak pernah mencapai transport; AST validation dan blocked construct policy tetap aktif. |

## Prioritas P0 — Job Reliability

| ID | Module | Action | Status | Acceptance criteria |
|---|---|---|---|---|
| JOB-001 | Job | Tambahkan concurrency test untuk transition repository dengan banyak worker. | `READY` | Tidak ada state korup, active count negatif, atau transition ilegal; repository tetap konsisten. |
| JOB-002 | Job | Tambahkan test stale running task recovery. | `READY` | Task stale berubah ke timeout, event/status konsisten, lalu record dibersihkan sesuai policy. |
| JOB-003 | Job | Tambahkan test capacity rejection melalui orchestrator. | `READY` | Saat kapasitas penuh, task baru ditolak dengan kategori error yang tepat dan tidak membuat record parsial. |
| JOB-004 | Job | Tambahkan test metadata sanitization untuk token, secret, credential, authorization, dan nilai panjang. | `READY` | Sensitive keys menjadi `[REDACTED]`, nilai dibatasi panjangnya, dan metadata non-sensitive tetap dipertahankan. |
| JOB-005 | Job | Klarifikasi apakah sanitizer lokal harus memakai Security aggregate atau cukup utility job sanitizer. | `CLARIFY_FIRST` | Keputusan arsitektur tertulis; tidak ada dua kebijakan redaction yang berbeda tanpa alasan. |

## Prioritas P0 — Render Correctness

| ID | Module | Action | Status | Acceptance criteria |
|---|---|---|---|---|
| RND-001 | Render/Job | Rancang dan implementasikan integrasi background render dengan Job lifecycle, bukan hanya capacity check. | `BLOCKED` setelah desain; mulai dengan design note sekarang | Background render menghasilkan task reference, progress/status dapat dipantau, cancel/cleanup mengikuti Job authority, dan direct synchronous render tetap kompatibel. |
| RND-002 | Render | Tambahkan acceptance test untuk overwrite, reject, dan unique-output policy pada output yang sudah ada. | `READY` setelah policy semantics ditulis dalam test | Setiap policy menghasilkan perilaku deterministik; tidak ada overwrite diam-diam jika policy melarangnya. |
| RND-003 | Render/Asset | Klarifikasi kontrak HDRI: apakah Render menerima local asset path yang sudah di-resolve Asset, atau Render harus meminta Asset aggregate. | `CLARIFY_FIRST` | FRD dan protocol menyatakan satu boundary yang jelas; tidak ada download langsung tersembunyi di Render. |
| RND-004 | Render | Tambahkan test HDRI missing-asset/error propagation setelah kontrak RND-003 disetujui. | `BLOCKED` oleh RND-003 | Error Asset not found dipetakan menjadi response Render yang stabil dan tidak bocor detail internal. |

## Prioritas P1 — Telemetry dan Observability

| ID | Module | Action | Status | Acceptance criteria |
|---|---|---|---|---|
| TLM-001 | Telemetry | Tetapkan schema version dan environment metadata yang tidak lagi selalu `unknown`. | `CLARIFY_FIRST` | Ada sumber version/platform yang disetujui, fallback jelas, dan schema version berubah hanya melalui aturan kompatibel. |
| TLM-002 | Telemetry | Definisikan transmission boundary setelah buffer: destination, consent, retry, failure fallback, dan no-blocking guarantee. | `CLARIFY_FIRST` | Telemetry opt-in, transmission failure tidak mengganggu operasi utama, retry/backoff terdokumentasi. |
| TLM-003 | Telemetry | Setelah TLM-001/TLM-002, implementasikan tests untuk schema increment, transmission failure, bounded buffer, drop count, dan backpressure metrics. | `BLOCKED` | Semua acceptance criteria telemetri dapat diverifikasi tanpa mengirim data nyata. |
| DIA-001 | Diagnostics | Tambahkan metrics untuk buffer saturation, dropped events, dan transmission failures setelah Telemetry contract disepakati. | `BLOCKED` | Diagnostics dapat menampilkan metric tanpa mengambil alih ownership Telemetry. |

## Prioritas P1 — Shared Contracts dan Protocol Completeness

| ID | Module | Action | Status | Acceptance criteria |
|---|---|---|---|---|
| SHR-001 | Shared | Review abstract methods dengan `pass` pada `WorkflowProtocol`, `CommandCatalogProtocol`, dan `ExecuteActionProtocol`. | `READY` untuk review; coding `CLARIFY_FIRST` | Setiap method jelas apakah memang abstract contract, harus memakai `@abstractmethod`, atau membutuhkan implementasi konkret. Tidak ada stub yang dianggap business logic selesai. |
| SHR-002 | Shared | Tambahkan contract signature tests setelah keputusan SHR-001. | `BLOCKED` oleh SHR-001 | Test memverifikasi method signature, required taxonomy types, dan implementor mapping. |
| SHR-003 | Shared | Tambahkan `.agents/rules/README.md` sebagai index canonical seluruh rule file. | `READY` | Semua rule file terdaftar, prerequisite order jelas, dan workflow tidak lagi merujuk file yang tidak ada. |

## Prioritas P1 — MCP, CLI, dan Dispatcher

| ID | Module | Action | Status | Acceptance criteria |
|---|---|---|---|---|
| MCP-001 | MCP | Verifikasi protocol version negotiation terhadap versi MCP target sebelum menambah behavior baru. | `CLARIFY_FIRST` | Versi target, rejection behavior, dan compatibility matrix tertulis. |
| MCP-002 | MCP | Tambahkan test oversized response untuk summarize, substitute, dan truncate setelah contract MCP dikonfirmasi. | `BLOCKED` oleh MCP-001 | Setiap strategi menghasilkan response valid, bounded, dan tracking ID tetap terbawa. |
| MCP-003 | MCP | Tambahkan test tracking ID propagation ke semua response surface. | `READY` setelah response contract dipastikan | Tracking ID stabil dari request sampai response dan error envelope. |
| CLI-001 | CLI | Tambahkan integration test command-to-dispatcher untuk JSON output, exit code, auto-wire, dan error masking. | `READY` | CLI end-to-end menghasilkan response JSON dan exit code yang konsisten pada success, validation, connection, dan upstream error. |
| CLI-002 | CLI | Tetapkan taxonomy exit error user-correctable versus system-internal sebelum mengubah `ERROR_CATEGORIES`. | `CLARIFY_FIRST` | Script dapat membedakan input user, konfigurasi, koneksi, dan internal failure tanpa memecahkan compatibility. |
| DSP-001 | Dispatcher | Tambahkan tests untuk payload size, tracking ID generation, timeout bounds, dan destructive-action confirmation. | `READY` setelah schema source dipastikan | Request invalid ditolak sebelum dispatch dengan kategori dan field detail yang stabil. |

## Prioritas P2 — Scene dan Asset

| ID | Module | Action | Status | Acceptance criteria |
|---|---|---|---|---|
| SCN-001 | Scene | Klarifikasi policy linked object, child hierarchy, dan large-scene summarization. | `CLARIFY_FIRST` | Policy delete/detach/reject dan summary/pagination ditulis eksplisit di FRD/protocol. |
| SCN-002 | Scene | Setelah SCN-001, tambahkan tests linked-object cleanup, child policy, pagination, dan summarized inspection. | `BLOCKED` | Tidak ada object yang terhapus di luar policy; response besar tetap bounded. |
| AST-001 | Asset | Verifikasi provider adapter contract, concurrent same-asset deduplication, dan full search→download→extract→import flow. | `CLARIFY_FIRST` | Ownership provider, cache key, dedup lock, dan pipeline boundary terdokumentasi. |
| AST-002 | Asset | Setelah AST-001, tambahkan integration test pipeline dengan mocked provider dan archive security. | `BLOCKED` | Satu flow end-to-end berhasil, failure setiap tahap dipetakan, dan tidak ada duplicate download. |

## Item yang Tidak Boleh Langsung Dieksekusi

Item berikut tidak boleh diubah menjadi coding task hanya berdasarkan wording lama: perubahan protocol MCP tanpa target spec, perubahan telemetry transmission tanpa consent/destination contract, perubahan HDRI tanpa keputusan Asset boundary, perubahan CLI error taxonomy tanpa compatibility decision, perubahan Scene summarization tanpa size policy, serta perubahan Job redaction tanpa keputusan apakah Security aggregate menjadi single authority.

## Urutan Eksekusi yang Disarankan

Tahap pertama adalah menambahkan tests keamanan dan reliability Job karena acceptance criteria-nya paling jelas dan risiko regresinya tinggi. Tahap kedua adalah menyelesaikan keputusan kontrak pada Shared, Render/Job, Telemetry, MCP, Scene, Asset, dan CLI. Tahap ketiga adalah mengimplementasikan perubahan yang sudah disetujui berdasarkan hasil klarifikasi, lalu menjalankan regresi penuh, lint, architecture scan, dan Blender E2E smoke test.

## Definition of Done

Action item dianggap selesai hanya jika perubahan memiliki test atau bukti acceptance yang sesuai, tidak melanggar AES layer boundaries, tidak menduplikasi ownership module lain, tercakup dalam FRD/protocol, lulus test suite dan lint yang relevan, serta plan item diubah dari `open` menjadi `resolved` dengan link commit/PR. Item `needs-clarification` tidak boleh ditandai resolved hanya karena source terlihat masuk akal.

## References

- [`PLAN_REVALIDATION_ALL_FEATURE_MODULES_20260814.md`](PLAN_REVALIDATION_ALL_FEATURE_MODULES_20260814.md)
- [`PLAN_REVALIDATION_EVIDENCE_20260814.md`](PLAN_REVALIDATION_EVIDENCE_20260814.md)
- [`ARCHITECTURE.md`](../ARCHITECTURE.md)
- [`PRD.md`](../PRD.md)
- [`Revalidated plans`](../.agents/plans/)
