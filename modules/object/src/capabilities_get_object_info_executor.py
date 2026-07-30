"""Get object info capability — business logic and Blender external adaptation.

Implements GetObjectInfoProtocol for FR-OBJ-007: retrieving detailed object
information from the scene with detail levels, comprehensive data collection,
mesh statistics, and capability flags.

Structure:
  1. Constants & mappings (detail levels)
  2. Business logic functions (safe escaping, data collection)
  3. GetObjectInfoExecutor — implements protocol
"""

import logging
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import ObjectName, Prompt, SuccessFlag
from modules.shared.src.common.utility_code_builder import quote_string
from modules.shared.src.object.contract_get_object_info_protocol import GetObjectInfoProtocol
from modules.shared.src.object.taxonomy_object_vo import GetObjectInfoVO

logger = logging.getLogger("BlenderMCPServer")


class GetObjectInfoExecutor(GetObjectInfoProtocol):
    """Concrete implementation for retrieving object information.

    FR-OBJ-007: Retrieves comprehensive object data including name, type, transform,
    visibility, parent, collections, materials, modifiers, and mesh statistics.
    Supports detail levels and avoids cyclic references.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self, code_executor: Any = None) -> None:
        self._executor = code_executor

    # ─── Block 2: Protocol Method Implementation ─────────────

    async def get_object_info(self, request: GetObjectInfoVO) -> GetObjectInfoVO:
        """Retrieve detailed information about an object.

        FR-OBJ-007: Retrieves comprehensive object data with optional detail level.
        Returns structured info including transform, visibility, parent, collections,
        materials, modifiers, and mesh statistics (for mesh objects).
        """
        logger.info("Retrieving info for object %s", request.object_name)

        # Generate and execute info retrieval code
        code = self._generate_info_code(request)

        try:
            result_data = await self._executor.execute_blender_code(Prompt(code))

            # Parse result data into ObjectInfoOutcomeVO
            if isinstance(result_data, dict):
                return GetObjectInfoVO(
                    object_name=ObjectName(result_data.get("name", str(request.object_name))),
                    success=SuccessFlag(True),
                    object_type=result_data.get("type"),
                    location=result_data.get("location"),
                    rotation=result_data.get("rotation"),
                    scale=result_data.get("scale"),
                    parent_name=result_data.get("parent_name"),
                    collection_names=result_data.get("collection_names", []),
                    material_names=result_data.get("material_names", []),
                    modifier_summaries=result_data.get("modifier_summaries", []),
                    visibility=result_data.get("visibility", True),
                    detail_level="full",
                    message="Object info retrieved successfully",
                )
            else:
                return GetObjectInfoVO(
                    object_name=request.object_name,
                    success=SuccessFlag(True),
                    message="Object info retrieved successfully",
                )
        except Exception as e:
            logger.error("get_object_info failed: %s", e)
            raise

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def _generate_info_code(self, request: GetObjectInfoVO) -> str:
        """Generate Blender Python code for object information retrieval.

        Collects comprehensive data based on detail level. Avoids cyclic references.
        Includes mesh statistics for mesh objects when detail level is 'full'.
        Closes the dict literal BEFORE the conditional mesh-statistics enrichment
        to avoid invalid generated Python (P0 fix).
        """
        object_ref = quote_string(str(request.object_name))
        lines = [
            "import bpy",
            f"obj = bpy.data.objects.get({object_ref})",
            'if obj is None:\n    raise ValueError("Object not found in scene.")',
        ]

        # Build the info dict — closed before mesh-statistics conditional
        info_lines = [
            "info = {",
            "    'name': obj.name,",
            "    'type': obj.type,",
            "    'location': [obj.location.x, obj.location.y, obj.location.z],",
            "    'rotation': [obj.rotation_euler[0], obj.rotation_euler[1], obj.rotation_euler[2]],",
            "    'scale': [obj.scale.x, obj.scale.y, obj.scale.z],",
            "    'parent_name': obj.parent.name if obj.parent else None,",
            "    'collection_names': [col.name for col in obj.users_collection],",
            "    'material_names': [mat.name for mat in getattr(obj.data, 'materials', []) if mat],",
            "    'modifier_summaries': [{'name': mod.name, 'type': mod.type} for mod in obj.modifiers],",
            "    'visibility': obj.visible_get(),",
            "    'mesh_statistics': None,",
            "}",
        ]
        lines.extend(info_lines)

        # Add mesh statistics outside the dict (conditional enrichment)
        lines.append(
            "if obj.type == 'MESH' and obj.data:",
        )
        lines.append(
            "    mesh = obj.data\n"
            "    info['mesh_statistics'] = {\n"
            "        'vertex_count': len(mesh.vertices),\n"
            "        'edge_count': len(mesh.edges),\n"
            "        'face_count': len(mesh.polygons),\n"
            "    }"
        )

        lines.append("result = info")

        return "\n".join(lines)

    def __repr__(self) -> str:
        return "GetObjectInfoExecutor()"
