from PyQt6.QtCore import QSettings

class StyleManager:
    """界面样式管理器"""
    
    @staticmethod
    def get_style_names():
        """获取所有可用样式名称"""
        return [
            "现代蓝",
            "暗夜黑",
            "简约白",
            "活力橙",
            "专业绿"
        ]
    
    @staticmethod
    def get_style(style_name):
        """根据样式名称获取样式表"""
        styles = {
            # 现代蓝 - 当前默认样式
            "现代蓝": """
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
                QComboBox {
                    border: 1px solid #eaeaea;
                    border-radius: A6px;
                    padding: 4px 8px;
                    background-color: white;
                    color: #333;
                    min-height: 25px;
                }
                QComboBox:hover {
                    border-color: #d4e8ff;
                }
                QComboBox:focus {
                    border-color: #2d8cf0;
                }
            """,
            
            # 暗夜黑 - 深色主题
            "暗夜黑": """
                QMainWindow {
                    background-color: #202124;
                }
                QGroupBox {
                    background-color: #2e2e30;
                    border: 1px solid #3e3e42;
                    border-radius: 8px;
                    margin-top: 14px;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 8px;
                    color: #e0e0e0;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 12px;
                    padding: 0 8px;
                    color: #e0e0e0;
                }
                QPushButton {
                    background-color: #3e3e42;
                    border: 1px solid #49494d;
                    padding: 8px 16px;
                    border-radius: 6px;
                    color: #e0e0e0;
                    font-weight: 500;
                    font-size: 13px;
                    min-height: 36px;
                }
                QPushButton:hover {
                    background-color: #49494d;
                    border-color: #5a5a5e;
                }
                QPushButton:pressed {
                    background-color: #5a5a5e;
                    border-color: #6a6a6e;
                }
                QListWidget {
                    background-color: #2e2e30;
                    border: 1px solid #3e3e42;
                    border-radius: 8px;
                    padding: 8px;
                    font-size: 14px;
                    color: #e0e0e0;
                    selection-background-color: #3f3f46;
                }
                QListWidget::item {
                    padding: 12px 8px;
                    border-bottom: 1px solid #3e3e42;
                    font-size: 15px;
                }
                QListWidget::item:selected {
                    background-color: #3f3f46;
                    color: #ffffff;
                    border-radius: 6px;
                }
                QListWidget::item:hover {
                    background-color: #35353a;
                }
                QListWidget::item:alternate {
                    background-color: #333337;
                }
                QLabel {
                    color: #e0e0e0;
                    font-size: 14px;
                }
                QSlider::handle:horizontal {
                    background: #007acc;
                    border: 1px solid #007acc;
                    width: 16px;
                    height: 16px;
                    margin: -7px 0;
                    border-radius: 8px;
                }
                QSlider::groove:horizontal {
                    height: 6px;
                    background: #3e3e42;
                    margin: 0 4px;
                    border-radius: 3px;
                }
                QSlider::add-page:horizontal {
                    background: #3e3e42;
                    border-radius: 3px;
                }
                QSlider::sub-page:horizontal {
                    background: #007acc;
                    border-radius: 3px;
                }
                QStatusBar {
                    color: #b0b0b0;
                    font-size: 13px;
                    padding: 4px 6px;
                }
                QComboBox {
                    border: 1px solid #3e3e42;
                    border-radius: 6px;
                    padding: 4px 8px;
                    background-color: #2e2e30;
                    color: #e0e0e0;
                    min-height: 25px;
                }
                QComboBox:hover {
                    border-color: #49494d;
                }
                QComboBox:focus {
                    border-color: #007acc;
                }
            """,
            
            # 简约白 - 极简风格
            "简约白": """
                QMainWindow {
                    background-color: #ffffff;
                }
                QGroupBox {
                    background-color: #fafafa;
                    border: 1px solid #eeeeee;
                    border-radius: 4px;
                    margin-top: 14px;
                    font-weight: normal;
                    font-size: 14px;
                    padding: 8px;
                    color: #333;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 12px;
                    padding: 0 8px;
                    color: #333;
                }
                QPushButton {
                    background-color: #ffffff;
                    border: 1px solid #e0e0e0;
                    padding: 8px 16px;
                    border-radius: 4px;
                    color: #333;
                    font-weight: normal;
                    font-size: 13px;
                    min-height: 32px;
                }
                QPushButton:hover {
                    background-color: #f5f5f5;
                    border-color: #d0d0d0;
                }
                QPushButton:pressed {
                    background-color: #e8e8e8;
                    border-color: #c0c0c0;
                }
                QListWidget {
                    background-color: #ffffff;
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 14px;
                    selection-background-color: #f2f2f2;
                }
                QListWidget::item {
                    padding: 10px 6px;
                    border-bottom: 1px solid #f0f0f0;
                    font-size: 14px;
                }
                QListWidget::item:selected {
                    background-color: #f2f2f2;
                    color: #333;
                    border-radius: 4px;
                }
                QListWidget::item:hover {
                    background-color: #f9f9f9;
                }
                QListWidget::item:alternate {
                    background-color: #fbfbfb;
                }
                QLabel {
                    color: #333;
                    font-size: 14px;
                }
                QSlider::handle:horizontal {
                    background: #888888;
                    border: 1px solid #888888;
                    width: 14px;
                    height: 14px;
                    margin: -6px 0;
                    border-radius: 7px;
                }
                QSlider::groove:horizontal {
                    height: 4px;
                    background: #d0d0d0;
                    margin: 0 4px;
                    border-radius: 2px;
                }
                QSlider::add-page:horizontal {
                    background: #d0d0d0;
                    border-radius: 2px;
                }
                QSlider::sub-page:horizontal {
                    background: #888888;
                    border-radius: 2px;
                }
                QStatusBar {
                    color: #666;
                    font-size: 13px;
                    padding: 4px 6px;
                }
                QComboBox {
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                    padding: 4px 8px;
                    background-color: #ffffff;
                    color: #333;
                    min-height: 25px;
                }
                QComboBox:hover {
                    border-color: #d0d0d0;
                }
                QComboBox:focus {
                    border-color: #888888;
                }
            """,
            
            # 活力橙 - 充满活力的风格
            "活力橙": """
                QMainWindow {
                    background-color: #fffaf5;
                }
                QGroupBox {
                    background-color: white;
                    border: 1px solid #ffe6cc;
                    border-radius: 8px;
                    margin-top: 14px;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 8px;
                    color: #d35400;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 12px;
                    padding: 0 8px;
                    color: #e67e22;
                }
                QPushButton {
                    background-color: #ffffff;
                    border: 1px solid #ffe6cc;
                    padding: 8px 16px;
                    border-radius: 6px;
                    color: #d35400;
                    font-weight: 500;
                    font-size: 13px;
                    min-height: 36px;
                }
                QPushButton:hover {
                    background-color: #fff0dd;
                    border-color: #ffcc99;
                    color: #e67e22;
                }
                QPushButton:pressed {
                    background-color: #ffe0b3;
                    border-color: #e67e22;
                    color: #d35400;
                }
                QListWidget {
                    background-color: white;
                    border: 1px solid #ffe6cc;
                    border-radius: 8px;
                    padding: 8px;
                    font-size: 14px;
                    selection-background-color: #fff0dd;
                }
                QListWidget::item {
                    padding: 12px 8px;
                    border-bottom: 1px solid #fff0dd;
                    font-size: 15px;
                }
                QListWidget::item:selected {
                    background-color: #fff0dd;
                    color: #d35400;
                    border-radius: 6px;
                }
                QListWidget::item:hover {
                    background-color: #fffaf0;
                }
                QListWidget::item:alternate {
                    background-color: #fffcf7;
                }
                QLabel {
                    color: #333;
                    font-size: 14px;
                }
                QSlider::handle:horizontal {
                    background: #f39c12;
                    border: 1px solid #f39c12;
                    width: 16px;
                    height: 16px;
                    margin: -7px 0;
                    border-radius: 8px;
                }
                QSlider::groove:horizontal {
                    height: 6px;
                    background: #ffe6cc;
                    margin: 0 4px;
                    border-radius: 3px;
                }
                QSlider::add-page:horizontal {
                    background: #ffe6cc;
                    border-radius: 3px;
                }
                QSlider::sub-page:horizontal {
                    background: #f39c12;
                    border-radius: 3px;
                }
                QStatusBar {
                    color: #d35400;
                    font-size: 13px;
                    padding: 4px 6px;
                }
                QComboBox {
                    border: 1px solid #ffe6cc;
                    border-radius: 6px;
                    padding: 4px 8px;
                    background-color: white;
                    color: #d35400;
                    min-height: 25px;
                }
                QComboBox:hover {
                    border-color: #ffcc99;
                }
                QComboBox:focus {
                    border-color: #f39c12;
                }
            """,
            
            # 专业绿 - 商务风格
            "专业绿": """
                QMainWindow {
                    background-color: #f5faf8;
                }
                QGroupBox {
                    background-color: white;
                    border: 1px solid #d4e6dd;
                    border-radius: 8px;
                    margin-top: 14px;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 8px;
                    color: #004d40;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 12px;
                    padding: 0 8px;
                    color: #00695c;
                }
                QPushButton {
                    background-color: #ffffff;
                    border: 1px solid #d4e6dd;
                    padding: 8px 16px;
                    border-radius: 6px;
                    color: #004d40;
                    font-weight: 500;
                    font-size: 13px;
                    min-height: 36px;
                }
                QPushButton:hover {
                    background-color: #e7f5ef;
                    border-color: #b2d8cb;
                    color: #00695c;
                }
                QPushButton:pressed {
                    background-color: #d4e6dd;
                    border-color: #00695c;
                    color: #004d40;
                }
                QListWidget {
                    background-color: white;
                    border: 1px solid #d4e6dd;
                    border-radius: 8px;
                    padding: 8px;
                    font-size: 14px;
                    selection-background-color: #e7f5ef;
                }
                QListWidget::item {
                    padding: 12px 8px;
                    border-bottom: 1px solid #e7f5ef;
                    font-size: 15px;
                }
                QListWidget::item:selected {
                    background-color: #e7f5ef;
                    color: #004d40;
                    border-radius: 6px;
                }
                QListWidget::item:hover {
                    background-color: #f2f9f6;
                }
                QListWidget::item:alternate {
                    background-color: #f7fbf9;
                }
                QLabel {
                    color: #333;
                    font-size: 14px;
                }
                QSlider::handle:horizontal {
                    background: #00897b;
                    border: 1px solid #00897b;
                    width: 16px;
                    height: 16px;
                    margin: -7px 0;
                    border-radius: 8px;
                }
                QSlider::groove:horizontal {
                    height: 6px;
                    background: #d4e6dd;
                    margin: 0 4px;
                    border-radius: 3px;
                }
                QSlider::add-page:horizontal {
                    background: #d4e6dd;
                    border-radius: 3px;
                }
                QSlider::sub-page:horizontal {
                    background: #00897b;
                    border-radius: 3px;
                }
                QStatusBar {
                    color: #004d40;
                    font-size: 13px;
                    padding: 4px 6px;
                }
                QComboBox {
                    border: 1px solid #d4e6dd;
                    border-radius: 6px;
                    padding: 4px 8px;
                    background-color: white;
                    color: #004d40;
                    min-height: 25px;
                }
                QComboBox:hover {
                    border-color: #b2d8cb;
                }
                QComboBox:focus {
                    border-color: #00897b;
                }
            """
        }
        
        return styles.get(style_name, styles["现代蓝"])
        
    @staticmethod
    def get_colored_button_style(style_name, button_type):
        """获取有颜色按钮的样式"""
        # 为有颜色的按钮定制特殊样式
        styles = {
            "现代蓝": {
                "add": """
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
                """,
                "delete": """
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
                """,
                "complete": """
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
                """,
                "refresh": """
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
                """
            },
            
            "暗夜黑": {
                "add": """
                    QPushButton {
                        background-color: #007acc; 
                        color: white; 
                        border-color: #007acc;
                        font-weight: bold;
                        padding: 10px 16px;
                    }
                    QPushButton:hover {
                        background-color: #1a88d2;
                        border-color: #1a88d2;
                    }
                    QPushButton:pressed {
                        background-color: #0068ad;
                        border-color: #0068ad;
                    }
                """,
                "delete": """
                    QPushButton {
                        background-color: #b71c1c; 
                        color: white; 
                        border-color: #b71c1c;
                    }
                    QPushButton:hover {
                        background-color: #c62828;
                        border-color: #c62828;
                    }
                    QPushButton:pressed {
                        background-color: #a11717;
                        border-color: #a11717;
                    }
                """,
                "complete": """
                    QPushButton {
                        background-color: #2e7d32; 
                        color: white; 
                        border-color: #2e7d32;
                    }
                    QPushButton:hover {
                        background-color: #388e3c;
                        border-color: #388e3c;
                    }
                    QPushButton:pressed {
                        background-color: #276d2a;
                        border-color: #276d2a;
                    }
                """,
                "refresh": """
                    QPushButton {
                        background-color: #007acc;
                        color: white;
                        border-color: #007acc;
                        font-weight: bold;
                        padding: 10px 16px;
                    }
                    QPushButton:hover {
                        background-color: #1a88d2;
                        border-color: #1a88d2;
                    }
                    QPushButton:pressed {
                        background-color: #0068ad;
                        border-color: #0068ad;
                    }
                """
            },
            
            "简约白": {
                "add": """
                    QPushButton {
                        background-color: #444444; 
                        color: white; 
                        border-color: #444444;
                        font-weight: bold;
                        padding: 10px 16px;
                    }
                    QPushButton:hover {
                        background-color: #666666;
                        border-color: #666666;
                    }
                    QPushButton:pressed {
                        background-color: #333333;
                        border-color: #333333;
                    }
                """,
                "delete": """
                    QPushButton {
                        background-color: #e53935; 
                        color: white; 
                        border-color: #e53935;
                    }
                    QPushButton:hover {
                        background-color: #f44336;
                        border-color: #f44336;
                    }
                    QPushButton:pressed {
                        background-color: #d32f2f;
                        border-color: #d32f2f;
                    }
                """,
                "complete": """
                    QPushButton {
                        background-color: #43a047; 
                        color: white; 
                        border-color: #43a047;
                    }
                    QPushButton:hover {
                        background-color: #4caf50;
                        border-color: #4caf50;
                    }
                    QPushButton:pressed {
                        background-color: #388e3c;
                        border-color: #388e3c;
                    }
                """,
                "refresh": """
                    QPushButton {
                        background-color: #444444;
                        color: white;
                        border-color: #444444;
                        font-weight: bold;
                        padding: 10px 16px;
                    }
                    QPushButton:hover {
                        background-color: #666666;
                        border-color: #666666;
                    }
                    QPushButton:pressed {
                        background-color: #333333;
                        border-color: #333333;
                    }
                """
            },
            
            "活力橙": {
                "add": """
                    QPushButton {
                        background-color: #e67e22; 
                        color: white; 
                        border-color: #e67e22;
                        font-weight: bold;
                        padding: 10px 16px;
                    }
                    QPushButton:hover {
                        background-color: #f39c12;
                        border-color: #f39c12;
                    }
                    QPushButton:pressed {
                        background-color: #d35400;
                        border-color: #d35400;
                    }
                """,
                "delete": """
                    QPushButton {
                        background-color: #e74c3c; 
                        color: white; 
                        border-color: #e74c3c;
                    }
                    QPushButton:hover {
                        background-color: #fc5c4c;
                        border-color: #fc5c4c;
                    }
                    QPushButton:pressed {
                        background-color: #c0392b;
                        border-color: #c0392b;
                    }
                """,
                "complete": """
                    QPushButton {
                        background-color: #27ae60; 
                        color: white; 
                        border-color: #27ae60;
                    }
                    QPushButton:hover {
                        background-color: #2ecc71;
                        border-color: #2ecc71;
                    }
                    QPushButton:pressed {
                        background-color: #219955;
                        border-color: #219955;
                    }
                """,
                "refresh": """
                    QPushButton {
                        background-color: #e67e22;
                        color: white;
                        border-color: #e67e22;
                        font-weight: bold;
                        padding: 10px 16px;
                    }
                    QPushButton:hover {
                        background-color: #f39c12;
                        border-color: #f39c12;
                    }
                    QPushButton:pressed {
                        background-color: #d35400;
                        border-color: #d35400;
                    }
                """
            },
            
            "专业绿": {
                "add": """
                    QPushButton {
                        background-color: #00897b; 
                        color: white; 
                        border-color: #00897b;
                        font-weight: bold;
                        padding: 10px 16px;
                    }
                    QPushButton:hover {
                        background-color: #00a896;
                        border-color: #00a896;
                    }
                    QPushButton:pressed {
                        background-color: #00796b;
                        border-color: #00796b;
                    }
                """,
                "delete": """
                    QPushButton {
                        background-color: #d32f2f; 
                        color: white; 
                        border-color: #d32f2f;
                    }
                    QPushButton:hover {
                        background-color: #e53935;
                        border-color: #e53935;
                    }
                    QPushButton:pressed {
                        background-color: #c62828;
                        border-color: #c62828;
                    }
                """,
                "complete": """
                    QPushButton {
                        background-color: #2e7d32; 
                        color: white; 
                        border-color: #2e7d32;
                    }
                    QPushButton:hover {
                        background-color: #388e3c;
                        border-color: #388e3c;
                    }
                    QPushButton:pressed {
                        background-color: #276d2a;
                        border-color: #276d2a;
                    }
                """,
                "refresh": """
                    QPushButton {
                        background-color: #00897b;
                        color: white;
                        border-color: #00897b;
                        font-weight: bold;
                        padding: 10px 16px;
                    }
                    QPushButton:hover {
                        background-color: #00a896;
                        border-color: #00a896;
                    }
                    QPushButton:pressed {
                        background-color: #00796b;
                        border-color: #00796b;
                    }
                """
            }
        }
        
        # 获取指定主题的按钮样式
        theme_styles = styles.get(style_name, styles["现代蓝"])
        return theme_styles.get(button_type, "")