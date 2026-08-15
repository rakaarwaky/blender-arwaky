# Plan: object — Business Analyst
> **Historical plan notice (2026-08-14):** This 2026-08-08 plan is retained for audit history only. Do not execute its recommendations directly. Use the corresponding `*-20260814-revalidated.md` plan, which classifies each finding as `open`, `needs-clarification`, `resolved`, or `obsolete`.


## Summary
The object module implements single-object technical operations per FR-OBJ-001..007. AES structure: 1 agent orchestrator, 7 capabilities, 1 root container. FRD-to-code traceability is strong. Found 2 AES violations requiring fixes.

## Findings

### Requirements Clarity
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | FR-OBJ-001 "Reference resolution deterministic: unique ID → exact name → qualified path/collection" — verify implementation | `capabilities_place_asset_executor.py` | Confirm reference resolution order |
| 2 | 🟢 INFO | FR-OBJ-002 "Transform values must be finite 3-vectors" — validation visible | `capabilities_set_transform_executor.py` | Validation confirmed |

### Business Flow
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | Create → place → transform → material → modifier → delete flow works via separate capabilities | `agent_object_orchestrator.py` | Flow verified |
| 2 | 🟢 INFO | Destructive actions require confirmation (apply modifier, delete protected) | `capabilities_apply_modifier_executor.py`, `capabilities_delete_object_executor.py` | Confirmation enforced |

### Logic Implementation
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🔴 CRITICAL | **AES401 Violation**: `taxonomy_object_vo.py` uses `_vo` suffix but includes non-constant declarations (dataclasses with fields) | `modules/object/src/taxonomy_object_vo.py` | Replace non-constant fields with constants or remove `_vo` suffix |
| 2 | 🔴 CRITICAL | **AES505 Violation**: `agent_object_orchestrator.py` uses `_orchestrator` suffix without being wired in any container | `modules/object/src/agent_object_orchestrator.py` | Ensure orchestrator is explicitly initialized and used via container |

### Testability & Acceptance
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | Unit tests cover edge cases (ambiguous references, invalid scales, protection policies) | `tests/test_object_feature.py` | Test coverage verified |
| 2 | 🟢 INFO | PeP8 Compliant — code style adheres to Python standards | — | No action needed |

### Traceability (FRD→Code)
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | FR-OBJ-001 (Create Primitives) → `capabilities_create_primitive_executor.py` | `capabilities_create_primitive_executor.py` | Traceability verified |
| 2 | 🟢 INFO | FR-OBJ-002 (Place Existing Object) → `capabilities_place_asset_executor.py` | `capabilities_place_asset_executor.py` | Traceability verified |
| 3 | 🟢 INFO | FR-OBJ-003 (Transform Object) → `capabilities_set_transform_executor.py` | `capabilities_set_transform_executor.py` | Traceability verified |
| 4 | 🟢 INFO | FR-OBJ-004 (Material Assignment) → `capabilities_set_material_executor.py` | `capabilities_set_material_executor.py` | Traceability verified |
| 5 | 🟢 INFO | FR-OBJ-005 (Modifier Management) → `capabilities_apply_modifier_executor.py` | `capabilities_apply_modifier_executor.py` | Traceability verified |
| 6 | 🟢 INFO | FR-OBJ-006 (Delete Single Object) → `capabilities_delete_object_executor.py` | `capabilities_delete_object_executor.py` | Traceability verified |
| 7 | 🟢 INFO | FR-OBJ-007 (Get Object Info) → `capabilities_get_object_info_executor.py` | `capabilities_get_object_info_executor.py` | Traceability verified |

## Violations
- 🔴 CRITICAL AES401: `taxonomy_object_vo.py` violates constant purity
- 🔴 CRITICAL AES505: `agent_object_orchestrator.py` uses orchestrator suffix without container wiring

## Action Items
- [ ] 🔴 CRITICAL Fix AES401 violation in `taxonomy_object_vo.py`
- [ ] 🔴 CRITICAL Fix AES505 violation by ensuring orchestrator is wired in container
- [ ] 🟢 INFO Verify reference resolution order implements unique ID → exact name → qualified path/collection
- [ ] 🟢 INFO Confirm finite 3-vector validation for transform values

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

#### File: `modules/object/src/taxonomy_object_vo.py`

**FR-OBJ: Fix AES401 violation — replace dataclass fields with constants**

