"""Infrastructure Layer: Technical adapters and service implementations.

All infrastructure components must follow the Dependency Injection (DI) pattern
and receive their dependencies (e.g., BlenderConnectionPort) via constructor.
"""

from .blender_connection_connector import BlenderConnection, BlenderConnectionFactory
from .blender_socket_adapter import BlenderSocketAdapter
from .code_execution_adapter import CodeExecutionAdapter
from .polyhaven_asset_adapter import PolyhavenAssetAdapter
from .scene_inspection_adapter import SceneInspectionAdapter
from .sketchfab_asset_adapter import SketchfabAssetAdapter
from .telemetry_signal_recorder import TelemetrySignalRecorder

__all__ = [
    "BlenderConnection",
    "BlenderConnectionFactory",
    "BlenderSocketAdapter",
    "PolyhavenAssetAdapter",
    "SketchfabAssetAdapter",
    "TelemetrySignalRecorder",
    "SceneInspectionAdapter",
    "CodeExecutionAdapter",
]

# ── Dead code cleanup (2026-07-18) ──────────────────────────────────────────
# The following modules were removed as dead code:
#   - command_catalog_client.py (duplicate of CommandCatalogAdapter in agent_di_container.py)
#   - polyhaven_api_client.py (unused; PolyhavenAssetAdapter handles all integration)
#   - sketchfab_api_client.py (unused; SketchfabAssetAdapter handles all integration)
#   - telemetry_api_util.py (unused; TelemetrySignalRecorder is the active implementation)
#   - telemetry_decorator_adapter.py (unused; same rationale as above)
