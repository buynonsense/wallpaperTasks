import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QListWidget, QListWidgetItem, QDialog, 
                            QTextEdit, QLabel, QFileDialog, QMessageBox, QMenu,
                            QSystemTrayIcon, QApplication, QSlider, QGroupBox, QStyle,
                            QComboBox, QLineEdit)
from PyQt6.QtCore import Qt, QSize, QSettings
from PyQt6.QtGui import QIcon, QAction

from task_manager import TaskManager
from wallpaper_manager import WallpaperManager
from logo_generator import create_logo
from style_manager import StyleManager
from wallpaper_preview import WallpaperPreview
from wallpaper_settings import WallpaperSettingsDialog

class MarkdownEditor(QDialog):
    """Markdown编辑对话框"""
    def __init__(self, title="", content="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("编辑任务")
        self.resize(600, 400)
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 标题编辑区域
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("任务标题:"))
        self.title_edit = QLineEdit(title)
        self.title_edit.setPlaceholderText("输入任务标题...")
        title_layout.addWidget(self.title_edit)
        layout.addLayout(title_layout)
        
        # 添加说明标签
        help_text = """任务内容 (支持Markdown语法)：
# 标题
**粗体**
*斜体*
- 列表项
1. 有序列表"""
        
        help_label = QLabel(help_text)
        layout.addWidget(help_label)
        
        # 内容编辑器
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("在这里输入任务详细内容...")
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
    
    def get_title(self):
        """获取编辑后的标题"""
        return self.title_edit.text()
    
    def get_content(self):
        """获取编辑后的内容"""
        return self.editor.toPlainText()

