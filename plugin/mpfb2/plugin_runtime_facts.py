"""Runtime facts and safe Blender probe for the MPFB2 provider."""

from __future__ import annotations

from dataclasses import dataclass

from modules.plugin.src.taxonomy_plugin_vo import BlenderVersion


@dataclass(frozen=True)
class Mpfb2RuntimeFacts:
    """Facts discovered from a Blender runtime without importing MPFB2 internals."""

    blender_version: BlenderVersion
    installed: bool
    active: bool


def probe_blender_runtime(runtime: object | None = None) -> Mpfb2RuntimeFacts:
    """Probe Blender app and enabled add-on registry through public attributes."""
    candidate = runtime or _load_blender_runtime()
    if candidate is None:
        return Mpfb2RuntimeFacts(
            blender_version=BlenderVersion("0.0"),
            installed=False,
            active=False,
        )

    app = getattr(candidate, "app", None)
    version = _read_blender_version(app)
    addons = _read_enabled_addons(candidate)
    active = any(_is_mpfb2_name(name) for name in addons) or _has_mpfb2_operator(candidate)
    return Mpfb2RuntimeFacts(
        blender_version=version,
        installed=active,
        active=active,
    )


def _load_blender_runtime() -> object | None:
    """Load bpy only when the probe is explicitly invoked inside Blender."""
    try:
        import bpy
    except ImportError:
        return None
    return bpy


def _read_blender_version(app: object | None) -> BlenderVersion:
    """Read the public bpy.app.version tuple."""
    version = getattr(app, "version", (0, 0, 0))
    return BlenderVersion(".".join(str(part) for part in version[:3]))


def _read_enabled_addons(runtime: object) -> tuple[str, ...]:
    """Read enabled add-on keys without importing provider modules."""
    context = getattr(runtime, "context", None)
    preferences = getattr(context, "preferences", None)
    addons = getattr(preferences, "addons", None)
    keys = getattr(addons, "keys", None)
    if not callable(keys):
        return ()
    return tuple(str(key) for key in keys())


def _has_mpfb2_operator(runtime: object) -> bool:
    """Detect an enabled modern extension through its public operator namespace."""
    operators = getattr(runtime, "ops", None)
    mpfb_namespace = getattr(operators, "mpfb", None)
    return callable(getattr(mpfb_namespace, "create_human", None))


def _is_mpfb2_name(name: str) -> bool:
    """Match public add-on registry names without relying on private modules."""
    normalized = name.casefold().replace("-", "_")
    return normalized in {"mpfb", "mpfb2"} or normalized.endswith(".mpfb")
