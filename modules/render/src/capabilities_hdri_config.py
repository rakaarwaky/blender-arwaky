"""Capability: HDRI configuration executor.

Implements HdriConfigProtocol — handles HDRI environment lighting setup,
strength/rotation configuration, and world environment management through
the server module's code execution capability.
"""

from __future__ import annotations

import json
import logging

logger = logging.getLogger("BlenderMCPServer")


class HdriConfigExecutor:
    """Business logic for HDRI environment lighting configuration."""

    def __init__(self, code_executor: object) -> None:
        """Initialize with a code executor from the server module.

        Args:
            code_executor: A callable or server capability that executes Python code.
        """
        self._code_executor = code_executor

    async def configure_hdri(self, request: dict) -> dict:
        """Set up HDRI-based environment lighting.

        FR-RND-004: Applies environment lighting from locally available HDRI asset.
        Resolves strength (0.0-10.0), rotation, and overwrite policy.
        Returns resolved environment reference and applied settings.

        Args:
            request: HDRI setup parameters including path, strength, rotation,
                visibility, and overwrite policy.

        Returns:
            Dictionary with environment reference and applied settings.
        """
        hdri_path = request.get("hdri_path", "")
        strength = request.get("strength", 1.0)
        rotation = request.get("rotation", 0.0)
        is_visible = request.get("is_visible", True)
        overwrite_policy = request.get("overwrite_policy", "replace")

        logger.info(
            "Configuring HDRI: path=%s, strength=%.2f, rotation=%.2f, visible=%s, policy=%s",
            hdri_path,
            strength,
            rotation,
            is_visible,
            overwrite_policy,
        )

        safe_path = json.dumps(hdri_path)
        safe_strength = str(float(strength))
        safe_rotation = str(float(rotation))
        safe_visible = "True" if is_visible else "False"

        code = (
            "import bpy\n"
            f"hdri_path = {safe_path}\n"
            f"strength = {safe_strength}\n"
            f"rotation = {safe_rotation}\n"
            f"display_viewport = {safe_visible}\n"
            # Create world if needed
            "world = bpy.context.scene.world\n"
            "if world is None:\n"
            "    world = bpy.data.worlds.new('World')\n"
            "    bpy.context.scene.world = world\n"
            "world.use_nodes = True\n"
            # Check if environment node exists
            "env_node = None\n"
            "for node in world.node_tree.nodes:\n"
            "    if node.type == 'ENVIRONMENT_TEXTURE':\n"
            "        env_node = node\n"
            "        break\n"
            # Handle overwrite policy
            "if env_node is not None and hdri_path:\n"
            f"    if '{overwrite_policy}' == 'replace':\n"
            "        world.node_tree.nodes.remove(env_node)\n"
            "        env_node = None\n"
            f"    elif '{overwrite_policy}' == 'reject':\n"
            "        raise Exception('Environment already exists, reject policy active')\n"
            # Create new environment texture node
            "if not env_node:\n"
            "    tex_node = world.node_tree.nodes.new(type='ShaderNodeTexEnvironment')\n"
            f"    tex_node.image = bpy.data.images.load(hdri_path)\n"
            "    ht_node = world.node_tree.nodes.new(type='ShaderNodeHoldTile')\n"
            "    world.node_tree.links.new(tex_node.outputs['Color'], ht_node.inputs['Image'])\n"
            "    bsdf_node = world.node_tree.nodes['World BSDF']\n"
            "    world.node_tree.links.new(ht_node.outputs['Result'], bsdf_node.inputs['Surface'])\n"
            # Set up strength and rotation
            "if env_node:\n"
            f"    strength_node = world.node_tree.nodes.new(type='ShaderNodeValToTriple')\n"
            f"    strength_node.inputs[0].default_value = {safe_strength}\n"
            "    world.node_tree.links.new(strength_node.outputs['Z'], bsdf_node.inputs['Strength'])\n"
        )

        try:
            await self._execute_code(code)
            result = {
                "environment_ref": hdri_path,
                "applied_strength": float(strength),
                "message": f"HDRI environment '{hdri_path}' configured successfully",
            }
            logger.info("HDRI configured successfully: %s", hdri_path)
            return result
        except Exception as e:
            logger.error("HDRI configuration failed: %s", e)
            return {
                "environment_ref": hdri_path,
                "applied_strength": 0.0,
                "message": f"HDRI configuration failed: {e}",
            }

    async def _execute_code(self, code: str) -> None:
        """Execute Python code through the server module's code execution capability.

        Args:
            code: Python code string to execute in Blender.

        Raises:
            RuntimeError: If code execution fails.
        """
        if callable(self._code_executor):
            result = await self._code_executor(code)
            if isinstance(result, str):
                logger.info("HDRI config code execution: %s", result[:200])
        else:
            raise RuntimeError(f"Unexpected code_executor type: {type(self._code_executor)}")
