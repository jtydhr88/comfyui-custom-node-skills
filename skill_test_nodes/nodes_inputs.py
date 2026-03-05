"""
Covers: comfyui-node-inputs
- INT (default, min, max, step, control_after_generate, display_mode, tooltip)
- FLOAT (default, min, max, step, round, display_mode, gradient_stops)
- STRING (single-line, multi-line, placeholder, dynamic_prompts)
- BOOLEAN (default, label_on, label_off, tooltip)
- COMBO (options, default, tooltip, control_after_generate)
- COMBO with Enum
- COMBO with file upload (UploadType, FolderType)
- COMBO with remote options (RemoteOptions)
- MULTICOMBO (options, default, placeholder, chip)
- COLOR (default, socketless)
- BOUNDING_BOX (default, socketless, component)
- CURVE (default, socketless)
- WEBCAM
- IMAGECOMPARE (socketless)
- Input options: optional, tooltip, lazy, advanced, raw_link
- force_input, socketless
- Optional inputs
- Hidden inputs (all 6)
- Lazy evaluation (check_lazy_status)
"""

import torch
from enum import Enum
from comfy_api.latest import io


# --- inputs: INT with all options ---
class SkillTest_IntInputs(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_IntInputs",
            display_name="[Test] INT Inputs",
            category="skill_tests/inputs",
            inputs=[
                io.Int.Input("seed",
                    default=0,
                    min=0,
                    max=0xffffffffffffffff,
                    step=1,
                    control_after_generate=True,
                    display_mode=io.NumberDisplay.number,
                    tooltip="Random seed for generation",
                ),
                io.Int.Input("slider_int",
                    default=50,
                    min=0,
                    max=100,
                    step=1,
                    display_mode=io.NumberDisplay.slider,
                ),
                io.Int.Input("fixed_control",
                    default=0,
                    min=0,
                    max=100,
                    control_after_generate=io.ControlAfterGenerate.fixed,
                ),
                io.Int.Input("increment_control",
                    default=0,
                    min=0,
                    max=100,
                    control_after_generate=io.ControlAfterGenerate.increment,
                ),
                io.Int.Input("decrement_control",
                    default=100,
                    min=0,
                    max=100,
                    control_after_generate=io.ControlAfterGenerate.decrement,
                ),
                io.Int.Input("randomize_control",
                    default=0,
                    min=0,
                    max=100,
                    control_after_generate=io.ControlAfterGenerate.randomize,
                ),
            ],
            outputs=[io.String.Output("TEXT")],
        )

    @classmethod
    def execute(cls, seed, slider_int, fixed_control, increment_control,
                decrement_control, randomize_control):
        result = f"seed={seed}, slider={slider_int}, fixed={fixed_control}, inc={increment_control}, dec={decrement_control}, rand={randomize_control}"
        return io.NodeOutput(result)


# --- inputs: FLOAT with all options ---
class SkillTest_FloatInputs(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_FloatInputs",
            display_name="[Test] FLOAT Inputs",
            category="skill_tests/inputs",
            inputs=[
                io.Float.Input("number_float",
                    default=1.0,
                    min=0.0,
                    max=10.0,
                    step=0.01,
                    round=0.001,
                    display_mode=io.NumberDisplay.number,
                    tooltip="A plain number float",
                ),
                io.Float.Input("slider_float",
                    default=5.0,
                    min=0.0,
                    max=10.0,
                    step=0.1,
                    display_mode=io.NumberDisplay.slider,
                ),
                io.Float.Input("gradient_float",
                    default=0.5,
                    min=0.0,
                    max=1.0,
                    step=0.01,
                    display_mode=io.NumberDisplay.gradient_slider,
                    gradient_stops=[
                        {"offset": 0.0, "color": [0, 0, 0]},
                        {"offset": 1.0, "color": [255, 255, 255]},
                    ],
                ),
            ],
            outputs=[io.String.Output("TEXT")],
        )

    @classmethod
    def execute(cls, number_float, slider_float, gradient_float):
        return io.NodeOutput(f"num={number_float}, slider={slider_float}, gradient={gradient_float}")


