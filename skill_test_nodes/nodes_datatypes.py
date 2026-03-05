"""
Covers: comfyui-node-datatypes
- IMAGE type operations (shape, clamp, batch)
- MASK type operations (invert, dim check, convert)
- LATENT type operations (dict copy, preserve keys)
- Custom types (io.Custom inline)
- @comfytype decorator
- AnyType wildcard
- MultiType (with and without widget override)
- Type conversion patterns (IMAGE <-> MASK, resize)
- Tensor safety (is not None)
"""

import torch
import torch.nn.functional as F
from typing import Any
from comfy_api.latest import io
from comfy_api.latest._io import comfytype, ComfyTypeIO


# --- datatypes: IMAGE operations ---
class SkillTest_ImageOps(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_ImageOps",
            display_name="[Test] IMAGE Operations",
            category="skill_tests/datatypes",
            inputs=[
                io.Image.Input("image"),
                io.Float.Input("brightness", default=1.5, min=0.0, max=3.0),
            ],
            outputs=[
                io.Image.Output("IMAGE"),
                io.String.Output("INFO"),
            ],
        )

    @classmethod
    def execute(cls, image, brightness):
        b, h, w, c = image.shape
        result = torch.clamp(image * brightness, 0.0, 1.0)
        info = f"batch={b}, height={h}, width={w}, channels={c}"
        return io.NodeOutput(result, info)


# --- datatypes: MASK operations ---
class SkillTest_MaskOps(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_MaskOps",
            display_name="[Test] MASK Operations",
            category="skill_tests/datatypes",
            inputs=[
                io.Mask.Input("mask"),
                io.Boolean.Input("invert", default=False),
            ],
            outputs=[
                io.Mask.Output("MASK"),
                io.Image.Output("IMAGE"),
            ],
        )

    @classmethod
    def execute(cls, mask, invert):
        # Ensure batch dim
        if mask.dim() == 2:
            mask = mask.unsqueeze(0)

        if invert:
            mask = 1.0 - mask

        # MASK [B,H,W] -> IMAGE [B,H,W,C]
        image_from_mask = mask.unsqueeze(-1).repeat(1, 1, 1, 3)

        return io.NodeOutput(mask, image_from_mask)


# --- datatypes: LATENT operations ---
class SkillTest_LatentOps(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_LatentOps",
            display_name="[Test] LATENT Operations",
            category="skill_tests/datatypes",
            inputs=[
                io.Latent.Input("latent"),
                io.Float.Input("scale", default=1.0, min=0.0, max=2.0),
            ],
            outputs=[
                io.Latent.Output("LATENT"),
                io.String.Output("INFO"),
            ],
        )

    @classmethod
    def execute(cls, latent, scale):
        samples = latent["samples"]  # [B, C, H, W]
        b, c, h, w = samples.shape

        # Always preserve extra keys when modifying
        result = latent.copy()
        result["samples"] = samples * scale

        info = f"batch={b}, channels={c}, latent_h={h}, latent_w={w}"
        return io.NodeOutput(result, info)


# --- datatypes: Custom type (io.Custom inline) ---
MyData = io.Custom("SKILL_TEST_DATA")


class SkillTest_CustomType(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_CustomType",
            display_name="[Test] Custom Type",
            category="skill_tests/datatypes",
            inputs=[
                io.String.Input("key", default="test"),
                io.Float.Input("value", default=1.0),
            ],
            outputs=[MyData.Output("MY_DATA")],
        )

    @classmethod
    def execute(cls, key, value):
        return io.NodeOutput({"key": key, "value": value})


class SkillTest_CustomTypeConsumer(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_CustomTypeConsumer",
            display_name="[Test] Custom Type Consumer",
            category="skill_tests/datatypes",
            inputs=[MyData.Input("data")],
            outputs=[io.String.Output("TEXT")],
        )

    @classmethod
    def execute(cls, data):
        return io.NodeOutput(f"key={data['key']}, value={data['value']}")


