#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
随机数与分辨率节点集合（后端）
random_number_node.py
"""

import random
import re
import torch
import comfy.model_management


class ChaoRandomIntegerNode:
    def __init__(self):
        self.current_sequence_value = None
        self.last_min = None
        self.last_max = None
        self.last_reset_sequence = 0  # 跟踪上一次处理的reset_sequence值

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "min_value": ("INT", {"default": 1, "min": -10000, "max": 10000}),
                "max_value": ("INT", {"default": 50, "min": -10000, "max": 10000}),
                "mode": (["random", "sequence"], {"default": "sequence"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            # reset_sequence 作为 hidden 输入，仅由前端 JS 通过按钮触发时设置
            "hidden": {
                "reset_sequence": ("INT", {"default": 0}),
            },
        }

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("number_text", "number_int")
    FUNCTION = "generate_number"
    CATEGORY = "🍡ComfyUI-chao"

    def generate_number(self, min_value, max_value, mode, seed, reset_sequence=0):
        # 保证 min <= max
        if min_value > max_value:
            min_value, max_value = max_value, min_value

        # 随机模式
        if mode == "random":
            random.seed(seed)
            result = random.randint(min_value, max_value)
            return (str(result), result)

        # 序列模式
        # 转换reset_sequence为整数以确保类型正确
        reset_sequence = int(reset_sequence)
        
        # 如果reset_sequence为1或2且与上一次不同，重置为最小值
        # 这样1和2之间来回切换可以实现多次重置
        if reset_sequence in (1, 2) and reset_sequence != self.last_reset_sequence:
            self.current_sequence_value = min_value
            self.last_min = min_value
            self.last_max = max_value
            self.last_reset_sequence = reset_sequence  # 更新上一次的reset_sequence值
            return (str(self.current_sequence_value), self.current_sequence_value)
        
        # 只有当reset_sequence为1或2时才更新last_reset_sequence
        # 这样reset_sequence=0时不会清除之前的重置状态
        if reset_sequence in (1, 2):
            self.last_reset_sequence = reset_sequence

        # 如果 min/max 改变，自动重置
        if self.last_min != min_value or self.last_max != max_value:
            self.current_sequence_value = min_value
            self.last_min = min_value
            self.last_max = max_value
            return (str(self.current_sequence_value), self.current_sequence_value)

        # 第一次执行
        if self.current_sequence_value is None:
            self.current_sequence_value = min_value
            self.last_min = min_value
            self.last_max = max_value
            return (str(self.current_sequence_value), self.current_sequence_value)

        # 正常递增并循环
        self.current_sequence_value += 1
        if self.current_sequence_value > max_value:
            self.current_sequence_value = min_value

        return (str(self.current_sequence_value), self.current_sequence_value)


NODE_CLASS_MAPPINGS = {
    "ChaoRandomIntegerNode": ChaoRandomIntegerNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ChaoRandomIntegerNode": "随机整数-chao",
}
