from PyQt6.QtWidgets import QTextBrowser, QApplication, QGraphicsOpacityEffect
from PyQt6.QtCore import QSize, Qt, QSizeF, QMarginsF
from PyQt6.QtGui import QPainter, QColor, QPixmap, QTextDocument, QPageSize, QFont
import markdown
import sys

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
        
        # 自定义CSS样式 - 修复字体比例问题
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
            </style>
        """
    
    def render_markdown(self, md_text, width=500, font_size=16, completed=False):
        """渲染Markdown为QPixmap图像"""
        # 如果任务已完成，使用暗色
        text_color = "#aaaaaa" if completed else "white"
        
        # 转换Markdown为HTML
        html = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])
        
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