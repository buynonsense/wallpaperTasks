import os
import sys
import markdown
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPixmap, QTextDocument, QFont

# 尝试导入MermaidRenderer
MERMAID_SUPPORT = False
try:
    # 确保当前目录在搜索路径中
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
    
    # 尝试导入
    from mermaid_renderer import MermaidRenderer
    MERMAID_SUPPORT = True
    print("Mermaid渲染器导入成功")
except ImportError as e:
    print(f"导入MermaidRenderer失败: {e}")
    MERMAID_SUPPORT = False
    print("未能导入MermaidRenderer，Mermaid图表将不可用")

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
        
        # 初始化Mermaid渲染器
        if (MERMAID_SUPPORT):
            try:
                self.mermaid_renderer = MermaidRenderer()
                print("Mermaid渲染器初始化成功")
            except Exception as e:
                print(f"Mermaid渲染器初始化失败: {e}")
                self.mermaid_renderer = None
        else:
            self.mermaid_renderer = None
        
        # 自定义CSS样式
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
                    padding-right: 15px;
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
                
                /* 增强列表样式 */
                ul, ol {
                    margin-left: 0.8em;
                    padding-left: 1.5em;
                    margin-bottom: 0.8em;
                }
                
                /* 有序列表样式 */
                ol {
                    list-style-type: decimal;
                    list-style-position: outside;
                }
                
                /* 嵌套的有序列表使用字母 */
                ol ol {
                    list-style-type: lower-alpha;
                    margin-left: 0.5em;
                }
                
                /* 三级嵌套用小写罗马数字 */
                ol ol ol {
                    list-style-type: lower-roman;
                }
                
                /* 无序列表样式 */
                ul {
                    list-style-type: disc;
                }
                
                ul ul {
                    list-style-type: circle;
                }
                
                ul ul ul {
                    list-style-type: square;
                }
                
                /* 列表项通用样式 */
                li {
                    margin: 0.3em 0;
                    padding-left: 0.2em;
                }
                
                /* 嵌套列表项增加缩进 */
                li li {
                    margin-left: 0.5em;
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
                del, s {
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
        
        import re
        # 替换删除线语法
        md_text = re.sub(r'~~(.*?)~~', r'<del>\1</del>', md_text)
        
        # 预处理任务列表语法
        md_text = re.sub(r'\[ \]', r'&#9744;', md_text)
        md_text = re.sub(r'\[x\]', r'&#9745;', md_text, flags=re.IGNORECASE)
        
        # 处理嵌套列表和字母列表
        # 1. 确保所有缩进的列表项保留缩进
        lines = md_text.split('\n')
        for i in range(len(lines)):
            # 处理缩进的有序子列表
            if re.match(r'\s+\d+\.\s', lines[i]):
                indent = len(re.match(r'(\s+)', lines[i]).group(1))
                lines[i] = '    ' * (indent // 4) + lines[i].strip()
            
            # 处理字母序号列表 (a. b. c.)
            if re.match(r'\s*[a-z]\.\s', lines[i], re.IGNORECASE):
                # 将字母列表转换为HTML列表项
                letter = re.match(r'\s*([a-z])\.\s', lines[i], re.IGNORECASE).group(1)
                content = re.sub(r'\s*[a-z]\.\s', '', lines[i], flags=re.IGNORECASE)
                # 修复方式 1：使用双引号包裹整个字符串
                lines[i] = f"<li style=\"list-style-type: lower-alpha;\">{content}</li>"
                # 或修复方式 2：使用转义字符
                # lines[i] = f"<li style=\'list-style-type: lower-alpha;\'>{content}</li>"
        
        md_text = '\n'.join(lines)
        
        # 若包含Mermaid则单独处理
        mermaid_blocks = None
        if self.mermaid_renderer:
            try:
                mermaid_blocks = self.mermaid_renderer.extract_mermaid_blocks(md_text)
                if (mermaid_blocks):
                    print(f"检测到{len(mermaid_blocks)}个Mermaid图表")
                    return self._render_with_mermaid(md_text, mermaid_blocks, width, font_size, text_color, completed)
            except Exception as e:
                print(f"提取Mermaid代码块失败: {e}")
        
        # 使用extra扩展转换Markdown为HTML
        html = markdown.markdown(md_text, extensions=[
            'tables', 'fenced_code', 'extra', 'nl2br', 'sane_lists'
        ])
        
        # 修正嵌套列表和字母列表的CSS
        html = f"""
        <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                {self.css_style}
                <style>
                    /* 字母序号列表样式 */
                    ol ol {{
                        list-style-type: lower-alpha;
                    }}
                    /* 墛强嵌套列表样式 */
                    li {{
                        margin: 0.3em 0;
                    }}
                    li li {{
                        margin-left: 1em;
                    }}
                </style>
            </head>
            <body style="color: {text_color};">
                {html}
            </body>
        </html>
        """
        
        # 设置文档和字体
        self.document.setHtml(html)
        font = QFont("Microsoft YaHei", font_size)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.document.setDefaultFont(font)
        self.document.setTextWidth(width - 20)
        
        doc_height = self.document.size().height()
        max_height = 500
        actual_height = min(int(doc_height), max_height)
        
        pixmap = QPixmap(width, actual_height)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        self.document.drawContents(painter)
        painter.end()
        
        return pixmap
    
    def _render_with_mermaid(self, md_text, mermaid_blocks, width, font_size, text_color, completed):
        """处理包含Mermaid图表的Markdown"""
        if not self.mermaid_renderer:
            print("Mermaid渲染器不可用，返回普通渲染")
            return self.render_markdown(md_text, width, font_size, completed)
            
        # 渲染所有Mermaid块
        mermaid_images = []
        for block in mermaid_blocks:
            try:
                print(f"渲染Mermaid代码块: {block[:30]}...")
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
            'tables', 'fenced_code', 'extra', 'nl2br'
        ])
        
        # 将Mermaid占位符替换为图像HTML标签
        for i, pixmap in enumerate(mermaid_images):
            if (pixmap):
                # 保存临时图像文件
                img_path = os.path.join(self.mermaid_renderer.temp_dir, f"mermaid_temp_{i}.png")
                pixmap.save(img_path)
                # 替换占位符为图像标签 - 确保HTML字符串格式正确
                html = html.replace(
                    f"!![MERMAID_DIAGRAM_{i}]!!", 
                    f'<div class="mermaid-container"><img src="{img_path}" alt="Mermaid Diagram"></div>'
                )
            else:
                # 替换为错误消息 - 确保字符串格式正确，避免Python误解析样式属性
                error_html = '<div style="color:#ff6666;text-align:center;padding:10px;border:1px solid #ff6666;border-radius:5px;margin:10px 0;">无法渲染Mermaid图表</div>'
                html = html.replace(f"!![MERMAID_DIAGRAM_{i}]!!", error_html)
        
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
        max_height = 600  # 墛加最大高度以容纳图表
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
        
        return pixmap
    
    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'mermaid_renderer') and self.mermaid_renderer:
            try:
                self.mermaid_renderer.close()
                print("已关闭Mermaid渲染器")
            except Exception as e:
                print(f"关闭Mermaid渲染器出错: {e}")