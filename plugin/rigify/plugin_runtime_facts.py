from __future__ import annotations

from dataclasses import dataclass

from modules.plugin.src.taxonomy_plugin_vo import BlenderVersion


@dataclass(frozen=True)
class RigifyRuntimeFacts:
    """Facts discovered from Blender without importing Rigify internals."""

    blender_version: BlenderVersion
    installed: bool
    active: bool


def probe_blender_runtime(runtime: object | None = None) -> RigifyRuntimeFacts:
    """Probe Blender version and public Rigify availability indicators."""
    candidate = runtime or _load_blender_runtime()
    if candidate is None:
        return RigifyRuntimeFacts(BlenderVersion("0.0"), False, False)

    version = _read_blender_version(getattr(candidate, "app", None))
    addons = _read_enabled_addons(candidate)
    active = any(_is_rigify_name(name) for name in addons) or _has_rigify_operator(candidate)
    return RigifyRuntimeFacts(version, active, active)


def _load_blender_runtime() -> object | None:
    """Load bpy only when called inside Blender."""
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
    """Read enabled add-on names without importing provider modules."""
    context = getattr(runtime, "context", None)
    preferences = getattr(context, "preferences", None)
    addons = getattr(preferences, "addons", None)
    keys = getattr(addons, "keys", None)
    return tuple(str(key) for key in keys()) if callable(keys) else ()


def _has_rigify_operator(runtime: object) -> bool:
    """Detect Rigify through its public human metarig operator."""
    operators = getattr(runtime, "ops", None)
    object_namespace = getattr(operators, "object", None)
    return callable(getattr(object_namespace, "armature_human_metarig_add", None))


def _is_rigify_name(name: str) -> bool:
    """Match public add-on registry names conservatively."""
    normalized = name.casefold().replace("-", "_")
    return normalized in {"rigify", "rigify.__init__"} or normalized.endswith(".rigify")
