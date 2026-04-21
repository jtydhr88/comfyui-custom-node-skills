---
name: comfyui-node-inputs
description: ComfyUI node input types - INT, FLOAT, STRING, BOOLEAN, COMBO widgets, hidden inputs, optional inputs, lazy inputs, force_input. Use when configuring node inputs, adding widgets, or customizing input behavior.
---

# ComfyUI Node Inputs

Inputs define what data a node accepts. Widget inputs create UI controls; connection inputs create socket slots.

## Widget Input Types

### INT

```python
io.Int.Input("seed",
    default=0,
    min=0,
    max=0xffffffffffffffff,
    step=1,
    control_after_generate=True,  # adds increment/decrement/randomize control
    display_mode=io.NumberDisplay.number,  # "number", "slider", or "gradient_slider"
    tooltip="Random seed for generation",
)
```

**NumberDisplay options**: `io.NumberDisplay.number`, `io.NumberDisplay.slider`, `io.NumberDisplay.gradient_slider`

**ControlAfterGenerate options**: `True` (default randomize), or `io.ControlAfterGenerate.fixed`, `.increment`, `.decrement`, `.randomize`

### FLOAT

```python
io.Float.Input("strength",
    default=1.0,
    min=0.0,
    max=10.0,
    step=0.01,
    round=0.001,         # rounding precision
    display_mode=io.NumberDisplay.slider,
    gradient_stops=[{"offset": 0.0, "color": [0, 0, 0]}, {"offset": 1.0, "color": [255, 255, 255]}],  # for gradient_slider mode
    tooltip="Effect strength",
)
```

### STRING

```python
# Single-line string
io.String.Input("name",
    default="",
    placeholder="Enter name...",
)

# Multi-line text area
io.String.Input("prompt",
    multiline=True,
    default="",
    placeholder="Enter prompt...",
    dynamic_prompts=True,  # enable dynamic prompt syntax
)
```

### BOOLEAN

```python
io.Boolean.Input("enabled",
    default=True,
    label_on="Enabled",
    label_off="Disabled",
    tooltip="Toggle this feature",
)
```

### COMBO (Dropdown)

```python
io.Combo.Input("mode",
    options=["option_a", "option_b", "option_c"],
    default="option_a",
    tooltip="Select processing mode",
    control_after_generate=True,  # adds increment/decrement/randomize control
)
```

**Combo with Enum**:
```python
from enum import Enum

class BlendMode(Enum):
    NORMAL = "normal"
    MULTIPLY = "multiply"
    SCREEN = "screen"

io.Combo.Input("blend", options=BlendMode, default=BlendMode.NORMAL)
# Enum values auto-converted to string list
```

**Combo with file upload**:
```python
io.Combo.Input("image_file",
    options=[],
    upload=io.UploadType.image,          # .image, .audio, .video, .model (for generic file upload)
    image_folder=io.FolderType.input,    # .input, .output, .temp
)
```

**Dynamic combo with remote options**:
```python
io.Combo.Input("model_name",
    options=[],
    remote=io.RemoteOptions(
        route="/internal/models/checkpoints",
        refresh_button=True,
        control_after_refresh="first",  # "first" or "last"
        timeout=5000,        # ms
        max_retries=3,
        refresh=60000,       # TTL refresh interval in ms
    ),
)
```

### MULTICOMBO (Multi-select Dropdown)

```python
io.MultiCombo.Input("tags",
    options=["tag1", "tag2", "tag3", "tag4"],
    default=["tag1"],
    placeholder="Select tags...",
    chip=True,  # display as chips
)
# Value type: list[str]
```

### COLOR (Color Picker)

```python
io.Color.Input("color",
    default="#ffffff",
    socketless=True,  # widget only by default
)
# Value type: str (hex color)
```

### BOUNDING_BOX (Rectangle Selector)

```python
io.BoundingBox.Input("region",
    default={"x": 0, "y": 0, "width": 512, "height": 512},
    socketless=True,
    component="my_component",  # optional custom UI component name
    force_input=False,
)
# Value type: {"x": int, "y": int, "width": int, "height": int}
```

### CURVE (Spline Editor)

```python
io.Curve.Input("curve",
    default=[(0.0, 0.0), (1.0, 1.0)],  # linear ramp
    socketless=True,
)
# Value type: list[tuple[float, float]]
```

### WEBCAM (Camera Capture)

```python
io.Webcam.Input("capture")
# Value type: str
```

### IMAGECOMPARE (Comparison Widget)

```python
io.ImageCompare.Input("comparison", socketless=True)
# Value type: dict
```

## Input Options (Common to All)

```python
io.Image.Input("image",
    optional=True,        # not required; creates optional input socket
    tooltip="Description shown on hover",
    lazy=True,            # lazy evaluation - only computed when needed
    advanced=True,        # hidden by default in compact mode
    raw_link=True,        # receive raw link reference instead of value
)
```

### force_input

Forces a widget input to appear as a connection socket instead of a widget:

```python
io.Float.Input("value",
    default=1.0,
    force_input=True,   # shows as socket, not slider
)
```

### socketless

Makes a widget input appear only as a widget with no input socket:

