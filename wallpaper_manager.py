import os
import sys
import tempfile
import ctypes
from PIL import Image, ImageDraw, ImageFont
import markdown
from bs4 import BeautifulSoup

class WallpaperManager:
    """壁纸管理器，负责在壁纸上添加任务清单"""
    
    def __init__(self, task_manager):
        """初始化壁纸管理器"""
        self.task_manager = task_manager
        
        # 保存原始壁纸路径
        self.original_wallpaper = self._get_current_wallpaper()
        
        # 创建临时文件目录
        self.temp_dir = os.path.join(tempfile.gettempdir(), "wallpaper_tasks")
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # 字体设置 - 固定使用微软雅黑
        self.font_size = 24  # 默认字体大小
        
        # 监听任务变更
        self.task_manager.add_change_listener(self.refresh_wallpaper)
    
    def set_font_size(self, size):
        """设置字体大小"""
        self.font_size = size
    
    def _get_current_wallpaper(self):
        """获取当前壁纸路径"""
        try:
            # 使用Windows API获取
            ubuf = ctypes.create_unicode_buffer(512)
            ctypes.windll.user32.SystemParametersInfoW(0x0073, len(ubuf), ubuf, 0)
            return ubuf.value
        except:
            try:
                # 备用方法: 尝试从注册表获取
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                    r"Control Panel\Desktop")
                return winreg.QueryValueEx(key, "Wallpaper")[0]
            except:
                try:
                    # 第三种方法: 尝试获取转码的壁纸位置
                    wallpaper_path = os.path.join(
                        os.environ['APPDATA'], 'Microsoft', 
                        'Windows', 'Themes', 'TranscodedWallpaper')
                    if os.path.exists(wallpaper_path):
                        return wallpaper_path
                except:
                    pass
                return ""
    
    def _set_wallpaper(self, path):
        """设置壁纸"""
        try:
            ctypes.windll.user32.SystemParametersInfoW(0x0014, 0, path, 3)
            return True
        except Exception as e:
            print(f"设置壁纸失败: {e}")
            return False
    
    def refresh_wallpaper(self):
        """刷新壁纸，添加任务列表"""
        try:
            # 始终从原始壁纸开始，而不是当前壁纸
            if self.original_wallpaper and os.path.exists(self.original_wallpaper):
                img = Image.open(self.original_wallpaper)
            else:
                print("无法获取原始壁纸，使用纯色背景")
                img = Image.new('RGB', (1920, 1080), (30, 30, 40))
            
            # 创建绘图对象
            draw = ImageDraw.Draw(img)
            
            # 绘制任务区域背景 (更宽的半透明区域)
            width, height = img.size
            # 修改任务区域：上方预留更多空间，底部接触屏幕
            top_margin = int(height * 0.15)  # 顶部预留15%的屏幕空间
            task_area = (int(width * 0.5), top_margin, width - 50, height - 20)  # 底部接近屏幕边缘
            overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            
            # 使用圆角矩形背景，更美观
            radius = 20
            # 绘制圆角矩形
            overlay_draw.rectangle(
                [task_area[0], task_area[1] + radius, task_area[2], task_area[3] - radius],
                fill=(30, 30, 40, 160)  # 降低不透明度，提高可读性
            )
            overlay_draw.rectangle(
                [task_area[0] + radius, task_area[1], task_area[2] - radius, task_area[3]],
                fill=(30, 30, 40, 160)
            )
            # 绘制四个角
            overlay_draw.pieslice([task_area[0], task_area[1], task_area[0] + radius * 2, task_area[1] + radius * 2],
                                180, 270, fill=(30, 30, 40, 160))
            overlay_draw.pieslice([task_area[2] - radius * 2, task_area[1], task_area[2], task_area[1] + radius * 2],
                                270, 360, fill=(30, 30, 40, 160))
            overlay_draw.pieslice([task_area[0], task_area[3] - radius * 2, task_area[0] + radius * 2, task_area[3]],
                                90, 180, fill=(30, 30, 40, 160))
            overlay_draw.pieslice([task_area[2] - radius * 2, task_area[3] - radius * 2, task_area[2], task_area[3]],
                                0, 90, fill=(30, 30, 40, 160))
            
            # 如果原图没有Alpha通道，转换为RGBA
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # 合并半透明覆盖层
            img = Image.alpha_composite(img, overlay)
            img = img.convert('RGB')  # 转回RGB用于保存
            
            # 查找微软雅黑字体
            title_font_size = self.font_size + 14  # 标题字体比正文大一些
            
            try:
                # 尝试加载微软雅黑字体
                font_dir = os.path.join(os.environ['WINDIR'], 'Fonts')
                font_path = os.path.join(font_dir, 'msyh.ttc')
                
                title_font = ImageFont.truetype(font_path, title_font_size)
                task_font = ImageFont.truetype(font_path, self.font_size)
                status_font = ImageFont.truetype(font_path, self.font_size + 2)
            except Exception as e:
                print(f"加载字体失败: {e}, 使用默认字体")
                # 使用默认字体
                title_font = ImageFont.load_default()
                task_font = ImageFont.load_default()
                status_font = ImageFont.load_default()
            
            # 绘制标题和彩色分隔线
            draw = ImageDraw.Draw(img)
            title_text = "今日任务清单"
            draw.text((task_area[0] + 30, task_area[1] + 30), title_text, 
                    fill=(240, 240, 255), font=title_font)
            
            # 绘制分隔线
            line_y = task_area[1] + 90
            draw.line([(task_area[0] + 20, line_y), (task_area[2] - 20, line_y)], 
                    fill=(100, 150, 250), width=3)
            
            # 获取任务列表
            tasks = self.task_manager.get_all_tasks()
            
            # 绘制任务，使用更好的文本换行
            y_pos = line_y + 40
            task_width = task_area[2] - task_area[0] - 80  # 可用于文本的宽度
            
            for task in tasks:
                # 处理Markdown内容
                try:
                    html = markdown.markdown(task["content"])
                    soup = BeautifulSoup(html, "html.parser")
                    text = soup.get_text()
                except:
                    # 如果Markdown处理失败，直接使用原文本
                    text = task["content"]
                
                # 根据任务状态选择颜色
                color = (180, 180, 180) if task["is_completed"] else (255, 255, 255)
                status_color = (150, 255, 150) if task["is_completed"] else (255, 255, 255)
                
                # 绘制任务完成状态
                status = "✓" if task["is_completed"] else "◯"
                draw.text((task_area[0] + 25, y_pos), status, fill=status_color, font=status_font)
                
                # 处理文本换行 - 考虑字符宽度
                lines = []
                current_line = ""
                max_chars = 30  # 根据更大的字体，减少每行字符数
                
                words = text.split()
                for word in words:
                    if len(current_line + " " + word if current_line else word) <= max_chars:
                        current_line += (" " + word if current_line else word)
                    else:
                        lines.append(current_line)
                        current_line = word
                
                if current_line:
                    lines.append(current_line)
                
                # 显示文本
                text_x = task_area[0] + 70
                for i, line in enumerate(lines[:3]):  # 限制最多3行
                    draw.text((text_x, y_pos + i * 36), line, fill=color, font=task_font)
                
                # 如果有更多行但未显示，添加省略号
                if len(lines) > 3:
                    draw.text((text_x, y_pos + 3 * 36), "...", fill=color, font=task_font)
                
                # 避免任务超出区域
                if y_pos > task_area[3] - 40:
                    draw.text((task_area[0] + 70, y_pos), "更多任务...", fill=(255, 255, 255), font=task_font)
                    break
            
            # 如果没有任务，显示提示信息
            if not tasks:
                draw.text(
                    (task_area[0] + 70, y_pos), 
                    '暂无任务，点击"添加任务"开始',
                    fill=(200, 200, 200), 
                    font=task_font
                )
            
            # 保存修改后的壁纸
            output_path = os.path.join(self.temp_dir, "wallpaper_with_tasks.jpg")
            img.save(output_path, quality=95)
            
            # 设置为壁纸
            self._set_wallpaper(output_path)
            
            return True
        except Exception as e:
            print(f"刷新壁纸失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def restore_original_wallpaper(self):
        """恢复原始壁纸"""
        if self.original_wallpaper and os.path.exists(self.original_wallpaper):
            return self._set_wallpaper(self.original_wallpaper)
        return False