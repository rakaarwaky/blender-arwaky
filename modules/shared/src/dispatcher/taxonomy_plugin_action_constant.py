"""Canonical schemas for optional plugin package lifecycle actions."""

from __future__ import annotations

PLUGIN_ACTION_SCHEMAS: dict[str, dict[str, object]] = {
    "randomize_character": {
        "description": "Create one deterministic or newly seeded random MPFB2 human character",
        "parameters": {
            "plugin_id": {"type": "string", "required": False, "default": "mpfb2"},
            "name": {"type": "string", "required": False, "default": "MPFB_RandomHuman"},
            "seed": {"type": "integer", "required": False, "default": 0, "minimum": 0},
        },
    },
    "remove_character": {
        "description": "Remove one verified MPFB2 character closure from the Blender scene",
        "destructive_flag": True,
        "parameters": {
            "plugin_id": {"type": "string", "required": False, "default": "mpfb2"},
            "object_name": {"type": "string", "required": True},
            "confirm": {"type": "boolean", "required": True, "default": False},
        },
    },
    "create_character": {
        "description": "Create one MPFB2 human character through the explicitly mapped provider operation",
        "parameters": {
            "plugin_id": {"type": "string", "required": False, "default": "mpfb2"},
            "name": {"type": "string", "required": False, "default": "MPFB_Human"},
        },
    },
    "list_plugins": {
        "description": "List registered optional providers and their runtime capability metadata",
        "parameters": {},
    },
    "download_plugin": {
        "description": "Download a plugin package to a verified local cache",
        "parameters": {
            "plugin_id": {"type": "string", "required": True},
            "source_url": {"type": "string", "required": True},
            "sha256": {"type": "string", "required": True},
            "cache_path": {"type": "string", "required": True},
        },
    },
    "verify_plugin": {
        "description": "Verify a cached plugin package checksum and archive safety",
        "parameters": {
            "plugin_id": {"type": "string", "required": True},
            "sha256": {"type": "string", "required": True},
            "cache_path": {"type": "string", "required": True},
        },
    },
    "install_plugin": {
        "description": "Verify and install a plugin package through the mapped Blender lifecycle",
        "parameters": {
            "plugin_id": {"type": "string", "required": True},
            "sha256": {"type": "string", "required": True},
            "cache_path": {"type": "string", "required": True},
            "blender_path": {"type": "string", "required": True},
            "repository_id": {"type": "string", "required": False, "default": "user_default"},
            "extension_id": {"type": "string", "required": True},
            "enable": {"type": "boolean", "required": False, "default": True},
        },
    },
    "enable_plugin": {
        "description": "Enable an installed Blender plugin through its mapped extension id",
        "parameters": {
            "plugin_id": {"type": "string", "required": True},
            "sha256": {"type": "string", "required": True},
            "cache_path": {"type": "string", "required": True},
            "blender_path": {"type": "string", "required": True},
            "repository_id": {"type": "string", "required": False, "default": "user_default"},
            "extension_id": {"type": "string", "required": True},
        },
    },
    "disable_plugin": {
        "description": "Disable an installed Blender plugin through its mapped extension id",
        "destructive_flag": True,
        "parameters": {
            "plugin_id": {"type": "string", "required": True},
            "blender_path": {"type": "string", "required": True},
            "extension_id": {"type": "string", "required": True},
        },
    },
    "remove_plugin": {
        "description": "Remove an installed Blender plugin through its mapped extension id",
        "destructive_flag": True,
        "parameters": {
            "plugin_id": {"type": "string", "required": True},
            "blender_path": {"type": "string", "required": True},
            "extension_id": {"type": "string", "required": True},
        },
    },
}
