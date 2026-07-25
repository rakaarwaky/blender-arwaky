"""Contract: Protocol for executing Python code in Blender.

Implemented by Capabilities that handle code validation,
execution queue, and result formatting.
AES Protocol layer — depends only on Taxonomy.
"""

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import Prompt


class ICodeExecutionProtocol(ABC):
    """Protocol for executing Python code in Blender."""

    @abstractmethod
    async def execute_blender_code(self, code: Prompt) -> Prompt:
        """Execute arbitrary Python code in Blender and return result."""
        pass