class MainWindow(QMainWindow):
    """主窗口"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("桌面壁纸任务清单")
        self.resize(800, 800)  # 增加窗口高度从600到800
        
        # 设置应用图标
        app_icon = create_logo()
        self.setWindowIcon(app_icon)
        
        # 加载设置
        self.settings = QSettings("WallpaperTasks", "Application")
        self.font_size = self.settings.value("font_size", 24, type=int)
        self.style_name = self.settings.value("style_name", "现代蓝", type=str)
        
        # 初始化管理器
        self.task_manager = TaskManager()
        self.wallpaper_manager = WallpaperManager(self.task_manager)
        self.wallpaper_manager.set_font_size(self.font_size)
        
        # 从设置中加载任务区域位置
        try:
            position = self.settings.value("task_position", [0.5, 0.15, 0.95, 0.95])
            
            # 验证并修复位置数据
            if not isinstance(position, list) or len(position) != 4:
                position = [0.5, 0.15, 0.95, 0.95]
            
            # 确保所有值都是浮点数并在有效范围内
            position = [
                float(val) if isinstance(val, (int, float, str)) and 0 <= float(val) <= 1 else 0.5 
                for val in position
            ]
            
            # 应用位置设置
            self.wallpaper_manager.set_task_area(*position)
            
        except Exception as e:
            print(f"加载任务位置设置出错: {e}")
            # 使用默认位置
            self.wallpaper_manager.set_task_area(0.5, 0.15, 0.95, 0.95)
        
        # 初始刷新壁纸
        self.wallpaper_manager.refresh_wallpaper()
        
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
        
        # 任务列表面板 - 添加选项卡
        tasks_panel = QGroupBox("任务列表")
        tasks_layout = QVBoxLayout(tasks_panel)
        
        # 添加已完成/未完成任务切换
        task_filter_layout = QHBoxLayout()
        self.show_active_button = QPushButton("待办任务")
        self.show_completed_button = QPushButton("已完成")
        
        # 设置初始状态
        self.show_active_button.setChecked(True)
        self.show_active_button.setStyleSheet("font-weight: bold;")
        
        self.show_active_button.clicked.connect(lambda: self.filter_tasks("active"))
        self.show_completed_button.clicked.connect(lambda: self.filter_tasks("completed"))
        
        task_filter_layout.addWidget(self.show_active_button)
        task_filter_layout.addWidget(self.show_completed_button)
        task_filter_layout.addStretch(1)
        
        tasks_layout.addLayout(task_filter_layout)
        
        # 任务列表 - 修复滚动问题
        self.task_list = QListWidget()
        self.task_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.task_list.customContextMenuRequested.connect(self.show_context_menu)
        self.task_list.setAlternatingRowColors(True)
        self.task_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)  # 确保显示滚动条
        self.task_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.task_list.setMinimumHeight(300)  # 设置最小高度确保有足够空间
        self.task_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #eaeaea;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                selection-background-color: #e5f1ff;
            }
            QListWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #f0f0f0;
                font-size: 15px;
                border-radius: 4px;
                margin: 2px 0px;
            }
            QListWidget::item:selected {
                background-color: #e5f1ff;
                color: #2d8cf0;
                border: 1px solid #a0cfff;
                border-left: 4px solid #2d8cf0;
            }
            QListWidget::item:hover {
                background-color: #f5f9ff;
            }
            QListWidget::item:alternate {
                background-color: #fcfcfc;
            }
            /* 确保滚动条可见 */
            QScrollBar:vertical {
                border: none;
                background: #f5f5f5;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c1c1c1;
                min-height: 30px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a8a8a8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        self.task_list.itemDoubleClicked.connect(self.edit_task)
        tasks_layout.addWidget(self.task_list)
        
        # 任务操作按钮区
        task_buttons_layout = QHBoxLayout()
        
        # 添加任务按钮
        self.add_button = QPushButton("添加任务")
        self.add_button.setIcon(QIcon.fromTheme("list-add", self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogNewFolder)))
        
        # 编辑任务保持默认样式
        self.edit_button = QPushButton("编辑任务")
        self.edit_button.setIcon(QIcon.fromTheme("document-edit", self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView)))
        
        # 删除任务按钮
        self.delete_button = QPushButton("删除任务")
        self.delete_button.setIcon(QIcon.fromTheme("edit-delete", self.style().standardIcon(QStyle.StandardPixmap.SP_DialogDiscardButton)))
        
        # 完成/未完成按钮
        self.complete_button = QPushButton("完成/未完成")
        self.complete_button.setIcon(QIcon.fromTheme("emblem-default", self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton)))
        
        self.wallpaper_toggle_button = QPushButton("切换壁纸显示")
        self.wallpaper_toggle_button.setIcon(QIcon.fromTheme("preferences-desktop-wallpaper", self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)))
        task_buttons_layout.addWidget(self.wallpaper_toggle_button)

        task_buttons_layout.addWidget(self.add_button)
        task_buttons_layout.addWidget(self.edit_button)
        task_buttons_layout.addWidget(self.delete_button)
        task_buttons_layout.addWidget(self.complete_button)
        
        tasks_layout.addLayout(task_buttons_layout)
        main_layout.addWidget(tasks_panel, 1)  # 让任务列表区域占据更多空间
        
        # 设置面板 - 简化后的版本
        settings_panel = QGroupBox("壁纸设置")
        settings_layout = QVBoxLayout(settings_panel)
        
        # 添加打开设置按钮
        wallpaper_settings_button = QPushButton("打开壁纸位置设置...")
        wallpaper_settings_button.clicked.connect(self.open_wallpaper_settings)
        settings_layout.addWidget(wallpaper_settings_button)
        
        # 添加皮肤选择 (保留此功能)
        style_layout = QHBoxLayout()
        style_layout.addWidget(QLabel("界面风格:"))
        
        self.style_combo = QComboBox()
        for style_name in StyleManager.get_style_names():
            self.style_combo.addItem(style_name)
        
        # 设置当前样式
        index = self.style_combo.findText(self.style_name)
        if index >= 0:
            self.style_combo.setCurrentIndex(index)
        
        self.style_combo.currentTextChanged.connect(self.on_style_changed)
        style_layout.addWidget(self.style_combo)
        settings_layout.addLayout(style_layout)
        
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
        self.wallpaper_toggle_button.clicked.connect(self.toggle_selected_task_wallpaper)

        # 创建系统托盘
        self.setup_tray_icon()
        
        # 加载任务
        self.load_tasks()
        
        # 设置状态栏
        self.statusBar().showMessage("程序已启动", 3000)
        self.statusBar().setStyleSheet("color: #666; padding: 2px 5px;")
        
        # 应用初始样式 - 放在组件创建完成后
        self.apply_style(self.style_name)
        
        # 初始化过滤状态
        self.current_filter = "active"

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
        
        # 清理Markdown渲染器
        if hasattr(self.wallpaper_manager, 'md_renderer'):
            self.wallpaper_manager.md_renderer.cleanup()
        
        # 隐藏托盘图标
        self.tray_icon.hide()
        
        # 退出应用
        QApplication.quit()
    
    def load_tasks(self):
        """加载任务列表，根据过滤条件显示"""
        self.task_list.clear()
        
        tasks = self.task_manager.get_all_tasks()
        
        # 根据过滤条件显示任务
        if hasattr(self, 'current_filter') and self.current_filter == "completed":
            # 仅显示已完成任务
            filtered_tasks = [task for task in tasks if task["is_completed"]]
        else:
            # 默认显示未完成任务
            filtered_tasks = [task for task in tasks if not task["is_completed"]]
        
        for task in filtered_tasks:
            item = QListWidgetItem()
            
            # 获取任务标题和内容
            if "title" in task and task["title"].strip():
                display_text = task["title"]
            else:
                # 对于旧任务数据可能没有标题，使用内容的第一行
                display_text = task["content"].split('\n')[0]
                if len(display_text) > 50:
                    display_text = display_text[:47] + "..."
            
            # 为显示在壁纸上的任务添加标记
            show_on_wallpaper = task.get("show_on_wallpaper", True)
            if show_on_wallpaper and not task["is_completed"]:
                display_text = "🖼️ " + display_text  # 添加壁纸图标
            
            # 设置文本
            item.setText(display_text)
            
            # 存储完整任务数据
            item.setData(Qt.ItemDataRole.UserRole, task)
            
            # 设置已完成任务的样式
            if task["is_completed"]:
                item.setForeground(Qt.GlobalColor.gray)
                # 添加删除线效果
                font = item.font()
                font.setStrikeOut(True)
                item.setFont(font)
            
            self.task_list.addItem(item)
            
        # 根据当前过滤类型设置按钮文本
        if hasattr(self, 'current_filter') and self.current_filter == "completed":
            self.complete_button.setText("标记为未完成")
        else:
            self.complete_button.setText("标记为已完成")
    
    def add_task(self):
        """添加新任务"""
        dialog = MarkdownEditor(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            title = dialog.get_title()
            content = dialog.get_content()
            if title.strip() or content.strip():
                self.task_manager.add_task(title, content)
                self.load_tasks()
    
    def edit_task(self):
        """编辑任务"""
        current_item = self.task_list.currentItem()
        if current_item:
            task = current_item.data(Qt.ItemDataRole.UserRole)
            title = task.get("title", "")
            content = task.get("content", "")
            
            dialog = MarkdownEditor(title, content, parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_title = dialog.get_title()
                new_content = dialog.get_content()
                if new_title.strip() or new_content.strip():
                    self.task_manager.update_task(task["id"], title=new_title, content=new_content)
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
            
            # 添加在壁纸上显示/隐藏的选项
            show_on_wallpaper = task.get("show_on_wallpaper", True)
            wallpaper_action = context_menu.addAction(
                "从壁纸中隐藏" if show_on_wallpaper else "在壁纸中显示")
            
            delete_action = context_menu.addAction("删除")
            
            action = context_menu.exec(self.task_list.mapToGlobal(position))
            
            if action == edit_action:
                self.edit_task()
            elif action == complete_action:
                self.toggle_task_completion()
            elif action == wallpaper_action:
                self.toggle_task_wallpaper_visibility(task)
            elif action == delete_action:
                self.delete_task()

    def toggle_task_wallpaper_visibility(self, task):
        """切换任务在壁纸上的显示状态"""
        current_state = task.get("show_on_wallpaper", True)
        self.task_manager.update_task(task["id"], show_on_wallpaper=not current_state)
        
        # 更新视觉提示
        self.load_tasks()
        
        # 刷新壁纸
        self.refresh_wallpaper()
    
    def toggle_selected_task_wallpaper(self):
        """切换选中任务在壁纸上的显示状态"""
        current_item = self.task_list.currentItem()
        if current_item:
            task = current_item.data(Qt.ItemDataRole.UserRole)
            self.toggle_task_wallpaper_visibility(task)

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
    
    def apply_style(self, style_name):
        """应用指定的界面样式"""
        # 设置全局样式
        self.setStyleSheet(StyleManager.get_style(style_name))
        
        # 设置彩色按钮样式
        if hasattr(self, 'add_button'):
            self.add_button.setStyleSheet(StyleManager.get_colored_button_style(style_name, "add"))
        if hasattr(self, 'delete_button'):
            self.delete_button.setStyleSheet(StyleManager.get_colored_button_style(style_name, "delete"))
        if hasattr(self, 'complete_button'):
            self.complete_button.setStyleSheet(StyleManager.get_colored_button_style(style_name, "complete"))
        if hasattr(self, 'refresh_button'):
            self.refresh_button.setStyleSheet(StyleManager.get_colored_button_style(style_name, "refresh"))
    
    def on_style_changed(self, style_name):
        """界面风格变更处理"""
        self.style_name = style_name
        self.settings.setValue("style_name", style_name)
        self.apply_style(style_name)
        self.statusBar().showMessage(f"已切换到 {style_name} 风格", 3000)
    
    def filter_tasks(self, filter_type):
        """过滤任务列表显示"""
        self.current_filter = filter_type
        
        # 更新按钮样式
        if filter_type == "active":
            self.show_active_button.setStyleSheet("font-weight: bold;")
            self.show_completed_button.setStyleSheet("")
        else:
            self.show_active_button.setStyleSheet("")
            self.show_completed_button.setStyleSheet("font-weight: bold;")
        
        # 重新加载任务
        self.load_tasks()
    
    def on_position_changed(self, x1, y1, x2, y2):
        """任务清单位置变化处理"""
        # 保存到设置
        self.settings.setValue("task_position", [x1, y1, x2, y2])
        
        # 更新壁纸管理器
        self.wallpaper_manager.set_task_area(x1, y1, x2, y2)
        
        # 自动刷新壁纸
        self.statusBar().showMessage("正在更新任务位置...", 1000)
        
        # 使用延迟刷新，避免拖动时频繁更新
        if hasattr(self, "_refresh_timer"):
            self._refresh_timer.stop()
        else:
            from PyQt6.QtCore import QTimer
            self._refresh_timer = QTimer()
            self._refresh_timer.setSingleShot(True)
            self._refresh_timer.timeout.connect(self.refresh_wallpaper)
        
        self._refresh_timer.start(500)  # 500毫秒后刷新壁纸
    
    def open_wallpaper_settings(self):
        """打开壁纸设置窗口"""
        dialog = WallpaperSettingsDialog(self.wallpaper_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 更新界面上的字体大小滑块（如果有）
            if hasattr(self, 'font_slider'):
                self.font_slider.setValue(self.settings.value("font_size", 24, type=int))
            
            # 显示状态消息
            self.statusBar().showMessage("壁纸设置已更新", 3000)