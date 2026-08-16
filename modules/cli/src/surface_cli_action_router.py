"""Execution adapter used by the CLI-backed dispatcher composition root."""

from __future__ import annotations

import asyncio
import json
from dataclasses import asdict, is_dataclass

from modules.plugin.src.taxonomy_plugin_vo import (
    PluginActionName,
    PluginCachePath,
    PluginId,
    PluginInstallPath,
    PluginMessage,
    PluginPackageRequestVO,
    PluginSha256,
    PluginSourceUrl,
)
from modules.shared.src.asset.taxonomy_asset_vo import (
    AssetDownloadCacheVO,
    AssetExtractArchiveVO,
)
from modules.shared.src.cli.capabilities_cli_registry import Registry
from modules.shared.src.common.taxonomy_core_vo import (
    AssetId,
    AssetType,
    FilePath,
    JobId,
    MaxSize,
    ProviderName,
    SearchQuery,
)
from modules.shared.src.gateway.capabilities_socket_client import BlenderSocketClient
from modules.shared.src.job.taxonomy_job_vo import (
    CancellationReason,
    CancelTaskCommand,
    CorrelationId,
    CreateTaskCommand,
    OperationType,
    TaskMetadata,
)
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    BridgeEndpointVO,
    LauncherConfigVO,
    LaunchMode,
    LaunchRequestVO,
    ProbeDepth,
)


