"""Place asset capability — business logic and Blender external adaptation.

Implements PlaceAssetProtocol for FR-OBJ-001: positioning an asset or existing
object at target transform.

Structure:
  1. Constants & mappings
  2. Business logic functions (safe string escaping, tuple formatting)
  3. PlaceAssetExecutor — implements protocol
"""

import logging

from modules.shared.src.common.taxonomy_core_vo import CoordinateList, ObjectName, Prompt
from modules.shared.src.object.contract_place_asset_protocol import PlaceAssetProtocol
from modules.shared.src.object.taxonomy_object_request_vo import PlaceAssetRequestVO
from modules.shared.src.object.taxonomy_object_result_vo import PlacementResultVO
from modules.shared.src.server.contract_code_execution_protocol import ICodeExecutionProtocol

logger = logging.getLogger("BlenderMCPServer")


class PlaceAssetExecutor(PlaceAssetProtocol):
    """Concrete implementation for placing assets and existing objects."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self, code_executor: ICodeExecutionProtocol) -> None:
        self._executor = code_executor

    # ─── Block 2: Protocol Method Implementation ─────────────

    async def place_asset(self, request: PlaceAssetRequestVO) -> PlacementResultVO:
        """Position an existing object or imported asset at target transform.

        FR-OBJ-001: If object_name is provided, place that specific object.
        Otherwise, place currently selected objects (asset import context).
        """
        logger.info("Placing asset %s at %s", request.asset_id, request.location)

        if request.object_name:
            code = (
                "import bpy\n"
                f"obj = bpy.data.objects.get({PlaceAssetExecutor._safe_str(str(request.object_name))})\n"
                "if obj is None:\n"
                '    raise ValueError("Object not found in scene.")\n'
                f"obj.location = {PlaceAssetExecutor._tuple_str(request.location)}\n"
            )
        else:
            code = (
                "import bpy\n"
                "for obj in bpy.context.selected_objects:\n"
                f"    obj.location = {PlaceAssetExecutor._tuple_str(request.location)}\n"
            )

        try:
            await self._executor.execute_blender_code(Prompt(code))
            return PlacementResultVO(
                success=True,  # type: ignore[arg-type]
                object_name=request.object_name or ObjectName(str(request.asset_id)),
                asset_id=request.asset_id,
                location=CoordinateList(request.location),
                message="Asset placed successfully",
            )
        except Exception as e:
            logger.error("Failed to place asset: %s", e)
            raise

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    @staticmethod
    def _safe_str(v: str) -> str:
        """Safely embed a string into generated Python code using repr()."""
        return repr(v)

    @staticmethod
    def _tuple_str(coords: CoordinateList) -> str:
        """Format a 3-element sequence of floats for embedding in generated Python code."""
        return f"({coords[0]}, {coords[1]}, {coords[2]})"

    def __repr__(self) -> str:
        return "PlaceAssetExecutor()"
