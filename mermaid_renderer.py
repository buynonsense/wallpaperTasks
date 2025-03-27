import os
import asyncio
import tempfile
import re
from pyppeteer import launch
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
from PyQt6.QtCore import Qt, QRect, QSettings, QEventLoop
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QApplication

class MermaidRenderer:
    """Mermaid图表渲染器，使用pyppeteer/puppeteer将Mermaid语法转换为图像"""
    
    def __init__(self):
        self.temp_dir = os.path.join(tempfile.gettempdir(), "wallpaper_tasks_mermaid")
        os.makedirs(self.temp_dir, exist_ok=True)
        self.browser = None
        
        # 尝试获取Chrome路径
        self.chrome_path = self._find_chrome()
        if self.chrome_path:
            print(f"Chrome路径自动检测成功: {self.chrome_path}")
        else:
            print("未检测到Chrome路径，将在需要时提示用户")
    
    def _find_chrome(self):
        """自动查找Chrome浏览器路径"""
        # 首先检查是否有已保存的路径
        settings = QSettings("WallpaperTasks", "Application")
        saved_path = settings.value("chrome_path", "")
        if saved_path and os.path.exists(saved_path):
            return saved_path
        
        # 常见的Chrome安装路径
        possible_paths = [
            # 64位 Chrome
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            # 32位 Chrome
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            # 用户安装的Chrome
            os.path.join(os.environ['LOCALAPPDATA'], r"Google\Chrome\Application\chrome.exe"),
            # Edge 浏览器 (也基于Chromium)
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ]
        
        # 检查可能的路径
        for path in possible_paths:
            if os.path.exists(path):
                # 保存找到的路径
                settings.setValue("chrome_path", path)
                return path
        
        return None
        
    async def _get_browser(self):
        """懒加载浏览器实例"""
        if self.browser is None:
            try:
                # 如果有Chrome路径，使用它
                if hasattr(self, 'chrome_path') and self.chrome_path and os.path.exists(self.chrome_path):
                    self.browser = await launch(
                        headless=True,
                        executablePath=self.chrome_path,
                        args=['--no-sandbox', '--disable-setuid-sandbox']
                    )
                else:
                    # 否则尝试默认路径(通常会失败)
                    self.browser = await launch(
                        headless=True,
                        args=['--no-sandbox', '--disable-setuid-sandbox']
                    )
            except Exception as e:
                print(f"启动浏览器失败: {e}")
                self._browser_failed = True
                raise
        return self.browser
    
    async def render_mermaid_to_png(self, mermaid_code, output_path):
        """将Mermaid代码渲染为PNG图像"""
        browser = await self._get_browser()
        page = await browser.newPage()
        
        # 使用Mermaid在线渲染HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
            <script>
                mermaid.initialize({{
                    startOnLoad: true,
                    theme: 'dark',
                    securityLevel: 'loose',
                    fontFamily: 'Microsoft YaHei',
                    background: 'transparent'
                }});
            </script>
            <style>
                body, html {{
                    margin: 0;
                    padding: 0;
                    background-color: transparent;
                }}
                .mermaid {{
                    color: white;
                    background-color: transparent;
                }}
            </style>
        </head>
        <body>
            <div class="mermaid">
                {mermaid_code}
            </div>
        </body>
        </html>
        """
        
        # 写入临时HTML文件
        html_path = os.path.join(self.temp_dir, "mermaid.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        # 打开HTML文件并等待Mermaid渲染完成
        await page.goto(f"file://{html_path}")
        await page.waitForSelector(".mermaid svg")
        
        # 找到SVG元素并截图
        svg_element = await page.querySelector(".mermaid svg")
        await svg_element.screenshot({"path": output_path, "omitBackground": True})
        
        await page.close()
        return output_path
    
    def close(self):
        """关闭浏览器实例"""
        async def _close():
            if self.browser:
                await self.browser.close()
                self.browser = None
        
        asyncio.get_event_loop().run_until_complete(_close())
    
    def render_mermaid(self, mermaid_code):
        """渲染Mermaid代码为QPixmap"""
        # 创建唯一的输出路径
        output_path = os.path.join(self.temp_dir, f"mermaid_{hash(mermaid_code)}.png")
        
        # 如果已缓存，直接返回
        if os.path.exists(output_path):
            return QPixmap(output_path)
        
        try:
            # 尝试渲染
            asyncio.get_event_loop().run_until_complete(
                self.render_mermaid_to_png(mermaid_code, output_path)
            )
            return QPixmap(output_path)
        except Exception as e:
            print(f"Mermaid渲染错误: {e}")
            
            # 只在第一次错误时提示用户
            if not hasattr(self, '_shown_chrome_prompt'):
                self._shown_chrome_prompt = True
                
                # 创建事件循环以便在异步环境中显示对话框
                loop = QEventLoop()
                chrome_selected = [False]
                
                # 显示对话框的函数
                def show_chrome_dialog():
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.setWindowTitle("Mermaid图表渲染失败")
                    msg.setText("无法启动浏览器来渲染Mermaid图表")
                    msg.setInformativeText("需要手动选择Chrome或Edge浏览器的位置\n\n"
                                        "这只影响Mermaid图表的渲染，其他功能不受影响。")
                    msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    msg.setDefaultButton(QMessageBox.StandardButton.Yes)
                    result = msg.exec()
                    
                    if result == QMessageBox.StandardButton.Yes:
                        path, _ = QFileDialog.getOpenFileName(
                            None, "选择Chrome或Edge浏览器", "", 
                            "浏览器 (*.exe)"
                        )
                        
                        if path and os.path.exists(path):
                            # 保存用户选择的路径
                            settings = QSettings("WallpaperTasks", "Application")
                            settings.setValue("chrome_path", path)
                            self.chrome_path = path
                            self.browser = None  # 重置以便下次使用新路径
                            chrome_selected[0] = True
                    
                    loop.quit()
                
                # 在主线程中显示对话框
                QApplication.instance().invokeMethod(show_chrome_dialog, Qt.ConnectionType.QueuedConnection)
                
                # 等待对话框完成
                loop.exec()
                
                # 如果用户选择了新的Chrome路径，重试渲染
                if chrome_selected[0]:
                    try:
                        asyncio.get_event_loop().run_until_complete(
                            self.render_mermaid_to_png(mermaid_code, output_path)
                        )
                        return QPixmap(output_path)
                    except Exception as retry_e:
                        print(f"重试渲染仍然失败: {retry_e}")
            
            # 返回错误图像
            return self._create_error_image("无法渲染Mermaid图表")
    
    def _create_error_image(self, message):
        """创建错误提示图像"""
        pixmap = QPixmap(400, 100)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制错误提示背景
        painter.setBrush(QColor(255, 0, 0, 40))
        painter.setPen(QColor(255, 0, 0, 160))
        painter.drawRect(0, 0, 399, 99)
        
        # 绘制错误消息
        painter.setPen(QColor(255, 255, 255))
        font = QFont("Microsoft YaHei", 10)
        painter.setFont(font)
        painter.drawText(QRect(10, 10, 380, 80), Qt.AlignmentFlag.AlignCenter, message)
        
        painter.end()
        return pixmap
    
    @staticmethod
    def extract_mermaid_blocks(md_text):
        """从Markdown文本中提取所有Mermaid代码块"""
        pattern = r"```mermaid\s*([\s\S]*?)\s*```"
        return re.findall(pattern, md_text)
    
    @staticmethod
    def replace_mermaid_blocks(md_text, replacements):
        """替换Markdown文本中的Mermaid代码块为占位符"""
        pattern = r"```mermaid\s*([\s\S]*?)\s*```"
        result = md_text
        for i, match in enumerate(re.finditer(pattern, md_text)):
            if i < len(replacements):
                placeholder = f"!![MERMAID_DIAGRAM_{i}]!!"
                result = result.replace(match.group(0), placeholder)
        return result

class MarkdownRenderer:
    """Markdown渲染器，将Markdown文本渲染为图像"""
    
    def __init__(self):
        # 确保有QApplication实例
        self.app = QApplication.instance()
        if not self.app:
            # 静默创建QApplication实例用于离屏渲染
            self.app = QApplication(sys.argv)
        
        # 创建文本文档用于渲染HTML
        self.document = QTextDocument()
        self.document.setDocumentMargin(0)  # 移除边距
        
        # 创建Mermaid渲染器
        self.mermaid_renderer = MermaidRenderer()
        
        # 自定义CSS样式 - 增加删除线支持
        self.css_style = """
            <style>
                * {
                    font-family: 'Microsoft YaHei', sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 0;
                }
                body {
                    color: white;
                    padding: 10px;
                    padding-right: 15px;  /* 避免文本太靠近右边缘 */
                }
                h1, h2, h3, h4, h5, h6 {
                    color: #e0e0ff;
                    margin-top: 0.5em;
                    margin-bottom: 0.3em;
                    font-weight: bold;
                }
                h1 { font-size: 1.6em; }
                h2 { font-size: 1.4em; }
                h3 { font-size: 1.2em; }
                strong { color: #ffffb0; }
                em { color: #b0ffff; }
                del { color: #ff9090; text-decoration: line-through; }
                ul, ol {
                    margin-left: 0.8em;
                    padding-left: 0.8em;
                }
                li {
                    margin: 0.2em 0;
                }
                code {
                    background-color: rgba(80, 80, 80, 0.3);
                    padding: 0.1em 0.3em;
                    border-radius: 3px;
                    font-family: Consolas, monospace;
                }
                blockquote {
                    border-left: 3px solid #aaa;
                    margin-left: 0.5em;
                    padding-left: 0.5em;
                    color: #cccccc;
                }
                a { color: #80c0ff; }
                img { max-width: 100%; }
                hr {
                    border: none;
                    border-top: 1px solid #555;
                    margin: 0.8em 0;
                }
                /* 隐藏所有滚动条 */
                ::-webkit-scrollbar {
                    display: none;
                    width: 0px;
                    height: 0px;
                }
                /* 添加删除线支持 */
                .del, del, s {
                    text-decoration: line-through;
                    color: #ff9090;
                }
                /* Mermaid图表容器 */
                .mermaid-container {
                    text-align: center;
                    margin: 10px 0;
                }
            </style>
        """
    
    def render_markdown(self, md_text, width=500, font_size=16, completed=False):
        """渲染Markdown为QPixmap图像"""
        # 如果任务已完成，使用暗色
        text_color = "#aaaaaa" if completed else "white"
        
        # 处理Mermaid图表
        mermaid_blocks = self.mermaid_renderer.extract_mermaid_blocks(md_text)
        if mermaid_blocks:
            # 处理包含Mermaid的Markdown
            return self._render_with_mermaid(md_text, mermaid_blocks, width, font_size, text_color, completed)
        
        # 转换Markdown为HTML - 添加扩展支持
        html = markdown.markdown(md_text, extensions=[
            'tables', 'fenced_code', 'extra', 'sane_lists', 'nl2br'
        ])
        
        # 包装HTML并应用样式，确保正确的字体比例
        html = f"""
        <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                {self.css_style}
            </head>
            <body style="color: {text_color};">
                {html}
            </body>
        </html>
        """
        
        # 设置文档和字体
        self.document.setHtml(html)
        
        # 设置正确的字体和字体大小
        font = QFont("Microsoft YaHei", font_size)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.document.setDefaultFont(font)
        
        # 设置文档大小，防止挤压
        self.document.setTextWidth(width - 20)  # 减去一些内边距，防止文本挤压
        
        # 计算实际高度
        doc_height = self.document.size().height()
        
        # 控制最大高度
        max_height = 500  # 防止内容过长
        actual_height = min(int(doc_height), max_height)
        
        # 创建透明背景的图像
        pixmap = QPixmap(width, actual_height)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # 设置渲染选项 - 确保正确的DPI和无滚动条
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        # 直接绘制文档内容，而不是渲染整个控件
        self.document.drawContents(painter)
        painter.end()
        
        return pixmap
    
    def _render_with_mermaid(self, md_text, mermaid_blocks, width, font_size, text_color, completed):
        """处理包含Mermaid图表的Markdown"""
        # 渲染所有Mermaid块
        mermaid_images = []
        for block in mermaid_blocks:
            try:
                pixmap = self.mermaid_renderer.render_mermaid(block)
                # 等比例缩放图表以适应宽度
                if pixmap.width() > width - 40:  # 留出边距
                    pixmap = pixmap.scaled(
                        width - 40, 
                        int(pixmap.height() * (width - 40) / pixmap.width()), 
                        Qt.AspectRatioMode.KeepAspectRatio, 
                        Qt.TransformationMode.SmoothTransformation
                    )
                mermaid_images.append(pixmap)
            except Exception as e:
                print(f"Mermaid渲染错误: {e}")
                # 为失败的图表添加一个占位符
                mermaid_images.append(None)
        
        # 替换Markdown中的Mermaid块为占位符
        md_with_placeholders = self.mermaid_renderer.replace_mermaid_blocks(md_text, mermaid_images)
        
        # 渲染不含Mermaid的Markdown
        html = markdown.markdown(md_with_placeholders, extensions=[
            'tables', 'fenced_code', 'extra', 'sane_lists', 'nl2br'
        ])
        
        # 将Mermaid占位符替换为图像HTML标签
        for i, pixmap in enumerate(mermaid_images):
            if pixmap:
                # 保存临时图像文件
                img_path = f"mermaid_temp_{i}.png"
                pixmap.save(img_path)
                # 替换占位符为图像标签
                html = html.replace(
                    f"!![MERMAID_DIAGRAM_{i}]!!", 
                    f'<div class="mermaid-container"><img src="{img_path}" alt="Mermaid Diagram"></div>'
                )
            else:
                # 替换为错误消息
                html = html.replace(
                    f"!![MERMAID_DIAGRAM_{i}]!!", 
                    '<div style="color:#ff6666;text-align:center;padding:10px;border:1px solid #ff6666;border-radius:5px;margin:10px 0;">'
                    '无法渲染Mermaid图表</div>'
                )
        
        # 包装HTML并应用样式
        html = f"""
        <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                {self.css_style}
            </head>
            <body style="color: {text_color};">
                {html}
            </body>
        </html>
        """
        
        # 设置文档和字体
        self.document.setHtml(html)
        
        # 设置正确的字体和字体大小
        font = QFont("Microsoft YaHei", font_size)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.document.setDefaultFont(font)
        
        # 设置文档大小
        self.document.setTextWidth(width - 20)
        
        # 计算实际高度
        doc_height = self.document.size().height()
        
        # 控制最大高度，但为Mermaid图表留出更多空间
        max_height = 600  # 增加最大高度以容纳图表
        actual_height = min(int(doc_height), max_height)
        
        # 创建透明背景的图像
        pixmap = QPixmap(width, actual_height)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # 设置渲染选项
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        # 绘制文档内容
        self.document.drawContents(painter)
        painter.end()
        
        # 清理临时文件
        for i in range(len(mermaid_images)):
            try:
                os.remove(f"mermaid_temp_{i}.png")
            except:
                pass
        
        return pixmap
    
    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'mermaid_renderer'):
            self.mermaid_renderer.close()