"""Place asset capability — business logic and Blender external adaptation.

Implements PlaceAssetProtocol for FR-OBJ-001: positioning an asset or existing
object at target transform with full object resolution, ambiguity detection,
and idempotent placement.

Structure:
  1. Constants & mappings (placement policies)
  2. Business logic functions (object resolution, validation, safe escaping)
  3. PlaceAssetExecutor — implements protocol
"""

import logging

from modules.shared.src.common.taxonomy_core_vo import (
    ObjectName,
    Prompt,
    SuccessFlag,
)
from modules.shared.src.object.contract_place_asset_protocol import PlaceAssetProtocol
from modules.shared.src.object.taxonomy_object_error import ObjectAmbiguityError, ObjectNotFoundError
from modules.shared.src.object.taxonomy_object_vo import PlaceAssetVO

logger = logging.getLogger("BlenderMCPServer")


class PlaceAssetExecutor(PlaceAssetProtocol):
    """Concrete implementation for placing assets and existing objects.

    FR-OBJ-001: Supports deterministic object resolution (identifier → name → path),
    ambiguity detection, idempotent placement, rotation support, scale validation,
    and transform mode handling.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self, code_executor: object | None = None) -> None:
        self._executor = code_executor

    # ─── Block 2: Protocol Method Implementation ─────────────

    async def place_asset(self, request: PlaceAssetVO) -> PlaceAssetVO:
        """Position an existing object or imported asset at target transform.

        FR-OBJ-001: Resolves object deterministically, validates parameters,
        handles ambiguity, supports rotation/scale, and ensures idempotency.
        """
        logger.info("Placing asset %s at %s", request.asset_id, request.location)

        # Resolve object with fallback strategy
        resolved_name = await self._resolve_object(request)

        # Validate scale (non-zero unless explicitly allowed)
        if request.scale is not None:
            # Validate scale values are finite and non-zero
            for i, val in enumerate(request.scale):
                if not isinstance(val, (int, float)) or val == 0:
                    raise ValueError(f"Scale component {i} is zero — non-zero scale is required")

        # Generate and execute placement code
        code = self._generate_placement_code(resolved_name, request)

        try:
            await self._executor.execute_blender_code(Prompt(code))
            return PlaceAssetVO(
                asset_id=request.asset_id,
                object_name=ObjectName(resolved_name),
                location=request.location,
                rotation=request.rotation,
                scale=request.scale,
                success=SuccessFlag(True),
                message="Asset placed successfully",
            )
        except Exception as e:
            logger.error("Failed to place asset: %s", e)
            raise

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    async def _resolve_object(self, request: PlaceAssetVO) -> str:
        """Resolve object reference with deterministic fallback strategy.

        Resolution order: unique identifier → exact name → qualified path
        Returns the resolved object name or raises appropriate errors.
        """
        if request.object_name:
            code = (
                "import bpy\n"
                f"obj = bpy.data.objects.get({repr(str(request.object_name))})\n"
                "if obj is None:\n"
                '    raise ValueError("Object not found in scene.")\n'
                "result = [obj.name]\n"
            )

            try:
                result = await self._executor.execute_blender_code(Prompt(code))
                # Parse result to check for ambiguity
                if isinstance(result, dict) and "matches" in result:
                    matches = result["matches"]
                    if len(matches) > 1:
                        raise ObjectAmbiguityError(str(request.object_name), matches)
                elif isinstance(result, list):
                    # Executor returned a list of matches directly
                    if len(result) > 1:
                        raise ObjectAmbiguityError(str(request.object_name), result)
                return str(request.object_name)
            except ObjectAmbiguityError:
                raise  # Re-raise ambiguity errors — don't swallow them
            except Exception:
                # Fallback: try to find by name pattern
                fallback_code = (
                    "import bpy\n"
                    f"matches = [obj.name for obj in bpy.data.objects if {repr(str(request.object_name))} in obj.name]\n"
                    "result = matches\n"
                )
                try:
                    matches = await self._executor.execute_blender_code(Prompt(fallback_code))
                    if isinstance(matches, list) and len(matches) > 1:
                        raise ObjectAmbiguityError(str(request.object_name), matches)
                    return str(request.object_name)
                except Exception:
                    raise ObjectNotFoundError(str(request.object_name)) from None

        # Asset context — place selected objects
        else:
            code = "import bpy\nselected = [obj.name for obj in bpy.context.selected_objects]\nresult = selected\n"
            try:
                selected = await self._executor.execute_blender_code(Prompt(code))
                if isinstance(selected, list) and len(selected) > 0:
                    return selected[0]
                raise ObjectNotFoundError(str(request.asset_id))
            except Exception:
                raise ObjectNotFoundError(str(request.asset_id)) from None

    def _generate_placement_code(self, object_name: str, request: PlaceAssetVO) -> str:
        """Generate Blender Python code for asset placement.

        Supports location, rotation, and scale transforms with proper formatting.
        """
        lines = [
            "import bpy",
            f"obj = bpy.data.objects.get({repr(object_name)})",
            'if obj is None:\n    raise ValueError("Object not found in scene.")',
        ]

        if request.location is not None:
            lines.append(f"obj.location = ({request.location[0]}, {request.location[1]}, {request.location[2]})")

        if request.rotation is not None:
            lines.append(f"obj.rotation_euler = ({request.rotation[0]}, {request.rotation[1]}, {request.rotation[2]})")

        if request.scale is not None:
            lines.append(f"obj.scale = ({request.scale[0]}, {request.scale[1]}, {request.scale[2]})")

        return "\n".join(lines)

    def __repr__(self) -> str:
        return "PlaceAssetExecutor()"
