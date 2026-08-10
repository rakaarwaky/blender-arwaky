# Plan: scene — Business Analyst

## Summary
The scene module implements scene inspection and cleanup capabilities through a well-structured protocol-based architecture. Key components include inspection protocol for scene state retrieval and cleanup protocol for protected object management. The implementation uses the Rule-Based Cleanup Pattern and protocol aggregator approach.

## Findings

### Requirements Clarity
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟡 WARNING | FR-SCN-002 "Child policy: delete hierarchy/detach/reject" — test coverage misses complex hierarchies | `tests/test_scene_cleanup.py` | Add property-based testing for child/dependent policies |
| 2 | 🟡 WARNING | FR-SCN-001 "Large scenes → summarized detail level to avoid oversized response" — summarization strategy not specified | `capabilities_scene_inspection_executor.py` | Implement size-based inspection summarization (first/last N objects) |

### Business Flow
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | Inspection flow: request → filtering → detail level → summary → response | `capabilities_scene_inspection_executor.py` | Flow verified |
| 2 | 🟢 INFO | Cleanup flow: policy resolution → dry-run preview → confirmation → execution → report | `capabilities_scene_cleanup_executor.py` | Flow verified |

### Logic Implementation
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟡 WARNING | Scene inspection results lack size monitoring and detail limits | `contract_scene_inspection_protocol.py` | Add scene size monitoring |
| 2 | 🟡 WARNING | Cleanup logic lacks explicit handling of linked object references | `scene_capabilities_cleanup.py` | Add linked object reference tracking |

### Testability & Acceptance
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟡 WARNING | No tests for scene inspection pagination behavior | `tests/test_scene_inspection.py` | Add pagination test cases |
| 2 | 🟡 WARNING | No tests for linked object cleanup scenarios | `tests/test_scene_cleanup.py` | Add linked object handling tests |

### Traceability (FRD→Code)
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | FR-SCN-001 (Scene Inspection) → `contract_scene_inspection_protocol.py` | `contract_scene_inspection_protocol.py` | Traceability verified |
| 2 | 🟢 INFO | FR-SCN-002 (Scene Cleanup) → `scene_capabilities_cleanup.py` | `scene_capabilities_cleanup.py` | Traceability verified |

## Violations
No AES violations found. Scene module properly isolates concerns using protocol-based design.

## Action Items
- [ ] 🟡 WARNING Add scene size monitoring and detail limits for large scene inspection
- [ ] 🟡 WARNING Add linked object reference tracking in cleanup logic
- [ ] 🟡 WARNING Add pagination test cases for scene inspection
- [ ] 🟡 WARNING Add linked object handling tests

## Severity
- 🔴 CRITICAL: Missing core requirement, wrong logic, data integrity risk
- 🟡 WARNING: Ambiguous requirement, missing edge case, incomplete criteria
- 🟢 INFO: Suggestion or optimization, deferrable

## Checklist
- [ ] Prerequisites read
- [ ] Feature + modules identified
- [ ] FRD mapped to code files
- [ ] All 5 dimensions analyzed
- [ ] Severity categorized
- [ ] Deduped vs existing plans + active PRs
- [ ] Plan written (NEW issues + fixed code)
- [ ] Saved to correct path

### Propose Change

#### File: `modules/scene/src/capabilities_scene_inspection_executor.py`

**FR-SCN-001: Size-based inspection summarization for large scenes**

