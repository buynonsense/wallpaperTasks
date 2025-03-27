import os
import asyncio
import tempfile
import re
from pyppeteer import launch
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QTextBrowser, QApplication, QGraphicsOpacityEffect
from PyQt6.QtCore import QSize, Qt, QSizeF, QMarginsF
from PyQt6.QtGui import QPainter, QColor, QPixmap, QTextDocument, QPageSize, QFont
import markdown
import sys
import re
# from mermaid_renderer import MermaidRenderer

class MermaidRenderer:
    """Mermaid图表渲染器，使用pyppeteer/puppeteer将Mermaid语法转换为图像"""
    
    def __init__(self):
        self.temp_dir = os.path.join(tempfile.gettempdir(), "wallpaper_tasks_mermaid")
        os.makedirs(self.temp_dir, exist_ok=True)
        self.browser = None
        
    async def _get_browser(self):
        """懒加载浏览器实例"""
        if self.browser is None:
            chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"  # 根据实际情况修改路径
            self.browser = await launch(
                headless=True,
                executablePath=chrome_path,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
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
        
        # 否则渲染并返回
        asyncio.get_event_loop().run_until_complete(
            self.render_mermaid_to_png(mermaid_code, output_path)
        )
        return QPixmap(output_path)
    
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