---
name: comfyui-node-basics
description: ComfyUI custom node fundamentals - V3 node structure, Schema, inputs/outputs, registration. Use when creating new ComfyUI custom nodes, defining node classes, or setting up a custom node project.
---

# ComfyUI Custom Node Basics (V3 API)

ComfyUI uses Python classes to define nodes. The **V3 API** is the current recommended approach. Nodes inherit from `io.ComfyNode` and define a schema + execute method.

## Quick Start

```python
from comfy_api.latest import ComfyExtension, io

class MyNode(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="MyNode",
            display_name="My Custom Node",
            category="my_category",
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
```

## V3 Node Class Structure

Every V3 node requires:

1. **Inherit from `io.ComfyNode`**
2. **`define_schema(cls)`** - classmethod returning `io.Schema`
3. **`execute(cls, ...)`** - classmethod performing the computation

```python
from typing_extensions import override
from comfy_api.latest import ComfyExtension, io

class ImageBrighten(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="ImageBrighten",          # unique identifier
            display_name="Brighten Image",     # shown in UI
            category="image/adjust",           # menu path
            description="Adjusts image brightness",
            inputs=[
                io.Image.Input("image"),
                io.Float.Input("factor", default=1.2, min=0.0, max=3.0, step=0.1),
            ],
            outputs=[
                io.Image.Output("IMAGE"),
            ],
        )

    @classmethod
    def execute(cls, image, factor):
        result = torch.clamp(image * factor, 0.0, 1.0)
        return io.NodeOutput(result)
```

## io.Schema Fields

```python
io.Schema(
    node_id="UniqueNodeID",            # required: unique string ID
    display_name="Display Name",        # optional: shown in UI menus
    category="category/subcategory",    # menu hierarchy (default "sd")
    description="Node description",     # optional: tooltip text
    inputs=[...],                       # list of Input objects
    outputs=[...],                      # list of Output objects
    hidden=[...],                       # list of Hidden enum values
    is_output_node=False,               # True for nodes with side effects (save, preview)
    is_experimental=False,              # marks as experimental
    is_deprecated=False,                # marks as deprecated
    is_dev_only=False,                  # hidden unless dev mode enabled
    is_api_node=False,                  # marks as API-only node
    is_input_list=False,                # receive full lists instead of individual items
    not_idempotent=False,               # prevents caching
    accept_all_inputs=False,            # accept arbitrary inputs via **kwargs
    enable_expand=False,                # allow node expansion (subgraphs)
    search_aliases=["alias1", "alias2"],# alternative search terms
    essentials_category="Basic",        # optional: Essentials tab category
    price_badge=None,                   # optional: PriceBadge for API nodes
)
```

## V3 Node Registration

V3 nodes are registered via `ComfyExtension` and `comfy_entrypoint()`:

```python
from typing_extensions import override
from comfy_api.latest import ComfyExtension, io

class MyNode(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="MyNode",
            display_name="My Node",
            category="my_nodes",
            inputs=[io.String.Input("text", multiline=True)],
            outputs=[io.String.Output()],
        )

    @classmethod
    def execute(cls, text):
        return io.NodeOutput(text.upper())


class MyExtension(ComfyExtension):
    @override
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [MyNode]


async def comfy_entrypoint() -> MyExtension:
    return MyExtension()
```

The `comfy_entrypoint()` function must be defined at the module level (in the file directly imported by ComfyUI).

## V1 Node Structure (Legacy Reference)

V1 nodes use class attributes and `NODE_CLASS_MAPPINGS`:

```python
class MyNodeV1:
    CATEGORY = "my_category"
    FUNCTION = "execute"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0}),
            }
        }

    def execute(self, image, strength):
        return (image * strength,)

NODE_CLASS_MAPPINGS = {"MyNodeV1": MyNodeV1}
NODE_DISPLAY_NAME_MAPPINGS = {"MyNodeV1": "My Node V1"}
```

## Key Differences: V3 vs V1

| Aspect | V3 | V1 |
|---|---|---|
| Base class | `io.ComfyNode` | Plain class |
| Execute method | `execute` classmethod (fixed name) | Instance method (custom name via `FUNCTION`) |
| Inputs | `io.Schema(inputs=[...])` | `INPUT_TYPES()` dict |
| Outputs | `io.Schema(outputs=[...])` | `RETURN_TYPES` tuple |
| Return value | `io.NodeOutput(...)` | Plain tuple |
| Registration | `ComfyExtension` + `comfy_entrypoint()` | `NODE_CLASS_MAPPINGS` dict |
| State | No instance state (classmethods) | Instance state allowed |
| Hidden inputs | `cls.hidden.prompt`, etc. | kwargs from `"hidden"` dict |

## Important Rules

- `node_id` must be globally unique across all nodes
- `execute()` parameters must match input IDs exactly
- All methods are `@classmethod` in V3 (no instance state)
- Return `io.NodeOutput(val1, val2, ...)` matching output count
- Category uses `/` separator for hierarchy: `"image/transform"`
- Prefix category with `_` to hide from menus: `"_for_testing"`

## See Also

- `comfyui-node-datatypes` - Data types (IMAGE, LATENT, MASK, etc.)
- `comfyui-node-inputs` - Input configuration details
- `comfyui-node-outputs` - Output types and UI outputs
- `comfyui-node-packaging` - Project structure and packaging
- `comfyui-node-lifecycle` - Execution lifecycle and caching
