import logging
from typing import Any

from ..common.expert_base_aggregate import ExpertBaseOrchestratorAggregate
from ..common.agent_workflow_agent_aggregate import WorkflowAgentOrchestratorAggregate
from ..common.taxonomy_core_vo import SuccessFlag
from ..scene.taxonomy_scene_info_vo import SceneInfo

logger = logging.getLogger("BlenderMCPServer.Workflow")


class WorkflowAgentOrchestrator(WorkflowAgentOrchestratorAggregate):
    """
    High-level coordinator that delegates to domain experts.
    Provides both single-step and autonomous loop workflows.
    """

    _success_ref: SuccessFlag = SuccessFlag(True)

    def __init__(
        self,
        scene_expert: ExpertBaseOrchestratorAggregate,
        asset_expert: ExpertBaseOrchestratorAggregate,
        refinement_expert: ExpertBaseOrchestratorAggregate,
    ):
        self.tool_scene_ops = scene_expert
        self.asset = asset_expert
        self.refinement = refinement_expert

    async def create_scene_from_prompt(self, prompt: str) -> dict[str, Any]:
        """
        Full pipeline: prompt -> tool_scene_ops.
        1. Cleanup
        2. Asset acquisition (search + AI generate if needed)
        3. Placement
        4. Environment & lighting
        5. Camera setup
        6. Render config_application
        """
        logger.info(f"Creating tool_scene_ops from prompt: {prompt}")

        results: dict[str, Any] = {"steps": [], "final_state": {}}
        # Step 1: Cleanup
        cleanup_res = await self.tool_scene_ops.execute("cleanup", {})
        results["steps"].append({"step": "cleanup", "result": cleanup_res})

        # Step 2: Asset search
        asset_search = await self.asset.execute("search", {"query": prompt})
        results["steps"].append({"step": "asset_search", "result": asset_search})

        # Step 3: Environment & lighting
        env_res = await self.tool_scene_ops.execute("setup_environment", {"hdri_name": "default_studio"})
        results["steps"].append({"step": "environment", "result": env_res})

        # Step 4: Camera
        cam_res = await self.tool_scene_ops.execute(
            "setup_camera", {"location": [0, -5, 2], "rotation": [1.0, 0, 0], "target": [0, 0, 0]}
        )
        results["steps"].append({"step": "camera", "result": cam_res})

        # Step 5: Render
        render_res = await self.tool_scene_ops.execute(
            "setup_render", {"engine": "CYCLES", "samples": 128, "resolution": [1920, 1080]}
        )
        results["steps"].append({"step": "render", "result": render_res})

        results["final_state"] = await self.tool_scene_ops.execute("info", {})
        results["success"] = all(s.get("result", {}).get("success", False) for s in results["steps"])

        return results

    async def run_autonomous_refinement(self, objective: str, max_iterations: int = 5) -> dict[str, Any]:
        """
        Autonomous loop: the RefinementExpert decides and applies improvements.
        """
        logger.info(f"Starting autonomous refinement. Objective: {objective}")
        result = await self.refinement.execute(
            "refine_loop", {"objective": objective, "max_iterations": max_iterations}
        )
        return result

    async def get_expert_status(self) -> dict[str, str]:
        return {
            "tool_scene_ops": "initialized",
            "asset": "initialized",
            "refinement": "initialized",
        }
