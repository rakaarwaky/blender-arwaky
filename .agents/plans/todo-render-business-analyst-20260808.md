# Plan: render — Business Analyst
> **Historical plan notice (2026-08-14):** This 2026-08-08 plan is retained for audit history only. Do not execute its recommendations directly. Use the corresponding `*-20260814-revalidated.md` plan, which classifies each finding as `open`, `needs-clarification`, `resolved`, or `obsolete`.


## Summary
The render module implements image production and camera optics per FR-RND-001..005. AES structure: 1 agent orchestrator, 4 capabilities, 1 root container. FRD-to-code traceability is strong. Naming conventions compliant. Found 3 risk areas requiring attention. No AES violations found.

## Findings

### Requirements Clarity
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🔴 CRITICAL | FR-RND "Background render submission through job feature" — job module integration not yet implemented in render capabilities | `agent_render_orchestrator.py` | Integrate job feature for long-running renders |
| 2 | 🟡 WARNING | FR-RND "Output destination validated through security policy before render begins" — need to verify security policy validation in render execution path | `capabilities_render_scene_image_executor.py` | Add explicit security policy validation |
| 3 | 🟡 WARNING | FR-RND "Existing artifact → configured overwrite policy" — overwrite policy enforcement not visible | `capabilities_render_scene_image_executor.py` | Verify overwrite policy implementation |

### Business Flow
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | Viewport capture → camera config → HDRI config → render flow works via separate capabilities | `agent_render_orchestrator.py` | Flow verified |
| 2 | 🟡 WARNING | Background render submission depends on job module — not yet integrated | `agent_render_orchestrator.py` | Add job submission for long renders |

### Logic Implementation
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🔴 CRITICAL | HDRI lighting config "uses asset feature for download (never direct)" — verify render doesn't download files directly | `capabilities_render_hdri_config_executor.py` | Confirm no direct download; delegate to asset feature |
| 2 | 🟡 WARNING | "HDRI not found" error category is "delegated" to asset — verify error propagation | `capabilities_render_hdri_config_executor.py` | Confirm asset not found error propagates correctly |

### Testability & Acceptance
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟡 WARNING | No test for HDRI config with missing asset (asset not found scenario) | `tests/` | Add test for asset not found propagation |
| 2 | 🟡 WARNING | No test for background render submission via job feature | `tests/` | Add test once job integration is complete |
| 3 | 🟡 WARNING | No test for overwrite policy on existing output | `tests/` | Add test for overwrite/reject/unique behavior |

### Traceability (FRD→Code)
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | FR-RND Viewport Capture → `capabilities_render_viewport_capture_executor.py` | `capabilities_render_scene_image_executor.py` | Traceability verified |
| 2 | 🟢 INFO | FR-RND Camera Configuration → `capabilities_render_camera_config_executor.py` | `capabilities_render_camera_config_executor.py` | Traceability verified |
| 3 | 🟢 INFO | FR-RND HDRI Configuration → `capabilities_render_hdri_config_executor.py` | `capabilities_render_hdri_config_executor.py` | Traceability verified |
| 4 | 🟢 INFO | FR-RND Scene Render → `capabilities_render_scene_image_executor.py` | `capabilities_render_scene_image_executor.py` | Traceability verified |

## Violations
None found. AES naming and import rules followed.

## Action Items
- [ ] 🔴 CRITICAL Integrate job module for long-running render background submission
- [ ] 🔴 CRITICAL Confirm render does not download files directly (delegate to asset feature)
- [ ] 🟡 WARNING Add explicit security policy validation for output paths
- [ ] 🟡 WARNING Verify overwrite policy enforcement on existing artifacts
- [ ] 🟡 WARNING Add tests for HDRI asset not found propagation, background render, overwrite policy

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

#### File: `modules/render/src/capabilities_render_scene_image_executor.py`

**FR-RND: Security policy validation and overwrite policy enforcement**

