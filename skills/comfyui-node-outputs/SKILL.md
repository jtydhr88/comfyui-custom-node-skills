---
name: comfyui-node-outputs
description: ComfyUI node output types - NodeOutput, UI outputs, PreviewImage, PreviewMask, SavedImages, PreviewAudio, PreviewText, PreviewVideo. Use when returning results from nodes, displaying previews, or saving output files.
---

# ComfyUI Node Outputs

Nodes return data through `io.NodeOutput`. V3 provides built-in UI helpers for previews and file saving.

## Basic Output

```python
class SimpleNode(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SimpleNode",
            display_name="Simple Node",
            category="example",
            inputs=[io.Float.Input("a"), io.Float.Input("b")],
            outputs=[
                io.Float.Output("SUM"),
                io.Float.Output("PRODUCT"),
            ],
        )

    @classmethod
    def execute(cls, a, b):
        # Values must match output order
        return io.NodeOutput(a + b, a * b)
```

## Output Configuration

```python
io.Schema(
    outputs=[
        io.Image.Output("IMAGE"),                    # basic output
        io.Float.Output("VALUE", display_name="Result"),  # custom display name
        io.String.Output("TEXT", tooltip="The processed text"),
        io.Image.Output("FRAMES", is_output_list=True),  # outputs a list
    ],
)
```

## NodeOutput Variants

```python
# Data only
return io.NodeOutput(image_tensor, mask_tensor)

# UI only (output node with no data outputs)
return io.NodeOutput(ui=ui.PreviewImage(images, cls=cls))

# Data + UI
return io.NodeOutput(image_tensor, ui=ui.PreviewImage(images, cls=cls))

# No output
return io.NodeOutput()

# Block execution
return io.NodeOutput(block_execution="Reason for blocking")

# Node expansion (positional args are outputs, not result= keyword)
return io.NodeOutput(output_ref, expand=graph.finalize())
```

## UI Preview Helpers

Import `ui` from `comfy_api.latest`:

```python
from comfy_api.latest import io, ui
```

### PreviewImage

Display image previews on the node. Saves to temp directory automatically.

```python
# Constructor: PreviewImage(image, animated=False, cls=None)
class PreviewNode(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="PreviewNode",
            display_name="Preview Image",
            category="image",
            is_output_node=True,
            inputs=[io.Image.Input("images")],
            outputs=[],
            hidden=[io.Hidden.prompt, io.Hidden.extra_pnginfo],
        )

    @classmethod
    def execute(cls, images):
        return io.NodeOutput(ui=ui.PreviewImage(images, cls=cls))
```

### PreviewMask

```python
# Constructor: PreviewMask(mask, animated=False, cls=None)
# Auto-converts mask to 3-channel grayscale for display
return io.NodeOutput(ui=ui.PreviewMask(masks, cls=cls))
```

### PreviewAudio

```python
# Constructor: PreviewAudio(audio, cls=None)
# Saves as FLAC to temp directory
return io.NodeOutput(ui=ui.PreviewAudio(audio, cls=cls))
```

### PreviewVideo

```python
# Constructor: PreviewVideo(values: list[SavedResult | dict])
return io.NodeOutput(ui=ui.PreviewVideo(saved_video_results))
```

### PreviewText

Display text output:

```python
return io.NodeOutput(ui=ui.PreviewText(value))
```

### PreviewUI3D

Display 3D model preview:

```python
return io.NodeOutput(ui=ui.PreviewUI3D(
    model_file=saved_result,   # SavedResult for the 3D file
    camera_info=camera_dict,   # camera position/target/zoom
    bg_image=image_tensor,     # optional background image (via **kwargs)
))
```

## Saving Images

### Using ImageSaveHelper

The `ui.ImageSaveHelper` class provides static methods for various image formats:

```python
# Save as PNG (returns list[SavedResult])
results = ui.ImageSaveHelper.save_images(
    images,                              # tensor [B,H,W,C]
    filename_prefix="ComfyUI",
    folder_type=io.FolderType.output,    # output, temp, or input
    cls=cls,                             # node class (for metadata)
    compress_level=4,
)

# Save and get UI object directly (saves to output folder)
saved_ui = ui.ImageSaveHelper.get_save_images_ui(images, "ComfyUI", cls=cls)
return io.NodeOutput(ui=saved_ui)

# Save animated PNG
result = ui.ImageSaveHelper.save_animated_png(
    images, "anim", io.FolderType.output, cls=cls, fps=12.0, compress_level=4
)

# Save animated PNG and get UI
saved_ui = ui.ImageSaveHelper.get_save_animated_png_ui(images, "anim", cls=cls, fps=12.0, compress_level=4)

# Save animated WebP
result = ui.ImageSaveHelper.save_animated_webp(
    images, "anim", io.FolderType.output, cls=cls,
    fps=12.0, lossless=False, quality=80, method=4
)

# Save animated WebP and get UI
saved_ui = ui.ImageSaveHelper.get_save_animated_webp_ui(
    images, "anim", cls=cls, fps=12.0, lossless=False, quality=80, method=4
)
```

