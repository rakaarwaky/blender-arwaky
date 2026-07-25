from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from modules.shared.src.common.capabilities_action_execute import ActionExecuteActions
from modules.render.src.capabilities_asset_search_collector import AssetSearchCollector
from modules.object.capabilities_import_export_executor import ImportExportExecutor
from modules.object.src.capabilities_object_operate_executor import ObjectOperateExecutor
from modules.render.src.capabilities_render_operate_executor import RenderOperateExecutor
from modules.scene.capabilities_scene_operate_executor import SceneOperateExecutor
from modules.shared.src.common.capabilities_workflow_executor import WorkflowExecutor
from taxonomy import (
    ActionName,
    ApplyModifierRequestVO,
    AssetId,
    AssetMetadataVO,
    AssetName,
    AssetSearchResponseVO,
    AssetType,
    BlenderMCPError,
    BlenderObject,
    BlenderObjectList,
    CleanupSceneRequestVO,
    CoordinateList,
    CreatePrimitiveRequestVO,
    DeleteObjectRequestVO,
    ErrorMessage,
    ExportModelRequestVO,
    FilePath,
    GetObjectInfoRequestVO,
    GetSceneInfoRequestVO,
    GetScreenshotRequestVO,
    HdriId,
    ImportGlbRequestVO,
    ObjectName,
    ObjectType,
    PlaceAssetRequestVO,
    PrimitiveType,
    Prompt,
    ProviderError,
    ProviderName,
    RenderEngine,
    RenderRequestVO,
    RenderSamples,
    RotationVector,
    RuleName,
    SceneInfo,
    SearchQuery,
    SetMaterialRequestVO,
    SetObjectTransformRequestVO,
    SetupEnvironmentRequestVO,
    StringList,
    TagList,
    UseDenoising,
    Vector3D,
)


@pytest.mark.unit
class TestAssetSearchCollector:
    """Tests for AssetSearchCollector."""

    @pytest.mark.asyncio
    async def test_search_all_success(self):
        mock_provider = MagicMock()
        mock_asset = AssetMetadataVO(
            id=AssetId("a1"),
            name=AssetName("A1"),
            type=AssetType("models"),
            provider=ProviderName("polyhaven"),
            thumbnail_url=None,
            tags=TagList(["tag"])
        )
        mock_response = AssetSearchResponseVO(assets=[mock_asset], provider=ProviderName("polyhaven"))
        mock_provider.search_assets = AsyncMock(return_value=mock_response)

        collector = AssetSearchCollector(providers={"polyhaven": mock_provider})
        res = await collector.search_all(SearchQuery("wood"))
        assert len(res) == 1
        assert res[0].name == "A1"

    @pytest.mark.asyncio
    async def test_search_all_provider_error(self):
        mock_provider = MagicMock()
        mock_provider.search_assets = AsyncMock(side_effect=ProviderError(ErrorMessage("API down")))

        collector = AssetSearchCollector(providers={"polyhaven": mock_provider})
        # Should catch and log error, returning empty list
        res = await collector.search_all(SearchQuery("wood"))
        assert len(res) == 0

    @pytest.mark.asyncio
    async def test_search_all_filtered_providers(self):
        mock_p1 = MagicMock()
        mock_p1.search_assets = AsyncMock(return_value=MagicMock(assets=[]))
        mock_p2 = MagicMock()
        mock_p2.search_assets = AsyncMock(return_value=MagicMock(assets=[]))
        collector = AssetSearchCollector(providers={"p1": mock_p1, "p2": mock_p2})

        await collector.search_all(SearchQuery("wood"), providers=StringList(["p1"]))
        mock_p1.search_assets.assert_called_once()
        mock_p2.search_assets.assert_not_called()

    @pytest.mark.asyncio
    async def test_fetch_and_import_success(self):
        mock_provider = MagicMock()
        mock_provider.download_asset = AsyncMock(return_value=MagicMock(file_path="/path/to/my_asset.glb"))

        collector = AssetSearchCollector(providers={"polyhaven": mock_provider})
        res = await collector.fetch_and_import(ProviderName("polyhaven"), AssetId("my_asset"))
        assert res.id == "my_asset"
        assert res.blender_id == "my_asset"

    @pytest.mark.asyncio
    async def test_fetch_and_import_provider_not_found(self):
        collector = AssetSearchCollector(providers={})
        with pytest.raises(ProviderError) as exc:
            await collector.fetch_and_import(ProviderName("polyhaven"), AssetId("my_asset"))
        assert "not found" in str(exc.value)

    @pytest.mark.asyncio
    async def test_fetch_and_import_empty_filepath(self):
        mock_provider = MagicMock()
        mock_provider.download_asset = AsyncMock(return_value=MagicMock(file_path=None))

        collector = AssetSearchCollector(providers={"polyhaven": mock_provider})
        with pytest.raises(ProviderError) as exc:
            await collector.fetch_and_import(ProviderName("polyhaven"), AssetId("my_asset"))
        assert "no file path" in str(exc.value)


