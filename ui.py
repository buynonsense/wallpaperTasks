import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QListWidget, QListWidgetItem, QDialog, 
                            QTextEdit, QLabel, QFileDialog, QMessageBox, QMenu,
                            QSystemTrayIcon, QApplication, QSlider, QGroupBox, QStyle,
                            QComboBox)
from PyQt6.QtCore import Qt, QSize, QSettings
from PyQt6.QtGui import QIcon, QAction

from task_manager import TaskManager
from wallpaper_manager import WallpaperManager
from logo_generator import create_logo

class MarkdownEditor(QDialog):
    """Markdown编辑对话框"""
    def __init__(self, content="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("编辑任务")
        self.resize(600, 400)
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 添加说明标签
        help_text = """支持Markdown语法：
# 标题
**粗体**
*斜体*
- 列表项
1. 有序列表
[链接](https://example.com)"""
        
        help_label = QLabel(help_text)
        layout.addWidget(help_label)
        
        # 编辑器
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("在这里输入任务内容...")
        self.editor.setText(content)
        layout.addWidget(self.editor)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("保存")
        self.cancel_button = QPushButton("取消")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        # 连接信号
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
    
    def get_content(self):
        """获取编辑后的内容"""
        return self.editor.toPlainText()

class MainWindow(QMainWindow):
    """主窗口"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("桌面壁纸任务清单")
        self.resize(800, 600)  # 更大的窗口尺寸
        
        # 设置应用图标
        app_icon = create_logo()
        self.setWindowIcon(app_icon)
        
        # 加载设置
        self.settings = QSettings("WallpaperTasks", "Application")
        self.font_size = self.settings.value("font_size", 24, type=int)
        
        # 初始化管理器
        self.task_manager = TaskManager()
        self.wallpaper_manager = WallpaperManager(self.task_manager)
        self.wallpaper_manager.set_font_size(self.font_size)
        
        # 初始刷新壁纸
        self.wallpaper_manager.refresh_wallpaper()
        
        # 设置整体样式 - 现代年轻化风格
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QGroupBox {
                background-color: white;
                border: 1px solid #eaeaea;
                border-radius: 8px;
                margin-top: 14px;
                font-weight: bold;
                font-size: 14px;
                padding: 8px;
                color: #333;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #444;
            }
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #eaeaea;
                padding: 8px 16px;
                border-radius: 6px;
                color: #555;
                font-weight: 500;
                font-size: 13px;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: #f0f7ff;
                color: #2d8cf0;
                border-color: #d4e8ff;
            }
            QPushButton:pressed {
                background-color: #e0f0ff;
                border-color: #2d8cf0;
                color: #2d8cf0;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #eaeaea;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                selection-background-color: #f0f7ff;
            }
            QLabel {
                color: #333;
                font-size: 14px;
            }
            QSlider::handle:horizontal {
                background: #2d8cf0;
                border: 1px solid #2d8cf0;
                width: 16px;
                height: 16px;
                margin: -7px 0;
                border-radius: 8px;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #e0e0e0;
                margin: 0 4px;
                border-radius: 3px;
            }
            QSlider::add-page:horizontal {
                background: #e0e0e0;
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: #2d8cf0;
                border-radius: 3px;
            }
            QStatusBar {
                color: #666;
                font-size: 13px;
                padding: 4px 6px;
            }
        """)
        
        # 设置中心窗口
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 顶部信息面板
        info_panel = QGroupBox("任务壁纸")
        info_layout = QVBoxLayout(info_panel)
        
        info_label = QLabel("在桌面壁纸上显示您的任务清单")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("font-size: 16px; color: #333; margin: 8px 0; font-weight: bold;")
        info_layout.addWidget(info_label)
        
        main_layout.addWidget(info_panel)
        
        # 任务列表面板
        tasks_panel = QGroupBox("任务列表")
        tasks_layout = QVBoxLayout(tasks_panel)
        
        # 任务列表
        self.task_list = QListWidget()
        self.task_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.task_list.customContextMenuRequested.connect(self.show_context_menu)
        self.task_list.setAlternatingRowColors(True)
        self.task_list.setStyleSheet("""
            QListWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #f0f0f0;
                font-size: 15px;
            }
            QListWidget::item:selected {
                background-color: #f0f7ff;
                color: #2d8cf0;
                border-radius: 6px;
            }
            QListWidget::item:hover {
                background-color: #fafbfc;
            }
            QListWidget::item:alternate {
                background-color: #fcfcfc;
            }
        """)
        tasks_layout.addWidget(self.task_list)
        
        # 任务操作按钮区
        task_buttons_layout = QHBoxLayout()
        
        # 添加任务按钮 - 蓝色
        self.add_button = QPushButton("添加任务")
        self.add_button.setIcon(QIcon.fromTheme("list-add", self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogNewFolder)))
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #2d8cf0; 
                color: white; 
                border-color: #2d8cf0;
                font-weight: bold;
                padding: 10px 16px;
            }
            QPushButton:hover {
                background-color: #54a8ff;
                border-color: #54a8ff;
            }
            QPushButton:pressed {
                background-color: #2a80d8;
                border-color: #2a80d8;
            }
        """)
        
        # 编辑任务保持默认样式，已有悬停和按下效果
        self.edit_button = QPushButton("编辑任务")
        self.edit_button.setIcon(QIcon.fromTheme("document-edit", self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView)))
        
        # 删除任务按钮 - 红色
        self.delete_button = QPushButton("删除任务")
        self.delete_button.setIcon(QIcon.fromTheme("edit-delete", self.style().standardIcon(QStyle.StandardPixmap.SP_DialogDiscardButton)))
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #f56c6c; 
                color: white; 
                border-color: #f56c6c;
            }
            QPushButton:hover {
                background-color: #ff8585;
                border-color: #ff8585;
            }
            QPushButton:pressed {
                background-color: #e05858;
                border-color: #e05858;
            }
        """)
        
        # 完成/未完成按钮 - 绿色
        self.complete_button = QPushButton("完成/未完成")
        self.complete_button.setIcon(QIcon.fromTheme("emblem-default", self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton)))
        self.complete_button.setStyleSheet("""
            QPushButton {
                background-color: #67c23a; 
                color: white; 
                border-color: #67c23a;
            }
            QPushButton:hover {
                background-color: #7ed321;
                border-color: #7ed321;
            }
            QPushButton:pressed {
                background-color: #5daf34;
                border-color: #5daf34;
            }
        """)
        
        task_buttons_layout.addWidget(self.add_button)
        task_buttons_layout.addWidget(self.edit_button)
        task_buttons_layout.addWidget(self.delete_button)
        task_buttons_layout.addWidget(self.complete_button)
        
        tasks_layout.addLayout(task_buttons_layout)
        main_layout.addWidget(tasks_panel, 1)  # 让任务列表区域占据更多空间
        
        # 设置面板
        settings_panel = QGroupBox("壁纸设置")
        settings_layout = QVBoxLayout(settings_panel)
        
        # 字体大小设置
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("壁纸字体大小:"))
        font_layout.addWidget(QLabel("小"), 0)
        
        self.font_slider = QSlider(Qt.Orientation.Horizontal)
        self.font_slider.setMinimum(16)
        self.font_slider.setMaximum(40)
        self.font_slider.setValue(self.font_size)
        self.font_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.font_slider.setTickInterval(4)
        font_layout.addWidget(self.font_slider, 1)
        
        font_layout.addWidget(QLabel("大"), 0)
        settings_layout.addLayout(font_layout)
        
        # 壁纸控制按钮
        wallpaper_buttons = QHBoxLayout()
        
        self.import_button = QPushButton("导入任务")
        self.import_button.setIcon(QIcon.fromTheme("document-open", self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton)))
        
        self.export_button = QPushButton("导出任务")
        self.export_button.setIcon(QIcon.fromTheme("document-save", self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton)))
        
        wallpaper_buttons.addWidget(self.import_button)
        wallpaper_buttons.addWidget(self.export_button)
        wallpaper_buttons.addStretch(1)
        
        self.refresh_button = QPushButton("刷新壁纸")
        self.refresh_button.setIcon(QIcon.fromTheme("view-refresh", self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload)))
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #2d8cf0;
                color: white;
                border-color: #2d8cf0;
                font-weight: bold;
                padding: 10px 16px;
            }
            QPushButton:hover {
                background-color: #54a8ff;
                border-color: #54a8ff;
            }
            QPushButton:pressed {
                background-color: #2a80d8;
                border-color: #2a80d8;
            }
        """)
        
        self.restore_button = QPushButton("恢复原壁纸")
        self.restore_button.setIcon(QIcon.fromTheme("edit-undo", self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton)))
        
        wallpaper_buttons.addWidget(self.refresh_button)
        wallpaper_buttons.addWidget(self.restore_button)
        
        settings_layout.addLayout(wallpaper_buttons)
        main_layout.addWidget(settings_panel)
        
        # 连接信号
        self.add_button.clicked.connect(self.add_task)
        self.edit_button.clicked.connect(self.edit_task)
        self.delete_button.clicked.connect(self.delete_task)
        self.complete_button.clicked.connect(self.toggle_task_completion)
        self.import_button.clicked.connect(self.import_tasks)
        self.export_button.clicked.connect(self.export_tasks)
        self.refresh_button.clicked.connect(self.refresh_wallpaper)
        self.restore_button.clicked.connect(self.restore_wallpaper)
        self.font_slider.valueChanged.connect(self.on_font_size_changed)
        
        # 创建系统托盘
        self.setup_tray_icon()
        
        # 加载任务
        self.load_tasks()
        
        # 设置状态栏
        self.statusBar().showMessage("程序已启动", 3000)
        self.statusBar().setStyleSheet("color: #666; padding: 2px 5px;")

    def setup_tray_icon(self):
        """设置系统托盘图标"""
        # 创建并显示系统托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        
        # 使用自定义图标
        self.tray_icon.setIcon(create_logo())
        
        # 创建托盘菜单
        tray_menu = QMenu()
        
        # 添加菜单项
        show_action = QAction("显示窗口", self)
        show_action.triggered.connect(self.show)
        
        refresh_action = QAction("刷新壁纸", self)
        refresh_action.triggered.connect(self.refresh_wallpaper)
        
        restore_action = QAction("恢复原壁纸", self)
        restore_action.triggered.connect(self.restore_wallpaper)
        
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close_application)
        
        # 添加到菜单
        tray_menu.addAction(show_action)
        tray_menu.addAction(refresh_action)
        tray_menu.addAction(restore_action)
        tray_menu.addSeparator()
        tray_menu.addAction(exit_action)
        
        # 设置菜单
        self.tray_icon.setContextMenu(tray_menu)
        
        # 显示托盘图标
        self.tray_icon.show()
        
        # 连接信号
        self.tray_icon.activated.connect(self.tray_icon_activated)
    
    def tray_icon_activated(self, reason):
        """托盘图标被激活时的处理"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
            self.raise_()
            self.activateWindow()
    
    def closeEvent(self, event):
        """窗口关闭事件处理"""
        if self.tray_icon.isVisible():
            QMessageBox.information(self, "桌面壁纸任务清单",
                                  "程序将继续在后台运行。\n"
                                  "您可以通过系统托盘图标访问程序。")
            self.hide()
            event.ignore()
        else:
            event.accept()
    
    def close_application(self):
        """完全退出应用程序"""
        # 恢复原壁纸
        self.wallpaper_manager.restore_original_wallpaper()
        
        # 隐藏托盘图标
        self.tray_icon.hide()
        
        # 退出应用
        QApplication.quit()
    
    def load_tasks(self):
        """加载任务列表"""
        self.task_list.clear()
        
        tasks = self.task_manager.get_all_tasks()
        for task in tasks:
            item = QListWidgetItem()
            
            # 设置任务文本
            display_text = task["content"]
            if len(display_text) > 50:  # 限制显示长度
                display_text = display_text[:47] + "..."
            
            # 添加完成状态标记
            prefix = "✓ " if task["is_completed"] else "□ "
            item.setText(prefix + display_text)
            
            # 存储完整任务数据
            item.setData(Qt.ItemDataRole.UserRole, task)
            
            # 设置已完成任务的样式
            if task["is_completed"]:
                item.setForeground(Qt.GlobalColor.gray)
            
            self.task_list.addItem(item)
    
    def add_task(self):
        """添加新任务"""
        dialog = MarkdownEditor(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            content = dialog.get_content()
            if content.strip():
                self.task_manager.add_task(content)
                self.load_tasks()
    
    def edit_task(self):
        """编辑任务"""
        current_item = self.task_list.currentItem()
        if current_item:
            task = current_item.data(Qt.ItemDataRole.UserRole)
            dialog = MarkdownEditor(task["content"], parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                content = dialog.get_content()
                if content.strip():
                    self.task_manager.update_task(task["id"], content=content)
                    self.load_tasks()
    
    def delete_task(self):
        """删除任务"""
        current_item = self.task_list.currentItem()
        if current_item:
            task = current_item.data(Qt.ItemDataRole.UserRole)
            confirm = QMessageBox.question(
                self, "确认删除", 
                "确定要删除此任务吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if confirm == QMessageBox.StandardButton.Yes:
                self.task_manager.delete_task(task["id"])
                self.load_tasks()
    
    def toggle_task_completion(self):
        """切换任务完成状态"""
        current_item = self.task_list.currentItem()
        if current_item:
            task = current_item.data(Qt.ItemDataRole.UserRole)
            self.task_manager.update_task(task["id"], is_completed=not task["is_completed"])
            self.load_tasks()
    
    def import_tasks(self):
        """导入任务"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入任务", "", "JSON文件 (*.json)")
        
        if file_path:
            if self.task_manager.import_tasks(file_path):
                self.load_tasks()
                QMessageBox.information(self, "导入成功", "任务已成功导入")
            else:
                QMessageBox.warning(self, "导入失败", "无法导入任务，请检查文件格式")
    
    def export_tasks(self):
        """导出任务"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出任务", "", "JSON文件 (*.json)")
        
        if file_path:
            if self.task_manager.export_tasks(file_path):
                QMessageBox.information(self, "导出成功", "任务已成功导出")
            else:
                QMessageBox.warning(self, "导出失败", "无法导出任务")
    
    def refresh_wallpaper(self):
        """手动刷新壁纸"""
        if self.wallpaper_manager.refresh_wallpaper():
            self.statusBar().showMessage("壁纸已刷新", 3000)
        else:
            QMessageBox.warning(self, "刷新失败", "无法刷新壁纸")
    
    def restore_wallpaper(self):
        """恢复原壁纸"""
        if self.wallpaper_manager.restore_original_wallpaper():
            self.statusBar().showMessage("已恢复原壁纸", 3000)
        else:
            QMessageBox.warning(self, "恢复失败", "无法恢复原壁纸")
    
    def show_context_menu(self, position):
        """显示右键菜单"""
        current_item = self.task_list.currentItem()
        if current_item:
            task = current_item.data(Qt.ItemDataRole.UserRole)
            
            context_menu = QMenu(self)
            edit_action = context_menu.addAction("编辑")
            complete_action = context_menu.addAction(
                "标记为未完成" if task["is_completed"] else "标记为完成")
            delete_action = context_menu.addAction("删除")
            
            action = context_menu.exec(self.task_list.mapToGlobal(position))
            
            if action == edit_action:
                self.edit_task()
            elif action == complete_action:
                self.toggle_task_completion()
            elif action == delete_action:
                self.delete_task()
    
    def on_font_size_changed(self, value):
        """字体大小滑块数值变化处理"""
        self.font_size = value
        self.settings.setValue("font_size", value)
        # 刷新壁纸，应用新字体大小
        if hasattr(self, 'wallpaper_manager'):
            self.wallpaper_manager.set_font_size(value)
            self.refresh_wallpaper()
    
    def on_font_changed(self, font_name):
        """字体选择变化处理"""
        self.font_name = font_name
        self.settings.setValue("font_name", font_name)
        
        # 获取字体文件路径
        font_file = None
        if font_name in self.system_fonts:
            font_file = self.system_fonts[font_name].get('file')
        
        # 更新壁纸管理器的字体
        if hasattr(self, 'wallpaper_manager'):
            success = self.wallpaper_manager.set_font(font_name, font_file)
            if success:
                self.refresh_wallpaper()
                self.statusBar().showMessage(f"已设置字体: {font_name}", 3000)
            else:
                # 字体设置失败，还原到之前的选择
                self.statusBar().showMessage(f"字体 '{font_name}' 不可用，将使用默认字体", 5000)
                
                # 还原到默认字体
                default_font = "Microsoft YaHei"
                index = self.font_combo.findText(default_font)
                if index >= 0:
                    self.font_combo.blockSignals(True)  # 暂时阻止信号触发循环
                    self.font_combo.setCurrentIndex(index)
                    self.font_combo.blockSignals(False)
                    self.font_name = default_font
                    self.settings.setValue("font_name", default_font)
                    
                # 使用默认字体刷新
                self.wallpaper_manager.set_font(default_font)
                self.refresh_wallpaper()