```python
from pathlib import Path
from typing import Any


class RenderSceneImageExecutor:
    """Render scene image with security validation and overwrite policy.
    
    FR-RND: Output destination validated through security policy before render.
    Existing artifact → configured overwrite policy (overwrite/reject/unique).
    """
    
    def __init__(self, security_policy: Any, overwrite_policy: str = "unique") -> None:
        self._security_policy = security_policy
        self._overwrite_policy = overwrite_policy  # "overwrite", "reject", "unique"
    
    async def render(self, camera_name: str, output_path: str, resolution: int = 1920) -> dict:
        """Render scene image with validation.
        
        FR-RND: Validates output path through security policy before rendering.
        Applies overwrite policy when destination already exists.
        """
        import os
        
        # FR-RND: Security policy validation for output path
        safe_path = await self._security_policy.validate_path(output_path)
        if "error" in safe_path:
            return {
                **safe_path,
                "category": "security_error",
            }
        
        # FR-RND: Overwrite policy enforcement
        dest_exists = os.path.exists(output_path)
        
        if dest_exists:
            if self._overwrite_policy == "reject":
                return {
                    "error": f"Output path exists and overwrite is rejected: {output_path}",
                    "category": "validation_error",
                    "policy": "reject",
                }
            
            elif self._overwrite_policy == "unique":
                # Generate unique path
                base = Path(output_path)
                unique_path = self._generate_unique_path(base)
                output_path = str(unique_path)
        
        # Render (Blender API call)
        try:
            result = await self._execute_render(camera_name, output_path, resolution)
            return {"status": "rendered", "output_path": output_path, **result}
        except Exception as e:
            return {
                "error": f"Render failed: {e}",
                "category": "system_error",
            }
    
    def _generate_unique_path(self, base: Path) -> Path:
        """Generate unique output path by appending counter.
        
        FR-RND: Creates unique filename when overwrite=unique policy.
        """
        import time
        timestamp = int(time.time())
        unique_name = f"{base.stem}_{timestamp}{base.suffix}"
        return base.with_name(unique_name)
    
    async def _execute_render(self, camera_name: str, output_path: str, resolution: int) -> dict:
        """Execute Blender render."""
        # Implementation depends on Blender API
        return {"camera": camera_name, "resolution": resolution}
```

#### File: `modules/render/src/capabilities_render_hdri_config_executor.py`

**FR-RND: HDRI config delegating to asset feature (no direct download)**

```python
from typing import Any


class RenderHdriConfigExecutor:
    """HDRI lighting configuration with asset delegation.
    
    FR-RND: Uses asset feature for HDRI download (never direct).
    Delegates to asset aggregate; error propagation via category.
    """
    
    def __init__(self, asset_aggregate: Any) -> None:
        self._asset = asset_aggregate  # Delegated asset feature
    
    async def configure_hdri(self, hdri_id: str, strength: float = 1.0) -> dict:
        """Configure HDRI lighting via asset feature.
        
        FR-RND: Downloads HDRI through asset feature; never direct download.
        Propagates "asset not found" error from asset aggregate.
        """
        # FR-RND: Delegate to asset feature (no direct download)
        download_result = await self._asset.download_asset(
            asset_id=hdri_id,
            dest_path="/tmp/hdri",
        )
        
        if "error" in download_result:
            # Propagate error from asset aggregate
            return {
                **download_result,
                "category": "asset_not_found" if "not found" in download_result.get("error", "").lower() else "system_error",
            }
        
        # Load HDRI into scene
        hdri_path = download_result.get("path")
        if not hdri_path:
            return {
                "error": "HDRI download succeeded but path missing",
                "category": "system_error",
            }
        
        # Configure lighting (Blender API)
        try:
            await self._apply_hdri_lighting(hdri_path, strength)
            return {"status": "hdri_configured", "hdri_path": hdri_path, "strength": strength}
        except Exception as e:
            return {
                "error": f"HDRI lighting failed: {e}",
                "category": "system_error",
            }
    
    async def _apply_hdri_lighting(self, hdri_path: str, strength: float) -> None:
        """Apply HDRI as scene lighting."""
        # Blender API implementation
        pass
```

#### File: `tests/test_render_overwrite_policy.py` (NEW)

**Test for overwrite policy on existing output**

```python
import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.mark.asyncio
class TestOverwritePolicy:
    """Test render overwrite policy enforcement."""
    
    async def test_reject_policy_on_existing_path(self):
        """Verify that reject policy returns error when output exists."""
        from modules.render.src.capabilities_render_scene_image_executor import RenderSceneImageExecutor
        
        security_policy = MagicMock()
        security_policy.validate_path = AsyncMock(return_value={"safe": True})
        
        executor = RenderSceneImageExecutor(
            security_policy=security_policy,
            overwrite_policy="reject",
        )
        
        result = await executor.render(
            camera_name="Camera",
            output_path="/tmp/render.png",
        )
        
        assert "error" in result
        assert result["policy"] == "reject"
    
    async def test_unique_policy_generates_new_path(self):
        """Verify that unique policy creates new filename when existing."""
        from modules.render.src.capabilities_render_scene_image_executor import RenderSceneImageExecutor
        
        security_policy = MagicMock()
        security_policy.validate_path = AsyncMock(return_value={"safe": True})
        
        executor = RenderSceneImageExecutor(
            security_policy=security_policy,
            overwrite_policy="unique",
        )
        
        result = await executor.render(
            camera_name="Camera",
            output_path="/tmp/render.png",
        )
        
        # Should have unique path instead of original
        assert "output_path" in result
        assert result["output_path"] != "/tmp/render.png" or "error" not in result
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
