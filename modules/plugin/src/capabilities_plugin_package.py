"""Safe plugin package acquisition and filesystem lifecycle capability."""

from __future__ import annotations

import hashlib
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

from .contract_plugin_package_protocol import PluginPackageProtocol
from .taxonomy_plugin_vo import (
    PluginActionName,
    PluginCachePath,
    PluginInstallPath,
    PluginMessage,
    PluginPackageRequestVO,
    PluginPackageResultVO,
)


class PluginPackageCapability(PluginPackageProtocol):
    """Download and install verified Blender extension packages."""

    _MAX_PACKAGE_BYTES = 100 * 1024 * 1024
    _ACTIONS = {"download_plugin", "verify_plugin", "install_plugin", "remove_plugin"}

    def execute(
        self,
        action: PluginActionName,
        request: PluginPackageRequestVO,
    ) -> PluginPackageResultVO:
        """Run one allow-listed filesystem/package lifecycle operation."""
        action_name = str(action)
        if action_name not in self._ACTIONS:
            return self._result(request, action, False, "unsupported")
        try:
            if action_name == "download_plugin":
                self._download(request)
                return self._result(request, action, True, "downloaded")
            if action_name == "verify_plugin":
                self._verify(request)
                return self._result(request, action, True, "verified")
            if action_name == "install_plugin":
                self._verify(request)
                self._install(request)
                return self._result(request, action, True, "installed")
            self._remove(request)
            return self._result(request, action, True, "removed")
        except (OSError, ValueError, urllib.error.URLError, zipfile.BadZipFile) as error:
            return self._result(request, action, False, str(error))

    def _download(self, request: PluginPackageRequestVO) -> None:
        """Download only from HTTPS and enforce a bounded package size."""
        url = str(request.source_url)
        if not url.startswith("https://"):
            raise ValueError("plugin source must use HTTPS")
        destination = self._safe_path(request.cache_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(url, timeout=30) as response, destination.open("wb") as output:  # nosec B310
            total = 0
            while chunk := response.read(1024 * 1024):
                total += len(chunk)
                if total > self._MAX_PACKAGE_BYTES:
                    destination.unlink(missing_ok=True)
                    raise ValueError("plugin package exceeds maximum size")
                output.write(chunk)

    def _verify(self, request: PluginPackageRequestVO) -> None:
        """Verify SHA-256 and reject unsafe or malformed extension archives."""
        package = self._safe_path(request.cache_path)
        expected = str(request.sha256).lower()
        if len(expected) != 64 or any(character not in "0123456789abcdef" for character in expected):
            raise ValueError("sha256 must be a 64-character hexadecimal digest")
        digest = hashlib.sha256(package.read_bytes()).hexdigest()
        if digest != expected:
            raise ValueError("plugin package checksum mismatch")
        with zipfile.ZipFile(package) as archive:
            self._validate_archive(archive)

    def _install(self, request: PluginPackageRequestVO) -> None:
        """Extract a verified package atomically into the requested install path."""
        package = self._safe_path(request.cache_path)
        destination = self._safe_path(request.install_path)
        if destination.exists():
            raise ValueError("plugin install path already exists")
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=destination.parent) as temporary:
            temporary_path = Path(temporary)
            with zipfile.ZipFile(package) as archive:
                archive.extractall(temporary_path)
            source = self._normalize_package_root(temporary_path)
            source.rename(destination)

    def _remove(self, request: PluginPackageRequestVO) -> None:
        """Remove only the explicit plugin install path."""
        destination = self._safe_path(request.install_path)
        if not destination.exists():
            raise ValueError("plugin install path not found")
        if destination.is_symlink() or not destination.is_dir():
            raise ValueError("plugin install path is not a directory")
        shutil.rmtree(destination)

    @staticmethod
    def _validate_archive(archive: zipfile.ZipFile) -> None:
        """Reject traversal, absolute paths, symlinks, and empty archives."""
        members = archive.infolist()
        if not members:
            raise ValueError("plugin package is empty")
        for member in members:
            path = PurePosixPath(member.filename)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError("plugin package contains an unsafe path")
            if member.is_dir():
                continue
            mode = (member.external_attr >> 16) & 0o170000
            if mode == 0o120000:
                raise ValueError("plugin package cannot contain symlinks")
        if not any(Path(member.filename).name == "__init__.py" for member in members):
            raise ValueError("plugin package must contain __init__.py")

    @staticmethod
    def _normalize_package_root(directory: Path) -> Path:
        """Accept a flat extension archive or one top-level package directory."""
        entries = [entry for entry in directory.iterdir() if entry.name != "__MACOSX"]
        if len(entries) == 1 and entries[0].is_dir():
            return entries[0]
        return directory

    @staticmethod
    def _safe_path(value: PluginCachePath | PluginInstallPath) -> Path:
        """Reject empty, relative, and traversal-containing filesystem paths."""
        raw = str(value)
        path = Path(raw)
        if not raw or not path.is_absolute() or ".." in path.parts:
            raise ValueError("plugin path must be absolute and traversal-free")
        return path

    @staticmethod
    def _result(
        request: PluginPackageRequestVO,
        action: PluginActionName,
        success: bool,
        message: str,
    ) -> PluginPackageResultVO:
        """Build the normalized package result."""
        return PluginPackageResultVO(
            plugin_id=request.plugin_id,
            operation=action,
            success=success,
            package_path=PluginCachePath(str(request.cache_path)),
            install_path=PluginInstallPath(str(request.install_path)),
            message=PluginMessage(message),
        )
