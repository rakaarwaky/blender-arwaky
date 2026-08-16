"""Safe plugin package acquisition and Blender lifecycle capability."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

from .contract_plugin_package_protocol import PluginPackageProtocol
from .taxonomy_plugin_vo import (
    PluginActionName,
    PluginCachePath,
    PluginId,
    PluginInstallPath,
    PluginMessage,
    PluginPackageRequestVO,
    PluginPackageResultVO,
)


class PluginPackageCapability(PluginPackageProtocol):
    """Download, verify, install, and control explicit Blender plugin packages."""

    _MAX_PACKAGE_BYTES = 100 * 1024 * 1024
    _ACTIONS = {
        "download_plugin",
        "verify_plugin",
        "install_plugin",
        "enable_plugin",
        "disable_plugin",
        "remove_plugin",
    }

    def execute(
        self,
        action: PluginActionName,
        request: PluginPackageRequestVO,
    ) -> PluginPackageResultVO:
        """Run one allow-listed package lifecycle action."""
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
                self._install(request)
                return self._result(request, action, True, "installed")
            if action_name == "enable_plugin":
                self._enable(request)
                return self._result(request, action, True, "enabled")
            if action_name == "disable_plugin":
                self._disable(request)
                return self._result(request, action, True, "disabled")
            self._remove(request)
            return self._result(request, action, True, "removed")
        except (
            OSError,
            RuntimeError,
            ValueError,
            subprocess.SubprocessError,
            urllib.error.URLError,
            zipfile.BadZipFile,
        ) as error:
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
        """Verify SHA-256 and reject unsafe legacy or extension archives."""
        package = self._safe_path(request.cache_path)
        expected = str(request.sha256).lower()
        if len(expected) != 64 or any(character not in "0123456789abcdef" for character in expected):
            raise ValueError("sha256 must be a 64-character hexadecimal digest")
        if hashlib.sha256(package.read_bytes()).hexdigest() != expected:
            raise ValueError("plugin package checksum mismatch")
        with zipfile.ZipFile(package) as archive:
            self._validate_archive(archive)

    def _install(self, request: PluginPackageRequestVO) -> None:
        """Install through Blender when an executable is supplied, otherwise extract legacy ZIP."""
        self._verify(request)
        if request.blender_path:
            self._run_extension_command(request, "install-file", enable=request.enable)
            return
        if not request.install_path:
            raise ValueError("install_path or blender_path is required")
        package = self._safe_path(request.cache_path)
        destination = self._safe_path(request.install_path)
        if destination.exists():
            raise ValueError("plugin install path already exists")
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=destination.parent) as temporary:
            with zipfile.ZipFile(package) as archive:
                archive.extractall(temporary)
            self._normalize_package_root(Path(temporary)).rename(destination)

    def _enable(self, request: PluginPackageRequestVO) -> None:
        """Enable an extension by reinstalling its verified package with Blender --enable."""
        self._verify(request)
        self._require_blender(request)
        self._run_extension_command(request, "install-file", enable=True)

    def _disable(self, request: PluginPackageRequestVO) -> None:
        """Disable a named extension through Blender's official extension operator."""
        self._require_blender(request)
        extension_id = self._extension_id(request)
        repository_id = str(request.repository_id).strip().casefold().replace("-", "_")
        if repository_id != "user_default":
            raise ValueError("disable currently supports only the mapped user_default repository")
        expression = (
            "import bpy; "
            "repos=bpy.context.preferences.extensions.repos; "
            "repo=next((item for item in repos if item.name.casefold().replace(' ', '_') == 'user_default'), None); "
            "raise RuntimeError('user_default repository not found') if repo is None else None; "
            f"result=bpy.ops.extensions.package_disable(repo_directory=repo.directory, pkg_id={extension_id!r}); "
            "raise RuntimeError(str(result)) if 'FINISHED' not in result else None"
        )
        self._run_blender(request, ("--background", "--python-expr", expression))

    def _remove(self, request: PluginPackageRequestVO) -> None:
        """Remove an installed extension through Blender or an explicit legacy path."""
        if request.blender_path:
            self._require_extension_id(request)
            self._run_blender(
                request, ("--background", "--command", "extension", "remove", self._extension_id(request))
            )
            return
        destination = self._safe_path(request.install_path)
        if not destination.exists() or destination.is_symlink() or not destination.is_dir():
            raise ValueError("plugin install path is not a directory")
        shutil.rmtree(destination)

    def _run_extension_command(
        self,
        request: PluginPackageRequestVO,
        subcommand: str,
        *,
        enable: bool,
    ) -> None:
        """Run Blender's explicit extension install-file command."""
        enable_arguments = ("--enable",) if enable else ()
        self._run_blender(
            request,
            (
                "--background",
                "--command",
                "extension",
                subcommand,
                "--repo",
                str(request.repository_id),
                *enable_arguments,
                str(self._safe_path(request.cache_path)),
            ),
        )

    @staticmethod
    def _run_blender(request: PluginPackageRequestVO, arguments: tuple[str, ...]) -> None:
        """Run a fixed Blender command without shell interpretation or user code."""
        blender_path = PluginPackageCapability._safe_path(request.blender_path)
        completed = subprocess.run(
            (str(blender_path), *arguments), capture_output=True, text=True, timeout=120, check=False
        )
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout).strip()[-1000:]
            raise RuntimeError(detail or "Blender plugin command failed")

    @staticmethod
    def _validate_archive(archive: zipfile.ZipFile) -> None:
        """Reject traversal, absolute paths, symlinks, and unsupported archives."""
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
        names = {Path(member.filename).name for member in members}
        if "__init__.py" not in names and "blender_manifest.toml" not in names:
            raise ValueError("plugin package must contain __init__.py or blender_manifest.toml")

    @staticmethod
    def _normalize_package_root(directory: Path) -> Path:
        """Accept a flat legacy archive or one top-level package directory."""
        entries = [entry for entry in directory.iterdir() if entry.name != "__MACOSX"]
        if len(entries) == 1 and entries[0].is_dir():
            return entries[0]
        return directory

    @staticmethod
    def _safe_path(value: PluginCachePath | PluginInstallPath | None) -> Path:
        """Reject empty, relative, and traversal-containing filesystem paths."""
        raw = str(value or "")
        path = Path(raw)
        if not raw or not path.is_absolute() or ".." in path.parts:
            raise ValueError("plugin path must be absolute and traversal-free")
        return path

    @staticmethod
    def _extension_id(request: PluginPackageRequestVO) -> str:
        """Return the explicitly mapped Blender extension id."""
        return str(PluginPackageCapability._require_extension_id(request))

    @staticmethod
    def _require_extension_id(request: PluginPackageRequestVO) -> PluginId:
        """Require a provider-mapped extension id rather than accepting arbitrary module names."""
        if not request.extension_id:
            raise ValueError("extension_id is required for Blender extension lifecycle")
        return request.extension_id

    @staticmethod
    def _require_blender(request: PluginPackageRequestVO) -> None:
        """Require an explicit Blender executable for runtime lifecycle operations."""
        if not request.blender_path:
            raise ValueError("blender_path is required for Blender extension lifecycle")

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
