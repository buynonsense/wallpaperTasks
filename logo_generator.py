from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QPen, QFont
from PyQt6.QtCore import Qt, QRect, QSize

def create_logo():
    """创建应用 Logo"""
    # 创建 64x64 的图标
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # 绘制圆形背景
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(QColor(70, 130, 220)))
    painter.drawEllipse(4, 4, 56, 56)
    
    # 绘制任务清单图标
    painter.setPen(QPen(QColor(255, 255, 255), 2))
    painter.setBrush(QBrush(QColor(240, 240, 250)))
    painter.drawRoundedRect(18, 15, 28, 34, 3, 3)
    
    # 绘制任务列表线条
    painter.setPen(QPen(QColor(70, 130, 220), 1))
    painter.drawLine(22, 24, 42, 24)
    painter.drawLine(22, 32, 42, 32)
    painter.drawLine(22, 40, 42, 40)
    
    # 绘制复选框
    painter.setPen(QPen(QColor(50, 180, 100), 2))
    painter.drawLine(25, 32, 28, 36)
    painter.drawLine(28, 36, 34, 28)
    
    painter.end()
    
    return QIcon(pixmap)