class CliActionRouter:
    """Route local feature actions locally and Blender actions over the active TCP bridge."""

    _ASSET_ACTIONS = {
        "search_assets",
        "get_provider_metadata",
        "download_asset",
        "extract_asset",
    }
    _PLUGIN_PROVIDER_ACTIONS = {
        "create_character",
        "randomize_character",
        "remove_character",
        "install_mpfb_asset_pack",
        "inspect_mpfb_assets",
    }
    _PLUGIN_ACTIONS = {
        "list_plugins",
        "download_plugin",
        "verify_plugin",
        "install_plugin",
        "enable_plugin",
        "disable_plugin",
        "remove_plugin",
        "download_mpfb_asset_pack",
        "verify_mpfb_asset_pack",
    }
    _LAUNCHER_ACTIONS = {
        "launch_blender",
        "shutdown_blender",
        "get_runtime_status",
        "register_executable",
    }

    def __init__(
        self,
        launcher: object,
        *,
        job: object | None = None,
        config: object | None = None,
        security: object | None = None,
        asset: object | None = None,
        plugin: object | None = None,
    ) -> None:
        self._launcher = launcher
        self._job = job
        self._config = config
        self._security = security
        self._asset = asset
        self._plugin = plugin

    def execute_action(self, action_name: str, params: dict[str, object]) -> dict[str, object]:
        if action_name in self._LAUNCHER_ACTIONS:
            return self._execute_launcher(action_name, params)
        if action_name in {"submit_task", "list_tasks", "get_capacity_status", "get_task_status", "cancel_task"}:
            return self._execute_job(action_name, params)
        if action_name in {"get_config", "set_config"}:
            return self._execute_config(action_name, params)
        if action_name in self._ASSET_ACTIONS:
            return self._execute_asset(action_name, params)
        if action_name in self._PLUGIN_PROVIDER_ACTIONS:
            return self._execute_plugin_provider(action_name, params)
        if action_name in self._PLUGIN_ACTIONS:
            return self._execute_plugin(action_name, params)

        wire_action = action_name
        with BlenderSocketClient(port=Registry().get_port()) as client:
            response = client.send_command(wire_action, params)
        if response.get("status") != "success":
            raise RuntimeError(str(response.get("message", f"Action failed: {action_name}")))
        result = response.get("result", {})
        return result if isinstance(result, dict) else {"result": result}

    def _execute_asset(self, action_name: str, params: dict[str, object]) -> dict[str, object]:
        if action_name == "search_assets":
            query = SearchQuery(str(params.get("query", "curated")))
            providers = params.get("providers")
            provider_list = [str(value) for value in providers] if isinstance(providers, list) else None
            assets = asyncio.run(self._asset.search(query, provider_list))
            return {"assets": [asdict(asset) for asset in assets], "total": len(assets)}

        if action_name == "get_provider_metadata":
            provider = ProviderName(str(params.get("provider", "")).strip())
            asset_id = AssetId(str(params.get("asset_id", "")).strip())
            if not str(provider) or not str(asset_id):
                raise ValueError("provider and asset_id are required")
            return asyncio.run(self._asset.get_provider_metadata(provider, asset_id))

        if action_name == "download_asset":
            request = AssetDownloadCacheVO(
                provider=ProviderName(str(params.get("provider", "")).strip()),
                asset_id=AssetId(str(params.get("asset_id", "")).strip()),
                asset_type=AssetType(str(params.get("asset_type", "model")).strip()),
                cache_dir=FilePath(str(params.get("cache_dir", "")).strip()),
                resolution=str(params["resolution"]) if params.get("resolution") is not None else None,
                overwrite_policy=str(params.get("overwrite_policy", "reuse")),
                max_size=MaxSize(int(params["max_size"])) if params.get("max_size") is not None else None,
            )
            result = asyncio.run(self._asset.download_to_cache(request))
            return asdict(result)

        request = AssetExtractArchiveVO(
            artifact_path=FilePath(str(params.get("artifact_path", "")).strip()),
            destination=FilePath(str(params.get("destination", "")).strip()),
            max_entries=int(params.get("max_entries", 1000)),
            max_extracted_size=int(params.get("max_extracted_size", 1_073_741_824)),
            allow_symlinks=bool(params.get("allow_symlinks", False)),
        )
        result = asyncio.run(self._asset.extract_archive(request))
        return asdict(result)

    def _execute_plugin_provider(self, action_name: str, params: dict[str, object]) -> dict[str, object]:
        """Route explicitly mapped provider operations through the Blender bridge."""
        from plugin.mpfb2.plugin_operations import (
            Mpfb2AssetPackRequest,
            Mpfb2CreateCharacterRequest,
            Mpfb2RandomizeCharacterRequest,
            Mpfb2RemoveCharacterRequest,
            map_create_character,
            map_inspect_mpfb_assets,
            map_install_mpfb_asset_pack,
            map_randomize_character,
            map_remove_character,
        )

        plugin_id = str(params.get("plugin_id", "mpfb2")).strip()
        if plugin_id != "mpfb2":
            raise ValueError(f"{action_name} is mapped only to provider mpfb2")
        if action_name == "install_mpfb_asset_pack":
            command = map_install_mpfb_asset_pack(
                Mpfb2AssetPackRequest(
                    asset_pack_id=str(params.get("asset_pack_id", "makehuman_system_assets")),
                    cache_path=str(params.get("cache_path", "")),
                    sha256=str(params.get("sha256", "")),
                )
            )
        elif action_name == "inspect_mpfb_assets":
            command = map_inspect_mpfb_assets()
        elif action_name == "create_character":
            command = map_create_character(Mpfb2CreateCharacterRequest(name=str(params.get("name", "MPFB_Human"))))
        elif action_name == "randomize_character":
            command = map_randomize_character(
                Mpfb2RandomizeCharacterRequest(
                    name=str(params.get("name", "MPFB_RandomHuman")),
                    seed=params.get("seed", 0),
                )
            )
        elif action_name == "remove_character":
            command = map_remove_character(
                Mpfb2RemoveCharacterRequest(
                    object_name=str(params.get("object_name", "")),
                    confirm=params.get("confirm", False),
                )
            )
        else:
            raise ValueError(f"unsupported provider action: {action_name}")
        with BlenderSocketClient(port=Registry().get_port()) as client:
            response = client.send_command(command["type"], command["params"])
        if response.get("status") != "success":
            raise RuntimeError(str(response.get("message", "MPFB2 character operation failed")))
        result = response.get("result", {})
        return result if isinstance(result, dict) else {"result": result}

    def _execute_plugin(self, action_name: str, params: dict[str, object]) -> dict[str, object]:
        if self._plugin is None:
            raise RuntimeError("Plugin container is not configured")
        if action_name == "list_plugins":
            aggregate = self._plugin.aggregate()
            return {
                "plugins": [asdict(item) for item in aggregate.health_check()],
                "capabilities": [str(item) for item in aggregate.capabilities()],
            }
        is_asset_pack = action_name in {"download_mpfb_asset_pack", "verify_mpfb_asset_pack"}
        request = PluginPackageRequestVO(
            plugin_id=PluginId(str(params.get("plugin_id", params.get("asset_pack_id", ""))).strip()),
            source_url=PluginSourceUrl(str(params.get("source_url", "")).strip()),
            sha256=PluginSha256(str(params.get("sha256", "")).strip()),
            cache_path=PluginCachePath(str(params.get("cache_path", "")).strip()),
            install_path=PluginInstallPath(str(params.get("install_path", "")).strip()),
            blender_path=PluginInstallPath(str(params.get("blender_path", "")).strip())
            if params.get("blender_path")
            else None,
            repository_id=PluginMessage(str(params.get("repository_id", "user_default")).strip()),
            extension_id=PluginId(str(params.get("extension_id", "")).strip()) if params.get("extension_id") else None,
            enable=bool(params.get("enable", True)),
            asset_pack=is_asset_pack,
        )
        result = self._plugin.package().execute(PluginActionName(action_name), request)
        return asdict(result)

    def _execute_job(self, action_name: str, params: dict[str, object]) -> dict[str, object]:
        if action_name == "submit_task":
            operation_type = str(params.get("operation_type", "")).strip()
            if not operation_type:
                raise ValueError("operation_type is required")
            raw_metadata = params.get("metadata")
            metadata = None
            if raw_metadata is not None:
                if not isinstance(raw_metadata, dict):
                    raise ValueError("metadata must be an object")
                metadata = TaskMetadata({str(key): str(value) for key, value in raw_metadata.items()})
            correlation = str(params.get("correlation_id", "")).strip()
            result = self._job.submit_task(
                CreateTaskCommand(
                    operation_type=OperationType(operation_type),
                    correlation_id=CorrelationId(correlation) if correlation else None,
                    metadata=metadata,
                )
            )
            return asdict(result)

        if action_name == "list_tasks":
            snapshots = self._job.list_tasks()
            return {"tasks": [asdict(snapshot) for snapshot in snapshots], "count": len(snapshots)}

        if action_name == "get_capacity_status":
            return asdict(self._job.get_capacity_status())

        task_id = JobId(str(params.get("task_id", "")))
        if not str(task_id).strip():
            raise ValueError("task_id is required")
        if action_name == "get_task_status":
            return asdict(self._job.get_task_status(task_id))
        command = CancelTaskCommand(
            job_id=task_id,
            reason=CancellationReason(str(params.get("reason", "CLI cancellation"))),
        )
        result = self._job.cancel_task(command)
        if not result.accepted and result.outcome == "NOT_FOUND":
            raise LookupError(f"Task not found: {task_id}")
        return asdict(result)

    def _execute_config(self, action_name: str, params: dict[str, object]) -> dict[str, object]:
        if action_name == "get_config":
            key = str(params.get("key", ""))
            if key:
                value = self._config.get(key)
                return {"key": key, "value": self._config.redact_dict({key: value}).get(key)}
            return {"settings": self._config.redact_dict(self._config.get_snapshot().to_dict())}

        key = str(params.get("key", ""))
        if not key:
            raise ValueError("key is required")
        raw_value = params.get("value")
        if isinstance(raw_value, str):
            try:
                value = json.loads(raw_value)
            except json.JSONDecodeError:
                value = raw_value
        else:
            value = raw_value
        snapshot = self._config.set_config(key, value)
        return {"key": key, "value": self._config.redact_dict({key: snapshot.get(key)}).get(key)}

    def _execute_launcher(self, action_name: str, params: dict[str, object]) -> dict[str, object]:
        if action_name == "launch_blender":
            mode = LaunchMode(str(params.get("mode", LaunchMode.HEADLESS.value)))
            port = int(params.get("port", 9876))
            filepath = params.get("filepath")
            request = LaunchRequestVO(
                filepath=str(filepath) if filepath else None,
                mode=mode,
                bridge_endpoint=BridgeEndpointVO(port=port),
            )
            result = self._launcher.launch(request)
        elif action_name == "shutdown_blender":
            result = self._launcher.shutdown(force=bool(params.get("force", False)))
        elif action_name == "get_runtime_status":
            result = self._launcher.check_status(depth=ProbeDepth.FULL)
        else:
            path = params.get("path")
            result = self._launcher.locate_and_register(
                LauncherConfigVO(),
                str(path) if path else None,
            )
        if is_dataclass(result):
            return asdict(result)
        return result if isinstance(result, dict) else {"result": result}
