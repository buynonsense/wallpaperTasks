import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QListWidget, QListWidgetItem, QDialog, 
                            QTextEdit, QLabel, QFileDialog, QMessageBox, QMenu,
                            QSystemTrayIcon, QApplication)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction

from task_manager import TaskManager
from wallpaper_manager import WallpaperManager

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
        self.resize(800, 600)  # 增大窗口尺寸
        
        # 设置应用样式表
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f7;
            }
            QLabel {
                font-size: 14px;
                color: #333;
                margin: 5px;
            }
            QListWidget {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #ddd;
                padding: 5px;
                font-size: 14px;
            }
            QListWidget::item {
                border-bottom: 1px solid #eee;
                padding: 8px;
            }
            QListWidget::item:selected {
                background-color: #e0f0ff;
                color: #333;
            }
            QPushButton {
                background-color: #4a7bff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3a6eff;
            }
            QPushButton:pressed {
                background-color: #2a5eff;
            }
        """)
        
        # 初始化管理器
        self.task_manager = TaskManager()
        self.wallpaper_manager = WallpaperManager(self.task_manager)
        
        # 初始刷新壁纸
        self.wallpaper_manager.refresh_wallpaper()
        
        # 设置中心窗口
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)  # 增加边距
        layout.setSpacing(15)  # 增加间距
        
        # 顶部信息
        info_label = QLabel("程序已启动，您的任务将显示在桌面壁纸上")
        info_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; padding: 10px;")
        layout.addWidget(info_label)
        
        # 任务列表
        self.task_list = QListWidget()
        self.task_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.task_list.customContextMenuRequested.connect(self.show_context_menu)
        self.task_list.setStyleSheet("font-size: 15px;")  # 增大字体
        self.task_list.setMinimumHeight(300)  # 设置最小高度
        layout.addWidget(self.task_list)
        
        # 按钮区域 - 使用更好的布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)  # 按钮间距
        
        self.add_button = QPushButton("添加任务")
        self.edit_button = QPushButton("编辑任务")
        self.delete_button = QPushButton("删除任务")
        self.complete_button = QPushButton("标记完成/未完成")
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.complete_button)
        
        layout.addLayout(button_layout)
        
        # 功能区域
        function_layout = QHBoxLayout()
        function_layout.setSpacing(10)
        
        self.import_button = QPushButton("导入")
        self.export_button = QPushButton("导出")
        self.refresh_button = QPushButton("刷新壁纸")
        self.restore_button = QPushButton("恢复原壁纸")
        
        # 设置特定按钮的样式
        self.refresh_button.setStyleSheet("""
            background-color: #42a5f5;
            padding: 8px 16px;
        """)
        self.restore_button.setStyleSheet("""
            background-color: #78909c;
            padding: 8px 16px;
        """)
        
        function_layout.addWidget(self.import_button)
        function_layout.addWidget(self.export_button)
        function_layout.addStretch()
        function_layout.addWidget(self.refresh_button)
        function_layout.addWidget(self.restore_button)
        
        layout.addLayout(function_layout)
        
        # 连接信号
        self.add_button.clicked.connect(self.add_task)
        self.edit_button.clicked.connect(self.edit_task)
        self.delete_button.clicked.connect(self.delete_task)
        self.complete_button.clicked.connect(self.toggle_task_completion)
        self.import_button.clicked.connect(self.import_tasks)
        self.export_button.clicked.connect(self.export_tasks)
        self.refresh_button.clicked.connect(self.refresh_wallpaper)
        self.restore_button.clicked.connect(self.restore_wallpaper)
        
        # 创建系统托盘
        self.setup_tray_icon()
        
        # 加载任务
        self.load_tasks()
    
    def setup_tray_icon(self):
        """设置系统托盘图标"""
        # 创建并显示系统托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        
        # 尝试使用内置图标
        self.tray_icon.setIcon(QIcon.fromTheme("task-due"))
        
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