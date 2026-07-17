"""
System Coordinator — Consolidated system-level services.

Merges: server_bootstrap_manager.py + system_utils_coordinator.py
Provides: config resolution, health checks, connection management, telemetry wrappers.
"""

import importlib
import logging
import os

from contract import ServerBootstrapManagerAggregate, SystemUtilsCoordinatorAggregate
from infrastructure.config_file_loader import get_config, get_project_root
from taxonomy import ConfigPath, ConfigValue, DirectoryPath, FilePath, ObjectName, SuccessFlag

logger = logging.getLogger("BlenderMCPServer")


# ═══════════════════════════════════════════════════════════════════════════════
# Infrastructure lazy loaders (from system_utils_coordinator.py)
# ═══════════════════════════════════════════════════════════════════════════════


def _get_record_startup():
    m = importlib.import_module("infrastructure.telemetry_signal_recorder")
    return m.record_startup


def _get_blender_conn_fn():
    m = importlib.import_module("infrastructure.blender_connection_connector")
    return m.get_blender_connection


def _get_shutdown_connection_fn():
    m = importlib.import_module("infrastructure.blender_connection_connector")
    return m.shutdown_connection


def _get_telemetry_config_class():
    m = importlib.import_module("infrastructure.telemetry_signal_recorder")
    return m.TelemetryConfig


# ═══════════════════════════════════════════════════════════════════════════════
# ServerBootstrapManager (merged from server_bootstrap_manager.py)
# ═══════════════════════════════════════════════════════════════════════════════


class ServerBootstrapManager(ServerBootstrapManagerAggregate):
    """Resolves configuration values for server startup."""

    _contract_name: ObjectName = ObjectName("ServerBootstrapManager")

    @staticmethod
    def get_project_root() -> FilePath:
        """Returns the root directory of the project."""
        return FilePath(str(get_project_root()))

    def to_request_dict(self) -> dict:
        """BlenderOpsIO: serialize bootstrap state."""
        return {
            "log_file": str(self.resolve_log_file()),
        }

    def get(self, path: ConfigPath, default: ConfigValue = None) -> ConfigValue:
        """Retrieve config value by dot-notation path."""
        return get_config(path, default)

    @staticmethod
    def resolve_log_file() -> FilePath:
        """Resolve and return full log file path."""
        project_root = str(get_project_root())
        log_dir_rel = str(get_config(ConfigPath("server.log_dir"), "log"))
        log_dir: DirectoryPath = DirectoryPath(os.path.join(project_root, log_dir_rel))
        os.makedirs(log_dir, exist_ok=True)
        log_file = str(get_config(ConfigPath("server.log_file"), "blender_run.log"))
        return FilePath(os.path.join(log_dir, log_file))

    @staticmethod
    def resolve_transport_config() -> tuple[str, str, str]:
        """Resolve transport, host, port configuration."""
        transport = str(
            os.environ.get(
                "MCP_TRANSPORT",
                get_config(ConfigPath("server.transport"), "stdio"),
            )
        )
        host = str(
            os.environ.get(
                "MCP_HOST",
                get_config(ConfigPath("server.host"), "127.0.0.1"),
            )
        )
        port_str = str(
            os.environ.get(
                "MCP_PORT",
                str(get_config(ConfigPath("server.port"), 8000)),
            )
        )
        return transport, host, port_str


# ═══════════════════════════════════════════════════════════════════════════════
# SystemUtilsCoordinator (merged from system_utils_coordinator.py)
# ═══════════════════════════════════════════════════════════════════════════════


class SystemUtilsCoordinator(SystemUtilsCoordinatorAggregate):
    """Handler-safe wrappers around infrastructure services."""

    _success_ref: SuccessFlag = SuccessFlag(True)
    _obj_ref: ObjectName = ObjectName("ref")

    @staticmethod
    def record_startup() -> None:
        """Record system startup telemetry (best effort, never raises)."""
        try:
            fn = _get_record_startup()
            fn()
        except Exception as e:
            logger.debug(f"Failed to record startup telemetry: {e}")

    @staticmethod
    def get_blender_connection() -> object:
        """Get or create the Blender socket connection."""
        fn = _get_blender_conn_fn()
        return fn()

    @staticmethod
    def shutdown_connection() -> None:
        """Close Blender socket connection gracefully."""
        try:
            fn = _get_shutdown_connection_fn()
            fn()
        except Exception as e:
            logger.debug(f"Error during shutdown: {e}")

    @staticmethod
    def health_check() -> dict[str, object]:
        """Return system health status dict."""
        health = {
            "blender_connected": False,
            "telemetry_enabled": False,
            "status": "initializing",
        }

        try:
            fn = _get_blender_conn_fn()
            conn = fn()
            health["blender_connected"] = True
            health["connection_info"] = str(conn)
        except Exception as e:
            health["blender_connected"] = False
            health["connection_error"] = str(e)

        try:
            cls = _get_telemetry_config_class()
            config_application = cls()
            health["telemetry_enabled"] = config_application.enabled
            health["telemetry_endpoint"] = None
        except Exception:
            logger.debug("TelemetryConfig not available for health check")

        health["status"] = "healthy" if health["blender_connected"] else "degraded"
        return health


# ═══════════════════════════════════════════════════════════════════════════════
# Module-level aliases for backward compatibility
# ═══════════════════════════════════════════════════════════════════════════════

record_startup = SystemUtilsCoordinator.record_startup
get_blender_connection = SystemUtilsCoordinator.get_blender_connection
shutdown_connection = SystemUtilsCoordinator.shutdown_connection
health_check = SystemUtilsCoordinator.health_check
