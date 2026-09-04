from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Mpfb2CreateCharacterRequest:
    """Canonical parameters accepted by the MPFB2 character operation."""

    name: str = "MPFB_Human"


@dataclass(frozen=True)
class Mpfb2RandomizeCharacterRequest:
    """Canonical parameters for creating one MPFB2 random human."""

    name: str = "MPFB_RandomHuman"
    seed: int = 0


@dataclass(frozen=True)
class Mpfb2AssetPackRequest:
    """Canonical parameters for installing one approved MPFB2 asset pack."""

    asset_pack_id: str = "makehuman_system_assets"
    cache_path: str = ""
    sha256: str = ""


@dataclass(frozen=True)
class Mpfb2RemoveCharacterRequest:
    """Canonical parameters for deleting one verified MPFB2 character."""

    object_name: str
    confirm: bool = False


def _validate_name(name: str, default: str) -> str:
    value = name.strip() or default
    if len(value) > 64:
        raise ValueError("character name must not exceed 64 characters")
    if any(ord(character) < 32 for character in value):
        raise ValueError("character name contains a forbidden control character")
    return value


def map_create_character(request: Mpfb2CreateCharacterRequest) -> dict[str, object]:
    """Map the canonical provider request to one fixed Blender wire action."""
    return {
        "type": "create_character",
        "params": {"plugin_id": "mpfb2", "name": _validate_name(request.name, "MPFB_Human")},
    }


def map_randomize_character(request: Mpfb2RandomizeCharacterRequest) -> dict[str, object]:
    """Map randomization to the one public MPFB2 random-human operator."""
    if isinstance(request.seed, bool) or not isinstance(request.seed, int) or request.seed < 0:
        raise ValueError("seed must be an integer greater than or equal to zero")
    if not math.isfinite(float(request.seed)):
        raise ValueError("seed must be finite")
    return {
        "type": "randomize_character",
        "params": {
            "plugin_id": "mpfb2",
            "name": _validate_name(request.name, "MPFB_RandomHuman"),
            "seed": request.seed,
        },
    }


def map_install_mpfb_asset_pack(request: Mpfb2AssetPackRequest) -> dict[str, object]:
    """Map one verified asset pack to the bounded Blender provider handler."""
    if request.asset_pack_id != "makehuman_system_assets":
        raise ValueError("only makehuman_system_assets is currently mapped")
    cache_path = Path(request.cache_path).expanduser()
    if not cache_path.is_absolute():
        raise ValueError("cache_path must be absolute")
    digest = request.sha256.lower().strip()
    if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
        raise ValueError("sha256 must be a 64-character hexadecimal digest")
    return {
        "type": "install_mpfb_asset_pack",
        "params": {
            "plugin_id": "mpfb2",
            "asset_pack_id": request.asset_pack_id,
            "cache_path": str(cache_path),
            "sha256": digest,
        },
    }


def map_inspect_mpfb_assets() -> dict[str, object]:
    """Map asset readiness inspection to the bounded Blender provider handler."""
    return {"type": "inspect_mpfb_assets", "params": {"plugin_id": "mpfb2"}}


def map_remove_character(request: Mpfb2RemoveCharacterRequest) -> dict[str, object]:
    """Map removal to the bounded Arwaky-owned character closure handler."""
    object_name = request.object_name.strip()
    if not object_name:
        raise ValueError("object_name is required")
    if len(object_name) > 128 or any(ord(character) < 32 for character in object_name):
        raise ValueError("object_name must be 1-128 characters without control characters")
    if request.confirm is not True:
        raise ValueError("remove-character requires confirm=true")
    return {
        "type": "remove_character",
        "params": {"plugin_id": "mpfb2", "object_name": object_name, "confirm": True},
    }
