from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QSlider, QGroupBox, QComboBox, QLineEdit, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QIcon

import os

from wallpaper_preview import WallpaperPreview

class WallpaperSettingsDialog(QDialog):
    """壁纸设置对话框"""
    def __init__(self, wallpaper_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("壁纸设置")
        self.resize(700, 500)
        
        # 保存对壁纸管理器的引用
        self.wallpaper_manager = wallpaper_manager
        
        # 加载设置
        self.settings = QSettings("WallpaperTasks", "Application")
        self.font_size = self.settings.value("font_size", 24, type=int)
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 预览面板
        preview_group = QGroupBox("任务位置预览")
        preview_layout = QVBoxLayout(preview_group)
        
        # 提示标签
        hint_label = QLabel("拖动蓝色区域调整任务清单在壁纸上的位置和大小")
        hint_label.setStyleSheet("color: #666;")
        preview_layout.addWidget(hint_label)
        
        # 预览控件
        self.preview = WallpaperPreview()
        self.preview.setMinimumHeight(300)  # 确保足够高度
        preview_layout.addWidget(self.preview)
        
        # 加载当前壁纸
        if self.wallpaper_manager.original_wallpaper:
            self.preview.set_wallpaper(self.wallpaper_manager.original_wallpaper)
        
        # 从设置中读取位置信息
        try:
            # 尝试读取位置信息，如果格式不正确则使用默认值
            position = self.settings.value("task_position", [0.5, 0.15, 0.95, 0.95])
            
            # 验证位置数据格式是否正确
            if not isinstance(position, list) or len(position) != 4:
                print("位置数据格式不正确，使用默认值")
                position = [0.5, 0.15, 0.95, 0.95]
            
            # 确保所有值都是浮点数
            position = [float(pos) if isinstance(pos, (int, float, str)) and 0 <= float(pos) <= 1 else 0.5 for pos in position]
            
        except Exception as e:
            print(f"读取位置设置出错: {e}")
            position = [0.5, 0.15, 0.95, 0.95]  # 使用默认值
        
        self.preview.set_task_area(*position)
        
        # 连接信号
        self.preview.positionChanged.connect(self.on_position_changed)
        
        layout.addWidget(preview_group)
        
        # 字体大小滑块
        font_group = QGroupBox("字体大小")
        font_layout = QHBoxLayout(font_group)
        
        font_layout.addWidget(QLabel("小"), 0)
        
        self.font_slider = QSlider(Qt.Orientation.Horizontal)
        self.font_slider.setMinimum(12)
        self.font_slider.setMaximum(24)
        self.font_slider.setValue(min(self.font_size, 24))
        self.font_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.font_slider.setTickInterval(2)
        font_layout.addWidget(self.font_slider, 1)
        
        font_layout.addWidget(QLabel("大"), 0)
        
        layout.addWidget(font_group)
        
        # 添加Mermaid图表设置区域
        mermaid_group = QGroupBox("Mermaid图表设置")
        mermaid_layout = QVBoxLayout(mermaid_group)

        # 添加Chrome路径设置
        chrome_layout = QHBoxLayout()
        chrome_layout.addWidget(QLabel("Chrome浏览器路径:"))

        self.chrome_path_edit = QLineEdit()
        settings = QSettings("WallpaperTasks", "Application")
        chrome_path = settings.value("chrome_path", "")
        self.chrome_path_edit.setText(chrome_path)
        self.chrome_path_edit.setReadOnly(True)
        chrome_layout.addWidget(self.chrome_path_edit, 1)

        self.browse_chrome_button = QPushButton("浏览...")
        self.browse_chrome_button.clicked.connect(self.browse_chrome_path)
        chrome_layout.addWidget(self.browse_chrome_button)

        mermaid_layout.addLayout(chrome_layout)

        # 添加说明文本
        info_label = QLabel("Mermaid图表渲染需要Chrome或Edge浏览器。设置此路径可确保正确渲染图表，"
                          "但不会影响程序的其他功能。")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-size: 12px;")
        mermaid_layout.addWidget(info_label)

        layout.addWidget(mermaid_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.refresh_button = QPushButton("应用更改并刷新壁纸")
        self.refresh_button.setStyleSheet("""
            background-color: #2d8cf0;
            color: white;
            font-weight: bold;
            padding: 10px 16px;
        """)
        
        self.cancel_button = QPushButton("取消")
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.refresh_button)
        
        layout.addLayout(button_layout)
        
        # 连接信号
        self.refresh_button.clicked.connect(self.apply_settings)
        self.cancel_button.clicked.connect(self.reject)
        self.font_slider.valueChanged.connect(self.on_font_size_changed)
    
    def on_position_changed(self, x1, y1, x2, y2):
        """位置变化处理"""
        # 暂存新位置
        self.new_position = [x1, y1, x2, y2]
    
    def on_font_size_changed(self, size):
        """字体大小变化处理"""
        # 暂存新字体大小
        self.new_font_size = size
    
    def apply_settings(self):
        """应用设置并刷新壁纸"""
        # 保存位置
        if hasattr(self, 'new_position'):
            self.settings.setValue("task_position", self.new_position)
            self.wallpaper_manager.set_task_area(*self.new_position)
        
        # 保存字体大小
        if hasattr(self, 'new_font_size'):
            self.settings.setValue("font_size", self.new_font_size)
            self.wallpaper_manager.set_font_size(self.new_font_size)
        
        # 刷新壁纸
        self.wallpaper_manager.refresh_wallpaper()
        
        # 关闭对话框
        self.accept()
    
    def browse_chrome_path(self):
        """浏览并设置Chrome浏览器路径"""
        path, _ = QFileDialog.getOpenFileName(
            self, "选择Chrome或Edge浏览器", "", "浏览器 (*.exe)"
        )
        if path and os.path.exists(path):
            self.chrome_path_edit.setText(path)
            settings = QSettings("WallpaperTasks", "Application")
            settings.setValue("chrome_path", path)
            
            # 通知渲染器chrome路径已更改
            if hasattr(self.wallpaper_manager, 'md_renderer') and \
               hasattr(self.wallpaper_manager.md_renderer, 'mermaid_renderer'):
                renderer = self.wallpaper_manager.md_renderer.mermaid_renderer
                renderer.chrome_path = path
                renderer.browser = None  # 重置浏览器实例
                if hasattr(renderer, '_browser_failed'):
                    delattr(renderer, '_browser_failed')
                if hasattr(renderer, '_shown_chrome_prompt'):
                    delattr(renderer, '_shown_chrome_prompt')
            
            QMessageBox.information(self, "设置已保存", 
                                  "Chrome路径已更新。下次渲染Mermaid图表时将使用新路径。")