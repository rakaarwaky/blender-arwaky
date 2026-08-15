"""Canonical schemas for optional plugin package lifecycle actions."""

from __future__ import annotations

PLUGIN_ACTION_SCHEMAS: dict[str, dict[str, object]] = {
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
            "install_path": {"type": "string", "required": False, "default": ""},
        },
    },
    "verify_plugin": {
        "description": "Verify a cached plugin package checksum and archive safety",
        "parameters": {
            "plugin_id": {"type": "string", "required": True},
            "source_url": {"type": "string", "required": False, "default": ""},
            "sha256": {"type": "string", "required": True},
            "cache_path": {"type": "string", "required": True},
            "install_path": {"type": "string", "required": False, "default": ""},
        },
    },
    "install_plugin": {
        "description": "Verify and install a plugin package atomically",
        "parameters": {
            "plugin_id": {"type": "string", "required": True},
            "source_url": {"type": "string", "required": False, "default": ""},
            "sha256": {"type": "string", "required": True},
            "cache_path": {"type": "string", "required": True},
            "install_path": {"type": "string", "required": True},
        },
    },
    "remove_plugin": {
        "description": "Remove an installed plugin after explicit confirmation",
        "destructive_flag": True,
        "parameters": {
            "plugin_id": {"type": "string", "required": True},
            "source_url": {"type": "string", "required": False, "default": ""},
            "sha256": {"type": "string", "required": False, "default": ""},
            "cache_path": {"type": "string", "required": False, "default": ""},
            "install_path": {"type": "string", "required": True},
        },
    },
}
