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