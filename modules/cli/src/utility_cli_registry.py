"""CLI registry — tracks active Blender instance state via registry.json.

Shared utility between CLI surface commands. Manages active entity, PID,
and port with thread-safe singleton access.
"""

from __future__ import annotations

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
                    instance = super().__new__(cls)
                    instance._path = registry_path
                    instance._state = RegistryState()
                    instance._file_lock = threading.Lock()
                    instance._load()
                    cls._instance = instance
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        with cls._lock:
            cls._instance = None

    def _load(self) -> None:
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
        with self._file_lock:
            data = {"active_entity": self._state.active_entity, "port": self._state.port, "pid": self._state.pid}
            with open(self._path, "w") as f:
                json.dump(data, f, indent=2)

    def get_active(self) -> str | None:
        return self._state.active_entity

    def get_port(self) -> int:
        return self._state.port

    def get_pid(self) -> int | None:
        return self._state.pid

    def is_active(self) -> bool:
        return self._state.active_entity is not None

    def set_active(self, filepath: str, pid: int, port: int = DEFAULT_PORT) -> None:
        self._state = RegistryState(active_entity=filepath, port=port, pid=pid)
        self._save()

    def clear(self) -> None:
        self._state = RegistryState()
        self._save()

    def assert_no_active(self) -> str:
        if self._state.active_entity:
            return f"Blender sedang aktif digunakan oleh '{self._state.active_entity}'. Tutup terlebih dahulu."
        return ""

    def assert_active(self, filepath: str) -> str:
        if not self._state.active_entity:
            return "Tidak ada Blender yang aktif. Jalankan: blender-arwaky init --filepath <path>"
        if self._state.active_entity != filepath:
            return f"Entity '{filepath}' tidak terdaftar. Active entity: '{self._state.active_entity}'."
        return ""
