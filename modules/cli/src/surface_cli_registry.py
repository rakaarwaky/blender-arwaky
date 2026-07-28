"""Registry: Manages active Blender instance state via registry.json.

FR-CLI-001: Parse and Route Commands — registry provides instance state for command routing decisions
"""

import json
import os
import threading
from dataclasses import dataclass
from typing import Optional

REGISTRY_FILE = "registry.json"
DEFAULT_PORT = 9876


@dataclass
class RegistryState:
    """State of the active Blender instance."""

    active_entity: str | None = None
    port: int = DEFAULT_PORT
    pid: int | None = None


class Registry:
    """Thread-safe singleton managing registry.json."""

    _instance: Optional["Registry"] = None
    _lock = threading.Lock()

    def __new__(cls, registry_path: str = REGISTRY_FILE) -> "Registry":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._path = registry_path
                    cls._instance._state = RegistryState()
                    cls._instance._file_lock = threading.Lock()
                    cls._instance._load()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset singleton (for testing)."""
        with cls._lock:
            cls._instance = None

    def _load(self) -> None:
        """Load state from registry.json."""
        if os.path.exists(self._path):
            try:
                with open(self._path) as f:
                    data = json.load(f)
                self._state = RegistryState(
                    active_entity=data.get("active_entity"),
                    port=data.get("port", DEFAULT_PORT),
                    pid=data.get("pid"),
                )
            except (json.JSONDecodeError, KeyError):
                self._state = RegistryState()

    def _save(self) -> None:
        """Save state to registry.json."""
        with self._file_lock:
            data = {
                "active_entity": self._state.active_entity,
                "port": self._state.port,
                "pid": self._state.pid,
            }
            with open(self._path, "w") as f:
                json.dump(data, f, indent=2)

    def get_active(self) -> str | None:
        """Get the active entity filepath."""
        return self._state.active_entity

    def get_port(self) -> int:
        """Get the active port."""
        return self._state.port

    def get_pid(self) -> int | None:
        """Get the active Blender PID."""
        return self._state.pid

    def is_active(self) -> bool:
        """Check if a Blender instance is active."""
        return self._state.active_entity is not None

    def set_active(self, filepath: str, pid: int, port: int = DEFAULT_PORT) -> None:
        """Register an active Blender instance."""
        self._state = RegistryState(
            active_entity=filepath,
            port=port,
            pid=pid,
        )
        self._save()

    def clear(self) -> None:
        """Clear the active instance (after close)."""
        self._state = RegistryState()
        self._save()

    def assert_no_active(self) -> str:
        """Check if Blender is already active. Returns error message or empty string."""
        if self._state.active_entity:
            return (
                f"Blender sedang aktif digunakan oleh '{self._state.active_entity}'. "
                f"Tutup terlebih dahulu dengan: blender-arwaky close --filepath '{self._state.active_entity}'"
            )
        return ""

    def assert_active(self, filepath: str) -> str:
        """Check if the specified entity is active. Returns error message or empty string."""
        if not self._state.active_entity:
            return "Tidak ada Blender yang aktif. Jalankan: blender-arwaky init --filepath <path>"
        if self._state.active_entity != filepath:
            return (
                f"Entity '{filepath}' tidak terdaftar. "
                f"Active entity: '{self._state.active_entity}'. "
                f"Jalankan init terlebih dahulu."
            )
        return ""
