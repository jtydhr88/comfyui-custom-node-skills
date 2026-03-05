"""
Covers: comfyui-node-lifecycle
- fingerprint_inputs (cache control)
- not_idempotent flag
- validate_inputs (return True or error string)
- Skipping type validation (input_types parameter)
- Output nodes (is_output_node)
- List processing (is_input_list, is_output_list)
- Error handling (OOM pattern)
- Server communication (PromptServer.send_sync)
- folder_paths usage (from comfyui-node-packaging)
"""

import time
import random
import torch
import folder_paths
from server import PromptServer
from comfy_api.latest import io, ComfyAPISync


# --- lifecycle: fingerprint_inputs (cache control) ---
class SkillTest_FingerprintNode(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_FingerprintNode",
            display_name="[Test] Fingerprint (Always Re-run)",
            category="skill_tests/lifecycle",
            inputs=[
                io.Float.Input("min_val", default=0.0),
                io.Float.Input("max_val", default=1.0),
            ],
            outputs=[io.Float.Output("FLOAT")],
        )

    @classmethod
    def fingerprint_inputs(cls, min_val, max_val):
        # Return unique value each time -> always re-execute
        return time.time()

    @classmethod
    def execute(cls, min_val, max_val):
        return io.NodeOutput(random.uniform(min_val, max_val))


# --- lifecycle: not_idempotent flag ---
class SkillTest_NotIdempotent(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_NotIdempotent",
            display_name="[Test] Not Idempotent",
            category="skill_tests/lifecycle",
            not_idempotent=True,
            inputs=[io.String.Input("label", default="ping")],
            outputs=[io.String.Output("TEXT")],
        )

    @classmethod
    def execute(cls, label):
        return io.NodeOutput(f"{label} @ {time.time()}")


# --- lifecycle: validate_inputs ---
class SkillTest_ValidateNode(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_ValidateNode",
            display_name="[Test] Validate Inputs",
            category="skill_tests/lifecycle",
            inputs=[
                io.Int.Input("width", default=512, min=1, max=8192),
                io.Int.Input("height", default=512, min=1, max=8192),
            ],
            outputs=[io.Image.Output("IMAGE")],
        )

    @classmethod
    def validate_inputs(cls, width, height):
        if width % 8 != 0 or height % 8 != 0:
            return "Width and height must be multiples of 8"
        if width * height > 4096 * 4096:
            return "Total pixels exceed maximum (4096x4096)"
        return True

    @classmethod
    def execute(cls, width, height):
        return io.NodeOutput(torch.zeros(1, height, width, 3))


# --- lifecycle: Skip type validation (input_types parameter) ---
class SkillTest_SkipTypeValidation(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_SkipTypeValidation",
            display_name="[Test] Skip Type Validation",
            category="skill_tests/lifecycle",
            inputs=[
                io.AnyType.Input("anything"),
            ],
            outputs=[io.String.Output("TEXT")],
        )

    @classmethod
    def validate_inputs(cls, input_types: dict = None, **kwargs):
        # Returning True skips the default type checking
        return True

    @classmethod
    def execute(cls, anything):
        return io.NodeOutput(f"type={type(anything).__name__}")


# --- lifecycle: Output node ---
class SkillTest_OutputNode(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_OutputNode",
            display_name="[Test] Output Node",
            category="skill_tests/lifecycle",
            is_output_node=True,
            inputs=[
                io.String.Input("data", multiline=True),
                io.String.Input("filename", default="output.txt"),
            ],
            outputs=[],
            hidden=[io.Hidden.prompt, io.Hidden.extra_pnginfo],
        )

    @classmethod
    def execute(cls, data, filename):
        import os
        output_dir = folder_paths.get_output_directory()
        with open(os.path.join(output_dir, filename), 'w') as f:
            f.write(data)
        return io.NodeOutput()


# --- lifecycle: List processing (is_input_list + is_output_list) ---
class SkillTest_ListProcessing(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_ListProcessing",
            display_name="[Test] List Processing",
            category="skill_tests/lifecycle",
            is_input_list=True,
            inputs=[
                io.Image.Input("images"),
                io.Int.Input("batch_size", default=1),
            ],
            outputs=[
                io.Image.Output("IMAGE", is_output_list=True),
                io.Int.Output("COUNT"),
            ],
        )

    @classmethod
    def execute(cls, images, batch_size):
        # With is_input_list=True, all inputs arrive as lists
        # Widget values: use [0] to get scalar
        bs = batch_size[0]
        # images is already a list of tensors
        count = len(images)
        return io.NodeOutput(images, count)


# --- lifecycle: Error handling (OOM pattern) ---
class SkillTest_ErrorHandling(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_ErrorHandling",
            display_name="[Test] Error Handling",
            category="skill_tests/lifecycle",
            inputs=[
                io.Image.Input("image"),
                io.Int.Input("scale", default=2, min=1, max=8),
            ],
            outputs=[io.Image.Output("IMAGE")],
        )

    @classmethod
    def execute(cls, image, scale):
        try:
            b, h, w, c = image.shape
            result = image.repeat(1, scale, scale, 1)
        except RuntimeError as e:
            if "out of memory" in str(e):
                torch.cuda.empty_cache()
                # Fallback: just return original
                result = image
            else:
                raise
        return io.NodeOutput(result)


# --- lifecycle: Server communication (PromptServer.send_sync) ---
class SkillTest_ServerComm(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_ServerComm",
            display_name="[Test] Server Communication",
            category="skill_tests/lifecycle",
            is_output_node=True,
            inputs=[
                io.String.Input("message", default="Hello from node!"),
            ],
            outputs=[],
        )

    @classmethod
    def execute(cls, message):
        PromptServer.instance.send_sync(
            "skill_test.status",
            {"message": message, "progress": 100}
        )
        return io.NodeOutput()


# --- lifecycle: folder_paths usage (from packaging skill) ---
class SkillTest_FolderPaths(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_FolderPaths",
            display_name="[Test] folder_paths",
            category="skill_tests/lifecycle",
            inputs=[],
            outputs=[io.String.Output("TEXT")],
        )

    @classmethod
    def execute(cls):
        input_dir = folder_paths.get_input_directory()
        output_dir = folder_paths.get_output_directory()
        temp_dir = folder_paths.get_temp_directory()
        models = folder_paths.get_filename_list("checkpoints")
        return io.NodeOutput(
            f"input={input_dir}\noutput={output_dir}\ntemp={temp_dir}\nmodels_count={len(models)}"
        )


# --- lifecycle: Complete lifecycle example ---
class SkillTest_FullLifecycle(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_FullLifecycle",
            display_name="[Test] Full Lifecycle",
            category="skill_tests/lifecycle",
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
        return threshold

    @classmethod
    def check_lazy_status(cls, image, threshold, optional_ref=None):
        if threshold > 0.8 and optional_ref is None:
            return ["optional_ref"]
        return []

    @classmethod
    def execute(cls, image, threshold, optional_ref=None):
        node_id = cls.hidden.unique_id

        api = ComfyAPISync()
        api.execution.set_progress(0, 2)

        gray = image[:, :, :, 0] * 0.299 + image[:, :, :, 1] * 0.587 + image[:, :, :, 2] * 0.114
        mask = (gray > threshold).float()

        api.execution.set_progress(1, 2)

        result = image * mask.unsqueeze(-1)
        if optional_ref is not None:
            result = result + optional_ref * (1 - mask.unsqueeze(-1))

        api.execution.set_progress(2, 2)
        return io.NodeOutput(result, mask)