# --- datatypes: @comfytype decorator ---
@comfytype(io_type="SKILL_TEST_ADVANCED_DATA")
class AdvancedData(ComfyTypeIO):
    Type = dict[str, Any]


class SkillTest_ComfyType(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_ComfyType",
            display_name="[Test] @comfytype",
            category="skill_tests/datatypes",
            inputs=[io.String.Input("name", default="test")],
            outputs=[AdvancedData.Output("DATA")],
        )

    @classmethod
    def execute(cls, name):
        return io.NodeOutput({"name": name, "values": [1, 2, 3]})


# --- datatypes: AnyType wildcard ---
class SkillTest_AnyType(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_AnyType",
            display_name="[Test] AnyType",
            category="skill_tests/datatypes",
            inputs=[
                io.AnyType.Input("anything"),
            ],
            outputs=[io.String.Output("TEXT")],
        )

    @classmethod
    def execute(cls, anything):
        return io.NodeOutput(f"type={type(anything).__name__}")


# --- datatypes: MultiType (type list) ---
class SkillTest_MultiType(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_MultiType",
            display_name="[Test] MultiType",
            category="skill_tests/datatypes",
            inputs=[
                io.MultiType.Input("data",
                    types=[io.Image, io.Mask, io.Latent],
                    optional=True,
                ),
            ],
            outputs=[io.String.Output("TEXT")],
        )

    @classmethod
    def execute(cls, data=None):
        if data is None:
            return io.NodeOutput("no data")
        return io.NodeOutput(f"received type: {type(data).__name__}")


# --- datatypes: MultiType with widget override ---
class SkillTest_MultiTypeWidget(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_MultiTypeWidget",
            display_name="[Test] MultiType Widget",
            category="skill_tests/datatypes",
            inputs=[
                io.MultiType.Input(
                    io.Float.Input("value", default=1.0),
                    types=[io.Float, io.Int],
                ),
            ],
            outputs=[io.String.Output("TEXT")],
        )

    @classmethod
    def execute(cls, value):
        return io.NodeOutput(f"value={value} (type={type(value).__name__})")


# --- datatypes: Type conversion patterns ---
class SkillTest_TypeConvert(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_TypeConvert",
            display_name="[Test] Type Convert",
            category="skill_tests/datatypes",
            inputs=[
                io.Image.Input("image"),
                io.Int.Input("new_width", default=256, min=1, max=4096),
                io.Int.Input("new_height", default=256, min=1, max=4096),
            ],
            outputs=[
                io.Mask.Output("MASK"),
                io.Image.Output("RESIZED"),
            ],
        )

    @classmethod
    def execute(cls, image, new_width, new_height):
        # IMAGE [B,H,W,C] -> MASK [B,H,W] (luminance)
        mask = 0.299 * image[:, :, :, 0] + 0.587 * image[:, :, :, 1] + 0.114 * image[:, :, :, 2]

        # Resize image tensor
        resized = F.interpolate(
            image.permute(0, 3, 1, 2),  # [B,C,H,W] for interpolate
            size=(new_height, new_width), mode='bilinear', align_corners=False
        ).permute(0, 2, 3, 1)  # back to [B,H,W,C]

        return io.NodeOutput(mask, resized)


# --- datatypes: Tensor safety ---
class SkillTest_TensorSafety(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_TensorSafety",
            display_name="[Test] Tensor Safety",
            category="skill_tests/datatypes",
            inputs=[
                io.Image.Input("image"),
                io.Mask.Input("mask", optional=True),
            ],
            outputs=[io.Image.Output("IMAGE")],
        )

    @classmethod
    def execute(cls, image, mask=None):
        # CORRECT: use "is not None" for tensor checks
        if mask is not None:
            if mask.dim() == 2:
                mask = mask.unsqueeze(0)
            image = image * mask.unsqueeze(-1)

        # For boolean conditions on tensors, use .all() or .any()
        if (image > 0.5).any():
            image = torch.clamp(image, 0.0, 1.0)

        return io.NodeOutput(image)
