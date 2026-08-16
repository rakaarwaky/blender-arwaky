# Laporan E2E CLI Blender Arwaky

Pengujian ini dijalankan terhadap Blender nyata dalam mode headless menggunakan fixture `/tmp/blender_arwaky_cli_fixture.blend`, dengan addon aktif melalui server loop headless repository.

## Hasil Subcommand

| Subcommand | Skenario | Hasil |
| --- | --- | --- |
| `init` | Start fixture pada port `19876` | Lulus, exit code `0`, PID tercatat di registry |
| `status` | Membaca sesi aktif | Lulus, `active=true`, `running=true` |
| `run` | Action `get_scene_info` | Lulus, exit code `0`, 3 object terbaca |
| `run` | Action `get_object_info` dengan `{"name":"Cube"}` | Lulus, exit code `0` |
| `run` | Action `render` pada 160×120 | Lulus, exit code `0`, PNG terbentuk |
| `screenshot` | Viewport/camera screenshot 320×240 dengan `focus-object` | Lulus, exit code `0`, PNG terbentuk |
| `render` | Full render 320×240 | Lulus, exit code `0`, PNG terbentuk |
| `close` | Save attempt, terminate PID, clear registry | Lulus, exit code `0` |
| `status` setelah close | Memastikan tidak ada sesi aktif | Lulus, `active=false` |

Invalid action juga diuji dan menghasilkan perilaku yang benar: exit code `2`, kategori `validation_error`, serta daftar action yang tersedia.

## Perbaikan yang Ditemukan Saat E2E

Pertama, console entrypoint `blender-arwaky` menunjuk ke modul yang tidak ada, sehingga diperbaiki ke `modules.cli.src.root_cli_main_entry:main`.

Kedua, launcher CLI menghitung root project terlalu tinggi dan memasukkan direktori addon, bukan parent package, ke `sys.path`. Launcher sekarang memakai root repository yang benar.

Ketiga, Blender background langsung berakhir setelah addon di-enable karena tidak memiliki event loop untuk memproses command. Mode headless sekarang memakai `scripts/blender/run_server_headless.py` dan meneruskan port melalui `BLENDERMCP_PORT`.

Keempat, response addon berbentuk `{"status":"success","result":...}`, sedangkan CLI mengharapkan `success=true`. Handler `run`, `screenshot`, dan `render` sekarang menormalisasi response serta memeriksa error upstream.

Kelima, action render belum tersedia pada dispatch table addon. Handler `render` ditambahkan dengan pemulihan setting resolusi dan filepath setelah render selesai. Screenshot headless juga menerima `max_size` dan tidak lagi memanggil operator viewport GUI ketika Blender berjalan tanpa UI.

## Action CLI yang Tervalidasi

Action yang tervalidasi secara langsung adalah `get_scene_info`, `get_object_info`, dan `render`. Action `execute_blender_code` adalah canonical dispatcher action dan diakses melalui CLI `execute-blender-code` serta MCP `execute_command`.

## Verifikasi Regresi

Setelah perbaikan, test suite Python menghasilkan `897 passed, 1 skipped`. Ruff lint, Ruff format check, dan `git diff --check` juga lulus.