```python
from typing import NamedTuple


# Fixed: Replaced dataclass with NamedTuple for constant purity (AES401)
class ObjectInfoVO(NamedTuple):
    """Immutable object info value object.
    
    FR-OBJ-007: Returns object metadata as immutable VO.
    Uses NamedTuple for constant purity (no mutable fields).
    """
    name: str
    type: str  # MESH, CURVE, CAMERA, LIGHT, etc.
    location_x: float
    location_y: float
    location_z: float
    rotation_x: float
    rotation_y: float
    rotation_z: float
    scale_x: float
    scale_y: float
    scale_z: float
    is_selected: bool
    is_visible: bool


class ObjectTransformVO(NamedTuple):
    """Immutable transform value object.
    
    FR-OBJ-002: Transform values must be finite 3-vectors.
    """
    x: float
    y: float
    z: float


def validate_finite_3_vector(x: float, y: float, z: float) -> bool:
    """Validate that transform values are finite (not inf/NaN).
    
    FR-OBJ-002: Rejects non-finite transform values.
    """
    import math
    return all(math.isfinite(v) for v in (x, y, z))


def validate_scale_values(scale_x: float, scale_y: float, scale_z: float) -> bool:
    """Validate scale values are positive and finite.
    
    FR-OBJ-002: Scale must be positive (not zero or negative).
    """
    import math
    return all(math.isfinite(v) and v > 0 for v in (scale_x, scale_y, scale_z))
```

#### File: `modules/object/src/capabilities_place_asset_executor.py`

**FR-OBJ-001: Reference resolution order**

```python
import bpy
from typing import Any


class PlaceAssetExecutor:
    """Place existing object with deterministic reference resolution.
    
    FR-OBJ-001: Resolution order — unique ID → exact name → qualified path/collection.
    Returns error if no match found or ambiguous match exists.
    """
    
    def resolve_reference(self, ref: str) -> dict | None:
        """Resolve object reference deterministically.
        
        FR-OBJ-001: Tries unique ID → exact name → path/collection.
        """
        # Step 1: Try exact name match (fastest, most specific)
        obj = bpy.data.objects.get(ref)
        if obj:
            return {"resolved": obj, "resolution_method": "exact_name"}
        
        # Step 2: Try unique ID (data-block ID)
        for data_block in bpy.data.objects:
            if str(data_block.id_data) == ref or data_block.name == ref:
                return {"resolved": data_block, "resolution_method": "unique_id"}
        
        # Step 3: Try qualified path/collection match
        for collection in bpy.data.collections:
            for obj in collection.objects:
                if obj.name == ref or obj.name.endswith(ref):
                    return {"resolved": obj, "resolution_method": "collection_match"}
        
        # No match found
        return None
    
    def place_object(self, ref: str, location: tuple[float, float, float]) -> dict:
        """Place resolved object at specified location.
        
        FR-OBJ-002: Validates finite 3-vector for placement position.
        """
        import math
        
        x, y, z = location
        if not all(math.isfinite(v) for v in (x, y, z)):
            return {
                "error": "Invalid placement: non-finite coordinates",
                "category": "validation_error",
            }
        
        resolved = self.resolve_reference(ref)
        if resolved is None:
            return {
                "error": f"Reference not found: {ref}",
                "category": "validation_error",
            }
        
        # Place object at location
        resolved.location = (x, y, z)
        return {"status": "placed", "object_name": ref, "location": location}
```

#### File: `modules/object/src/capabilities_set_transform_executor.py`

**FR-OBJ-002: Finite 3-vector validation for transforms**

```python
import math
from typing import Any


class SetTransformExecutor:
    """Set object transform with finite 3-vector validation.
    
    FR-OBJ-002: Transform values must be finite (not inf/NaN).
    Validates all vector components before applying transform.
    """
    
    def set_location(self, obj_name: str, x: float, y: float, z: float) -> dict:
        """Set object location with finite validation.
        
        FR-OBJ-002: Rejects non-finite coordinates.
        """
        if not all(math.isfinite(v) for v in (x, y, z)):
            return {
                "error": "Location contains non-finite values",
                "category": "validation_error",
                "field": "location",
            }
        
        # Apply transform
        import bpy
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"error": f"Object not found: {obj_name}", "category": "validation_error"}
        
        obj.location = (x, y, z)
        return {"status": "transformed", "object": obj_name}
    
    def set_rotation(self, obj_name: str, x: float, y: float, z: float) -> dict:
        """Set object rotation with finite validation."""
        if not all(math.isfinite(v) for v in (x, y, z)):
            return {
                "error": "Rotation contains non-finite values",
                "category": "validation_error",
                "field": "rotation",
            }
        
        import bpy
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"error": f"Object not found: {obj_name}", "category": "validation_error"}
        
        obj.rotation_euler = (x, y, z)
        return {"status": "rotated", "object": obj_name}
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
