"""MCP Prompt Templates — system prompts for AI agents."""

from modules.shared.src.common.taxonomy_core_vo import Prompt


def get_layout_expert_prompt() -> Prompt:
    """Get the layout expert system prompt."""
    return Prompt("You are a Blender layout expert. Help users arrange objects in 3D scenes.")


def get_lighting_expert_prompt() -> Prompt:
    """Get the lighting expert system prompt."""
    return Prompt("You are a Blender lighting expert. Help users set up HDRI and scene lighting.")


def get_text_to_scene_orchestrator_prompt() -> Prompt:
    """Get the text-to-scene orchestrator prompt."""
    return Prompt("You are a scene orchestrator. Convert text descriptions into Blender scenes.")