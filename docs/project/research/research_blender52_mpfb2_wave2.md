# Wave 2 external verification notes

## Official sources

- Blender 5.2 LTS release: https://www.blender.org/download/releases/5-2/
- Blender LTS support: https://www.blender.org/download/lts/
- Blender extension command-line arguments: https://docs.blender.org/manual/en/latest/advanced/command_line/extension_arguments.html
- Blender extensions Python API: https://docs.blender.org/api/current/bpy.ops.extensions.html
- MPFB official extension listing: https://extensions.blender.org/add-ons/mpfb/
- MPFB getting started: https://static.makehumancommunity.org/mpfb/docs/getting_started.html

## Verified facts

- Blender 5.2.0 LTS portable binary was downloaded from the Berkeley OCF mirror because the primary transfer was corrupted. Archive size was 384441228 bytes and SHA-256 was `96f6c181a30f4950607839dc84d42a354b250d8a0231b098b59b7bc69c351c48`.
- Blender executable verified as `Blender 5.2.0 LTS`, build date 2026-07-14.
- Blender 5.2 supports `--background --command extension install-file --repo user_default --enable FILE` and `extension remove PACKAGE`.
- Official MPFB 2.0.17 package URL is the Blender Extensions download URL containing SHA-256 `4f0a879d64a39bf646fbf5f53601ac678855da329d650617dca5737548239a87`.
- MPFB2 package manifest declares extension id `mpfb`, version `2.0.17`, and `blender_version_min = "4.2.0"`.
- Real installation was completed in isolated profile `/tmp/blender-arwaky-wave2-profile` under `data/extensions/user_default/mpfb` using Blender 5.2 `extension install-file --enable`.
- MPFB2 real operator discovered in the installed package: `mpfb.create_human`, implemented at `ui/new_human/newhuman/operators/createhuman.py`. It creates a base mesh through `HumanService.create_human` and does not require importing MPFB internals from Arwaky.
- MPFB2 operation mapping added outside `modules/` in `plugin/mpfb2/plugin_operations.py`: canonical `create_character` maps to fixed wire action `create_character` with provider id `mpfb2` and bounded name.

## Current implementation direction

- Add canonical plugin action `create_character` to shared catalog.
- Route it through `CliActionRouter` using the explicit MPFB2 mapper and Blender TCP bridge.
- Add a fixed Blender addon handler for wire action `create_character` that calls only `bpy.ops.mpfb.create_human`; no user-provided Python is executed.
