"""
Covers: comfyui-node-packaging
- V3 registration (ComfyExtension, comfy_entrypoint, on_load, get_node_list)
- WEB_DIRECTORY

Covers: comfyui-node-advanced (NodeReplace in on_load)

NOTE: V1 legacy nodes are in a separate standalone file
(custom_nodes/skill_test_v1_legacy.py) because ComfyUI's loader treats
NODE_CLASS_MAPPINGS and comfy_entrypoint as mutually exclusive — if
NODE_CLASS_MAPPINGS is present, comfy_entrypoint is never called.
"""

from typing_extensions import override
from comfy_api.latest import ComfyAPI, ComfyExtension, io

# V3 node imports
from .nodes_basics import (
    SkillTest_BasicNode,
    SkillTest_SchemaFields,
    SkillTest_HiddenCategory,
    SkillTest_CategoryHierarchy,
)
from .nodes_inputs import (
    SkillTest_IntInputs,
    SkillTest_FloatInputs,
    SkillTest_StringInputs,
    SkillTest_BooleanInput,
    SkillTest_ComboInputs,
    SkillTest_MultiComboInput,
    SkillTest_ColorInput,
    SkillTest_BoundingBoxInput,
    SkillTest_CurveInput,
    SkillTest_WebcamInput,
    SkillTest_ImageCompareInput,
    SkillTest_InputOptions,
    SkillTest_ForceInput,
    SkillTest_SocketlessInput,
    SkillTest_HiddenInputs,
    SkillTest_LazyEval,
)
from .nodes_outputs import (
    SkillTest_MultiOutput,
    SkillTest_OutputConfig,
    SkillTest_PreviewImage,
    SkillTest_PreviewMask,
    SkillTest_PreviewAudio,
    SkillTest_PreviewText,
    SkillTest_DataPlusUI,
    SkillTest_BlockExecution,
    SkillTest_SaveImage,
    SkillTest_SaveAnimatedPNG,
    SkillTest_SaveAnimatedWebP,
    SkillTest_SaveAudio,
    SkillTest_ManualSave,
    SkillTest_NoOutput,
)
from .nodes_datatypes import (
    SkillTest_ImageOps,
    SkillTest_MaskOps,
    SkillTest_LatentOps,
    SkillTest_CustomType,
    SkillTest_CustomTypeConsumer,
    SkillTest_ComfyType,
    SkillTest_AnyType,
    SkillTest_MultiType,
    SkillTest_MultiTypeWidget,
    SkillTest_TypeConvert,
    SkillTest_TensorSafety,
)
from .nodes_advanced import (
    SkillTest_MatchType,
    SkillTest_SwitchNode,
    SkillTest_AutogrowPrefix,
    SkillTest_AutogrowNames,
    SkillTest_DynamicCombo,
    SkillTest_DynamicComboNested,
    SkillTest_DynamicSlot,
    SkillTest_NodeExpansion,
    SkillTest_AcceptAll,
    SkillTest_GateNode,
    SkillTest_AsyncNode,
    SkillTest_ProgressNode,
)
from .nodes_lifecycle import (
    SkillTest_FingerprintNode,
    SkillTest_NotIdempotent,
    SkillTest_ValidateNode,
    SkillTest_SkipTypeValidation,
    SkillTest_OutputNode,
    SkillTest_ListProcessing,
    SkillTest_ErrorHandling,
    SkillTest_ServerComm,
    SkillTest_FolderPaths,
    SkillTest_FullLifecycle,
)

# Frontend JS extensions
WEB_DIRECTORY = "./js"


class SkillTestExtension(ComfyExtension):
    @override
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [
            # basics
            SkillTest_BasicNode,
            SkillTest_SchemaFields,
            SkillTest_HiddenCategory,
            SkillTest_CategoryHierarchy,
            # inputs
            SkillTest_IntInputs,
            SkillTest_FloatInputs,
            SkillTest_StringInputs,
            SkillTest_BooleanInput,
            SkillTest_ComboInputs,
            SkillTest_MultiComboInput,
            SkillTest_ColorInput,
            SkillTest_BoundingBoxInput,
            SkillTest_CurveInput,
            SkillTest_WebcamInput,
            SkillTest_ImageCompareInput,
            SkillTest_InputOptions,
            SkillTest_ForceInput,
            SkillTest_SocketlessInput,
            SkillTest_HiddenInputs,
            SkillTest_LazyEval,
            # outputs
            SkillTest_MultiOutput,
            SkillTest_OutputConfig,
            SkillTest_PreviewImage,
            SkillTest_PreviewMask,
            SkillTest_PreviewAudio,
            SkillTest_PreviewText,
            SkillTest_DataPlusUI,
            SkillTest_BlockExecution,
            SkillTest_SaveImage,
            SkillTest_SaveAnimatedPNG,
            SkillTest_SaveAnimatedWebP,
            SkillTest_SaveAudio,
            SkillTest_ManualSave,
            SkillTest_NoOutput,
            # datatypes
            SkillTest_ImageOps,
            SkillTest_MaskOps,
            SkillTest_LatentOps,
            SkillTest_CustomType,
            SkillTest_CustomTypeConsumer,
            SkillTest_ComfyType,
            SkillTest_AnyType,
            SkillTest_MultiType,
            SkillTest_MultiTypeWidget,
            SkillTest_TypeConvert,
            SkillTest_TensorSafety,
            # advanced
            SkillTest_MatchType,
            SkillTest_SwitchNode,
            SkillTest_AutogrowPrefix,
            SkillTest_AutogrowNames,
            SkillTest_DynamicCombo,
            SkillTest_DynamicComboNested,
            SkillTest_DynamicSlot,
            SkillTest_NodeExpansion,
            SkillTest_AcceptAll,
            SkillTest_GateNode,
            SkillTest_AsyncNode,
            SkillTest_ProgressNode,
            # lifecycle
            SkillTest_FingerprintNode,
            SkillTest_NotIdempotent,
            SkillTest_ValidateNode,
            SkillTest_SkipTypeValidation,
            SkillTest_OutputNode,
            SkillTest_ListProcessing,
            SkillTest_ErrorHandling,
            SkillTest_ServerComm,
            SkillTest_FolderPaths,
            SkillTest_FullLifecycle,
        ]

    @override
    async def on_load(self):
        # NodeReplace demo: register a migration from a hypothetical old node
        api = ComfyAPI()
        await api.node_replacement.register(io.NodeReplace(
            new_node_id="SkillTest_BasicNode",
            old_node_id="SkillTest_OldBasicNode",
            old_widget_ids=["strength"],
            input_mapping=[
                {"new_id": "image", "old_id": "image"},
                {"new_id": "strength", "old_id": "strength"},
            ],
            output_mapping=[
                {"new_idx": 0, "old_idx": 0},
            ],
        ))


async def comfy_entrypoint() -> SkillTestExtension:
    return SkillTestExtension()
