"""Utility: File format detection via magic bytes.

Provides _detect_format_by_magic for validating actual file content
against expected formats in import capabilities.
"""

from __future__ import annotations

# Magic bytes signatures for supported asset formats.
# Used by _detect_format_by_magic to validate actual file content.
_MAGIC_SIGNATURES: dict[str, list[bytes]] = {
    "glb": [b"glTF"],
    "gltf": [b"{", b"["],  # JSON-based; check heuristically
    "png": [b"\x89PNG"],
    "jpg": [b"\xFF\xD8\xFF"],
    "jpeg": [b"\xFF\xD8\xFF"],
    "fbx": [b"FBX"],
    "exr": [b"\x76\x2f\x31\x01"],
}


def detect_format_by_magic(file_path: str) -> str | None:
    """Detect file format from magic bytes (first 16 bytes).

    Returns the format key (e.g. 'glb', 'png') or None if
    the signature is not recognised.
    """
    try:
        with open(file_path, "rb") as f:
            header = f.read(16)
    except OSError:
        return None

    for fmt, signatures in _MAGIC_SIGNATURES.items():
        for sig in signatures:
            if header[: len(sig)] == sig:
                return fmt

    return None