**Simple save node example:**

```python
class SaveImageNode(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SaveImageNode",
            display_name="Save Image",
            category="image",
            is_output_node=True,
            inputs=[
                io.Image.Input("images"),
                io.String.Input("filename_prefix", default="ComfyUI"),
            ],
            outputs=[],
            hidden=[io.Hidden.prompt, io.Hidden.extra_pnginfo],
        )

    @classmethod
    def execute(cls, images, filename_prefix):
        saved = ui.ImageSaveHelper.get_save_images_ui(images, filename_prefix, cls=cls)
        return io.NodeOutput(ui=saved)
```

### Manual Image Saving

```python
import os
import json
import numpy as np
from PIL import Image as PILImage
from PIL.PngImagePlugin import PngInfo
import folder_paths

class CustomSaveNode(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="CustomSaveNode",
            display_name="Custom Save",
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
        output_dir = folder_paths.get_output_directory()
        results = []

        for i, image in enumerate(images):
            # Convert tensor to PIL
            img_array = np.clip(255.0 * image.cpu().numpy(), 0, 255).astype(np.uint8)
            pil_image = PILImage.fromarray(img_array)

            # Add metadata
            metadata = PngInfo()
            if cls.hidden.prompt:
                metadata.add_text("prompt", json.dumps(cls.hidden.prompt))
            if cls.hidden.extra_pnginfo:
                for k, v in cls.hidden.extra_pnginfo.items():
                    metadata.add_text(k, json.dumps(v))

            # Save with counter
            filename = f"{prefix}_{i:05d}.png"
            filepath = os.path.join(output_dir, filename)
            pil_image.save(filepath, pnginfo=metadata)

            results.append(ui.SavedResult(
                filename=filename,
                subfolder="",
                type=io.FolderType.output,
            ))

        return io.NodeOutput(ui=ui.SavedImages(results))
```

## Saving Audio

The `ui.AudioSaveHelper` supports FLAC, MP3, and Opus formats:

```python
# Save audio (returns list[SavedResult])
results = ui.AudioSaveHelper.save_audio(
    audio,                               # {"waveform": Tensor, "sample_rate": int}
    filename_prefix="audio",
    folder_type=io.FolderType.output,
    cls=cls,
    format="flac",                       # "flac", "mp3", or "opus"
    quality="128k",                      # MP3: "V0","128k","320k"; Opus: "64k"-"320k"
)

# Save and get UI object
saved_ui = ui.AudioSaveHelper.get_save_audio_ui(audio, "audio", cls=cls, format="flac", quality="128k")
return io.NodeOutput(ui=saved_ui)
```

```python
class SaveAudioNode(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SaveAudioNode",
            display_name="Save Audio",
            category="audio",
            is_output_node=True,
            inputs=[
                io.Audio.Input("audio"),
                io.String.Input("prefix", default="audio"),
                io.Combo.Input("format", options=["flac", "mp3", "opus"], default="flac"),
            ],
            outputs=[],
            hidden=[io.Hidden.prompt, io.Hidden.extra_pnginfo],
        )

    @classmethod
    def execute(cls, audio, prefix, format):
        saved = ui.AudioSaveHelper.get_save_audio_ui(audio, prefix, cls=cls, format=format)
        return io.NodeOutput(ui=saved)
```

## Temporary Previews vs Permanent Saves

- **Previews** (PreviewImage, etc.) save to the `temp` directory and are ephemeral
- **Saves** (ImageSaveHelper.save_images) save to the `output` directory permanently
- Use `io.FolderType.temp`, `io.FolderType.output`, or `io.FolderType.input`

## V1 Output Patterns (Legacy Reference)

```python
class V1SaveNode:
    RETURN_TYPES = ()
    OUTPUT_NODE = True
    FUNCTION = "save"

    def save(self, images, prefix):
        # ... save logic ...
        return {
            "ui": {
                "images": [
                    {"filename": "out.png", "subfolder": "", "type": "output"}
                ]
            }
        }

# Data + UI in V1:
class V1PreviewAndOutput:
    RETURN_TYPES = ("IMAGE",)
    OUTPUT_NODE = True
    FUNCTION = "run"

    def run(self, image):
        # ... preview logic ...
        return {
            "ui": {"images": [...]},
            "result": (processed_image,),
        }
```

## See Also

- `comfyui-node-basics` - Node structure and Schema
- `comfyui-node-datatypes` - Data type formats
- `comfyui-node-lifecycle` - Execution flow
