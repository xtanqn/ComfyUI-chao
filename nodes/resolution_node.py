#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
常用分辨率节点
resolution_node.py
"""

import torch
import comfy.model_management
import os
import json


class ChaoCommonResolutionNode:
    def __init__(self):
        self.device = comfy.model_management.intermediate_device()
        # 加载分辨率数据
        self.resolution_data = self.load_resolution_data()

    def load_resolution_data(self):
        """加载分辨率JSON数据"""
        current_dir = os.path.dirname(os.path.realpath(__file__))
        json_path = os.path.join(current_dir, "..", "web", "extensions", "chao_resolution_node.json")
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 加载分辨率数据失败: {e}")
            return []

    @classmethod
    def INPUT_TYPES(cls):
        # 创建实例来加载数据
        instance = cls()
        resolution_data = instance.resolution_data
        
        # 提取所有比例
        ratio_order = [item["比例"] for item in resolution_data]
        if not ratio_order:
            ratio_order = ["1:1", "4:3", "3:2", "16:10", "16:9", "21:9", "3:4", "2:3", "9:16", "9:21", "其他"]
        
        # 提取所有分辨率作为默认值，确保验证通过
        all_resolutions = []
        for item in resolution_data:
            for res in item["分辨率"]:
                all_resolutions.append(res["resolution"])
        # 去重
        all_resolutions = list(set(all_resolutions))
        
        # 如果没有加载到数据，使用完整的默认分辨率列表
        if not all_resolutions:
            all_resolutions = [
                "64x64", "256x256", "512x512", "1024x1024",
                "640x480", "800x600", "1024x768", "1280x960",
                "1536x1024", "2400x1600",
                "1280x800", "1920x1200",
                "1280x720", "1920x1080", "2560x1440", "3840x2160",
                "2560x1080", "3440x1440",
                "480x640", "768x1024",
                "1024x1536", "1600x2400",
                "720x1280", "1080x1920",
                "1080x2520"
            ]
        
        return {
            "required": {
                "aspect_ratio": (ratio_order, {"default": "16:9"}),
                "resolution": (all_resolutions, {"default": "1920x1080"}),
                "批量张数": ("INT", {"default": 1, "min": 1, "max": 100, "step": 1}),
            },
            "optional": {
                "align_to_8": ("BOOLEAN", {"default": False, "label_on": "启用对齐到8倍数", "label_off": "禁用对齐到8倍数"}),
            }
        }

    RETURN_NAMES = ("Latent", "Width", "Height")
    RETURN_TYPES = ("LATENT", "INT", "INT")
    FUNCTION = "generate"
    CATEGORY = "🍡ComfyUI-chao"

    def generate(self, aspect_ratio, resolution, 批量张数=1, align_to_8=False):
        # 查找选中分辨率的说明信息
        resolution_desc = ""
        for item in self.resolution_data:
            if item["比例"] == aspect_ratio:
                for res in item["分辨率"]:
                    if res["resolution"] == resolution:
                        resolution_desc = res["说明"]
                        break
                break
        
        # 处理分辨率，仅在开关开启时对齐到8的倍数
        width, height = map(int, resolution.split('x'))
        if align_to_8:
            width = int((width // 8) * 8)
            height = int((height // 8) * 8)
        
        # 确保批量张数至少为1
        批量张数 = max(1, int(批量张数))
        
        # 生成latent（使用指定的批量张数）
        latent = torch.zeros([批量张数, 4, height // 8, width // 8], device=self.device)
        
        # 构建latent字典，包含批量张数和尺寸信息
        latent_dict = {
            "samples": latent,
            "batch_size": 批量张数,
            "width": width,
            "height": height
        }
        
        # 返回结果，包含分辨率说明
        print(f"🎯 选中比例: {aspect_ratio}, 分辨率: {resolution} ({width}x{height}), 批量张数: {批量张数}, 说明: {resolution_desc}")
        return (latent_dict, width, height)


NODE_CLASS_MAPPINGS = {
    "ChaoCommonResolutionNode": ChaoCommonResolutionNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ChaoCommonResolutionNode": "常用分辨率-chao",
}
