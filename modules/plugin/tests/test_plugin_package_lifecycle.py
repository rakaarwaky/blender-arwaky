from __future__ import annotations

import hashlib
import subprocess
import zipfile
from pathlib import Path

from modules.plugin.src.capabilities_plugin_package import PluginPackageCapability
from modules.plugin.src.taxonomy_plugin_vo import (
    PluginActionName,
    PluginCachePath,
    PluginId,
    PluginInstallPath,
    PluginPackageRequestVO,
    PluginSha256,
    PluginSourceUrl,
)


def _request(tmp_path: Path) -> PluginPackageRequestVO:
    package = tmp_path / "mpfb.zip"
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("blender_manifest.toml", 'id = "mpfb"\nversion = "2.0.17"\n')
    return PluginPackageRequestVO(
        plugin_id=PluginId("mpfb2"),
        source_url=PluginSourceUrl("https://example.invalid/mpfb.zip"),
        sha256=PluginSha256(hashlib.sha256(package.read_bytes()).hexdigest()),
        cache_path=PluginCachePath(str(package)),
        install_path=PluginInstallPath(""),
        blender_path=PluginInstallPath("/usr/bin/blender"),
        extension_id=PluginId("mpfb"),
    )


def test_legacy_install_and_remove_are_idempotent(tmp_path) -> None:
    package = tmp_path / "legacy.zip"
    install_path = tmp_path / "legacy-provider"
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("__init__.py", "provider = True\n")
    request = PluginPackageRequestVO(
        plugin_id=PluginId("legacy"),
        source_url=PluginSourceUrl("https://example.invalid/legacy.zip"),
        sha256=PluginSha256(hashlib.sha256(package.read_bytes()).hexdigest()),
        cache_path=PluginCachePath(str(package)),
        install_path=PluginInstallPath(str(install_path)),
    )
    capability = PluginPackageCapability()

    assert capability.execute(PluginActionName("install_plugin"), request).success
    assert capability.execute(PluginActionName("install_plugin"), request).success
    assert (install_path / "__init__.py").is_file()  # nosec B101
    assert capability.execute(PluginActionName("remove_plugin"), request).success
    assert capability.execute(PluginActionName("remove_plugin"), request).success
    assert not install_path.exists()  # nosec B101


def test_extension_lifecycle_uses_allowlisted_blender_commands(tmp_path, monkeypatch) -> None:
    calls: list[tuple[str, ...]] = []

    def fake_run(command, **kwargs):
        del kwargs
        calls.append(tuple(command))
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    capability = PluginPackageCapability()
    request = _request(tmp_path)

    assert capability.execute(PluginActionName("install_plugin"), request).success
    assert capability.execute(PluginActionName("enable_plugin"), request).success
    assert capability.execute(PluginActionName("disable_plugin"), request).success
    assert capability.execute(PluginActionName("remove_plugin"), request).success

    assert calls[0][1:7] == ("--background", "--command", "extension", "install-file", "--repo", "user_default")
    assert "--enable" in calls[0]
    assert "--enable" in calls[1]
    assert calls[2][1:3] == ("--background", "--python-expr")
    assert "bpy.ops.extensions.package_disable" in calls[2][3]
    assert "repo_directory=repo.directory" in calls[2][3]
    assert calls[3][1:5] == ("--background", "--command", "extension", "remove")
    assert calls[3][5] == "mpfb"