@pytest.mark.unit
class TestImportExportExecutor:
    """Tests for ImportExportExecutor."""

    @pytest.mark.asyncio
    async def test_import_glb_success(self):
        mock_blender = MagicMock()
        mock_blender.execute_code = AsyncMock(return_value=None)
        executor = ImportExportExecutor(mock_blender)

        res = await executor.import_glb(ImportGlbRequestVO(file_path=FilePath("/mock/file.glb"), object_name=ObjectName("MyGLB")))
        assert res.success is True
        assert res.object_name == "MyGLB"
        mock_blender.execute_code.assert_called_once()

    @pytest.mark.asyncio
    async def test_import_glb_exception(self):
        mock_blender = MagicMock()
        mock_blender.execute_code = AsyncMock(side_effect=Exception("Execute error"))
        executor = ImportExportExecutor(mock_blender)

        with pytest.raises(BlenderMCPError) as exc:
            await executor.import_glb(ImportGlbRequestVO(file_path=FilePath("/mock/file.glb")))
        assert "Import failed" in str(exc.value)

    @pytest.mark.asyncio
    async def test_export_model_success(self):
        mock_blender = MagicMock()
        mock_blender.execute_code = AsyncMock(return_value=None)
        executor = ImportExportExecutor(mock_blender)

        res = await executor.export_model(ExportModelRequestVO(file_path=FilePath("/mock/file.glb"), object_name=ObjectName("MyCube")))
        assert res.success is True
        assert res.object_name == "MyCube"
        mock_blender.execute_code.assert_called_once()

    @pytest.mark.asyncio
    async def test_export_model_exception(self):
        mock_blender = MagicMock()
        mock_blender.execute_code = AsyncMock(side_effect=Exception("Execute error"))
        executor = ImportExportExecutor(mock_blender)

        with pytest.raises(BlenderMCPError) as exc:
            await executor.export_model(ExportModelRequestVO(file_path=FilePath("/mock/file.glb"), object_name=ObjectName("MyCube")))
        assert "Export failed" in str(exc.value)