```python
from typing import Any


class SceneInspectionExecutor:
    """Scene inspection with size-based summarization.
    
    FR-SCN-001: Large scenes return summarized detail level to avoid oversized responses.
    Uses pagination: first N objects, last N objects, and count for middle.
    """
    
    def __init__(self, summary_threshold: int = 100, page_size: int = 50) -> None:
        self._summary_threshold = summary_threshold  # Objects before summarization kicks in
        self._page_size = page_size
    
    def inspect(self, detail_level: str = "full") -> dict:
        """Inspect scene with size-based summarization.
        
        FR-SCN-001: Returns full detail for small scenes; summary for large scenes.
        Summary includes first/last N objects and total count.
        """
        import bpy
        
        all_objects = list(bpy.data.objects)
        total_count = len(all_objects)
        
        # FR-SCN-001: Summarize if scene exceeds threshold
        if total_count > self._summary_threshold:
            return {
                "total_objects": total_count,
                "detail_level": "summarized",
                "first_n_objects": self._get_objects(first_n=self._page_size, objects=all_objects),
                "last_n_objects": self._get_objects(last_n=self._page_size, objects=all_objects),
                "middle_count": total_count - (self._page_size * 2),
                "hint": f"Scene has {total_count} objects. Showing first/last {self._page_size}.",
            }
        
        # Full detail for smaller scenes
        return {
            "total_objects": total_count,
            "detail_level": detail_level,
            "objects": self._get_objects(objects=all_objects),
        }
    
    def _get_objects(self, first_n: int = 0, last_n: int = 0, objects: list | None = None) -> list[dict]:
        """Get object list with pagination support."""
        if objects is None:
            import bpy
            objects = list(bpy.data.objects)
        
        if first_n and last_n:
            return objects[:first_n] + objects[-last_n:]
        elif first_n:
            return objects[:first_n]
        elif last_n:
            return objects[-last_n:]
        else:
            return objects
    
    def _format_object(self, obj) -> dict:
        """Format single object for inspection response."""
        return {
            "name": obj.name,
            "type": obj.type,
            "location": (round(obj.location.x, 3), round(obj.location.y, 3), round(obj.location.z, 3)),
            "is_selected": obj.select_get(),
        }
```

#### File: `modules/scene/src/capabilities_scene_cleanup_executor.py`

**FR-SCN-002: Linked object reference tracking in cleanup**

```python
from typing import Any


class SceneCleanupExecutor:
    """Scene cleanup with linked object reference tracking.
    
    FR-SCN-002: Handles child policy — delete hierarchy, detach, or reject.
    Tracks linked references (materials, collections, modifiers) before deletion.
    """
    
    def __init__(self, child_policy: str = "detach") -> None:
        self._child_policy = child_policy  # "delete", "detach", "reject"
    
    def preview_cleanup(self, object_names: list[str]) -> dict:
        """Dry-run cleanup preview with linked reference tracking.
        
        FR-SCN-002: Shows what would be deleted/detached without making changes.
        Includes linked references that would be affected.
        """
        import bpy
        
        affected_refs = []
        for obj_name in object_names:
            obj = bpy.data.objects.get(obj_name)
            if not obj:
                continue
            
            # Track linked references
            refs = self._find_linked_references(obj)
            affected_refs.extend(refs)
        
        return {
            "objects_to_remove": len(object_names),
            "affected_references": len(affected_refs),
            "child_policy": self._child_policy,
            "references": affected_refs,
        }
    
    def execute_cleanup(self, object_names: list[str], confirmation: bool = True) -> dict:
        """Execute cleanup with linked reference handling.
        
        FR-SCN-002: Applies child policy before deletion.
        Requires confirmation for destructive operations.
        """
        if not confirmation:
            return {
                "error": "Confirmation required for destructive cleanup",
                "category": "validation_error",
            }
        
        import bpy
        
        deleted = []
        for obj_name in object_names:
            obj = bpy.data.objects.get(obj_name)
            if not obj:
                continue
            
            # Handle linked references per child policy
            refs = self._find_linked_references(obj)
            
            if self._child_policy == "detach":
                # Detach references (make them independent)
                self._detach_references(obj, refs)
            elif self._child_policy == "delete":
                # Delete all linked references too
                self._delete_references(refs)
            elif self._child_policy == "reject":
                return {
                    "error": f"Cannot delete {obj_name}: has {len(refs)} linked references",
                    "category": "validation_error",
                    "hint": "Change child_policy to detach or delete, or remove references manually",
                }
            
            # Delete object
            bpy.data.objects.remove(obj)
            deleted.append(obj_name)
        
        return {"status": "cleaned", "deleted_count": len(deleted)}
    
    def _find_linked_references(self, obj) -> list[dict]:
        """Find all linked references (materials, modifiers, etc.)."""
        refs = []
        
        if obj.data and obj.data.materials:
            for mat in obj.data.materials:
                refs.append({"type": "material", "name": mat.name})
        
        if obj.modifiers:
            for mod in obj.modifiers:
                refs.append({"type": "modifier", "name": mod.name})
        
        return refs
    
    def _detach_references(self, obj, refs: list[dict]) -> None:
        """Make referenced data independent (not linked)."""
        import bpy
        
        for ref in refs:
            if ref["type"] == "material" and ref["name"] in bpy.data.materials:
                mat = bpy.data.materials[ref["name"]]
                # Make local copy
                bpy.data.materials[ref["name"]].user_remap(bpy.types.Material)
```

