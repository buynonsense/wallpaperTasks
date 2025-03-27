import os
import json
import uuid
from datetime import datetime

class TaskManager:
    def __init__(self):
        """初始化任务管理器"""
        # 任务数据存储路径
        self.data_path = os.path.join(os.environ['LOCALAPPDATA'], 'WallpaperTasks', 'tasks.json')
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        
        # 加载任务
        self.tasks = self._load_tasks()
        
        # 更改通知回调
        self.on_changed_callbacks = []
    
    def add_change_listener(self, callback):
        """添加任务变更监听器"""
        if callback not in self.on_changed_callbacks:
            self.on_changed_callbacks.append(callback)
    
    def remove_change_listener(self, callback):
        """移除任务变更监听器"""
        if callback in self.on_changed_callbacks:
            self.on_changed_callbacks.remove(callback)
    
    def _notify_changed(self):
        """通知所有监听器任务已变更"""
        for callback in self.on_changed_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"通知任务变更出错: {e}")
    
    def _load_tasks(self):
        """从文件加载任务"""
        if os.path.exists(self.data_path):
            try:
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    tasks = json.load(f)
                    
                    # 兼容旧数据，添加标题字段和显示字段
                    for task in tasks:
                        if "title" not in task:
                            # 使用内容的第一行作为标题
                            first_line = task["content"].split('\n')[0]
                            task["title"] = first_line[:50]  # 限制标题长度
                        
                        # 添加显示在壁纸上的标记，默认为True
                        if "show_on_wallpaper" not in task:
                            task["show_on_wallpaper"] = True
                    
                    return tasks
            except Exception as e:
                print(f"加载任务数据出错: {e}")
                return []
        else:
            return []
    
    def _save_tasks(self):
        """保存任务到文件"""
        try:
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存任务数据出错: {e}")
    
    def get_all_tasks(self):
        """获取所有任务"""
        return self.tasks.copy()
    
    def add_task(self, title, content=""):
        """添加新任务"""
        task = {
            "id": str(uuid.uuid4()),
            "title": title,  # 新增标题字段
            "content": content,
            "is_completed": False,
            "created_at": datetime.now().isoformat(),
            "completed_at": None,
            "show_on_wallpaper": True  # 默认显示在壁纸上
        }
        self.tasks.append(task)
        self._save_tasks()
        self._notify_changed()
        return task
    
    def update_task(self, task_id, title=None, content=None, is_completed=None, show_on_wallpaper=None):
        """更新任务"""
        for task in self.tasks:
            if task["id"] == task_id:
                if title is not None:
                    task["title"] = title
                if content is not None:
                    task["content"] = content
                if is_completed is not None:
                    task["is_completed"] = is_completed
                    task["completed_at"] = datetime.now().isoformat() if is_completed else None
                if show_on_wallpaper is not None:
                    task["show_on_wallpaper"] = show_on_wallpaper
                self._save_tasks()
                self._notify_changed()
                return True
        return False
    
    def delete_task(self, task_id):
        """删除任务"""
        original_count = len(self.tasks)
        self.tasks = [task for task in self.tasks if task["id"] != task_id]
        
        if len(self.tasks) < original_count:
            self._save_tasks()
            self._notify_changed()
            return True
        return False
    
    def set_data_path(self, path):
        """设置数据存储路径"""
        if path and path != self.data_path:
            self.data_path = path
            os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
            self._save_tasks()  # 保存现有任务到新位置
            self._notify_changed()
    
    def import_tasks(self, file_path):
        """从文件导入任务"""
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    imported_tasks = json.load(f)
                    
                    # 创建任务ID映射，用于识别相同任务
                    current_tasks_map = {task["id"]: task for task in self.tasks}
                    
                    # 处理导入的任务
                    for task in imported_tasks:
                        # 兼容旧数据，添加标题字段
                        if "title" not in task:
                            first_line = task["content"].split('\n')[0]
                            task["title"] = first_line[:50]  # 限制标题长度
                        
                        # 如果是已存在的任务，保留其壁纸显示设置
                        if task["id"] in current_tasks_map:
                            task["show_on_wallpaper"] = current_tasks_map[task["id"]].get("show_on_wallpaper", True)
                        # 对于新导入的任务，如果没有壁纸显示设置，则默认为True
                        elif "show_on_wallpaper" not in task:
                            task["show_on_wallpaper"] = True
                    
                    # 更新任务列表
                    self.tasks = imported_tasks
                    self._save_tasks()
                    self._notify_changed()
                    return True
                
            except Exception as e:
                print(f"导入任务出错: {e}")
                return False
        return False
    
    def export_tasks(self, file_path):
        """导出任务到文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"导出任务出错: {e}")
            return False