@pytest.mark.unit
class TestObjectOperateExecutor:
    """Tests for ObjectOperateExecutor."""

    @pytest.fixture
    def mock_blender(self):
        m = MagicMock()
        m.execute_code = AsyncMock(return_value=None)
        return m

    @pytest.mark.asyncio
    async def test_place_asset_success(self, mock_blender):
        executor = ObjectOperateExecutor(mock_blender)

        # 1. With object name
        res = await executor.place_asset(PlaceAssetRequestVO(asset_id=AssetId("chair"), location=CoordinateList([1.0, 2.0, 3.0]), object_name=ObjectName("chair_mesh")))
        assert res.success is True
        assert res.object_name == "chair_mesh"

        # 2. Without object name
        res2 = await executor.place_asset(PlaceAssetRequestVO(asset_id=AssetId("chair"), location=CoordinateList([1.0, 2.0, 3.0])))
        assert res2.success is True
        assert res2.object_name == "chair"

    @pytest.mark.asyncio
    async def test_place_asset_exception(self, mock_blender):
        mock_blender.execute_code = AsyncMock(side_effect=Exception("Write error"))
        executor = ObjectOperateExecutor(mock_blender)

        with pytest.raises(BlenderMCPError) as exc:
            await executor.place_asset(PlaceAssetRequestVO(asset_id=AssetId("chair"), location=CoordinateList([1, 2, 3])))
        assert "Failed to place" in str(exc.value)

    @pytest.mark.asyncio
    async def test_get_object_info(self, mock_blender):
        mock_blender.get_object_info = AsyncMock(return_value=BlenderObject(
            name=ObjectName("Cube"),
            type=ObjectType("MESH"),
            location=Vector3D(0.0, 0.0, 0.0),
            rotation=Vector3D(0.0, 0.0, 0.0),
            scale=Vector3D(1.0, 1.0, 1.0)
        ))
        executor = ObjectOperateExecutor(mock_blender)

        res = await executor.get_object_info(GetObjectInfoRequestVO(object_name=ObjectName("Cube")))
        assert res.success is True
        mock_blender.get_object_info.assert_called_once_with(ObjectName("Cube"))

        # Exception
        mock_blender.get_object_info = AsyncMock(side_effect=Exception("Not found"))
        with pytest.raises(BlenderMCPError):
            await executor.get_object_info(GetObjectInfoRequestVO(object_name=ObjectName("Cube")))

    @pytest.mark.asyncio
    async def test_set_object_transform(self, mock_blender):
        executor = ObjectOperateExecutor(mock_blender)

        res = await executor.set_object_transform(SetObjectTransformRequestVO(
            object_name=ObjectName("Cube"),
            location=CoordinateList([1, 2, 3]),
            rotation=CoordinateList([0, 0, 90]),
            scale=CoordinateList([2, 2, 2])
        ))
        assert res.success is True

        # Exception
        mock_blender.execute_code = AsyncMock(side_effect=Exception())
        with pytest.raises(BlenderMCPError):
            await executor.set_object_transform(SetObjectTransformRequestVO(object_name=ObjectName("Cube")))

    @pytest.mark.asyncio
    async def test_delete_object(self, mock_blender):
        executor = ObjectOperateExecutor(mock_blender)

        res = await executor.delete_object(DeleteObjectRequestVO(object_name=ObjectName("Cube")))
        assert res.success is True

        # Exception
        mock_blender.execute_code = AsyncMock(side_effect=Exception())
        with pytest.raises(BlenderMCPError):
            await executor.delete_object(DeleteObjectRequestVO(object_name=ObjectName("Cube")))

    @pytest.mark.asyncio
    async def test_create_primitive(self, mock_blender):
        executor = ObjectOperateExecutor(mock_blender)

        # Cube with all params
        res = await executor.create_primitive(CreatePrimitiveRequestVO(
            primitive_type=PrimitiveType("cube"),
            location=CoordinateList([0, 0, 0]),
            scale=CoordinateList([1, 1, 1]),
            name=ObjectName("MyBox")
        ))
        assert res.success is True
        assert res.object_name == "MyBox"

        # Torus
        res2 = await executor.create_primitive(CreatePrimitiveRequestVO(
            primitive_type=PrimitiveType("torus")
        ))
        assert res2.success is True
        assert res2.object_name == "Primitive"

        # Exception
        mock_blender.execute_code = AsyncMock(side_effect=Exception())
        with pytest.raises(BlenderMCPError):
            await executor.create_primitive(CreatePrimitiveRequestVO(primitive_type=PrimitiveType("cube")))

    @pytest.mark.asyncio
    async def test_set_material(self, mock_blender):
        executor = ObjectOperateExecutor(mock_blender)

        res = await executor.set_material(SetMaterialRequestVO(object_name=ObjectName("Cube"), material_name="Gold"))
        assert res.success is True

        # Exception
        mock_blender.execute_code = AsyncMock(side_effect=Exception())
        with pytest.raises(BlenderMCPError):
            await executor.set_material(SetMaterialRequestVO(object_name=ObjectName("Cube"), material_name="Gold"))

    @pytest.mark.asyncio
    async def test_apply_modifier(self, mock_blender):
        executor = ObjectOperateExecutor(mock_blender)

        res = await executor.apply_modifier(ApplyModifierRequestVO(object_name=ObjectName("Cube"), modifier_name="Subsurf"))
        assert res.success is True

        # Exception
        mock_blender.execute_code = AsyncMock(side_effect=Exception())
        with pytest.raises(BlenderMCPError):
            await executor.apply_modifier(ApplyModifierRequestVO(object_name=ObjectName("Cube"), modifier_name="Subsurf"))


