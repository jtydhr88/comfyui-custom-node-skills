---
name: comfyui-node-advanced
description: ComfyUI advanced node patterns - MatchType, Autogrow, DynamicCombo, DynamicSlot, node expansion, MultiType, wildcard inputs. Use when building complex nodes with dynamic inputs, type matching, or node expansion.
---

# ComfyUI Advanced Node Patterns (V3)

V3 provides advanced input patterns for dynamic, type-safe, and flexible node designs.

## MatchType - Generic Type Connections

`MatchType` ensures that inputs and outputs sharing a template have the same type at connection time. Like generics in typed languages.

```python
class PassThrough(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        # Template(template_id, allowed_types=AnyType) - optional type constraint
        template = io.MatchType.Template("T")
        return io.Schema(
            node_id="PassThrough",
            display_name="Pass Through",
            category="utils",
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
```

When the user connects an IMAGE to the input, the output automatically becomes IMAGE type.

### Switch Node Pattern

```python
class Switch(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        template = io.MatchType.Template("switch")
        return io.Schema(
            node_id="Switch",
            display_name="Switch",
            category="logic",
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
```

## MultiType - Accept Multiple Types

A single input that accepts several different types:

```python
io.MultiType.Input("data",
    types=[io.Image, io.Mask, io.Latent],
    optional=True,
)
```

## Autogrow - Dynamic Growing Inputs

Inputs that automatically add more slots as the user connects to them. Two template modes:

### TemplatePrefix (numbered slots)

```python
class ConcatImages(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="ConcatImages",
            display_name="Concat Images",
            category="image",
            inputs=[
                io.Autogrow.Input("images",
                    template=io.Autogrow.TemplatePrefix(
                        input=io.Image.Input("img"),  # template for each slot
                        prefix="image_",              # slot names: image_0, image_1, ...
                        min=2,                        # minimum visible slots (default 1)
                        max=16,                       # maximum slots (default 10, hard limit 100)
                    ),
                ),
            ],
            outputs=[io.Image.Output("IMAGE")],
        )

    @classmethod
    def execute(cls, images: io.Autogrow.Type):
        # images is a dict: {"image_0": tensor, "image_1": tensor, ...}
        tensors = [v for v in images.values() if v is not None]
        return io.NodeOutput(torch.cat(tensors, dim=0))
```

### TemplateNames (named slots)

```python
io.Autogrow.Input("inputs",
    template=io.Autogrow.TemplateNames(
        input=io.Float.Input("val"),
        names=["red", "green", "blue", "alpha"],  # specific slot names
        min=3,  # first 3 are required
    ),
)
# Creates slots: "red" (required), "green" (required), "blue" (required), "alpha" (optional)
```

**Key behaviors**:
- Widget inputs in template are forced to connection-only (`force_input=True`)
- Slots below `min` are required; above `min` are optional
- Maximum 100 names total

## DynamicCombo - Conditional Inputs

A combo dropdown where each option reveals different sub-inputs:

```python
class ProcessNode(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="ProcessNode",
            display_name="Process Node",
            category="processing",
            is_output_node=True,
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
        # mode is a dict with the combo value + sub-inputs
        # key for selected option matches the DynamicCombo input ID
        if mode["mode"] == "resize":
            width = mode["width"]
            height = mode["height"]
            # ... resize logic
        return io.NodeOutput(image)
```

**Nested DynamicCombo**:
```python
io.DynamicCombo.Input("outer", options=[
    io.DynamicCombo.Option("option1", [
        io.DynamicCombo.Input("inner", options=[
            io.DynamicCombo.Option("sub1", [io.Float.Input("val")]),
            io.DynamicCombo.Option("sub2", [io.Int.Input("count")]),
        ])
    ]),
])
```

## DynamicSlot - Connection-Triggered Inputs

An input slot that reveals additional inputs when connected:

```python
io.DynamicSlot.Input(
    slot=io.Image.Input("trigger_image"),  # the trigger slot
    inputs=[                               # revealed when connected
        io.Float.Input("opacity", default=1.0),
        io.Combo.Input("blend", options=["normal", "multiply"]),
    ],
    lazy=True,  # optional: lazy evaluate trigger input
)
```

When the user connects to `trigger_image`, the `opacity` and `blend` inputs appear. The trigger slot is always optional (hardcoded).

## Node Expansion - Subgraph Injection

Nodes can return a subgraph that replaces themselves during execution:

