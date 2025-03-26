import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
import ctypes

from ui import MainWindow

def set_app_id():
    """设置Windows任务栏应用ID"""
    app_id = "WallpaperTasks.Application"
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except:
        pass

def main():
    """程序主入口"""
    # 创建应用程序目录
    app_dir = os.path.join(os.environ['LOCALAPPDATA'], 'WallpaperTasks')
    os.makedirs(app_dir, exist_ok=True)
    
    # 初始化应用
    app = QApplication(sys.argv)
    app.setApplicationName("桌面壁纸任务清单")
    set_app_id()
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec())

if __name__ == "__main__":
    main()