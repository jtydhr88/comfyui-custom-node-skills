"""
Covers: comfyui-node-outputs
- Basic output (multiple outputs)
- Output configuration (display_name, tooltip, is_output_list)
- NodeOutput variants (data only, UI only, data+UI, no output, block_execution)
- PreviewImage, PreviewMask, PreviewAudio, PreviewText
- ImageSaveHelper (save_images, get_save_images_ui, save_animated_png, save_animated_webp)
- AudioSaveHelper (save_audio, get_save_audio_ui)
- Manual image saving (SavedResult, SavedImages)
- FolderType (output, temp, input)
"""

import os
import json
import torch
import numpy as np
from PIL import Image as PILImage
from PIL.PngImagePlugin import PngInfo
import folder_paths
from comfy_api.latest import io, ui


# --- outputs: Multiple outputs ---
class SkillTest_MultiOutput(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_MultiOutput",
            display_name="[Test] Multi Output",
            category="skill_tests/outputs",
            inputs=[
                io.Float.Input("a", default=3.0),
                io.Float.Input("b", default=4.0),
            ],
            outputs=[
                io.Float.Output("SUM"),
                io.Float.Output("PRODUCT"),
            ],
        )

    @classmethod
    def execute(cls, a, b):
        return io.NodeOutput(a + b, a * b)


# --- outputs: Output configuration (display_name, tooltip, is_output_list) ---
class SkillTest_OutputConfig(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_OutputConfig",
            display_name="[Test] Output Config",
            category="skill_tests/outputs",
            inputs=[
                io.Image.Input("image"),
            ],
            outputs=[
                io.Image.Output("IMAGE"),
                io.Float.Output("VALUE", display_name="Result"),
                io.String.Output("TEXT", tooltip="The processed text"),
                io.Image.Output("FRAMES", is_output_list=True),
            ],
        )

    @classmethod
    def execute(cls, image):
        return io.NodeOutput(image, 1.0, "processed", [image])


# --- outputs: PreviewImage ---
class SkillTest_PreviewImage(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_PreviewImage",
            display_name="[Test] Preview Image",
            category="skill_tests/outputs",
            is_output_node=True,
            inputs=[io.Image.Input("images")],
            outputs=[],
            hidden=[io.Hidden.prompt, io.Hidden.extra_pnginfo],
        )

    @classmethod
    def execute(cls, images):
        return io.NodeOutput(ui=ui.PreviewImage(images, cls=cls))


# --- outputs: PreviewMask ---
class SkillTest_PreviewMask(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_PreviewMask",
            display_name="[Test] Preview Mask",
            category="skill_tests/outputs",
            is_output_node=True,
            inputs=[io.Mask.Input("masks")],
            outputs=[],
        )

    @classmethod
    def execute(cls, masks):
        return io.NodeOutput(ui=ui.PreviewMask(masks, cls=cls))


# --- outputs: PreviewAudio ---
class SkillTest_PreviewAudio(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_PreviewAudio",
            display_name="[Test] Preview Audio",
            category="skill_tests/outputs",
            is_output_node=True,
            inputs=[io.Audio.Input("audio")],
            outputs=[],
        )

    @classmethod
    def execute(cls, audio):
        return io.NodeOutput(ui=ui.PreviewAudio(audio, cls=cls))


# --- outputs: PreviewText ---
class SkillTest_PreviewText(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_PreviewText",
            display_name="[Test] Preview Text",
            category="skill_tests/outputs",
            is_output_node=True,
            inputs=[io.String.Input("text", multiline=True, default="Hello!")],
            outputs=[],
        )

    @classmethod
    def execute(cls, text):
        return io.NodeOutput(ui=ui.PreviewText(text))


# --- outputs: Data + UI ---
class SkillTest_DataPlusUI(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_DataPlusUI",
            display_name="[Test] Data + UI Output",
            category="skill_tests/outputs",
            is_output_node=True,
            inputs=[io.Image.Input("images")],
            outputs=[io.Image.Output("IMAGE")],
            hidden=[io.Hidden.prompt, io.Hidden.extra_pnginfo],
        )

    @classmethod
    def execute(cls, images):
        return io.NodeOutput(images, ui=ui.PreviewImage(images, cls=cls))


# --- outputs: Block execution ---
class SkillTest_BlockExecution(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_BlockExecution",
            display_name="[Test] Block Execution",
            category="skill_tests/outputs",
            inputs=[
                io.Boolean.Input("allow", default=True),
                io.Image.Input("image"),
            ],
            outputs=[io.Image.Output("IMAGE")],
        )

    @classmethod
    def execute(cls, allow, image):
        if not allow:
            return io.NodeOutput(block_execution="Blocked by user")
        return io.NodeOutput(image)


