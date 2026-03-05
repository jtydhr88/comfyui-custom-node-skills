---
name: comfyui-node-packaging
description: ComfyUI custom node project structure - directory layout, __init__.py, registration, requirements.txt, publishing, WEB_DIRECTORY. Use when setting up a new custom node project, packaging nodes, or publishing to the registry.
---

# ComfyUI Custom Node Packaging

How to structure, register, and publish a custom node package.

## Project Structure

```
ComfyUI/custom_nodes/
  my_custom_nodes/
    __init__.py            # Entry point (required)
    nodes.py               # Node class definitions
    requirements.txt       # Python dependencies
    pyproject.toml         # Package metadata
    README.md              # Documentation
    js/                    # Frontend extensions (optional)
    │   └── my_extension.js
    docs/                  # Help pages (optional)
    │   └── MyNode.md
    locales/               # i18n translations (optional)
        └── zh/
            └── main.json
```

## Entry Point: __init__.py

### V3 Registration (Recommended)

```python
# __init__.py
from typing_extensions import override
from comfy_api.latest import ComfyExtension, io

from .nodes import MyNode1, MyNode2, MyNode3

WEB_DIRECTORY = "./js"  # optional: frontend JS extensions

class MyNodesExtension(ComfyExtension):
    @override
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [MyNode1, MyNode2, MyNode3]

    @override
    async def on_load(self):
        # Optional: run initialization logic when extension loads
        pass

async def comfy_entrypoint() -> MyNodesExtension:
    return MyNodesExtension()
```

### V1 Registration (Legacy)

```python
# __init__.py
from .nodes import MyNode1, MyNode2

NODE_CLASS_MAPPINGS = {
    "MyNode1": MyNode1,
    "MyNode2": MyNode2,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MyNode1": "My Node 1",
    "MyNode2": "My Node 2",
}

WEB_DIRECTORY = "./js"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
```

## Node Definitions File

```python
# nodes.py
import torch
from comfy_api.latest import io

class MyNode1(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="MyNode1_UniqueID",   # globally unique
            display_name="My Node 1",
            category="my_nodes",
            description="Does something useful",
            inputs=[
                io.Image.Input("image"),
                io.Float.Input("value", default=1.0, min=0.0, max=10.0),
            ],
            outputs=[io.Image.Output("IMAGE")],
        )

    @classmethod
    def execute(cls, image, value):
        return io.NodeOutput(image * value)
```

## Dependencies: requirements.txt

```
# requirements.txt
opencv-python>=4.8.0
requests>=2.28.0
```

**Important**: Only list dependencies not already included with ComfyUI. ComfyUI ships with: `torch`, `torchvision`, `torchaudio`, `numpy`, `PIL/Pillow`, `scipy`, `safetensors`, `transformers`, `accelerate`.

## pyproject.toml

```toml
[project]
name = "comfyui-my-nodes"
version = "1.0.0"
description = "My custom nodes for ComfyUI"
license = "MIT"
requires-python = ">=3.10"

[project.urls]
Repository = "https://github.com/username/comfyui-my-nodes"
```

## Frontend Extensions (JavaScript)

Place `.js` files in the `WEB_DIRECTORY`:

```
my_custom_nodes/
  js/
    my_widgets.js      # Custom widget implementations
    my_extension.js    # Extension hooks
```

```python
# __init__.py
WEB_DIRECTORY = "./js"
```

All `.js` files in this directory are loaded by the frontend automatically. CSS and other resources can be accessed at `extensions/my_custom_nodes/filename.css`.

## Help Pages

Create markdown documentation per node:

```
my_custom_nodes/
  docs/
    MyNode1.md         # filename matches node_id
```

```markdown
<!-- docs/MyNode1.md -->
# My Node 1

Processes images with adjustable value.

## Inputs
- **image**: The input image
- **value**: Processing strength (0.0 - 10.0)

## Outputs
- **IMAGE**: The processed image
```

## Internationalization (i18n)

```
my_custom_nodes/
  locales/
    zh/
      main.json
      nodeDefs.json    # node definition translations
```

```json
// locales/zh/nodeDefs.json
{
    "MyNode1_UniqueID": {
        "display_name": "我的节点1",
        "description": "处理图像",
        "inputs": {
            "image": { "display_name": "图像" },
            "value": { "display_name": "数值", "tooltip": "处理强度" }
        }
    }
}
```

## Single-File Node

