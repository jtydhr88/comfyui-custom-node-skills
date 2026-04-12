"""
Covers: comfyui-node-advanced
- MatchType (Template, Input, Output)
- Switch node with MatchType + lazy
- Autogrow TemplatePrefix
- Autogrow TemplateNames
- DynamicCombo (Options, nested)
- Node expansion (GraphBuilder, enable_expand)
- accept_all_inputs
- Execution blocking (block_execution)
- Async execute
- Progress reporting (ComfyAPISync / ComfyAPI)
- ComfyAPI runtime API
"""

import time
import torch
from comfy_api.latest import io, ComfyAPISync
from comfy_execution.graph_utils import GraphBuilder


# --- advanced: MatchType pass-through ---
class SkillTest_MatchType(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        template = io.MatchType.Template("T")
        return io.Schema(
            node_id="SkillTest_MatchType",
            display_name="[Test] MatchType Pass-Through",
            category="skill_tests/advanced",
            inputs=[
                io.MatchType.Input("value", template=template),
            ],
            outputs=[
                io.MatchType.Output(template=template, display_name="output"),
            ],
        )

    @classmethod
    def execute(cls, value):
        return io.NodeOutput(value)


# --- advanced: Switch node (MatchType + lazy) ---
class SkillTest_SwitchNode(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        template = io.MatchType.Template("switch")
        return io.Schema(
            node_id="SkillTest_SwitchNode",
            display_name="[Test] Switch Node",
            category="skill_tests/advanced",
            inputs=[
                io.Boolean.Input("switch"),
                io.MatchType.Input("on_false", template=template, lazy=True),
                io.MatchType.Input("on_true", template=template, lazy=True),
            ],
            outputs=[
                io.MatchType.Output(template=template, display_name="output"),
            ],
        )

    @classmethod
    def check_lazy_status(cls, switch, on_false=None, on_true=None):
        if switch and on_true is None:
            return ["on_true"]
        if not switch and on_false is None:
            return ["on_false"]

    @classmethod
    def execute(cls, switch, on_true, on_false):
        return io.NodeOutput(on_true if switch else on_false)


# --- advanced: Autogrow TemplatePrefix ---
class SkillTest_AutogrowPrefix(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_AutogrowPrefix",
            display_name="[Test] Autogrow Prefix",
            category="skill_tests/advanced",
            inputs=[
                io.Autogrow.Input("images",
                    template=io.Autogrow.TemplatePrefix(
                        input=io.Image.Input("img"),
                        prefix="image_",
                        min=2,
                        max=16,
                    ),
                ),
            ],
            outputs=[io.Image.Output("IMAGE")],
        )

    @classmethod
    def execute(cls, images: io.Autogrow.Type):
        tensors = [v for v in images.values() if v is not None]
        return io.NodeOutput(torch.cat(tensors, dim=0))


# --- advanced: Autogrow TemplateNames ---
class SkillTest_AutogrowNames(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_AutogrowNames",
            display_name="[Test] Autogrow Names",
            category="skill_tests/advanced",
            inputs=[
                io.Autogrow.Input("inputs",
                    template=io.Autogrow.TemplateNames(
                        input=io.Float.Input("val"),
                        names=["red", "green", "blue", "alpha"],
                        min=3,
                    ),
                ),
            ],
            outputs=[io.String.Output("TEXT")],
        )

    @classmethod
    def execute(cls, inputs: io.Autogrow.Type):
        parts = [f"{k}={v}" for k, v in inputs.items() if v is not None]
        return io.NodeOutput(", ".join(parts))


# --- advanced: DynamicCombo ---
class SkillTest_DynamicCombo(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_DynamicCombo",
            display_name="[Test] DynamicCombo",
            category="skill_tests/advanced",
            inputs=[
                io.DynamicCombo.Input("mode", options=[
                    io.DynamicCombo.Option("resize", [
                        io.Int.Input("width", default=512, min=1, max=8192),
                        io.Int.Input("height", default=512, min=1, max=8192),
                    ]),
                    io.DynamicCombo.Option("blur", [
                        io.Float.Input("radius", default=5.0, min=0.1, max=100.0),
                    ]),
                    io.DynamicCombo.Option("sharpen", [
                        io.Float.Input("amount", default=1.0, min=0.0, max=10.0),
                    ]),
                ]),
                io.Image.Input("image"),
            ],
            outputs=[io.Image.Output("IMAGE")],
        )

    @classmethod
    def execute(cls, mode: io.DynamicCombo.Type, image, **kwargs):
        selected = mode["mode"]
        if selected == "resize":
            width = mode["width"]
            height = mode["height"]
        elif selected == "blur":
            radius = mode["radius"]
        elif selected == "sharpen":
            amount = mode["amount"]
        return io.NodeOutput(image)


# --- advanced: Nested DynamicCombo ---
class SkillTest_DynamicComboNested(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_DynamicComboNested",
            display_name="[Test] Nested DynamicCombo",
            category="skill_tests/advanced",
            inputs=[
                io.DynamicCombo.Input("outer", options=[
                    io.DynamicCombo.Option("option1", [
                        io.DynamicCombo.Input("inner", options=[
                            io.DynamicCombo.Option("sub1", [
                                io.Float.Input("val", default=1.0),
                            ]),
                            io.DynamicCombo.Option("sub2", [
                                io.Int.Input("count", default=5),
                            ]),
                        ]),
                    ]),
                    io.DynamicCombo.Option("option2", [
                        io.String.Input("label", default="test"),
                    ]),
                ]),
            ],
            outputs=[io.String.Output("TEXT")],
        )

    @classmethod
    def execute(cls, outer: io.DynamicCombo.Type, **kwargs):
        return io.NodeOutput(str(outer))



# --- advanced: Node expansion (GraphBuilder) ---
class SkillTest_NodeExpansion(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_NodeExpansion",
            display_name="[Test] Node Expansion",
            category="skill_tests/advanced",
            enable_expand=True,
            inputs=[
                io.Image.Input("image"),
                io.Int.Input("repeat_count", default=2, min=1, max=5),
                io.Float.Input("brightness", default=1.2, min=0.1, max=3.0),
            ],
            outputs=[io.Image.Output("IMAGE")],
        )

    @classmethod
    def execute(cls, image, repeat_count, brightness):
        graph = GraphBuilder()
        current = image
        for i in range(repeat_count):
            node = graph.node("SkillTest_BasicNode",
                image=current,
                strength=brightness,
            )
            current = node.out(0)
        return io.NodeOutput(current, expand=graph.finalize())


# --- advanced: accept_all_inputs ---
class SkillTest_AcceptAll(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_AcceptAll",
            display_name="[Test] Accept All Inputs",
            category="skill_tests/advanced",
            accept_all_inputs=True,
            inputs=[
                io.Combo.Input("mode", options=["debug", "dump"]),
            ],
            outputs=[io.String.Output("TEXT")],
        )

    @classmethod
    def validate_inputs(cls, mode, **kwargs):
        return True

    @classmethod
    def execute(cls, mode, **kwargs):
        return io.NodeOutput(f"mode={mode}, extras={list(kwargs.keys())}")


# --- advanced: Execution blocking (gate) ---
class SkillTest_GateNode(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_GateNode",
            display_name="[Test] Gate Node",
            category="skill_tests/advanced",
            inputs=[
                io.Boolean.Input("allow"),
                io.Image.Input("image"),
            ],
            outputs=[io.Image.Output("IMAGE")],
        )

    @classmethod
    def execute(cls, allow, image):
        if not allow:
            return io.NodeOutput(block_execution="Gate is closed")
        return io.NodeOutput(image)


# --- advanced: Async execute ---
class SkillTest_AsyncNode(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_AsyncNode",
            display_name="[Test] Async Node",
            category="skill_tests/advanced",
            inputs=[io.String.Input("message", default="hello async")],
            outputs=[io.String.Output("TEXT")],
        )

    @classmethod
    async def execute(cls, message):
        import asyncio
        await asyncio.sleep(0.01)
        return io.NodeOutput(f"async: {message}")


# --- advanced: Progress reporting ---
class SkillTest_ProgressNode(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_ProgressNode",
            display_name="[Test] Progress Node",
            category="skill_tests/advanced",
            inputs=[
                io.Int.Input("steps", default=10, min=1, max=100),
            ],
            outputs=[io.String.Output("TEXT")],
        )

    @classmethod
    def execute(cls, steps):
        api = ComfyAPISync()
        for i in range(steps):
            time.sleep(0.01)
            api.execution.set_progress(i + 1, steps)
        return io.NodeOutput(f"completed {steps} steps")
