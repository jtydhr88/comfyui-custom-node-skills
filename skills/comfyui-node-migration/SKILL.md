---
name: comfyui-node-migration
description: ComfyUI V1 to V3 node migration - converting legacy nodes to the V3 API. Use when migrating existing custom nodes from V1 to V3, understanding differences between API versions, or modernizing node code.
---

# ComfyUI V1 → V3 Migration Guide

Migrate existing V1 nodes to the modern V3 API. V3 uses classmethods, typed inputs/outputs, and `ComfyExtension` registration.

## Migration Checklist

1. Change base class to `io.ComfyNode`
2. Replace `INPUT_TYPES()` with `define_schema()` returning `io.Schema`
3. Rename execution function to `execute` and make it a `@classmethod`
4. Replace return tuples with `io.NodeOutput(...)`
5. Replace `IS_CHANGED` with `fingerprint_inputs`
6. Replace `VALIDATE_INPUTS` with `validate_inputs`
7. Convert `check_lazy_status` to `@classmethod`
8. Replace `NODE_CLASS_MAPPINGS` with `ComfyExtension` + `comfy_entrypoint()`
9. Access hidden inputs via `cls.hidden` instead of kwargs
10. Remove `__init__` methods (no instance state in V3)

## Side-by-Side Comparison

### V1 (Before)

```python
import torch

class ImageInvertV1:
    CATEGORY = "image"
    FUNCTION = "invert"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    OUTPUT_TOOLTIPS = ("The inverted image",)
    DESCRIPTION = "Inverts image colors"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "strength": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                }),
            },
            "optional": {
                "mask": ("MASK",),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            },
        }

    @classmethod
    def IS_CHANGED(s, image, strength, mask=None, unique_id=None):
        return strength

    @classmethod
    def VALIDATE_INPUTS(s, image, strength, mask=None, unique_id=None):
        if strength < 0:
            return "Strength must be non-negative"
        return True

    def invert(self, image, strength, mask=None, unique_id=None):
        inverted = 1.0 - image
        result = image * (1 - strength) + inverted * strength
        if mask is not None:
            result = image * (1 - mask.unsqueeze(-1)) + result * mask.unsqueeze(-1)
        return (result,)

NODE_CLASS_MAPPINGS = {"ImageInvertV1": ImageInvertV1}
NODE_DISPLAY_NAME_MAPPINGS = {"ImageInvertV1": "Invert Image"}
```

### V3 (After)

```python
import torch
from typing_extensions import override
from comfy_api.latest import ComfyExtension, io

class ImageInvertV3(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="ImageInvertV3",
            display_name="Invert Image",
            description="Inverts image colors",
            category="image",
            inputs=[
                io.Image.Input("image"),
                io.Float.Input("strength", default=1.0, min=0.0, max=1.0, step=0.01),
                io.Mask.Input("mask", optional=True),
            ],
            outputs=[
                io.Image.Output("IMAGE", tooltip="The inverted image"),
            ],
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    def fingerprint_inputs(cls, image, strength, mask=None):
        return strength

    @classmethod
    def validate_inputs(cls, image, strength, mask=None):
        if strength < 0:
            return "Strength must be non-negative"
        return True

    @classmethod
    def execute(cls, image, strength, mask=None):
        node_id = cls.hidden.unique_id  # access hidden via cls.hidden

        inverted = 1.0 - image
        result = image * (1 - strength) + inverted * strength
        if mask is not None:
            result = image * (1 - mask.unsqueeze(-1)) + result * mask.unsqueeze(-1)
        return io.NodeOutput(result)


class MyExtension(ComfyExtension):
    @override
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [ImageInvertV3]

async def comfy_entrypoint() -> MyExtension:
    return MyExtension()
```

## Property Mapping

| V1 Property | V3 Equivalent |
|---|---|
| `CATEGORY = "image"` | `io.Schema(category="image")` |
| `FUNCTION = "my_func"` | Always `execute` (fixed name) |
| `RETURN_TYPES = ("IMAGE",)` | `outputs=[io.Image.Output()]` |
| `RETURN_NAMES = ("image",)` | `outputs=[io.Image.Output(display_name="image")]` |
| `OUTPUT_TOOLTIPS = ("tip",)` | `outputs=[io.Image.Output(tooltip="tip")]` |
| `OUTPUT_NODE = True` | `io.Schema(is_output_node=True)` |
| `DEPRECATED = True` | `io.Schema(is_deprecated=True)` |
| `EXPERIMENTAL = True` | `io.Schema(is_experimental=True)` |
| `API_NODE = True` | `io.Schema(is_api_node=True)` |
| `NOT_IDEMPOTENT = True` | `io.Schema(not_idempotent=True)` |
| `DESCRIPTION = "..."` | `io.Schema(description="...")` |
| `SEARCH_ALIASES = [...]` | `io.Schema(search_aliases=[...])` |
| `INPUT_IS_LIST = True` | `io.Schema(is_input_list=True)` |
| `OUTPUT_IS_LIST = (True,)` | `io.Image.Output(is_output_list=True)` |
| `DEV_ONLY = True` | `io.Schema(is_dev_only=True)` |
| `ESSENTIALS_CATEGORY = "Basic"` | `io.Schema(essentials_category="Basic")` |