@pytest.mark.unit
class TestRenderOperateExecutor:
    """Tests for RenderOperateExecutor."""

    @pytest.fixture
    def mock_blender(self):
        m = MagicMock()
        m.execute_code = AsyncMock(return_value=None)
        return m

    @pytest.mark.asyncio
    async def test_get_viewport_screenshot(self, mock_blender):
        mock_blender.get_screenshot = AsyncMock(return_value=(b"bytes", 1920, 1080))
        executor = RenderOperateExecutor(mock_blender)

        res = await executor.get_viewport_screenshot(GetScreenshotRequestVO(max_size=300))
        assert res.success is True
        assert res.image_data == b"bytes"

        # Exception
        mock_blender.get_screenshot = AsyncMock(side_effect=Exception())
        with pytest.raises(BlenderMCPError):
            await executor.get_viewport_screenshot(GetScreenshotRequestVO(max_size=300))

    @pytest.mark.asyncio
    async def test_setup_camera(self, mock_blender):
        executor = RenderOperateExecutor(mock_blender)

        res = await executor.setup_camera(CoordinateList([1, 2, 3]), RotationVector([0, 0, 0]), CoordinateList([0, 0, 0]))
        assert "successful" in str(res)

        # Exception
        mock_blender.execute_code = AsyncMock(side_effect=Exception())
        with pytest.raises(BlenderMCPError):
            await executor.setup_camera(CoordinateList([1, 2, 3]), RotationVector([0, 0, 0]))

    @pytest.mark.asyncio
    async def test_setup_render(self, mock_blender):
        executor = RenderOperateExecutor(mock_blender)

        res = await executor.setup_render(RenderEngine("CYCLES"), RenderSamples(64), CoordinateList([1920, 1080]), UseDenoising(True))
        assert "configured" in str(res)

        # Exception
        mock_blender.execute_code = AsyncMock(side_effect=Exception())
        with pytest.raises(BlenderMCPError):
            await executor.setup_render()

    @pytest.mark.asyncio
    async def test_apply_composition(self, mock_blender):
        executor = RenderOperateExecutor(mock_blender)

        res = await executor.apply_composition(RuleName("thirds"))
        assert "applied" in str(res)

        res2 = await executor.apply_composition(RuleName("golden"))
        assert "applied" in str(res2)

        # Exception
        mock_blender.execute_code = AsyncMock(side_effect=Exception())
        with pytest.raises(BlenderMCPError):
            await executor.apply_composition(RuleName("thirds"))

    @pytest.mark.asyncio
    async def test_render(self, mock_blender):
        executor = RenderOperateExecutor(mock_blender)

        res = await executor.render(RenderRequestVO(output_path="/tmp/render.png"))
        assert res.success is True

        # Exception
        mock_blender.execute_code = AsyncMock(side_effect=Exception())
        with pytest.raises(BlenderMCPError):
            await executor.render(RenderRequestVO(output_path="/tmp/render.png"))


@pytest.mark.unit
class TestSceneOperateExecutor:
    """Tests for SceneOperateExecutor."""

    @pytest.fixture
    def mock_blender(self):
        m = MagicMock()
        m.execute_code = AsyncMock(return_value=None)
        return m

    @pytest.mark.asyncio
    async def test_cleanup_scene(self, mock_blender):
        executor = SceneOperateExecutor(mock_blender)

        res = await executor.cleanup_scene(CleanupSceneRequestVO())
        assert res.success is True

        # Failed status returned
        mock_blender.execute_code = AsyncMock(side_effect=Exception("Write error"))
        res2 = await executor.cleanup_scene(CleanupSceneRequestVO())
        assert res2.success is False
        assert "Write error" in res2.message

    @pytest.mark.asyncio
    async def test_setup_environment(self, mock_blender):
        executor = SceneOperateExecutor(mock_blender)

        res = await executor.setup_environment(SetupEnvironmentRequestVO(hdri_id=HdriId("studio")))
        assert res.success is True

        # Exception path
        mock_blender.execute_code = AsyncMock(side_effect=Exception("HDRI error"))
        res2 = await executor.setup_environment(SetupEnvironmentRequestVO(hdri_id=HdriId("studio")))
        assert res2.success is False
        assert "HDRI error" in res2.message

    @pytest.mark.asyncio
    async def test_get_scene_info(self, mock_blender):
        mock_blender.get_scene_info = AsyncMock(return_value=SceneInfo(objects=BlenderObjectList([])))
        executor = SceneOperateExecutor(mock_blender)

        res = await executor.get_scene_info(GetSceneInfoRequestVO())
        assert res.success is True

        # Exception path
        mock_blender.get_scene_info = AsyncMock(side_effect=Exception("Socket crash"))
        with pytest.raises(BlenderMCPError):
            await executor.get_scene_info(GetSceneInfoRequestVO())


