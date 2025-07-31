#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人生成就系统(Life Achievement System,LAS)
主程序文件
"""

import tkinter as tk
import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(__file__))

from src.utils.config import WINDOW_CONFIG
from src.gui.main_window import MainWindowGUI
from src.utils.system_manager import SystemManager, WindowManager
from src.utils.event_manager import EventManager, EventHandlers
from src.utils.summary_manager import SummaryManager


class LASSystem:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(WINDOW_CONFIG["main_window"]["title"])
        self.root.geometry(WINDOW_CONFIG["main_window"]["geometry"])
        self.root.resizable(WINDOW_CONFIG["main_window"]["resizable"], WINDOW_CONFIG["main_window"]["resizable"])
        
        # 设置最小窗口大小
        self.root.minsize(WINDOW_CONFIG["main_window"]["min_width"], WINDOW_CONFIG["main_window"]["min_height"])
        
        # 初始化管理器
        self.system_manager = SystemManager(self)
        self.event_handlers = EventHandlers(self)
        self.window_manager = WindowManager(self)
        self.summary_manager = SummaryManager(self)
        
        # 初始化系统
        self.system_manager.init_system()
        
        # 创建GUI
        self.gui = MainWindowGUI(self)
        
        # 加载数据
        self.system_manager.load_data()
        
    def add_event_listener(self, listener):
        """添加事件监听器"""
        self.system_manager.main_system.event_manager.add_event_listener(listener)
    
    def remove_event_listener(self, listener):
        """移除事件监听器"""
        self.system_manager.main_system.event_manager.remove_event_listener(listener)
    
    def notify_data_changed(self, event_type="data_changed"):
        """通知所有监听器数据已变更"""
        self.system_manager.main_system.event_manager.notify_data_changed(event_type)
    
    def register_window_for_updates(self, window):
        """注册窗口以接收更新通知"""
        self.system_manager.main_system.event_manager.register_window_for_updates(window)
        
    def on_data_changed(self, event_type="data_changed"):
        """处理数据变更事件"""
        self.event_handlers.on_data_changed(event_type)
    
    def on_goal_type_changed(self):
        """目标类型选择改变时的处理"""
        self.event_handlers.on_goal_type_changed()
    
    def on_goal_double_click(self, event):
        """目标双击事件处理"""
        self.event_handlers.on_goal_double_click(event)
    
    def on_daily_task_double_click(self, event):
        """计划双击事件处理"""
        self.event_handlers.on_daily_task_double_click(event)
        
    def show_goals_window(self):
        """显示目标管理窗口"""
        self.window_manager.show_goals_window()
        
    def show_daily_tasks_window(self):
        """显示计划管理窗口"""
        self.window_manager.show_daily_tasks_window()
        
    def add_daily_task(self):
        """添加计划"""
        self.window_manager.add_daily_task()
        
    def add_goal(self):
        """添加目标"""
        self.window_manager.add_goal()
    
    def clear_summary_form(self):
        """清空总结表单"""
        self.summary_manager.clear_summary_form()
    
    def get_current_date_str(self):
        """获取当前日期字符串"""
        return self.system_manager.get_current_date_str()
    
    def save_summary(self):
        """保存总结"""
        self.summary_manager.save_summary_with_validation()

    def run(self):
        """运行系统"""
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"系统运行出错: {e}")


if __name__ == "__main__":
    app = LASSystem()
    app.run() 