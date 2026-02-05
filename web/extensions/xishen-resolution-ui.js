import { app } from "../../../scripts/app.js"

app.registerExtension({
  name: "xishen_common_resolution_filter",
  setup() {
    // 使用setup钩子确保扩展在正确时机加载
    console.log("Xishen Resolution Filter extension loaded");
  },
  
  async nodeCreated(node) {
    if (node.comfyClass !== "XishenCommonResolutionNode") return;
    
    console.log("Setting up filter for resolution node");
    
    // 加载分辨率数据
    let resolutionData = [];
    // 参考主题提示词节点的实现，使用import.meta.url获取当前脚本路径
    try {
      // 使用import.meta.url获取当前脚本的路径
      const scriptUrl = new URL(import.meta.url);
      const scriptPath = scriptUrl.pathname;
      const extensionPath = scriptPath.substring(0, scriptPath.lastIndexOf('/') + 1);
      // 构建JSON文件的路径，与当前脚本在同一目录下
      const jsonUrl = extensionPath + "xishen_resolution_node.json";
      
      const response = await fetch(jsonUrl);
      if (response.ok) {
        resolutionData = await response.json();
        console.log("Resolution data loaded successfully:", resolutionData);
      } else {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (error) {
      console.error("Failed to load resolution data:", error);
      // 立即使用硬编码的数据作为后备，而不是尝试多个路径
      resolutionData = [
        {"比例":"1:1","分辨率":[{"resolution":"64x64","说明":"网站极小图标、favicon"},{"resolution":"256x256","说明":"小图标、缩略图"},{"resolution":"512x512","说明":"应用程序图标、中等方形图"},{"resolution":"1024x1024","说明":"大尺寸方形设计"}]},
        {"比例":"4:3","分辨率":[{"resolution":"640x480","说明":"VGA标准，早期CRT显示器"},{"resolution":"800x600","说明":"SVGA，早期计算机显示器"},{"resolution":"1024x768","说明":"XGA，早期笔记本电脑、投影仪"},{"resolution":"1280x960","说明":"SXGA+，高端显示器"}]},
        {"比例":"3:2","分辨率":[{"resolution":"1536x1024","说明":"iPad显示分辨率"},{"resolution":"2400x1600","说明":"高分辨率平板显示器"}]},
        {"比例":"16:10","分辨率":[{"resolution":"1280x800","说明":"WXGA，笔记本电脑显示器"},{"resolution":"1920x1200","说明":"WUXGA，专业显示器"}]},
        {"比例":"16:9","分辨率":[{"resolution":"1280x720","说明":"高清视频入门标准"},{"resolution":"1920x1080","说明":"全高清，视频、游戏主流标准"},{"resolution":"2560x1440","说明":"电竞显示器、高清视频制作"},{"resolution":"3840x2160","说明":"4K超高清，专业视频、高端显示器"}]},
        {"比例":"21:9","分辨率":[{"resolution":"2560x1080","说明":"21:9宽屏显示器"},{"resolution":"3440x1440","说明":"超宽屏游戏显示器"}]},
        {"比例":"3:4","分辨率":[{"resolution":"480x640","说明":"竖版VGA"},{"resolution":"768x1024","说明":"竖版XGA"}]},
        {"比例":"2:3","分辨率":[{"resolution":"1024x1536","说明":"竖版iPad分辨率"},{"resolution":"1600x2400","说明":"竖版高分辨率平板"}]},
        {"比例":"9:16","分辨率":[{"resolution":"720x1280","说明":"竖版高清视频"},{"resolution":"1080x1920","说明":"竖版全高清，手机屏幕、短视频"}]},
        {"比例":"9:21","分辨率":[{"resolution":"1080x2520","说明":"超长条屏显示"}]}
      ];
      console.log("Using fallback resolution data:", resolutionData);
    }
    
    // 等待节点完全初始化
    setTimeout(() => {
      const ratioWidget = node.widgets.find(w => w.name === "aspect_ratio");
      const resWidget = node.widgets.find(w => w.name === "resolution");
      
      if (!ratioWidget || !resWidget) {
        console.error("Failed to find required widgets");
        return;
      }
      
      // 创建一个用于显示分辨率说明的元素
      let descElement = null;
      
      // 根据比例过滤分辨率的函数
      const filterByRatio = (ratio) => {
        const ratioItem = resolutionData.find(item => item["比例"] === ratio);
        if (ratioItem) {
          return ratioItem["分辨率"].map(res => res["resolution"]);
        }
        return [];
      };
      
      // 获取分辨率说明的函数
      const getResolutionDescription = (ratio, resolution) => {
        const ratioItem = resolutionData.find(item => item["比例"] === ratio);
        if (ratioItem) {
          const resItem = ratioItem["分辨率"].find(res => res["resolution"] === resolution);
          if (resItem) {
            return resItem["说明"];
          }
        }
        return "";
      };
      
      // 显示分辨率说明的函数
      const showResolutionDescription = (ratio, resolution) => {
        const description = getResolutionDescription(ratio, resolution);
        
        // 如果不存在说明元素，创建一个
        if (!descElement) {
          descElement = document.createElement("div");
          descElement.style.cssText = `
            margin-top: 8px;
            padding: 8px;
            background-color: rgba(0, 0, 0, 0.1);
            border-radius: 4px;
            font-size: 12px;
            color: #666;
            max-width: 300px;
          `;
          
          // 找到resolution widget的DOM元素并在其后添加说明
          if (resWidget.widgetEl) {
            resWidget.widgetEl.parentNode.appendChild(descElement);
          }
        }
        
        // 更新说明内容
        descElement.textContent = description;
      };
      
      // 替换比例下拉框的回调函数
      const originalRatioCallback = ratioWidget.callback;
      ratioWidget.callback = function(value) {
        // 调用原始回调
        if (originalRatioCallback) {
          originalRatioCallback.call(this, value);
        }
        
        // 执行过滤
        const filteredResolutions = filterByRatio(value);
        console.log(`Filtered for ${value}: ${filteredResolutions.length} options`);
        
        // 更新resolution widget的选项
        if (resWidget.options?.values) {
          resWidget.options.values = filteredResolutions;
        }
        
        // 确保有选中值
        if (filteredResolutions.length > 0) {
          // 如果当前值不在过滤列表中，选择第一个
          const currentValue = resWidget.value;
          if (!filteredResolutions.includes(currentValue)) {
            resWidget.value = filteredResolutions[0];
          }
        }
        
        // 更新分辨率说明
        showResolutionDescription(value, resWidget.value);
        
        // 强制刷新整个节点的UI
        if (resWidget.onChange) {
          resWidget.onChange(resWidget.value);
        }
        
        // 重新渲染画布
        if (node.graph) {
          node.graph.setDirtyCanvas(true, true);
        }
        
        // 直接更新DOM
        if (resWidget.widgetEl) {
          const select = resWidget.widgetEl.querySelector('select');
          if (select) {
            const currentVal = resWidget.value;
            select.innerHTML = '';
            
            filteredResolutions.forEach(res => {
              const option = document.createElement('option');
              option.value = res;
              option.textContent = res;
              select.appendChild(option);
            });
            
            select.value = currentVal;
          }
        }
      };
      
      // 替换分辨率下拉框的回调函数以更新说明
      const originalResCallback = resWidget.callback;
      resWidget.callback = function(value) {
        // 调用原始回调
        if (originalResCallback) {
          originalResCallback.call(this, value);
        }
        
        // 更新分辨率说明
        showResolutionDescription(ratioWidget.value, value);
        
        // 强制刷新UI
        if (node.graph) {
          node.graph.setDirtyCanvas(true, true);
        }
      };
      
      // 初始应用过滤和显示说明
      ratioWidget.callback(ratioWidget.value);
      
    }, 500);
  }
});

