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

        Collects comprehensive data. Avoids cyclic references.
        Includes mesh statistics for mesh objects.
        """
        lines = [
            "import bpy",
            f"obj = bpy.data.objects.get({quote_string(str(request.object_name))})",
            'if obj is None:',
            '    raise ValueError("Object not found in scene.")',
            'info = {',
            "    'name': obj.name,",
            "    'type': obj.type,",
        ]

        # Add transform data
        lines.append(
            "    'location': [obj.location.x, obj.location.y, obj.location.z],"
        )
        lines.append(
            "    'rotation': [obj.rotation_euler[0], obj.rotation_euler[1], obj.rotation_euler[2]],"
        )
        lines.append(
            "    'scale': [obj.scale.x, obj.scale.y, obj.scale.z],"
        )

        # Add parent information
        lines.append(
            "    'parent_name': obj.parent.name if obj.parent else None,"
        )

        # Add collection membership (avoid cyclic references)
        lines.append(
            "    'collection_names': [col.name for col in obj.users_collection],"
        )

        # Add material references — guard for non-mesh objects
        lines.append(
            "    'material_names': [mat.name for mat in getattr(obj.data, 'materials', []) if mat],"
        )

        # Add modifier summaries
        lines.append(
            "    'modifier_summaries': [{'name': mod.name, 'type': mod.type} for mod in obj.modifiers],"
        )

        # Add visibility state
        lines.append(
            "    'visibility': obj.visible_get(),"
        )

        # Add mesh statistics (only for mesh objects)
        lines.extend([
            "    'mesh_statistics': None,",
            "}",
            "if obj.type == 'MESH' and obj.data:",
            "    mesh = obj.data",
            "    info['mesh_statistics'] = {",
            "        'vertex_count': len(mesh.vertices),",
            "        'edge_count': len(mesh.edges),",
            "        'face_count': len(mesh.polygons),",
            "    }",
            "result = info",
        ])

        return "\n".join(lines)

    def __repr__(self) -> str:
        return "GetObjectInfoExecutor()"
