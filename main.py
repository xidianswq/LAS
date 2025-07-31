#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人生成就系统(Life Achievement System,LAS)
主程序文件
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import sys
from datetime import datetime, date
import sqlite3
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(os.path.dirname(__file__))

from src.utils.database import get_database_manager, execute_query, execute_update, execute_insert
from src.utils.level_utils import format_level_info
from src.utils.config import (
    DATABASE_NAME, GOAL_CONFIG, WINDOW_CONFIG, 
    LEVEL_SYSTEM_CONFIG, EXP_REWARD_CONFIG, DATABASE_TABLES, DEFAULT_DATA
)
from src.utils.database import DatabaseManager
from src.utils.daily_reset import init_daily_reset_manager
from src.gui.main_window import MainWindowGUI
from src.utils.data_manager import DataManager
from src.utils.summary_manager import SummaryManager
from src.utils.event_manager import EventManager


class LASSystem:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(WINDOW_CONFIG["main_window"]["title"])
        self.root.geometry(WINDOW_CONFIG["main_window"]["geometry"])
        self.root.resizable(WINDOW_CONFIG["main_window"]["resizable"], WINDOW_CONFIG["main_window"]["resizable"])
        
        # 设置最小窗口大小
        self.root.minsize(WINDOW_CONFIG["main_window"]["min_width"], WINDOW_CONFIG["main_window"]["min_height"])
        
        # 初始化管理器
        self.event_manager = EventManager(self)
        self.data_manager = DataManager(self)
        self.summary_manager = SummaryManager(self)
        
        # 初始化数据库
        self.init_database()
        
        # 初始化每日重置管理器
        self.init_daily_reset()
        
        # 创建GUI
        self.gui = MainWindowGUI(self)
        
        # 注册自己为事件监听器
        self.add_event_listener(self)
        
        # 加载数据
        self.load_data()
        
    def add_event_listener(self, listener):
        """添加事件监听器"""
        self.event_manager.add_event_listener(listener)
    
    def remove_event_listener(self, listener):
        """移除事件监听器"""
        self.event_manager.remove_event_listener(listener)
    
    def notify_data_changed(self, event_type="data_changed"):
        """通知所有监听器数据已变更"""
        self.event_manager.notify_data_changed(event_type)
    
    def register_window_for_updates(self, window):
        """注册窗口以接收更新通知"""
        self.event_manager.register_window_for_updates(window)
    
    def init_database(self):
        """初始化数据库"""
        self.db_path = DATABASE_NAME
        print(f"数据库路径: {self.db_path}")
        
        # 获取数据库管理器
        db_manager = get_database_manager()
        print(f"数据库管理器: {db_manager}")
        
        if not db_manager:
            print("❌ 数据库管理器初始化失败")
            return
        
        # 数据库管理器会自动创建表，这里不需要手动创建
        print("✅ 数据库初始化完成")
        
        # 数据库管理器会自动初始化默认数据，这里不需要手动初始化
        print("✅ 用户基本信息初始化完成")
        
    def init_daily_reset(self):
        """初始化每日重置管理器"""
        try:
            init_daily_reset_manager(self)
            print("✅ 每日重置管理器初始化成功")
        except Exception as e:
            print(f"❌ 每日重置管理器初始化失败: {e}")
        
    def load_data(self):
        """加载数据"""
        self.gui.update_time_display()
        self.gui.load_user_level()
        self.data_manager.refresh_goals()
        self.data_manager.refresh_daily_tasks() # 加载计划
        
        # 初始化新选项卡的内容
        self.data_manager.refresh_stats_display()
        
    def on_data_changed(self, event_type="data_changed"):
        """处理数据变更事件"""
        print(f"🏠 主窗口收到数据变更通知: {event_type}")
        
        # 根据事件类型刷新相应的数据
        if event_type in ["goal_added", "goal_changed", "goal_deleted", "goal_edited", "data_changed"]:
            # 刷新目标列表
            self.data_manager.refresh_goals()
            print("✅ 主窗口目标列表已刷新")
        
        if event_type in ["daily_task_added", "daily_task_changed", "daily_task_deleted", "daily_task_edited", "data_changed"]:
            # 刷新每日任务列表
            self.data_manager.refresh_daily_tasks()
            print("✅ 主窗口每日任务列表已刷新")
        
        # 刷新统计信息
        self.data_manager.refresh_stats_display()
        print("✅ 主窗口统计信息已刷新")
    
    def on_goal_type_changed(self):
        """目标类型选择改变时的处理"""
        self.data_manager.refresh_goals()
    
    def on_goal_double_click(self, event):
        """目标双击事件处理"""
        item = self.gui.goals_tree.selection()
        if not item:
            return
        
        # 获取目标ID
        goal_id = self.gui.goals_tree.item(item[0], "tags")[0]
        
        # 切换完成状态
        self.data_manager.toggle_goal_completion(goal_id)
    
    def on_daily_task_double_click(self, event):
        """计划双击事件处理"""
        item = self.gui.daily_tasks_tree.selection()
        if not item:
            return
            
        # 获取计划ID
        task_id = self.gui.daily_tasks_tree.item(item[0], "tags")[0]
        
        # 切换完成状态
        self.data_manager.toggle_daily_task_completion(task_id)
        
    def show_goals_window(self):
        """显示目标管理窗口"""
        from src.gui.goals_window import GoalsWindow
        GoalsWindow(self)
        
    def show_daily_tasks_window(self):
        """显示计划管理窗口"""
        from src.gui.daily_tasks_window import DailyTasksWindow
        DailyTasksWindow(self)
        
    def add_daily_task(self):
        """添加计划"""
        from src.gui.daily_tasks_window import DailyTasksWindow
        DailyTasksWindow(self)
        
    def add_goal(self):
        """添加目标"""
        from src.gui.goals_window import GoalsWindow
        GoalsWindow(self)
    
    def clear_summary_form(self):
        """清空总结表单"""
        self.summary_manager.clear_summary_form()
    
    def get_current_date_str(self):
        """获取当前日期字符串"""
        return datetime.now().strftime("%Y.%m.%d")
    

    
    def save_summary(self):
        """保存总结"""
        try:
            # 获取表单数据
            summary_date = self.gui.summary_date_var.get().strip()
            content = self.gui.summary_content_text.get(1.0, tk.END).strip()
            
            # 验证数据
            if not summary_date:
                messagebox.showwarning("警告", "请输入总结日期")
                return
            
            if not content:
                messagebox.showwarning("警告", "请输入总结内容")
                return
            
            # 验证日期格式
            try:
                # 将 YYYY.MM.DD 格式转换为 YYYY-MM-DD 格式
                date_parts = summary_date.split('.')
                if len(date_parts) == 3:
                    formatted_date = f"{date_parts[0]}-{date_parts[1].zfill(2)}-{date_parts[2].zfill(2)}"
                else:
                    formatted_date = summary_date
                
                # 验证日期格式
                datetime.strptime(formatted_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("错误", "日期格式不正确，请使用 YYYY.MM.DD 格式")
                return
            
            # 保存总结
            success = self.summary_manager.save_summary(content, formatted_date)
            
            if success:
                # 清空表单
                self.clear_summary_form()
                
                # 通知数据变更
                self.notify_data_changed("summary_added")
                
        except Exception as e:
            messagebox.showerror("错误", f"保存总结失败: {e}")

    def run(self):
        """运行系统"""
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"系统运行出错: {e}")


if __name__ == "__main__":
    app = LASSystem()
    app.run() 