## Input Type Mapping

| V1 Input | V3 Input |
|---|---|
| `("IMAGE",)` | `io.Image.Input("id")` |
| `("MASK",)` | `io.Mask.Input("id")` |
| `("LATENT",)` | `io.Latent.Input("id")` |
| `("MODEL",)` | `io.Model.Input("id")` |
| `("CLIP",)` | `io.Clip.Input("id")` |
| `("VAE",)` | `io.Vae.Input("id")` |
| `("CONDITIONING",)` | `io.Conditioning.Input("id")` |
| `("INT", {"default": 0, ...})` | `io.Int.Input("id", default=0, ...)` |
| `("FLOAT", {"default": 1.0, ...})` | `io.Float.Input("id", default=1.0, ...)` |
| `("STRING", {"multiline": True})` | `io.String.Input("id", multiline=True)` |
| `("BOOLEAN", {"default": True})` | `io.Boolean.Input("id", default=True)` |
| `(["opt1", "opt2"],)` | `io.Combo.Input("id", options=["opt1", "opt2"])` |
| `("CONTROL_NET",)` | `io.ControlNet.Input("id")` |
| `("CLIP_VISION",)` | `io.ClipVision.Input("id")` |
| `("CLIP_VISION_OUTPUT",)` | `io.ClipVisionOutput.Input("id")` |
| `("STYLE_MODEL",)` | `io.StyleModel.Input("id")` |
| `("GLIGEN",)` | `io.Gligen.Input("id")` |
| `("UPSCALE_MODEL",)` | `io.UpscaleModel.Input("id")` |
| `("AUDIO",)` | `io.Audio.Input("id")` |
| `("VIDEO",)` | `io.Video.Input("id")` |
| `("SAMPLER",)` | `io.Sampler.Input("id")` |
| `("SIGMAS",)` | `io.Sigmas.Input("id")` |
| `("NOISE",)` | `io.Noise.Input("id")` |
| `("GUIDER",)` | `io.Guider.Input("id")` |
| `("HOOKS",)` | `io.Hooks.Input("id")` |
| `("LORA_MODEL",)` | `io.LoraModel.Input("id")` |
| `("MESH",)` | `io.Mesh.Input("id")` |
| `("VOXEL",)` | `io.Voxel.Input("id")` |
| `("FILE_3D",)` | `io.File3DAny.Input("id")` |
| `("FILE_3D_GLB",)` | `io.File3DGLB.Input("id")` |
| `("SVG",)` | `io.SVG.Input("id")` |
| `("COLOR",)` | `io.Color.Input("id")` |
| `("BOUNDING_BOX",)` | `io.BoundingBox.Input("id")` |
| `("CURVE",)` | `io.Curve.Input("id")` |
| `("LATENT_UPSCALE_MODEL",)` | `io.LatentUpscaleModel.Input("id")` |
| `("MODEL_PATCH",)` | `io.ModelPatch.Input("id")` |
| `("HOOK_KEYFRAMES",)` | `io.HookKeyframes.Input("id")` |
| `("AUDIO_ENCODER",)` | `io.AudioEncoder.Input("id")` |
| `("AUDIO_ENCODER_OUTPUT",)` | `io.AudioEncoderOutput.Input("id")` |
| `("TRACKS",)` | `io.Tracks.Input("id")` |
| `("LOSS_MAP",)` | `io.LossMap.Input("id")` |
| `("TIMESTEPS_RANGE",)` | `io.TimestepsRange.Input("id")` |
| `("LATENT_OPERATION",)` | `io.LatentOperation.Input("id")` |
| `("WEBCAM",)` | `io.Webcam.Input("id")` |
| `("PHOTOMAKER",)` | `io.Photomaker.Input("id")` |
| `("WAN_CAMERA_EMBEDDING",)` | `io.WanCameraEmbedding.Input("id")` |
| `("LOAD_3D",)` | `io.Load3D.Input("id")` |
| `("LOAD_3D_ANIMATION",)` | `io.Load3DAnimation.Input("id")` |
| `("LOAD3D_CAMERA",)` | `io.Load3DCamera.Input("id")` |
| `("FILE_3D_GLTF",)` | `io.File3DGLTF.Input("id")` |
| `("FILE_3D_FBX",)` | `io.File3DFBX.Input("id")` |
| `("FILE_3D_OBJ",)` | `io.File3DOBJ.Input("id")` |
| `("FILE_3D_STL",)` | `io.File3DSTL.Input("id")` |
| `("FILE_3D_USDZ",)` | `io.File3DUSDZ.Input("id")` |
| `("POINT",)` | `io.Point.Input("id")` |
| `("FACE_ANALYSIS",)` | `io.FaceAnalysis.Input("id")` |
| `("BBOX",)` | `io.BBOX.Input("id")` |
| `("SEGS",)` | `io.SEGS.Input("id")` |
| `("IMAGECOMPARE",)` | `io.ImageCompare.Input("id")` |
| `("*",)` | `io.AnyType.Input("id")` or `io.MultiType.Input("id", types=[...])` |

