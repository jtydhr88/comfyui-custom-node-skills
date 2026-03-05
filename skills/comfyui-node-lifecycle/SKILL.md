---
name: comfyui-node-lifecycle
description: ComfyUI node execution lifecycle - caching, fingerprint_inputs/IS_CHANGED, validate_inputs/VALIDATE_INPUTS, check_lazy_status, execution order. Use when debugging execution, implementing caching control, input validation, or understanding execution flow.
---

# ComfyUI Node Execution Lifecycle

Understanding the execution lifecycle helps build efficient, correct nodes.

## Execution Flow Overview

```
1. Prompt received from frontend
2. Validation phase
   ├── Look up each node class
   ├── Call INPUT_TYPES() / define_schema() for input specs
   ├── Validate connections and types
   └── Call validate_inputs() for each node
3. Build execution order (topological sort from output nodes)
4. For each node in order:
   ├── Cache check (fingerprint_inputs)
   ├── Input resolution (get upstream values)
   ├── Lazy evaluation (check_lazy_status)
   ├── Execute function
   └── Store outputs in cache
5. Return results to frontend
```

## Execution Order

ComfyUI executes from **output nodes backward**:
1. Identifies output nodes (`is_output_node=True`)
2. Builds dependency graph
3. Topological sort determines execution order
4. Only nodes connected to output nodes execute

## Cache Control: fingerprint_inputs (V3) / IS_CHANGED (V1)

Controls when a node re-executes vs uses cached results.

```python
class RandomNode(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="RandomNode",
            display_name="Random Value",
            category="utils",
            inputs=[
                io.Float.Input("min_val", default=0.0),
                io.Float.Input("max_val", default=1.0),
            ],
            outputs=[io.Float.Output("FLOAT")],
        )

    @classmethod
    def fingerprint_inputs(cls, min_val, max_val):
        """Return value compared to last run. Different value = re-execute."""
        # Return unique value each time to always re-execute
        import time
        return time.time()

    @classmethod
    def execute(cls, min_val, max_val):
        import random
        return io.NodeOutput(random.uniform(min_val, max_val))
```

**How caching works**:
- Before execution, `fingerprint_inputs()` is called with the same args as `execute()`
- Return value is compared to the previous run's return value
- If **same** → skip execution, use cached output
- If **different** → re-execute the node
- If `fingerprint_inputs` is not defined → cache based on input values

**V1 equivalent** (`IS_CHANGED`):
```python
@classmethod
def IS_CHANGED(s, min_val, max_val):
    return time.time()  # always re-execute
```

### not_idempotent Flag

For nodes that should never be cached:

```python
io.Schema(
    node_id="AlwaysRunNode",
    not_idempotent=True,  # prevents all caching
    # ...
)
```

## Input Validation: validate_inputs (V3) / VALIDATE_INPUTS (V1)

Validates inputs before execution. Runs during the validation phase.

```python
class ValidatedNode(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="ValidatedNode",
            display_name="Validated Node",
            category="utils",
            inputs=[
                io.Int.Input("width", default=512, min=1, max=8192),
                io.Int.Input("height", default=512, min=1, max=8192),
            ],
            outputs=[io.Image.Output("IMAGE")],
        )

    @classmethod
    def validate_inputs(cls, width, height):
        """Return True if valid, or error string if invalid."""
        if width % 8 != 0 or height % 8 != 0:
            return "Width and height must be multiples of 8"
        if width * height > 4096 * 4096:
            return "Total pixels exceed maximum (4096x4096)"
        return True

    @classmethod
    def execute(cls, width, height):
        import torch
        return io.NodeOutput(torch.zeros(1, height, width, 3))
```

**V1 equivalent**:
```python
@classmethod
def VALIDATE_INPUTS(s, width, height):
    if width % 8 != 0:
        return "Width must be a multiple of 8"
    return True
```

### Skipping Type Validation

To accept any type (wildcard inputs), include `input_types` parameter:

```python
@classmethod
def validate_inputs(cls, input_types: dict = None, **kwargs):
    # input_types contains the actual types of connected inputs
    # Returning True skips the default type checking
    return True
```

## Lazy Evaluation: check_lazy_status

Controls which lazy inputs actually need evaluation. See `comfyui-node-inputs` for full details.

```python
@classmethod
def check_lazy_status(cls, condition, value_a=None, value_b=None):
    """Called before execute. Return names of inputs that need evaluation."""
    if condition and value_a is None:
        return ["value_a"]
    if not condition and value_b is None:
        return ["value_b"]
    return []
```

