"""
Covers: comfyui-node-migration (V1 legacy reference)
- V1 class attributes (CATEGORY, FUNCTION, RETURN_TYPES, RETURN_NAMES, etc.)
- INPUT_TYPES dict with required, optional, hidden
- IS_CHANGED
- VALIDATE_INPUTS
- check_lazy_status (V1: instance method)
- OUTPUT_NODE
- OUTPUT_TOOLTIPS
- V1 registration (NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS)
"""

import time
import torch


class SkillTest_V1BasicNode:
    """V1 legacy node for migration reference."""
    CATEGORY = "skill_tests/v1_legacy"
    FUNCTION = "execute"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    OUTPUT_TOOLTIPS = ("The processed image",)
    DESCRIPTION = "V1 legacy node demonstrating class attribute pattern"
    DEPRECATED = False
    EXPERIMENTAL = False

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
                "mode": (["normal", "multiply", "screen"],),
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

    @classmethod
    def IS_CHANGED(s, image, strength, mode, text, mask=None,
                   unique_id=None, prompt=None, extra_pnginfo=None):
        return strength

    @classmethod
    def VALIDATE_INPUTS(s, image, strength, mode, text, mask=None,
                        unique_id=None, prompt=None, extra_pnginfo=None):
        if strength < 0:
            return "Strength must be non-negative"
        return True

    def execute(self, image, strength, mode, text, mask=None,
                unique_id=None, prompt=None, extra_pnginfo=None):
        result = image * strength
        return (result,)


class SkillTest_V1OutputNode:
    """V1 output node with UI return."""
    CATEGORY = "skill_tests/v1_legacy"
    FUNCTION = "save"
    RETURN_TYPES = ()
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "prefix": ("STRING", {"default": "v1_output"}),
            },
        }

    def save(self, images, prefix):
        return {
            "ui": {
                "images": [
                    {"filename": f"{prefix}_00001.png", "subfolder": "", "type": "output"}
                ]
            }
        }


class SkillTest_V1DataAndUI:
    """V1 node returning both data and UI."""
    CATEGORY = "skill_tests/v1_legacy"
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
            },
        }

    def run(self, image):
        return {
            "ui": {"images": [{"filename": "preview.png", "subfolder": "", "type": "temp"}]},
            "result": (image,),
        }


class SkillTest_V1LazyNode:
    """V1 node with lazy evaluation (instance method)."""
    CATEGORY = "skill_tests/v1_legacy"
    FUNCTION = "execute"
    RETURN_TYPES = ("IMAGE",)

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "condition": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "if_true": ("IMAGE", {"lazy": True}),
                "if_false": ("IMAGE", {"lazy": True}),
            },
        }

    def check_lazy_status(self, condition, if_true=None, if_false=None):
        if condition and if_true is None:
            return ["if_true"]
        if not condition and if_false is None:
            return ["if_false"]
        return []

    def execute(self, condition, if_true=None, if_false=None):
        return (if_true if condition else if_false,)


# V1 Registration
NODE_CLASS_MAPPINGS = {
    "SkillTest_V1BasicNode": SkillTest_V1BasicNode,
    "SkillTest_V1OutputNode": SkillTest_V1OutputNode,
    "SkillTest_V1DataAndUI": SkillTest_V1DataAndUI,
    "SkillTest_V1LazyNode": SkillTest_V1LazyNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SkillTest_V1BasicNode": "[Test] V1 Basic Node",
    "SkillTest_V1OutputNode": "[Test] V1 Output Node",
    "SkillTest_V1DataAndUI": "[Test] V1 Data + UI",
    "SkillTest_V1LazyNode": "[Test] V1 Lazy Node",
}
