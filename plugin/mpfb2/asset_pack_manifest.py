"""Official MPFB2 asset-pack metadata used by the explicit provider boundary."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Mpfb2AssetPackManifest:
    """Pinned metadata for one approved MPFB2 asset pack."""

    asset_pack_id: str
    source_url: str
    sha256: str
    size_bytes: int
    license_name: str
    source_page: str


MAKEHUMAN_SYSTEM_ASSETS = Mpfb2AssetPackManifest(
    asset_pack_id="makehuman_system_assets",
    source_url=(
        "https://files.makehumancommunity.org/asset_packs/"
        "makehuman_system_assets/makehuman_system_assets_cc0.zip"
    ),
    sha256="b542127a8e25547c7c29c19f2d1d2adb9a664c80396ecd694095dbc8028a0107",
    size_bytes=280737770,
    license_name="CC0",
    source_page="https://static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html",
)


MPFB2_ASSET_PACK_MANIFESTS = {MAKEHUMAN_SYSTEM_ASSETS.asset_pack_id: MAKEHUMAN_SYSTEM_ASSETS}
