from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen, QMouseEvent
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal, QSize

class WallpaperPreview(QWidget):
    """壁纸预览控件，用于调整任务清单位置"""
    # 位置变化信号
    positionChanged = pyqtSignal(float, float, float, float)  # 相对坐标 x1, y1, x2, y2 (0-1范围)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 200)
        
        # 布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 预览标签
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #1e1e1e; border-radius: 8px;")
        layout.addWidget(self.preview_label)
        
        # 壁纸图像
        self.wallpaper = None
        self.scaled_wallpaper = None
        
        # 任务区域位置 (相对坐标 0-1)
        self.task_area = [0.5, 0.15, 0.95, 0.95]
        
        # 拖动状态
        self.dragging = False
        self.drag_start = QPoint()
        self.drag_area = None  # 当前拖动的是哪个部分 (whole, left, top, right, bottom)
        
        # 启用鼠标跟踪
        self.setMouseTracking(True)
    
    def set_wallpaper(self, wallpaper_path):
        """设置壁纸图像"""
        try:
            self.wallpaper = QPixmap(wallpaper_path)
            self.update_preview()
        except Exception as e:
            print(f"加载壁纸预览失败: {e}")
            # 创建默认背景
            self.wallpaper = QPixmap(1920, 1080)
            self.wallpaper.fill(QColor(30, 30, 40))
            self.update_preview()
    
    def set_task_area(self, x1, y1, x2, y2):
        """设置任务区域位置 (相对坐标 0-1)"""
        self.task_area = [x1, y1, x2, y2]
        self.update_preview()
        
    def update_preview(self):
        """更新预览图像"""
        if not self.wallpaper:
            return
            
        # 计算预览大小
        preview_size = self.preview_label.size()
        if preview_size.width() <= 0 or preview_size.height() <= 0:
            preview_size = QSize(400, 200)
            
        # 按比例缩放壁纸
        self.scaled_wallpaper = self.wallpaper.scaled(
            preview_size, 
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        # 创建预览图像
        preview = QPixmap(self.scaled_wallpaper.size())
        preview.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(preview)
        painter.drawPixmap(0, 0, self.scaled_wallpaper)
        
        # 绘制任务区域
        scaled_rect = self._get_scaled_task_rect()
        painter.setPen(QPen(QColor(50, 150, 255), 2, Qt.PenStyle.DashLine))
        painter.setBrush(QColor(50, 150, 255, 40))
        painter.drawRect(scaled_rect)
        
        # 绘制拖动手柄
        handle_size = 8
        painter.setPen(QPen(QColor(50, 150, 255), 1))
        painter.setBrush(QColor(50, 150, 255))
        
        # 四个角落
        painter.drawRect(scaled_rect.left() - handle_size//2, scaled_rect.top() - handle_size//2, handle_size, handle_size)
        painter.drawRect(scaled_rect.right() - handle_size//2, scaled_rect.top() - handle_size//2, handle_size, handle_size)
        painter.drawRect(scaled_rect.left() - handle_size//2, scaled_rect.bottom() - handle_size//2, handle_size, handle_size)
        painter.drawRect(scaled_rect.right() - handle_size//2, scaled_rect.bottom() - handle_size//2, handle_size, handle_size)
        
        painter.end()
        
        # 设置预览图像
        self.preview_label.setPixmap(preview)
    
    def _get_scaled_task_rect(self):
        """获取缩放后的任务区域矩形"""
        if not self.scaled_wallpaper:
            return QRect(0, 0, 0, 0)
        
        try:
            # 尝试计算任务区域矩形
            x1 = int(float(self.task_area[0]) * self.scaled_wallpaper.width())
            y1 = int(float(self.task_area[1]) * self.scaled_wallpaper.height())
            x2 = int(float(self.task_area[2]) * self.scaled_wallpaper.width())
            y2 = int(float(self.task_area[3]) * self.scaled_wallpaper.height())
            
            # 确保有效的矩形（至少1x1像素）
            if x2 <= x1:
                x2 = x1 + 10
            if y2 <= y1:
                y2 = y1 + 10
                
            return QRect(x1, y1, x2-x1, y2-y1)
            
        except Exception as e:
            print(f"计算任务区域矩形出错: {e}")
            # 返回默认矩形
            w = self.scaled_wallpaper.width()
            h = self.scaled_wallpaper.height()
            return QRect(int(w * 0.5), int(h * 0.15), int(w * 0.45), int(h * 0.8))
    
    def _get_drag_area(self, pos):
        """确定点击的是任务区域的哪个部分"""
        if not self.scaled_wallpaper:
            return None
            
        rect = self._get_scaled_task_rect()
        handle_size = 15  # 拖动手柄大小（稍大以便点击）
        
        # 检查四个角落
        if abs(pos.x() - rect.left()) < handle_size and abs(pos.y() - rect.top()) < handle_size:
            return "top-left"
        if abs(pos.x() - rect.right()) < handle_size and abs(pos.y() - rect.top()) < handle_size:
            return "top-right"
        if abs(pos.x() - rect.left()) < handle_size and abs(pos.y() - rect.bottom()) < handle_size:
            return "bottom-left"
        if abs(pos.x() - rect.right()) < handle_size and abs(pos.y() - rect.bottom()) < handle_size:
            return "bottom-right"
        
        # 检查四条边
        if abs(pos.x() - rect.left()) < handle_size and rect.top() < pos.y() < rect.bottom():
            return "left"
        if abs(pos.x() - rect.right()) < handle_size and rect.top() < pos.y() < rect.bottom():
            return "right"
        if abs(pos.y() - rect.top()) < handle_size and rect.left() < pos.x() < rect.right():
            return "top"
        if abs(pos.y() - rect.bottom()) < handle_size and rect.left() < pos.x() < rect.right():
            return "bottom"
        
        # 检查整个区域
        if rect.contains(pos):
            return "whole"
            
        return None
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 获取 QLabel 中的相对位置
            label_pos = self.preview_label.mapFrom(self, event.position().toPoint())
            
            # 确认位置在标签内
            if self.preview_label.rect().contains(label_pos):
                self.drag_area = self._get_drag_area(label_pos)
                if self.drag_area:
                    self.dragging = True
                    self.drag_start = label_pos
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        # 获取 QLabel 中的相对位置
        label_pos = self.preview_label.mapFrom(self, event.position().toPoint())
        
        # 设置默认光标
        cursor_shape = Qt.CursorShape.ArrowCursor
        
        # 更新光标形状
        if self.preview_label.rect().contains(label_pos):
            drag_area = self._get_drag_area(label_pos)
            if drag_area in ["left", "right"]:
                cursor_shape = Qt.CursorShape.SizeHorCursor
            elif drag_area in ["top", "bottom"]:
                cursor_shape = Qt.CursorShape.SizeVerCursor
            elif drag_area in ["top-left", "bottom-right"]:
                cursor_shape = Qt.CursorShape.SizeFDiagCursor
            elif drag_area in ["top-right", "bottom-left"]:
                cursor_shape = Qt.CursorShape.SizeBDiagCursor
            elif drag_area == "whole":
                cursor_shape = Qt.CursorShape.SizeAllCursor
        
        self.setCursor(cursor_shape)
        
        # 处理拖动
        if not self.dragging or not self.scaled_wallpaper:
            return
            
        # 处理拖动移动
        pos = self.preview_label.mapFrom(self, event.position().toPoint())
        dx = pos.x() - self.drag_start.x()
        dy = pos.y() - self.drag_start.y()
        
        # 计算相对移动距离
        rel_dx = dx / self.scaled_wallpaper.width()
        rel_dy = dy / self.scaled_wallpaper.height()
        
        x1, y1, x2, y2 = self.task_area.copy()
        
        # 更新任务区域位置
        if self.drag_area == "whole":
            # 移动整个区域
            x1 += rel_dx
            y1 += rel_dy
            x2 += rel_dx
            y2 += rel_dy
        elif self.drag_area == "left":
            x1 += rel_dx
        elif self.drag_area == "right":
            x2 += rel_dx
        elif self.drag_area == "top":
            y1 += rel_dy
        elif self.drag_area == "bottom":
            y2 += rel_dy
        elif self.drag_area == "top-left":
            x1 += rel_dx
            y1 += rel_dy
        elif self.drag_area == "top-right":
            x2 += rel_dx
            y1 += rel_dy
        elif self.drag_area == "bottom-left":
            x1 += rel_dx
            y2 += rel_dy
        elif self.drag_area == "bottom-right":
            x2 += rel_dx
            y2 += rel_dy
        
        # 限制在0-1范围内
        x1 = max(0, min(x1, 0.95))
        y1 = max(0, min(y1, 0.95))
        x2 = max(x1 + 0.05, min(x2, 1.0))
        y2 = max(y1 + 0.05, min(y2, 1.0))
        
        # 更新任务区域
        self.task_area = [x1, y1, x2, y2]
        self.update_preview()
        
        # 发射位置变化信号
        self.positionChanged.emit(x1, y1, x2, y2)
        
        # 更新拖动起点
        self.drag_start = pos
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.drag_area = None
    
    def resizeEvent(self, event):
        """窗口大小变化事件"""
        super().resizeEvent(event)
        self.update_preview()