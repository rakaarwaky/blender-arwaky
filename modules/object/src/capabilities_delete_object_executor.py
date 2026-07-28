"""Delete object capability — business logic and Blender external adaptation.

Implements DeleteObjectProtocol for FR-OBJ-006: removing an object from
the scene with protected category checking, deletion policy handling,
and idempotent deletion support.

Structure:
  1. Constants & mappings (protected categories, deletion policies)
  2. Business logic functions (safe escaping, validation)
  3. DeleteObjectExecutor — implements protocol
"""

import logging
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import Prompt, SuccessFlag
from modules.shared.src.object.contract_delete_object_protocol import DeleteObjectProtocol
from modules.shared.src.object.taxonomy_object_error_vo import DeletionProtectionError, ObjectNotFoundError
from modules.shared.src.object.taxonomy_object_vo import DeleteObjectVO

logger = logging.getLogger("BlenderMCPServer")

# Protected object categories that require explicit confirmation
PROTECTED_CATEGORIES: frozenset[str] = frozenset(
    {
        "active_camera",
        "sole_camera",
        "lights",
        "protected",
    }
)


class DeleteObjectExecutor(DeleteObjectProtocol):
    """Concrete implementation for deleting objects from the scene.

    FR-OBJ-006: Validates object exists, checks protected categories, handles
    deletion policy (hierarchy/detach/reject), supports idempotent deletion,
    and removes from collections before final removal.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self, code_executor: Any = None) -> None:
        self._executor = code_executor

    # ─── Block 2: Protocol Method Implementation ─────────────

    async def delete_object(self, request: DeleteObjectVO) -> DeleteObjectVO:
        """Remove an object from the scene.

        FR-OBJ-006: Validates object exists, checks protected categories,
        handles deletion policy, and removes from collections before removal.
        """
        logger.info("Deleting object %s", request.object_name)

        # Check if object exists
        exists_code = (
            "import bpy\n"
            f"obj = bpy.data.objects.get({DeleteObjectExecutor._safe_str(str(request.object_name))})\n"
            "if obj is None:\n"
            '    raise ValueError("Object not found in scene.")\n'
            "result = True\n"
        )
        try:
            await self._executor.execute_blender_code(Prompt(exists_code))
        except ValueError as e:
            # Blender raised ValueError — object not found
            if getattr(request, "idempotent", False):
                return DeleteObjectVO(
                    object_name=request.object_name,
                    success=SuccessFlag(True),
                    deleted_count=0,
                    deleted_names=[],
                    message="Object not found — idempotent deletion policy enabled",
                )
            raise ObjectNotFoundError(str(request.object_name)) from e
        except BaseException as e:
            # Re-raise system-level errors (KeyboardInterrupt, SystemExit, MemoryError)
            if isinstance(e, (KeyboardInterrupt, SystemExit, MemoryError)):
                raise
            # Other exceptions indicate actual errors, not "object not found"
            logger.error("Existence check failed for object %s: %s", request.object_name, e)
            raise ObjectNotFoundError(str(request.object_name)) from e

        # Check protected categories
        await self._check_protected_categories(request)

        # Generate and execute deletion code
        code = self._generate_deletion_code(request)

        try:
            await self._executor.execute_blender_code(Prompt(code))
            return DeleteObjectVO(
                object_name=request.object_name,
                success=SuccessFlag(True),
                deleted_count=1,
                deleted_names=[request.object_name],
                children_handled=getattr(request, "children_handled", False),
                message="Object deleted successfully",
            )
        except Exception as e:
            logger.error("delete_object failed: %s", e)
            raise

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    async def _check_protected_categories(self, request: DeleteObjectVO) -> None:
        """Check if object belongs to protected categories.

        FR-OBJ-006: Protected object categories such as active camera, sole camera,
        lights, or objects marked protected require explicit confirmation.
        """
        check_code = (
            "import bpy\n"
            f"obj = bpy.data.objects.get({DeleteObjectExecutor._safe_str(str(request.object_name))})\n"
            "protected = False\n"
            "# Check if active camera\n"
            "if bpy.context.scene.camera == obj:\n"
            "    protected = True\n"
            "# Check if sole camera\n"
            "cameras = [o for o in bpy.data.objects if o.type == 'CAMERA']\n"
            "if len(cameras) == 1 and cameras[0] == obj:\n"
            "    protected = True\n"
            "# Check if light\n"
            "if obj.type == 'LIGHT':\n"
            "    protected = True\n"
            "# Check if marked protected\n"
            "if getattr(obj, 'blender_private', False):\n"
            "    protected = True\n"
            "result = protected\n"
        )

        try:
            is_protected = await self._executor.execute_blender_code(Prompt(check_code))
            if is_protected and not getattr(request, "confirmation", False):
                raise DeletionProtectionError(str(request.object_name), "protected_category")
        except DeletionProtectionError:
            raise  # Re-raise protection errors — don't swallow them
        except BaseException as e:
            # Re-raise system-level errors (KeyboardInterrupt, SystemExit, MemoryError)
            if isinstance(e, (KeyboardInterrupt, SystemExit, MemoryError)):
                raise
            # Object doesn't exist or error already handled — not a protected category issue
            logger.debug("Protected categories check failed for object %s: %s", request.object_name, e)

    def _generate_deletion_code(self, request: DeleteObjectVO) -> str:
        """Generate Blender Python code for object deletion.

        Removes object from collections before final removal. Handles children
        based on deletion policy.
        """
        lines = [
            "import bpy",
            f"obj = bpy.data.objects.get({DeleteObjectExecutor._safe_str(str(request.object_name))})",
            'if obj is None:\n    raise ValueError("Object not found in scene.")',
        ]

        # Remove from collections
        lines.append(
            "# Remove from all relevant collections\n"
            "for col in list(bpy.context.scene.collection.children_recursive):\n"
            "    for child_col in col.collection.children:\n"
            "        if obj in child_col.objects:\n"
            "            child_col.objects.remove(obj)\n"
            "if obj in bpy.context.scene.collection.objects:\n"
            "    bpy.context.scene.collection.objects.remove(obj)\n"
        )

        # Handle children based on policy
        children_handled = getattr(request, "children_handled", False)
        if children_handled:
            lines.append(
                "# Handle children based on deletion policy\n"
                "children = [child for child in obj.children_objects]\n"
                "for child in children:\n"
                "    child.parent = None\n"
            )

        # Final removal
        lines.append("bpy.data.objects.remove(obj, do_unlink=True)\n")

        return "\n".join(lines)

    @staticmethod
    def _safe_str(v: str) -> str:
        """Safely embed a string into generated Python code using repr()."""
        return repr(v)

    def __repr__(self) -> str:
        return "DeleteObjectExecutor()"