```python
io.String.Input("note",
    default="",
    socketless=True,     # widget only, no connection socket
)
```

## Optional Inputs

```python
class MyNode(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="MyNode",
            display_name="My Node",
            category="example",
            inputs=[
                io.Image.Input("image"),                        # required
                io.Mask.Input("mask", optional=True),           # optional
                io.Float.Input("blend", default=0.5),           # has default widget
            ],
            outputs=[io.Image.Output("IMAGE")],
        )

    @classmethod
    def execute(cls, image, mask=None, blend=0.5):
        # Optional inputs default to None when not connected
        if mask is not None:
            image = image * (1 - blend) + image * mask.unsqueeze(-1) * blend
        return io.NodeOutput(image)
```

## Hidden Inputs

Hidden inputs receive server-provided values, not user input:

```python
class MyNode(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="MyNode",
            display_name="My Node",
            category="example",
            inputs=[io.String.Input("text")],
            outputs=[io.String.Output()],
            hidden=[
                io.Hidden.unique_id,       # node's unique ID
                io.Hidden.prompt,           # full prompt data
                io.Hidden.extra_pnginfo,    # PNG metadata dict
                io.Hidden.dynprompt,        # dynamic prompt object
                io.Hidden.auth_token_comfy_org,  # auth token
                io.Hidden.api_key_comfy_org,     # API key
            ],
        )

    @classmethod
    def execute(cls, text):
        # Access hidden values via cls.hidden
        node_id = cls.hidden.unique_id
        prompt = cls.hidden.prompt
        extra = cls.hidden.extra_pnginfo
        return io.NodeOutput(f"{text} (node: {node_id})")
```

## Lazy Evaluation

Lazy inputs are only evaluated when actually needed, saving computation:

```python
class ConditionalNode(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="ConditionalNode",
            display_name="Conditional",
            category="logic",
            inputs=[
                io.Boolean.Input("condition"),
                io.Image.Input("if_true", lazy=True),
                io.Image.Input("if_false", lazy=True),
            ],
            outputs=[io.Image.Output("IMAGE")],
        )

    @classmethod
    def check_lazy_status(cls, condition, if_true=None, if_false=None):
        """Return list of input names that need evaluation."""
        if condition and if_true is None:
            return ["if_true"]
        if not condition and if_false is None:
            return ["if_false"]
        return []

    @classmethod
    def execute(cls, condition, if_true, if_false):
        return io.NodeOutput(if_true if condition else if_false)
```

**Rules for lazy evaluation**:
- Mark inputs with `lazy=True`
- Implement `check_lazy_status()` classmethod
- Unevaluated inputs are `None`
- Return list of input names that need computing, or empty list
- Method may be called multiple times

## V1 Input Format (Legacy Reference)

```python
@classmethod
def INPUT_TYPES(s):
    return {
        "required": {
            "image": ("IMAGE",),
            "strength": ("FLOAT", {
                "default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01
            }),
            "mode": (["option_a", "option_b"],),
            "text": ("STRING", {"multiline": True, "default": ""}),
        },
        "optional": {
            "mask": ("MASK",),
        },
        "hidden": {
            "unique_id": "UNIQUE_ID",
            "prompt": "PROMPT",
            "extra_pnginfo": "EXTRA_PNGINFO",
        },
    }
```

## Complete Example: Multi-Input Node

```python
class AdvancedImageNode(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="AdvancedImageNode",
            display_name="Advanced Image",
            category="image/advanced",
            description="Demonstrates various input types",
            inputs=[
                # Required connection input
                io.Image.Input("image", tooltip="Input image"),
                # Required widget inputs
                io.Float.Input("brightness", default=1.0, min=0.0, max=3.0,
                               step=0.1, display_mode=io.NumberDisplay.slider),
                io.Float.Input("contrast", default=1.0, min=0.0, max=3.0, step=0.1),
                io.Int.Input("seed", default=0, min=0, max=0xffffffffffffffff,
                             control_after_generate=True),
                io.Combo.Input("blend_mode", options=["normal", "multiply", "screen"]),
                io.Boolean.Input("flip_horizontal", default=False),
                io.String.Input("label", default="", socketless=True),
                # Optional inputs
                io.Mask.Input("mask", optional=True),
                io.Image.Input("overlay", optional=True),
                # Advanced inputs (collapsed by default)
                io.Float.Input("gamma", default=1.0, min=0.1, max=3.0, advanced=True),
            ],
            outputs=[
                io.Image.Output("IMAGE"),
                io.Mask.Output("MASK"),
            ],
        )

    @classmethod
    def execute(cls, image, brightness, contrast, seed, blend_mode,
                flip_horizontal, label, mask=None, overlay=None, gamma=1.0):
        result = image * brightness
        if flip_horizontal:
            result = torch.flip(result, dims=[2])
        if mask is not None:
            result = result * mask.unsqueeze(-1)
        return io.NodeOutput(result, mask if mask is not None else torch.ones(result.shape[:3]))
```

## See Also

- `comfyui-node-basics` - Node structure overview
- `comfyui-node-datatypes` - Data type details
- `comfyui-node-advanced` - MatchType, Autogrow, DynamicCombo
- `comfyui-node-lifecycle` - Lazy evaluation details
