#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
事件管理模块
提供数据变更通知功能
"""


class EventManager:
    """事件管理器"""
    
    def __init__(self, main_system):
        self.main_system = main_system
        self.listeners = []
        self.windows = []
    
    def add_event_listener(self, listener):
        """添加事件监听器"""
        if listener not in self.listeners:
            self.listeners.append(listener)
    
    def remove_event_listener(self, listener):
        """移除事件监听器"""
        if listener in self.listeners:
            self.listeners.remove(listener)
    
    def register_window_for_updates(self, window):
        """注册窗口以接收更新通知"""
        if window not in self.windows:
            self.windows.append(window)
    
    def unregister_window(self, window):
        """取消注册窗口"""
        if window in self.windows:
            self.windows.remove(window)
    
    def notify_data_changed(self, event_type="data_changed"):
        """通知所有监听器数据已变更"""
        print(f"📢 事件管理器收到数据变更通知: {event_type}")
        
        # 通知所有监听器
        for listener in self.listeners:
            try:
                if hasattr(listener, 'on_data_changed'):
                    listener.on_data_changed(event_type)
            except Exception as e:
                print(f"通知监听器失败: {e}")
        
        # 通知所有注册的窗口
        for window in self.windows[:]:  # 使用切片避免在迭代时修改列表
            try:
                if hasattr(window, 'on_data_changed'):
                    window.on_data_changed(event_type)
            except Exception as e:
                print(f"通知窗口失败: {e}")
                # 如果窗口已关闭，从列表中移除
                self.windows.remove(window)


class EventHandlers:
    """事件处理器"""
    
    def __init__(self, main_system):
        self.main_system = main_system
    
    def on_data_changed(self, event_type="data_changed"):
        """处理数据变更事件"""
        print(f"🏠 主窗口收到数据变更通知: {event_type}")
        
        # 根据事件类型刷新相应的数据
        if event_type in ["goal_added", "goal_changed", "goal_deleted", "goal_edited", "data_changed"]:
            # 刷新目标列表
            self.main_system.data_manager.refresh_goals()
            print("✅ 主窗口目标列表已刷新")
        
        if event_type in ["daily_task_added", "daily_task_changed", "daily_task_deleted", "daily_task_edited", "data_changed"]:
            # 刷新每日任务列表
            self.main_system.data_manager.refresh_daily_tasks()
            print("✅ 主窗口每日任务列表已刷新")
        
        # 刷新统计信息
        self.main_system.data_manager.refresh_stats_display()
        print("✅ 主窗口统计信息已刷新")
    
    def on_goal_type_changed(self):
        """目标类型选择改变时的处理"""
        self.main_system.data_manager.refresh_goals()
    
    def on_goal_double_click(self, event):
        """目标双击事件处理"""
        item = self.main_system.gui.goals_tree.selection()
        if not item:
            return
        
        # 获取目标ID
        goal_id = self.main_system.gui.goals_tree.item(item[0], "tags")[0]
        
        # 切换完成状态
        self.main_system.data_manager.toggle_goal_completion(goal_id)
    
    def on_daily_task_double_click(self, event):
        """计划双击事件处理"""
        item = self.main_system.gui.daily_tasks_tree.selection()
        if not item:
            return
            
        # 获取计划ID
        task_id = self.main_system.gui.daily_tasks_tree.item(item[0], "tags")[0]
        
        # 切换完成状态
        self.main_system.data_manager.toggle_daily_task_completion(task_id) 