# --- inputs: STRING (single-line and multi-line) ---
class SkillTest_StringInputs(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_StringInputs",
            display_name="[Test] STRING Inputs",
            category="skill_tests/inputs",
            inputs=[
                io.String.Input("name",
                    default="",
                    placeholder="Enter name...",
                ),
                io.String.Input("prompt",
                    multiline=True,
                    default="",
                    placeholder="Enter prompt...",
                    dynamic_prompts=True,
                ),
            ],
            outputs=[io.String.Output("TEXT")],
        )

    @classmethod
    def execute(cls, name, prompt):
        return io.NodeOutput(f"name={name}, prompt={prompt}")


# --- inputs: BOOLEAN ---
class SkillTest_BooleanInput(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_BooleanInput",
            display_name="[Test] BOOLEAN Input",
            category="skill_tests/inputs",
            inputs=[
                io.Boolean.Input("enabled",
                    default=True,
                    label_on="Enabled",
                    label_off="Disabled",
                    tooltip="Toggle this feature",
                ),
            ],
            outputs=[io.String.Output("TEXT")],
        )

    @classmethod
    def execute(cls, enabled):
        return io.NodeOutput(f"enabled={enabled}")


# --- inputs: COMBO (basic, enum, upload, remote) ---
class BlendMode(Enum):
    NORMAL = "normal"
    MULTIPLY = "multiply"
    SCREEN = "screen"


class SkillTest_ComboInputs(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_ComboInputs",
            display_name="[Test] COMBO Inputs",
            category="skill_tests/inputs",
            inputs=[
                # Basic combo
                io.Combo.Input("mode",
                    options=["option_a", "option_b", "option_c"],
                    default="option_a",
                    tooltip="Select processing mode",
                    control_after_generate=True,
                ),
                # Combo with Enum
                io.Combo.Input("blend",
                    options=BlendMode,
                    default=BlendMode.NORMAL,
                ),
                # Combo with file upload
                io.Combo.Input("image_file",
                    options=[],
                    upload=io.UploadType.image,
                    image_folder=io.FolderType.input,
                ),
                # Dynamic combo with remote options
                io.Combo.Input("model_name",
                    options=[],
                    remote=io.RemoteOptions(
                        route="/internal/models/checkpoints",
                        refresh_button=True,
                        control_after_refresh="first",
                        timeout=5000,
                        max_retries=3,
                        refresh=60000,
                    ),
                ),
            ],
            outputs=[io.String.Output("TEXT")],
        )

    @classmethod
    def execute(cls, mode, blend, image_file, model_name):
        return io.NodeOutput(f"mode={mode}, blend={blend}, file={image_file}, model={model_name}")


# --- inputs: MULTICOMBO ---
class SkillTest_MultiComboInput(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_MultiComboInput",
            display_name="[Test] MULTICOMBO Input",
            category="skill_tests/inputs",
            inputs=[
                io.MultiCombo.Input("tags",
                    options=["tag1", "tag2", "tag3", "tag4"],
                    default=["tag1"],
                    placeholder="Select tags...",
                    chip=True,
                ),
            ],
            outputs=[io.String.Output("TEXT")],
        )

    @classmethod
    def execute(cls, tags):
        return io.NodeOutput(f"tags={tags}")


# --- inputs: COLOR ---
class SkillTest_ColorInput(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_ColorInput",
            display_name="[Test] COLOR Input",
            category="skill_tests/inputs",
            inputs=[
                io.Color.Input("color",
                    default="#ffffff",
                    socketless=True,
                ),
            ],
            outputs=[io.String.Output("TEXT")],
        )

    @classmethod
    def execute(cls, color):
        return io.NodeOutput(f"color={color}")


# --- inputs: BOUNDING_BOX ---
class SkillTest_BoundingBoxInput(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_BoundingBoxInput",
            display_name="[Test] BOUNDING_BOX Input",
            category="skill_tests/inputs",
            inputs=[
                io.BoundingBox.Input("region",
                    default={"x": 0, "y": 0, "width": 512, "height": 512},
                    socketless=True,
                ),
            ],
            outputs=[io.String.Output("TEXT")],
        )

    @classmethod
    def execute(cls, region):
        return io.NodeOutput(f"region={region}")


# --- inputs: CURVE ---
class SkillTest_CurveInput(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_CurveInput",
            display_name="[Test] CURVE Input",
            category="skill_tests/inputs",
            inputs=[
                io.Curve.Input("curve",
                    default=[(0.0, 0.0), (1.0, 1.0)],
                    socketless=True,
                ),
            ],
            outputs=[io.String.Output("TEXT")],
        )

    @classmethod
    def execute(cls, curve):
        return io.NodeOutput(f"curve={curve}")


