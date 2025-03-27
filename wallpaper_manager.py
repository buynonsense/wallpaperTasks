import os
import sys
import tempfile
import ctypes
from PIL import Image, ImageDraw, ImageFont
import markdown
from bs4 import BeautifulSoup
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QBuffer, QByteArray, QIODevice
import io
from markdown_renderer import MarkdownRenderer

class WallpaperManager:
    """壁纸管理器，负责在壁纸上添加任务清单"""
    
    def __init__(self, task_manager):
        """初始化壁纸管理器"""
        self.task_manager = task_manager
        
        # 保存原始壁纸路径
        self.original_wallpaper = self._get_current_wallpaper()
        
        # 在此加载原图并保存到内存中
        if self.original_wallpaper and os.path.exists(self.original_wallpaper):
            try:
                self.original_image = Image.open(self.original_wallpaper).copy()
            except Exception as e:
                print(f"加载原始壁纸图片失败: {e}")
                self.original_image = Image.new('RGB', (1920, 1080), (30, 30, 40))
        else:
            self.original_image = Image.new('RGB', (1920, 1080), (30, 30, 40))
        
        # 创建临时文件目录
        self.temp_dir = os.path.join(tempfile.gettempdir(), "wallpaper_tasks")
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # 字体设置 - 固定使用微软雅黑
        self.font_size = 24  # 默认字体大小
        
        # 任务区域位置 (相对坐标 0-1)
        self.task_area_rel = [0.5, 0.15, 0.95, 0.95]  # 默认位置
        
        # 创建Markdown渲染器
        self.md_renderer = MarkdownRenderer()
        
        # 监听任务变更
        self.task_manager.add_change_listener(self.refresh_wallpaper)
    
    def set_font_size(self, size):
        """设置字体大小"""
        self.font_size = size
    
    def set_task_area(self, x1, y1, x2, y2):
        """设置任务区域位置 (相对坐标 0-1)"""
        self.task_area_rel = [x1, y1, x2, y2]
    
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
        try:
            # 每次刷新时都重新加载原始壁纸，保证基础图像干净
            if self.original_wallpaper and os.path.exists(self.original_wallpaper):
                original_image = Image.open(self.original_wallpaper).copy()
            else:
                original_image = Image.new('RGB', (1920, 1080), (30, 30, 40))
            img = original_image.copy()
            
            # 计算任务区域
            width, height = img.size
            x1 = int(self.task_area_rel[0] * width)
            y1 = int(self.task_area_rel[1] * height)
            x2 = int(self.task_area_rel[2] * width)
            y2 = int(self.task_area_rel[3] * height)
            task_area = (x1, y1, x2, y2)
            
            # 绘制半透明任务区域背景
            from PIL import ImageDraw  # 确保导入ImageDraw
            overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            radius = 20
            overlay_draw.rectangle(
                [task_area[0], task_area[1] + radius, task_area[2], task_area[3] - radius],
                fill=(30, 30, 40, 160)
            )
            overlay_draw.rectangle(
                [task_area[0] + radius, task_area[1], task_area[2] - radius, task_area[1] + radius],
                fill=(30, 30, 40, 160)
            )
            overlay_draw.rectangle(
                [task_area[0] + radius, task_area[3] - radius, task_area[2] - radius, task_area[3]],
                fill=(30, 30, 40, 160)
            )
            overlay_draw.ellipse([task_area[0], task_area[1], task_area[0] + radius * 2, task_area[1] + radius * 2],
                                   fill=(30, 30, 40, 160))
            overlay_draw.ellipse([task_area[2] - radius * 2, task_area[1], task_area[2], task_area[1] + radius * 2],
                                   fill=(30, 30, 40, 160))
            overlay_draw.ellipse([task_area[0], task_area[3] - radius * 2, task_area[0] + radius * 2, task_area[3]],
                                   fill=(30, 30, 40, 160))
            overlay_draw.ellipse([task_area[2] - radius * 2, task_area[3] - radius * 2, task_area[2], task_area[3]],
                                   fill=(30, 30, 40, 160))
            
            img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
            
            # 后续绘制任务内容代码保持不变...
            # 创建绘图对象
            draw = ImageDraw.Draw(img)
            
            # 加载字体
            try:
                font_dir = os.path.join(os.environ['WINDIR'], 'Fonts')
                font_path = os.path.join(font_dir, 'msyh.ttc')  # 微软雅黑
                title_font = ImageFont.truetype(font_path, self.font_size + 12)
                task_font = ImageFont.truetype(font_path, self.font_size)
                status_font = ImageFont.truetype(font_path, self.font_size + 4)
            except Exception as e:
                print(f"加载字体失败: {e}，使用默认字体")
                title_font = ImageFont.load_default()
                task_font = ImageFont.load_default()
                status_font = ImageFont.load_default()
            
            # 绘制标题
            title = "任务清单"
            title_width = draw.textlength(title, font=title_font)
            title_x = task_area[0] + (task_area[2] - task_area[0] - title_width) // 2
            draw.text((title_x, task_area[1] + 20), title, fill=(255, 255, 255), font=title_font)
            
            # 获取任务列表 - 只显示标记为在壁纸上显示且未完成的任务
            all_tasks = self.task_manager.get_all_tasks()
            tasks = [task for task in all_tasks 
                     if not task["is_completed"] and task.get("show_on_wallpaper", True)]
            
            # 任务起始Y坐标
            y_pos = task_area[1] + 80
            task_width = task_area[2] - task_area[0] - 90  # 为状态图标留出空间
            
            # 处理任务列表 - 不再显示任务状态图标（移除方框）
            for task in tasks:
                try:
                    # 绘制任务标题
                    title = task.get("title", "").strip()
                    if not title:
                        # 如果没有标题，使用内容的第一行
                        title = task["content"].split('\n')[0]
                        if len(title) > 50:
                            title = title[:47] + "..."
                    
                    # 使用加粗字体渲染标题
                    draw.text(
                        (task_area[0] + 30, y_pos), 
                        title, 
                        fill=(220, 220, 255), 
                        font=title_font
                    )
                    
                    # 更新Y位置，为内容留出空间
                    y_pos += title_font.getbbox(title)[3] + 10
                    
                    # 使用Markdown渲染器渲染任务内容
                    md_width = task_area[2] - task_area[0] - 50  # 不再为状态图标留空间
                    rendered_pixmap = self.md_renderer.render_markdown(
                        task["content"], 
                        width=md_width, 
                        font_size=self.font_size, 
                        completed=False  # 已完成任务不会显示
                    )
                    
                    # 检查QPixmap是否有效
                    if rendered_pixmap.isNull():
                        raise RuntimeError("渲染的QPixmap无效")
                    
                    # 将QPixmap转换为PIL Image
                    arr = QByteArray()
                    qbuf = QBuffer(arr)
                    qbuf.open(QIODevice.OpenModeFlag.WriteOnly)
                    rendered_pixmap.save(qbuf, b"PNG")
                    
                    buffer = io.BytesIO(bytes(arr))
                    md_image = Image.open(buffer).convert("RGBA")
                    
                    # 计算粘贴位置 - 不再缩进
                    paste_x = task_area[0] + 30  # 从30像素开始，而不是70
                    paste_y = y_pos
                    
                    # 粘贴到壁纸上
                    img.paste(md_image, (paste_x, paste_y), md_image)
                    
                    # 更新下一个任务的y位置
                    y_pos += md_image.height + 25  # 任务间距
                    
                except Exception as e:
                    import traceback
                    print(f"渲染Markdown失败，回退到纯文本: {e}")
                    print("详细错误信息:")
                    traceback.print_exc()  # 打印完整的堆栈跟踪
                    # 回退到纯文本渲染
                    text = task["content"]
                    color = (180, 180, 180) if task["is_completed"] else (255, 255, 255)
                    
                    # 处理文本换行
                    lines = []
                    current_line = ""
                    max_chars = int(70 * (24 / self.font_size))  # 根据字体大小调整每行字符数
                    
                    words = text.split()
                    for word in words:
                        if len(current_line + " " + word if current_line else word) <= max_chars:
                            current_line += (" " + word if current_line else word)
                        else:
                            lines.append(current_line)
                            current_line = word
                    
                    if current_line:
                        lines.append(current_line)
                    
                    # 显示文本 - 不再缩进
                    text_x = task_area[0] + 30  # 从30像素开始，而不是70
                    line_height = int(self.font_size * 1.5)
                    for i, line in enumerate(lines[:3]):  # 限制最多3行
                        # 修改此处，直接传递color和font作为参数
                        draw.text((text_x, y_pos + i * line_height), line, fill=color, font=task_font)
                    
                    # 如果有更多行但未显示，添加省略号
                    if len(lines) > 3:
                        draw.text((text_x, y_pos + 3 * line_height), "...", fill=color, font=task_font)
                    
                    # 更新下一个任务的Y位置
                    line_count = min(len(lines), 3) + (1 if len(lines) > 3 else 0)
                    y_pos += line_count * line_height + 20  # 任务间距
                
                # 避免任务超出区域
                if y_pos > task_area[3] - 60:
                    draw.text((task_area[0] + 70, y_pos), "更多任务...", fill=(255, 255, 255), font=task_font)
                    break
            
            # 如果没有未完成任务，显示提示信息
            if not tasks:
                if all_tasks:
                    # 有任务但都已完成
                    message = '所有任务已完成！'
                else:
                    # 没有任务
                    message = '暂无任务，点击"添加任务"开始'
                    
                draw.text(
                    (task_area[0] + 30, task_area[1] + 120), 
                    message,
                    fill=(200, 200, 200), 
                    font=task_font
                )
            
            # 保存修改后的壁纸
            output_path = os.path.join(self.temp_dir, "wallpaper_with_tasks.jpg")
            img.save(output_path, quality=95)
            
            # 设置为桌面壁纸
            return self._set_wallpaper(output_path)
            
        except Exception as error:
            print(f"刷新壁纸失败: {error}")
            import traceback
            traceback.print_exc()
            return False
    
    def restore_original_wallpaper(self):
        """恢复原始壁纸"""
        if self.original_wallpaper and os.path.exists(self.original_wallpaper):
            return self._set_wallpaper(self.original_wallpaper)
        return False