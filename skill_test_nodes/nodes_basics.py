"""
Covers: comfyui-node-basics
- V3 node class structure (io.ComfyNode, define_schema, execute)
- All Schema fields
- Hidden category prefix "_"
- Multiple outputs
- Category hierarchy with "/"
"""

import torch
from comfy_api.latest import io


# --- basics: Quick Start / minimal V3 node ---
class SkillTest_BasicNode(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_BasicNode",
            display_name="[Test] Basic Node",
            category="skill_tests/basics",
            inputs=[
                io.Image.Input("image"),
                io.Float.Input("strength", default=1.0, min=0.0, max=1.0, step=0.01),
            ],
            outputs=[
                io.Image.Output("IMAGE"),
            ],
        )

    @classmethod
    def execute(cls, image, strength):
        result = image * strength
        return io.NodeOutput(result)


# --- basics: All Schema fields ---
class SkillTest_SchemaFields(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_SchemaFields",
            display_name="[Test] Schema Fields",
            category="skill_tests/basics",
            description="Demonstrates all io.Schema fields",
            inputs=[
                io.String.Input("text", default="hello"),
            ],
            outputs=[
                io.String.Output("TEXT"),
            ],
            hidden=[io.Hidden.unique_id],
            is_output_node=False,
            is_experimental=True,
            is_deprecated=False,
            is_dev_only=False,
            is_api_node=False,
            is_input_list=False,
            not_idempotent=False,
            accept_all_inputs=False,
            enable_expand=False,
            has_intermediate_output=False,
            search_aliases=["test_schema", "demo_fields"],
            # essentials_category="Basic",  # omit: internal use
            # price_badge=None,             # omit: API node use
        )

    @classmethod
    def execute(cls, text):
        node_id = cls.hidden.unique_id
        return io.NodeOutput(f"{text} (node:{node_id})")


# --- basics: Hidden category (underscore prefix) ---
class SkillTest_HiddenCategory(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_HiddenCategory",
            display_name="[Test] Hidden Category",
            category="_skill_tests/hidden",  # prefixed with "_" -> hidden from menus
            inputs=[io.Float.Input("x", default=0.0)],
            outputs=[io.Float.Output("FLOAT")],
        )

    @classmethod
    def execute(cls, x):
        return io.NodeOutput(x)


# --- basics: Category hierarchy with "/" ---
class SkillTest_CategoryHierarchy(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_CategoryHierarchy",
            display_name="[Test] Category Hierarchy",
            category="skill_tests/basics/sub/deep",
            inputs=[io.Int.Input("value", default=42)],
            outputs=[io.Int.Output("INT")],
        )

    @classmethod
    def execute(cls, value):
        return io.NodeOutput(value)