# --- inputs: WEBCAM ---
class SkillTest_WebcamInput(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_WebcamInput",
            display_name="[Test] WEBCAM Input",
            category="skill_tests/inputs",
            inputs=[
                io.Webcam.Input("capture"),
            ],
            outputs=[io.String.Output("TEXT")],
        )

    @classmethod
    def execute(cls, capture):
        return io.NodeOutput(f"capture_len={len(capture) if capture else 0}")


# --- inputs: IMAGECOMPARE ---
class SkillTest_ImageCompareInput(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_ImageCompareInput",
            display_name="[Test] IMAGECOMPARE Input",
            category="skill_tests/inputs",
            inputs=[
                io.ImageCompare.Input("comparison", socketless=True),
            ],
            outputs=[io.String.Output("TEXT")],
        )

    @classmethod
    def execute(cls, comparison):
        return io.NodeOutput(f"comparison={comparison}")


# --- inputs: Input options (optional, tooltip, lazy, advanced, raw_link) ---
class SkillTest_InputOptions(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_InputOptions",
            display_name="[Test] Input Options",
            category="skill_tests/inputs",
            inputs=[
                io.Image.Input("image",
                    tooltip="Required image input",
                ),
                io.Image.Input("optional_image",
                    optional=True,
                    tooltip="Optional image input",
                ),
                io.Float.Input("advanced_param",
                    default=1.0,
                    min=0.0,
                    max=10.0,
                    advanced=True,
                ),
            ],
            outputs=[io.String.Output("TEXT")],
        )

    @classmethod
    def execute(cls, image, optional_image=None, advanced_param=1.0):
        has_opt = optional_image is not None
        return io.NodeOutput(f"has_optional={has_opt}, advanced={advanced_param}")


# --- inputs: force_input ---
class SkillTest_ForceInput(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_ForceInput",
            display_name="[Test] force_input",
            category="skill_tests/inputs",
            inputs=[
                io.Float.Input("value",
                    default=1.0,
                    force_input=True,
                ),
            ],
            outputs=[io.Float.Output("FLOAT")],
        )

    @classmethod
    def execute(cls, value):
        return io.NodeOutput(value)


# --- inputs: socketless ---
class SkillTest_SocketlessInput(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_SocketlessInput",
            display_name="[Test] socketless",
            category="skill_tests/inputs",
            inputs=[
                io.String.Input("note",
                    default="",
                    socketless=True,
                ),
            ],
            outputs=[io.String.Output("TEXT")],
        )

    @classmethod
    def execute(cls, note):
        return io.NodeOutput(note)


# --- inputs: All 6 hidden inputs ---
class SkillTest_HiddenInputs(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_HiddenInputs",
            display_name="[Test] Hidden Inputs",
            category="skill_tests/inputs",
            inputs=[
                io.String.Input("text", default="test"),
            ],
            outputs=[io.String.Output("TEXT")],
            hidden=[
                io.Hidden.unique_id,
                io.Hidden.prompt,
                io.Hidden.extra_pnginfo,
                io.Hidden.dynprompt,
                io.Hidden.auth_token_comfy_org,
                io.Hidden.api_key_comfy_org,
            ],
        )

    @classmethod
    def execute(cls, text):
        node_id = cls.hidden.unique_id
        prompt = cls.hidden.prompt
        extra = cls.hidden.extra_pnginfo
        return io.NodeOutput(f"{text} (node:{node_id})")


# --- inputs: Lazy evaluation with check_lazy_status ---
class SkillTest_LazyEval(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SkillTest_LazyEval",
            display_name="[Test] Lazy Evaluation",
            category="skill_tests/inputs",
            inputs=[
                io.Boolean.Input("condition"),
                io.Image.Input("if_true", lazy=True),
                io.Image.Input("if_false", lazy=True),
            ],
            outputs=[io.Image.Output("IMAGE")],
        )

    @classmethod
    def check_lazy_status(cls, condition, if_true=None, if_false=None):
        if condition and if_true is None:
            return ["if_true"]
        if not condition and if_false is None:
            return ["if_false"]
        return []

    @classmethod
    def execute(cls, condition, if_true, if_false):
        return io.NodeOutput(if_true if condition else if_false)