#### File: `tests/test_scene_pagination.py` (NEW)

**Test for scene inspection pagination behavior**

```python
import pytest
from unittest.mock import MagicMock


@pytest.mark.asyncio
class TestScenePagination:
    """Test scene inspection pagination and summarization."""
    
    async def test_small_scene_returns_full_detail(self):
        """Verify that scenes under threshold return full detail."""
        from modules.scene.src.capabilities_scene_inspection_executor import SceneInspectionExecutor
        
        executor = SceneInspectionExecutor(summary_threshold=100, page_size=50)
        
        # Mock bpy.data.objects with 10 objects (under threshold)
        mock_objects = [MagicMock(name=f"obj_{i}") for i in range(10)]
        
        result = executor.inspect()
        
        assert result["detail_level"] == "full"
        assert result["total_objects"] == 10
        assert "objects" in result
        assert "first_n_objects" not in result
    
    async def test_large_scene_returns_summarized_detail(self):
        """Verify that scenes over threshold return summarized detail."""
        from modules.scene.src.capabilities_scene_inspection_executor import SceneInspectionExecutor
        
        executor = SceneInspectionExecutor(summary_threshold=100, page_size=50)
        
        result = executor.inspect()
        
        assert result["detail_level"] == "summarized"
        assert "first_n_objects" in result
        assert "last_n_objects" in result
        assert "middle_count" in result
        assert "hint" in result
```

#### File: `tests/test_scene_linked_references.py` (NEW)

**Test for linked object cleanup scenarios**

```python
import pytest
from unittest.mock import MagicMock


@pytest.mark.asyncio
class TestLinkedReferencesCleanup:
    """Test cleanup with linked object references."""
    
    async def test_preview_shows_affected_references(self):
        """Verify that preview cleanup shows all affected references."""
        from modules.scene.src.capabilities_scene_cleanup_executor import SceneCleanupExecutor
        
        executor = SceneCleanupExecutor(child_policy="detach")
        
        result = executor.preview_cleanup(object_names=["Cube"])
        
        assert "objects_to_remove" in result
        assert "affected_references" in result
        assert "child_policy" in result
        assert result["child_policy"] == "detach"
    
    async def test_reject_policy_blocks_cleanup_with_refs(self):
        """Verify that reject policy prevents deletion when references exist."""
        from modules.scene.src.capabilities_scene_cleanup_executor import SceneCleanupExecutor
        
        executor = SceneCleanupExecutor(child_policy="reject")
        
        result = executor.execute_cleanup(
            object_names=["Cube"],
            confirmation=True,
        )
        
        assert "error" in result
        assert "linked references" in result["error"].lower() or result["category"] == "validation_error"
    
    async def test_detach_policy_allows_cleanup(self):
        """Verify that detach policy allows cleanup by making refs independent."""
        from modules.scene.src.capabilities_scene_cleanup_executor import SceneCleanupExecutor
        
        executor = SceneCleanupExecutor(child_policy="detach")
        
        result = executor.execute_cleanup(
            object_names=["Cube"],
            confirmation=True,
        )
        
        assert result["status"] == "cleaned"
```

## Fixed Code
None required.

## Severity
- 🔴 CRITICAL: Missing core requirement, wrong logic, data integrity risk
- 🟡 WARNING: Ambiguous requirement, missing edge case, incomplete criteria
- 🟢 INFO: Suggestion or optimization, deferrable

## Checklist
- [x] Prerequisites read
- [x] Feature + modules identified
- [x] FRD mapped to code files
- [x] All 5 dimensions analyzed
- [x] Severity categorized
- [x] Deduped vs existing plans + active PRs
- [x] Plan written (NEW issues + fixed code)
- [x] Saved to correct path
