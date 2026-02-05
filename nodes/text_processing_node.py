#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本处理节点（去空行）
text_processing_node.py
"""

import re


class ChaoRemoveEmptyLinesNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"text": ("STRING", {"default": "", "multiline": True})}}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "remove_empty_lines"
    CATEGORY = "🍡ComfyUI-chao"

    def remove_empty_lines(self, text):
        parts = re.findall(r"(.*?)(\r\n|\n|\r|$)", text)
        kept = []
        for content, sep in parts:
            if content.strip() != "":
                kept.append(content + sep)
        return ("".join(kept),)


NODE_CLASS_MAPPINGS = {
    "ChaoRemoveEmptyLinesNode": ChaoRemoveEmptyLinesNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ChaoRemoveEmptyLinesNode": "去空行-chao",
}