# --- outputs: ImageSaveHelper ---
class SkillTest_SaveImage(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_SaveImage",
            display_name="[Test] Save Image",
            category="skill_tests/outputs",
            is_output_node=True,
            inputs=[
                io.Image.Input("images"),
                io.String.Input("filename_prefix", default="SkillTest"),
            ],
            outputs=[],
            hidden=[io.Hidden.prompt, io.Hidden.extra_pnginfo],
        )

    @classmethod
    def execute(cls, images, filename_prefix):
        saved = ui.ImageSaveHelper.get_save_images_ui(images, filename_prefix, cls=cls)
        return io.NodeOutput(ui=saved)


# --- outputs: ImageSaveHelper animated PNG ---
class SkillTest_SaveAnimatedPNG(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_SaveAnimatedPNG",
            display_name="[Test] Save Animated PNG",
            category="skill_tests/outputs",
            is_output_node=True,
            inputs=[
                io.Image.Input("images"),
                io.Float.Input("fps", default=12.0, min=1.0, max=60.0),
            ],
            outputs=[],
            hidden=[io.Hidden.prompt, io.Hidden.extra_pnginfo],
        )

    @classmethod
    def execute(cls, images, fps):
        saved = ui.ImageSaveHelper.get_save_animated_png_ui(
            images, "SkillTest_anim", cls=cls, fps=fps, compress_level=4
        )
        return io.NodeOutput(ui=saved)


# --- outputs: ImageSaveHelper animated WebP ---
class SkillTest_SaveAnimatedWebP(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_SaveAnimatedWebP",
            display_name="[Test] Save Animated WebP",
            category="skill_tests/outputs",
            is_output_node=True,
            inputs=[
                io.Image.Input("images"),
                io.Float.Input("fps", default=12.0, min=1.0, max=60.0),
                io.Int.Input("quality", default=80, min=1, max=100),
            ],
            outputs=[],
            hidden=[io.Hidden.prompt, io.Hidden.extra_pnginfo],
        )

    @classmethod
    def execute(cls, images, fps, quality):
        saved = ui.ImageSaveHelper.get_save_animated_webp_ui(
            images, "SkillTest_anim", cls=cls,
            fps=fps, lossless=False, quality=quality, method=4
        )
        return io.NodeOutput(ui=saved)


# --- outputs: AudioSaveHelper ---
class SkillTest_SaveAudio(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_SaveAudio",
            display_name="[Test] Save Audio",
            category="skill_tests/outputs",
            is_output_node=True,
            inputs=[
                io.Audio.Input("audio"),
                io.String.Input("prefix", default="SkillTest_audio"),
                io.Combo.Input("format", options=["flac", "mp3", "opus"], default="flac"),
            ],
            outputs=[],
            hidden=[io.Hidden.prompt, io.Hidden.extra_pnginfo],
        )

    @classmethod
    def execute(cls, audio, prefix, format):
        saved = ui.AudioSaveHelper.get_save_audio_ui(audio, prefix, cls=cls, format=format)
        return io.NodeOutput(ui=saved)


# --- outputs: Manual image saving with SavedResult / SavedImages ---
class SkillTest_ManualSave(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_ManualSave",
            display_name="[Test] Manual Save",
            category="skill_tests/outputs",
            is_output_node=True,
            inputs=[
                io.Image.Input("images"),
                io.String.Input("prefix", default="manual_output"),
            ],
            outputs=[],
            hidden=[io.Hidden.prompt, io.Hidden.extra_pnginfo],
        )

    @classmethod
    def execute(cls, images, prefix):
        output_dir = folder_paths.get_output_directory()
        results = []

        for i, image in enumerate(images):
            img_array = np.clip(255.0 * image.cpu().numpy(), 0, 255).astype(np.uint8)
            pil_image = PILImage.fromarray(img_array)

            metadata = PngInfo()
            if cls.hidden.prompt:
                metadata.add_text("prompt", json.dumps(cls.hidden.prompt))
            if cls.hidden.extra_pnginfo:
                for k, v in cls.hidden.extra_pnginfo.items():
                    metadata.add_text(k, json.dumps(v))

            filename = f"{prefix}_{i:05d}.png"
            filepath = os.path.join(output_dir, filename)
            pil_image.save(filepath, pnginfo=metadata)

            results.append(ui.SavedResult(
                filename=filename,
                subfolder="",
                type=io.FolderType.output,
            ))

        return io.NodeOutput(ui=ui.SavedImages(results))


# --- outputs: No output (empty NodeOutput) ---
class SkillTest_NoOutput(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_NoOutput",
            display_name="[Test] No Output",
            category="skill_tests/outputs",
            is_output_node=True,
            inputs=[io.String.Input("text", default="ping")],
            outputs=[],
        )

    @classmethod
    def execute(cls, text):
        return io.NodeOutput()