@pytest.mark.unit
class TestWorkflowExecutor:
    """Tests for WorkflowExecutor."""

    @pytest.fixture
    def mock_scene(self):
        m = MagicMock()
        m.cleanup_scene = AsyncMock()
        m.setup_environment = AsyncMock()
        m.blender = MagicMock()
        m.blender.execute_code = AsyncMock()
        m.generate_and_import_ai_asset = AsyncMock(return_value=Prompt("imported"))
        return m

    @pytest.fixture
    def mock_search(self):
        m = MagicMock()
        m.search_all = AsyncMock()
        return m

    @pytest.mark.asyncio
    async def test_create_basic_scene_success(self, mock_scene, mock_search):
        executor = WorkflowExecutor(mock_scene, mock_search)

        mock_search.search_all.return_value = [MagicMock(name="Chair")]
        res = await executor.create_basic_scene(Prompt("cozy chair"))
        assert res is True
        mock_scene.cleanup_scene.assert_called_once()
        mock_scene.blender.execute_code.assert_called_once()
        mock_scene.setup_environment.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_basic_scene_no_assets(self, mock_scene, mock_search):
        executor = WorkflowExecutor(mock_scene, mock_search)

        mock_search.search_all.return_value = []
        res = await executor.create_basic_scene(Prompt("cozy chair"))
        assert res is False

    @pytest.mark.asyncio
    async def test_create_basic_scene_exception(self, mock_scene, mock_search):
        executor = WorkflowExecutor(mock_scene, mock_search)

        mock_scene.cleanup_scene = AsyncMock(side_effect=BlenderMCPError(ErrorMessage("Blender crash")))
        res = await executor.create_basic_scene(Prompt("cozy chair"))
        assert res is False