**Key behaviors**:
- Only called if the node has lazy inputs
- May be called **multiple times** as inputs become available
- Unevaluated lazy inputs are `None`
- Return empty list (or `None`) when ready to execute
- Evaluated inputs retain their value across calls

## Output Nodes

Nodes with `is_output_node=True` are execution roots — ComfyUI traces backward from these:

```python
class SaveMyData(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SaveMyData",
            display_name="Save Data",
            category="output",
            is_output_node=True,  # marks as output node
            inputs=[
                io.String.Input("data"),
                io.String.Input("filename", default="output.txt"),
            ],
            outputs=[],  # output nodes may have no outputs
            hidden=[io.Hidden.prompt, io.Hidden.extra_pnginfo],
        )

    @classmethod
    def execute(cls, data, filename):
        import folder_paths, os
        output_dir = folder_paths.get_output_directory()
        with open(os.path.join(output_dir, filename), 'w') as f:
            f.write(data)
        return io.NodeOutput()
```

## List Processing

### Receiving Lists

```python
# V3: is_input_list=True in Schema (same as V1 INPUT_IS_LIST)
# All inputs arrive as lists — including widget values like batch_size
# Widget values: use widget_value[0] to get the scalar
# Shorter lists are padded by repeating the last value

# V1: INPUT_IS_LIST = True to receive full lists
class ListNode:
    INPUT_IS_LIST = True
    # Now execute() receives lists instead of individual items
```

### Outputting Lists

```python
# V3
io.Image.Output("IMAGE", is_output_list=True)

# V1
OUTPUT_IS_LIST = (True,)  # tuple matching RETURN_TYPES
```

## Error Handling

```python
@classmethod
def execute(cls, image, model):
    try:
        result = model.process(image)
    except RuntimeError as e:
        if "out of memory" in str(e):
            import torch
            torch.cuda.empty_cache()
            # Try with smaller batch
            result = process_in_chunks(image, model)
        else:
            raise
    return io.NodeOutput(result)
```

## Server Communication

Send messages to the frontend during execution:

```python
from server import PromptServer

@classmethod
def execute(cls, data):
    PromptServer.instance.send_sync(
        "my_extension.status",
        {"message": "Processing complete", "progress": 100}
    )
    return io.NodeOutput(data)
```

## Complete Lifecycle Example

```python
import time
import torch
from comfy_api.latest import ComfyExtension, io, ComfyAPISync

class FullLifecycleNode(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="FullLifecycleNode",
            display_name="Full Lifecycle Demo",
            category="example",
            inputs=[
                io.Image.Input("image"),
                io.Float.Input("threshold", default=0.5, min=0.0, max=1.0),
                io.Image.Input("optional_ref", optional=True, lazy=True),
            ],
            outputs=[
                io.Image.Output("IMAGE"),
                io.Mask.Output("MASK"),
            ],
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    def validate_inputs(cls, image, threshold, optional_ref=None):
        if threshold == 0.0:
            return "Threshold cannot be exactly 0"
        return True

    @classmethod
    def fingerprint_inputs(cls, image, threshold, optional_ref=None):
        # Re-execute if threshold changed; cache otherwise
        return threshold

    @classmethod
    def check_lazy_status(cls, image, threshold, optional_ref=None):
        # Only request optional_ref if threshold is high
        if threshold > 0.8 and optional_ref is None:
            return ["optional_ref"]
        return []

    @classmethod
    def execute(cls, image, threshold, optional_ref=None):
        node_id = cls.hidden.unique_id

        api = ComfyAPISync()  # use ComfyAPISync in sync execute; ComfyAPI in async
        api.execution.set_progress(0, 2)

        # Generate mask from threshold
        gray = image[:, :, :, 0] * 0.299 + image[:, :, :, 1] * 0.587 + image[:, :, :, 2] * 0.114
        mask = (gray > threshold).float()

        api.execution.set_progress(1, 2)

        # Apply mask
        result = image * mask.unsqueeze(-1)
        if optional_ref is not None:
            result = result + optional_ref * (1 - mask.unsqueeze(-1))

        api.execution.set_progress(2, 2)
        return io.NodeOutput(result, mask)
```

## See Also

- `comfyui-node-basics` - Node structure fundamentals
- `comfyui-node-inputs` - Input types and lazy evaluation
- `comfyui-node-advanced` - Expansion, MatchType, DynamicCombo
- `comfyui-node-outputs` - UI outputs and previews
