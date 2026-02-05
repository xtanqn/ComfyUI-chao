"""
4宫格拆分-chao 节点

该节点用于将一张4宫格图片拆分成4张独立的图片。
支持设置宫格中间的边框宽度和宫格图外围的边框宽度。

输入：
- image：4宫格图片（必需）
- split_width：宫格中间的边框宽度（默认：0）
- border_width：宫格图外围的边框宽度（默认：0）

输出：
- 分镜批次 (Batch 4)：包含4张拆分后图片的批次
"""

import torch
import numpy as np

class ChaoGridSplitNode:
    """
    4宫格拆分节点类
    
    该类定义了一个ComfyUI节点，用于将4宫格图片拆分成4张独立图片。
    支持设置宫格中间的边框宽度和外围的边框宽度。
    """
    
    # 节点分类
    CATEGORY = "🍡ComfyUI-chao"
    
    @classmethod
    def INPUT_TYPES(cls):
        """
        定义节点的输入类型
        """
        return {
            "required": {
                "image": ("IMAGE", {"forceInput": True}),  # 强制输入图片
                "宫格间距": ("INT", {
                    "default": 0, 
                    "min": 0, 
                    "max": 100, 
                    "step": 1
                }),
                "外围边框": ("INT", {
                    "default": 0, 
                    "min": 0, 
                    "max": 100, 
                    "step": 1
                }),
            }
        }
    
    # 定义节点的输出类型
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("分镜批次 (Batch 4)",)
    FUNCTION = "split_grid"
    
    def split_grid(self, image, 宫格间距=0, 外围边框=0):
        """
        拆分4宫格图片
        
        Args:
            image: 输入的4宫格图片 (shape: [batch_size, height, width, channels])
            宫格间距: 宫格中间的边框宽度
            外围边框: 宫格图外围的边框宽度
            
        Returns:
            包含4张拆分后图片的批次 (shape: [4, height/2, width/2, channels])
        """
        # 确保输入是4D张量 [batch_size, height, width, channels]
        if len(image.shape) != 4:
            raise ValueError("输入图片必须是4D张量 [batch_size, height, width, channels]")
        
        # 取第一个批次的图片（假设只有一张4宫格图片）
        grid_image = image[0].clone()
        
        # 获取图片尺寸
        height, width, channels = grid_image.shape
        
        # 计算单张图片的尺寸（考虑边框）
        # 总宽度 = 2*单张宽度 + 中间边框宽度 + 2*外围边框宽度
        # 总高度 = 2*单张高度 + 中间边框宽度 + 2*外围边框宽度
        single_width = (width - 2 * 外围边框 - 宫格间距) // 2
        single_height = (height - 2 * 外围边框 - 宫格间距) // 2
        
        # 确保尺寸有效
        if single_width <= 0 or single_height <= 0:
            raise ValueError(f"计算的单张图片尺寸无效: {single_width}x{single_height}")
        
        # 定义4个宫格的区域
        # 考虑外围边框宽度
        regions = [
            # 左上
            (外围边框, 外围边框, 外围边框 + single_width, 外围边框 + single_height),
            # 右上
            (外围边框 + single_width + 宫格间距, 外围边框, width - 外围边框, 外围边框 + single_height),
            # 左下
            (外围边框, 外围边框 + single_height + 宫格间距, 外围边框 + single_width, height - 外围边框),
            # 右下
            (外围边框 + single_width + 宫格间距, 外围边框 + single_height + 宫格间距, width - 外围边框, height - 外围边框)
        ]
        
        # 拆分图片
        split_images = []
        for i, (x1, y1, x2, y2) in enumerate(regions):
            # 裁剪区域
            split_img = grid_image[y1:y2, x1:x2]
            
            # 确保裁剪后的尺寸正确
            if split_img.shape[0] != single_height or split_img.shape[1] != single_width:
                # 如果尺寸不匹配，进行调整
                split_img = grid_image[y1:y1+single_height, x1:x1+single_width]
            
            split_images.append(split_img)
        
        # 将4张图片组合成一个批次
        batch_images = torch.stack(split_images, dim=0)
        
        # 验证输出尺寸
        assert batch_images.shape == (4, single_height, single_width, channels), \
            f"输出尺寸错误: {batch_images.shape}，期望: (4, {single_height}, {single_width}, {channels})"
        
        print(f"✅ 4宫格拆分成功: 输入尺寸={width}x{height}, 输出尺寸={single_width}x{single_height}, 中间边框={宫格间距}, 外围边框={外围边框}")
        
        return (batch_images,)

# 节点映射
NODE_CLASS_MAPPINGS = {
    "ChaoGridSplitNode": ChaoGridSplitNode,
}

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "ChaoGridSplitNode": "4宫格拆分-chao",
}