@pytest.mark.unit
class TestActionExecuteActions:
    """Tests for ActionExecuteActions capability dispatcher."""

    @pytest.mark.asyncio
    async def test_execute_unknown_action(self):
        dispatcher = ActionExecuteActions(orchestrator=MagicMock())
        res = await dispatcher.execute(ActionName("unknown_action_99"))
        assert "Unknown action" in str(res)

    @pytest.mark.asyncio
    async def test_execute_invalid_capability_format(self):
        dispatcher = ActionExecuteActions(orchestrator=MagicMock())
        with patch("taxonomy.blender_command_vo.CommandCatalog.COMMAND_CATALOG", {"some_action": {"capability": "InvalidFormatNoDot"}}):
            res = await dispatcher.execute(ActionName("some_action"))
            assert "Malformed capability ref" in str(res)

    @pytest.mark.asyncio
    async def test_execute_resolve_capability_error(self):
        dispatcher = ActionExecuteActions(orchestrator=MagicMock())
        with patch("taxonomy.blender_command_vo.CommandCatalog.COMMAND_CATALOG", {"some_action": {"capability": "BlenderPort.execute_code"}}):
            with patch.object(dispatcher, "_resolve_capability", return_value=None):
                res = await dispatcher.execute(ActionName("some_action"))
                assert "No capability" in str(res)

    @pytest.mark.asyncio
    async def test_execute_no_capability_matched(self):
        dispatcher = ActionExecuteActions(orchestrator=MagicMock())
        with patch("taxonomy.blender_command_vo.CommandCatalog.COMMAND_CATALOG", {"some_action": {"capability": "NonexistentProtocol.method"}}):
            res = await dispatcher.execute(ActionName("some_action"))
            assert "No capability" in str(res)

    @pytest.mark.asyncio
    async def test_execute_method_not_found(self):
        mock_orchestrator = MagicMock()
        mock_orchestrator.blender = MagicMock(spec=[])  # no methods
        dispatcher = ActionExecuteActions(orchestrator=mock_orchestrator)
        with patch("taxonomy.blender_command_vo.CommandCatalog.COMMAND_CATALOG", {"some_action": {"capability": "BlenderPort.nonexistent_method"}}):
            res = await dispatcher.execute(ActionName("some_action"))
            assert "has no method" in str(res)

    @pytest.mark.asyncio
    async def test_execute_method_success_and_exception(self):
        mock_cap = MagicMock()
        async def dummy_method(**kwargs):
            if "fail" in kwargs:
                raise Exception("method exception")
            mock_res = MagicMock()
            mock_res.model_dump_json.return_value = '{"success": true}'
            return mock_res

        mock_cap.dummy = dummy_method

        mock_orchestrator = MagicMock()
        mock_orchestrator.operate_scene_capability = mock_cap

        dispatcher = ActionExecuteActions(orchestrator=mock_orchestrator)

        # 1. Success with Pydantic dump
        with patch("taxonomy.blender_command_vo.CommandCatalog.COMMAND_CATALOG", {"some_action": {"capability": "SceneOperateProtocol.dummy"}}):
            res = await dispatcher.execute(ActionName("some_action"), args={"param": 1})
            assert "success" in str(res)

        # 2. Success with dict dump
        async def dict_method(**kwargs):
            return {"data": 123}
        mock_cap.dummy = dict_method
        with patch("taxonomy.blender_command_vo.CommandCatalog.COMMAND_CATALOG", {"some_action": {"capability": "SceneOperateProtocol.dummy"}}):
            res2 = await dispatcher.execute(ActionName("some_action"))
            assert "123" in str(res2)

        # 3. Method exception
        async def fail_method(**kwargs):
            raise Exception("method failure")
        mock_cap.dummy = fail_method
        with patch("taxonomy.blender_command_vo.CommandCatalog.COMMAND_CATALOG", {"some_action": {"capability": "SceneOperateProtocol.dummy"}}):
            res3 = await dispatcher.execute(ActionName("some_action"))
            assert "method failure" in str(res3)

    def test_resolve_all_capabilities(self):
        mock_orch = MagicMock()
        dispatcher = ActionExecuteActions(orchestrator=mock_orch)

        assert dispatcher._resolve_capability("BlenderPort") is mock_orch.blender
        assert dispatcher._resolve_capability("SceneOperateProtocol") is mock_orch.operate_scene_capability
        assert dispatcher._resolve_capability("AssetSearchProtocol") is mock_orch.search_asset_capability
        assert dispatcher._resolve_capability("AssetProviderPort") is mock_orch.search_asset_capability
        assert dispatcher._resolve_capability("ObjectOperateProtocol") is mock_orch.object_operate_capability
        assert dispatcher._resolve_capability("RenderOperateProtocol") is mock_orch.render_operate_capability
        assert dispatcher._resolve_capability("ImportExportProtocol") is mock_orch.import_export_capability
        assert dispatcher._resolve_capability("UnknownProtocol") is None

    @pytest.mark.asyncio
    async def test_execute_empty_action_name(self):
        dispatcher = ActionExecuteActions(orchestrator=MagicMock())
        res = await dispatcher.execute(ActionName(""))
        assert "cannot be empty" in str(res)

    @pytest.mark.asyncio
    async def test_execute_action_name_too_long(self):
        dispatcher = ActionExecuteActions(orchestrator=MagicMock())
        long_name = "a" * 101
        res = await dispatcher.execute(ActionName(long_name))
        assert "exceeds" in str(res)

    @pytest.mark.asyncio
    async def test_execute_action_name_invalid_format(self):
        dispatcher = ActionExecuteActions(orchestrator=MagicMock())
        res = await dispatcher.execute(ActionName("UPPERCASE_BAD"))
        assert "Invalid action name" in str(res)

    @pytest.mark.asyncio
    async def test_execute_non_dict_args(self):
        dispatcher = ActionExecuteActions(orchestrator=MagicMock())
        res = await dispatcher.execute(ActionName("get_scene_info"), args="not_a_dict")
        assert "must be a dict" in str(res)

    def test_serialize_plain_string(self):
        dispatcher = ActionExecuteActions(orchestrator=MagicMock())
        result = dispatcher._serialize("plain_string_result")
        assert result == "plain_string_result"

    def test_sanitize_args_strips_and_truncates(self):
        dispatcher = ActionExecuteActions(orchestrator=MagicMock())
        long_val = "x" * 60000
        args = {"key1": "  hello  ", "key2": long_val}
        sanitized = dispatcher._sanitize_args(args)
        assert sanitized["key1"] == "hello"
        assert len(sanitized["key2"]) == 50000