## Method Migration

### Execute Method

```python
# V1: instance method with custom name
class V1Node:
    FUNCTION = "process"
    def process(self, image, value):
        return (result,)

# V3: classmethod named "execute", returns NodeOutput
class V3Node(io.ComfyNode):
    @classmethod
    def execute(cls, image, value):
        return io.NodeOutput(result)
```

### IS_CHANGED → fingerprint_inputs

```python
# V1
@classmethod
def IS_CHANGED(s, **kwargs):
    return float("NaN")  # always re-execute

# V3
@classmethod
def fingerprint_inputs(cls, **kwargs):
    import time
    return time.time()  # always re-execute
```

### VALIDATE_INPUTS → validate_inputs

```python
# V1
@classmethod
def VALIDATE_INPUTS(s, input_types=None, **kwargs):
    return True

# V3
@classmethod
def validate_inputs(cls, input_types=None, **kwargs):
    return True
```

### check_lazy_status

```python
# V1: instance method
def check_lazy_status(self, **kwargs):
    return ["input_name"]

# V3: classmethod
@classmethod
def check_lazy_status(cls, **kwargs):
    return ["input_name"]
```

### Hidden Inputs

```python
# V1: received as kwargs
def execute(self, image, unique_id=None, prompt=None):
    node_id = unique_id

# V3: accessed via cls.hidden
@classmethod
def execute(cls, image):
    node_id = cls.hidden.unique_id
    prompt = cls.hidden.prompt
```

## Registration Migration

```python
# V1
NODE_CLASS_MAPPINGS = {
    "Node1": Node1Class,
    "Node2": Node2Class,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "Node1": "Node One",
    "Node2": "Node Two",
}
WEB_DIRECTORY = "./js"

# V3
from typing_extensions import override
from comfy_api.latest import ComfyExtension, io

class MyExtension(ComfyExtension):
    @override
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [Node1Class, Node2Class]

    @override
    async def on_load(self):
        # Optional: initialization logic
        pass

async def comfy_entrypoint() -> MyExtension:
    return MyExtension()

# WEB_DIRECTORY still works the same way for JS extensions
WEB_DIRECTORY = "./js"
```

## Output Node Migration

```python
# V1
class V1SaveNode:
    RETURN_TYPES = ()
    OUTPUT_NODE = True
    FUNCTION = "save"

    def save(self, images, prefix):
        # ... save logic ...
        return {"ui": {"images": results}}

# V3
from comfy_api.latest import io, ui

class V3SaveNode(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="V3SaveNode",
            display_name="Save",
            category="image",
            is_output_node=True,
            inputs=[
                io.Image.Input("images"),
                io.String.Input("prefix", default="output"),
            ],
            outputs=[],
            hidden=[io.Hidden.prompt, io.Hidden.extra_pnginfo],
        )

    @classmethod
    def execute(cls, images, prefix):
        saved = ui.ImageSaveHelper.get_save_images_ui(images, prefix, cls=cls)
        return io.NodeOutput(ui=saved)
```

## Key Gotchas

1. **No instance state**: V3 execute is a classmethod. Don't store state on `self`. Use external storage if needed.
2. **Fixed method name**: Always `execute`, never custom names.
3. **Hidden access changed**: Use `cls.hidden.prompt` not function parameters.
4. **Return type changed**: `io.NodeOutput(val)` not `(val,)`.
5. **Optional inputs**: Use `=None` default in execute params, not separate `"optional"` dict.
6. **Async support**: V3 execute can be `async def execute(cls, ...)`.

## See Also

- `comfyui-node-basics` - V3 node fundamentals
- `comfyui-node-packaging` - Project structure
- `comfyui-node-lifecycle` - Execution lifecycle differences
