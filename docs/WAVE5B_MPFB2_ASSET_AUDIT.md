# Wave 5B MPFB2 Asset Audit Notes

## Official pack

The official MakeHuman Community page identifies the `makehuman_system_assets` pack as the minimum recommended system pack for MPFB2. It is published as a ZIP archive with two official mirrors:

- `https://files2.makehumancommunity.org/asset_packs/makehuman_system_assets/makehuman_system_assets_cc0.zip`
- `https://files.makehumancommunity.org/asset_packs/makehuman_system_assets/makehuman_system_assets_cc0.zip`

The published pack is approximately 267 MB and includes system content such as proxy meshes, skins, eyes, eyebrows, eyelashes, hair, clothes, teeth, tongue, and related assets. The source page identifies the pack content as CC0, but the implementation must retain source and license metadata rather than infer license from the URL.

The official MPFB documentation states that asset packs are installed from the MPFB2 `Apply assets -> Library settings -> Install asset pack` flow. It also warns that Blender may need to restart before the new pack is detected.

## Installed MPFB2 API observations

The Blender 5.2 extension contains these relevant public service methods:

- `AssetService.check_asset_pack_zip(filename)` validates the MPFB2 archive structure.
- `AssetService.fix_and_extract_asset_pack_zip(filename, target_dir)` extracts a valid pack into an MPFB user-data directory while handling a single extra root directory and skipping `__MACOSX` entries.
- `AssetService.rescan_pack_metadata()` refreshes pack metadata.
- `AssetService.get_pack_names()` lists installed pack names.
- `AssetService.system_assets_pack_is_installed()` checks for `makehuman_system_assets` metadata.
- `LocationService.get_user_data("packs")` identifies the MPFB user pack directory.
- `LocationService.get_user_data()` identifies the MPFB user data root.

These APIs are provider-specific and must be called only from `plugin/mpfb2/` or through an explicitly mapped Blender wire action. The AES core must not import MPFB2 services.

## Pre-Wave 5B gap

Before Wave 5B, the plugin package lifecycle handled only the MPFB2 extension archive. It did not download, verify, validate, install, or discover MPFB2 asset packs. Wave 5B closes this gap for the official `makehuman_system_assets` pack; additional third-party and functional packs remain future provider scope.

## Security requirements

The asset URL must use HTTPS. The archive must be downloaded to an explicit absolute cache path, verified with SHA-256 before extraction, checked for MPFB2 pack structure, rejected if it contains traversal or symlink entries, extracted atomically into the MPFB pack directory, and rescanned through `AssetService`. The official source page does not publish a SHA-256 digest in the page content observed during this audit. The implementation therefore does not invent a provider-published digest: it pins the SHA-256 computed from the official HTTPS archive in `plugin/mpfb2/asset_pack_manifest.py` and still requires the digest in every canonical download, verify, and install request.

## Wave 5B implementation result

The canonical catalog now includes four explicit actions: `download-mpfb-asset-pack`, `verify-mpfb-asset-pack`, `install-mpfb-asset-pack`, and `inspect-mpfb-assets`. Download and verification reuse the generic bounded package capability in `modules/`, while provider-specific installation and inspection are mapped through explicit MPFB2 wire actions. The Blender handler uses `AssetService.check_asset_pack_zip`, `AssetService.fix_and_extract_asset_pack_zip`, `AssetService.rescan_pack_metadata`, and `AssetService.system_assets_pack_is_installed`.

The official archive was downloaded from the primary HTTPS mirror and pinned with these observed values:

| Field | Value |
|---|---|
| Pack | `makehuman_system_assets` |
| Size | 280,737,770 bytes |
| SHA-256 | `b542127a8e25547c7c29c19f2d1d2adb9a664c80396ecd694095dbc8028a0107` |
| Detected pack entries | 94 |
| Blender | 5.2.0 LTS |

## Live verification

The Blender 5.2 asset smoke test passed with marker `WAVE5B_MPFB_ASSET_SMOKE_OK`. It installed the official pack into the MPFB2 user data root, detected `makehuman_system_assets`, reported 94 asset entries, and created a character through `HumanService.create_human`. The previous `create_character` operator mapping was corrected because `bpy.ops.mpfb.create_human` is not registered in MPFB2 2.0.17; the handler now uses the public MPFB2 service API.

The visual smoke test applied a real skin from the installed system pack and produced a Blender render at 320x320. The render is a basic low-memory proof of textured character generation; it is not intended as a final artistic showcase.

## References

1. https://static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html — official system asset pack page.
2. https://static.makehumancommunity.org/assets/assetpacks/faq.html — official installation and archive structure guidance.
3. https://static.makehumancommunity.org/assets/downloadassets/index.html — official download modes and MPFB recommendation.
4. https://static.makehumancommunity.org/mpfb/docs/getting_started.html — official MPFB2 setup and asset-pack guidance.
5. https://github.com/makehumancommunity/mpfb2/blob/master/src/mpfb/services/assetservice.py — MPFB2 AssetService implementation reference.