For very simple nodes, everything can be in one file:

```python
# ComfyUI/custom_nodes/my_simple_node.py
import torch
from comfy_api.latest import ComfyExtension, io
from typing_extensions import override

class InvertImage(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SimpleInvert",
            display_name="Simple Invert",
            category="image",
            inputs=[io.Image.Input("image")],
            outputs=[io.Image.Output("IMAGE")],
        )

    @classmethod
    def execute(cls, image):
        return io.NodeOutput(1.0 - image)


class SimpleExtension(ComfyExtension):
    @override
    async def get_node_list(self):
        return [InvertImage]

async def comfy_entrypoint():
    return SimpleExtension()
```

## Key Imports

```python
# V3 API core
from comfy_api.latest import ComfyExtension, io, ui
from comfy_api.latest import ComfyAPI          # async runtime API (use with await)
from comfy_api.latest import ComfyAPISync      # sync runtime API (use in sync execute)
from comfy_api.latest import Input             # Input.Image, Input.Audio, Input.Mask, Input.Latent, Input.Video
from comfy_api.latest import InputImpl         # InputImpl.VideoFromFile, InputImpl.VideoFromComponents
from comfy_api.latest import Types             # Types.MESH, Types.VOXEL, Types.File3D, Types.VideoCodec
from typing_extensions import override

# Common utilities
import folder_paths                            # directory management
from server import PromptServer                # server-to-client messaging
from comfy_execution.graph_utils import GraphBuilder  # node expansion
```

## Using folder_paths

ComfyUI provides `folder_paths` for accessing standard directories:

```python
import folder_paths

# Standard directories
input_dir = folder_paths.get_input_directory()
output_dir = folder_paths.get_output_directory()
temp_dir = folder_paths.get_temp_directory()

# Model directories
checkpoint_paths = folder_paths.get_folder_paths("checkpoints")
lora_paths = folder_paths.get_folder_paths("loras")

# Register custom model folder
folder_paths.add_model_folder_path("my_models", "/path/to/models")

# Get model file list
models = folder_paths.get_filename_list("checkpoints")
```

## Publishing to ComfyUI Registry

### 1. Create `pyproject.toml`

```toml
[project]
name = "comfyui-my-nodes"
version = "1.0.0"
description = "My custom nodes"
license = "MIT"

[tool.comfy]
PublisherId = "your-publisher-id"
```

### 2. Publish

```bash
comfy node publish
```

### CI/CD with GitHub Actions

```yaml
# .github/workflows/publish.yml
name: Publish to ComfyUI Registry
on:
  push:
    tags:
      - 'v*'
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install comfy-cli
      - run: comfy node publish
        env:
          COMFY_API_KEY: ${{ secrets.COMFY_API_KEY }}
```

## Scaffolding with comfy-cli

```bash
# Install comfy-cli
pip install comfy-cli

# Create new custom node project
cd ComfyUI/custom_nodes
comfy node scaffold
```

This generates the boilerplate structure with all necessary files.

## Node ID Best Practices

- Use a **globally unique** prefix: `"MyProject_NodeName"` or `"username.NodeName"`
- Never change `node_id` after release (breaks saved workflows)
- Use `display_name` for user-facing name changes
- Use `search_aliases` for discoverability: `search_aliases=["alias1", "alias2"]`

## Common Patterns

### Organizing Multiple Node Files

```python
# __init__.py
from typing_extensions import override
from comfy_api.latest import ComfyExtension, io

from .image_nodes import BlurNode, SharpenNode, ResizeNode
from .text_nodes import ConcatNode, FormatNode
from .util_nodes import SwitchNode, DebugNode

class MyExtension(ComfyExtension):
    @override
    async def get_node_list(self):
        return [
            BlurNode, SharpenNode, ResizeNode,
            ConcatNode, FormatNode,
            SwitchNode, DebugNode,
        ]

async def comfy_entrypoint():
    return MyExtension()
```

### Conditional Node Loading

```python
class MyExtension(ComfyExtension):
    @override
    async def get_node_list(self):
        nodes = [BasicNode]
        try:
            import cv2
            from .opencv_nodes import OpenCVNode
            nodes.append(OpenCVNode)
        except ImportError:
            pass
        return nodes
```

## See Also

- `comfyui-node-basics` - Node class structure
- `comfyui-node-frontend` - JavaScript extension details
- `comfyui-node-migration` - V1 to V3 migration