```python
from comfy_execution.graph_utils import GraphBuilder

class RepeatNode(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="RepeatNode",
            display_name="Repeat KSampler",
            category="sampling",
            enable_expand=True,
            inputs=[
                io.Model.Input("model"),
                io.Int.Input("repeat_count", default=2, min=1, max=10),
                io.Latent.Input("latent"),
            ],
            outputs=[io.Latent.Output("LATENT")],
        )

    @classmethod
    def execute(cls, model, repeat_count, latent):
        graph = GraphBuilder()
        current_latent = latent
        for i in range(repeat_count):
            sampler = graph.node("KSampler",
                model=model,
                latent_image=current_latent,
                # ... other params
            )
            current_latent = sampler.out(0)
        return io.NodeOutput(current_latent, expand=graph.finalize())
```

**Key rules for node expansion**:
- Set `enable_expand=True` in Schema
- Use `GraphBuilder` to construct subgraphs safely
- Return `io.NodeOutput(output_ref, expand=graph.finalize())`
- Node IDs in subgraph must be deterministic and unique
- Each subnode is cached separately

## Accept All Inputs

Accept arbitrary inputs not defined in the schema:

```python
class FlexibleNode(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="FlexibleNode",
            display_name="Flexible Node",
            category="utils",
            accept_all_inputs=True,
            inputs=[io.Combo.Input("mode", options=["a", "b"])],
            outputs=[io.String.Output()],
        )

    @classmethod
    def validate_inputs(cls, mode, **kwargs):
        return True  # skip validation for dynamic inputs

    @classmethod
    def execute(cls, mode, **kwargs):
        # kwargs contains all dynamic inputs
        return io.NodeOutput(str(kwargs))
```

## Execution Blocking

Prevent downstream execution conditionally:

```python
class GateNode(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="GateNode",
            display_name="Gate",
            category="logic",
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
```

## Async Execute

V3 natively supports async execution:

```python
class AsyncNode(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="AsyncNode",
            display_name="Async Node",
            category="utils",
            inputs=[io.String.Input("url")],
            outputs=[io.String.Output()],
        )

    @classmethod
    async def execute(cls, url):
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                text = await response.text()
        return io.NodeOutput(text)
```

## Progress Reporting

Report progress during long operations:

```python
from comfy_api.latest import ComfyAPISync  # sync version; use ComfyAPI + await for async execute

class SlowNode(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SlowNode",
            display_name="Slow Node",
            category="utils",
            inputs=[io.Int.Input("steps", default=100)],
            outputs=[io.String.Output()],
        )

    @classmethod
    def execute(cls, steps):
        api = ComfyAPISync()
        for i in range(steps):
            # ... do work ...
            api.execution.set_progress(i + 1, steps)
        return io.NodeOutput("done")
```

## NodeReplace - Migration Between Nodes

Register replacements so old workflows auto-migrate to new nodes:

```python
from typing_extensions import override
from comfy_api.latest import ComfyAPI, ComfyExtension, io

class MyExtension(ComfyExtension):
    @override
    async def on_load(self):
        api = ComfyAPI()
        await api.node_replacement.register(io.NodeReplace(
            new_node_id="MyNewNode_v2",
            old_node_id="MyOldNode",
            old_widget_ids=["width", "height", "mode"],  # positional widget order
            input_mapping=[
                {"new_id": "image_in", "old_id": "image"},     # rename input
                {"new_id": "size", "set_value": 512},           # set fixed value
            ],
            output_mapping=[
                {"new_idx": 0, "old_idx": 0},       # index-based, not name-based
            ],
        ))

    @override
    async def get_node_list(self):
        return [MyNewNodeV2]
```

**InputMap types**:
- `InputMapOldId`: `{"new_id": str, "old_id": str}` — map old input to new
- `InputMapSetValue`: `{"new_id": str, "set_value": Any}` — set fixed value on new
- Dot notation for autogrow inputs: `{"new_id": "images.image0", "old_id": "image1"}`

**OutputMap** (index-based, not name-based):
- `{"new_idx": int, "old_idx": int}` — map old output index to new

**old_widget_ids**: Required because workflow JSON stores widget values by position, not by ID. This list maps positional indexes to input IDs for correct migration.

## ComfyAPI - Runtime API

```python
from comfy_api.latest import ComfyAPI, ComfyAPISync

# In sync execute(): use ComfyAPISync (no await)
api = ComfyAPISync()
api.execution.set_progress(value=50, max_value=100)
api.execution.set_progress(
    value=50, max_value=100,
    node_id=None,                   # optional: defaults to current node
    preview_image=pil_image,        # PIL Image or ImageInput tensor
    ignore_size_limit=False,
)

# In async execute(): use ComfyAPI (with await)
api = ComfyAPI()
await api.execution.set_progress(value=50, max_value=100)

# Node replacement registration (in async on_load)
await api.node_replacement.register(io.NodeReplace(...))
```

## See Also

- `comfyui-node-basics` - Node fundamentals
- `comfyui-node-inputs` - Basic input types
- `comfyui-node-lifecycle` - Execution lifecycle and caching
- `comfyui-node-outputs` - Output types and UI helpers
