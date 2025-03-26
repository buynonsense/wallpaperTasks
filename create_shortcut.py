import os
import sys
import win32com.client
import site

def create_shortcut():
    """创建桌面快捷方式"""
    try:
        # 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 主程序路径
        main_script = os.path.join(current_dir, "wallpaper_tasks", "main.py")
        
        # 确认文件存在
        if not os.path.exists(main_script):
            print(f"错误: 找不到主程序 {main_script}")
            return False
        
        # Python解释器路径
        python_exe = sys.executable
        
        # 创建快捷方式
        shell = win32com.client.Dispatch("WScript.Shell")
        desktop = shell.SpecialFolders("Desktop")
        shortcut_path = os.path.join(desktop, "桌面壁纸任务清单.lnk")
        
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = python_exe
        shortcut.Arguments = f'"{main_script}"'
        shortcut.WorkingDirectory = current_dir
        shortcut.Description = "桌面壁纸任务清单"
        shortcut.Save()
        
        print(f"桌面快捷方式已创建: {shortcut_path}")
        return True
    except Exception as e:
        print(f"创建快捷方式失败: {e}")
        return False

if __name__ == "__main__":
    create_shortcut()
    input("按Enter键退出...")