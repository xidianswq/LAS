#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统管理器
负责系统初始化、数据库管理、每日重置等核心功能
"""

import tkinter as tk
from datetime import datetime
from src.utils.database import get_database_manager
from src.utils.config import DATABASE_NAME, WINDOW_CONFIG
from src.utils.database import init_daily_reset_manager
from src.utils.data_manager import DataManager
from src.utils.summary_manager import SummaryManager
from src.utils.event_manager import EventManager


class SystemManager:
    """系统管理器"""
    
    def __init__(self, main_system):
        self.main_system = main_system
        self.root = main_system.root
        
    def init_system(self):
        """初始化系统"""
        # 初始化管理器
        self.main_system.event_manager = EventManager(self.main_system)
        self.main_system.data_manager = DataManager(self.main_system)
        self.main_system.summary_manager = SummaryManager(self.main_system)
        
        # 初始化数据库
        self.init_database()
        
        # 初始化每日重置管理器
        self.init_daily_reset()
        
        # 注册事件监听器
        self.main_system.add_event_listener(self.main_system)
        
    def init_database(self):
        """初始化数据库"""
        self.main_system.db_path = DATABASE_NAME
        print(f"数据库路径: {self.main_system.db_path}")
        
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
            self.main_system.daily_reset_manager = init_daily_reset_manager(self.main_system)
            if self.main_system.daily_reset_manager:
                print("✅ 每日重置管理器初始化成功")
            else:
                print("❌ 每日重置管理器初始化失败")
        except Exception as e:
            print(f"❌ 每日重置管理器初始化失败: {e}")
    
    def load_data(self):
        """加载数据"""
        self.main_system.gui.update_time_display()
        self.main_system.gui.load_user_level()
        self.main_system.gui.update_countdown_display()
        self.main_system.data_manager.refresh_goals()
        self.main_system.data_manager.refresh_daily_tasks()
        
        # 初始化新选项卡的内容
        self.main_system.data_manager.refresh_stats_display()
    
    def get_current_date_str(self):
        """获取当前日期字符串"""
        return datetime.now().strftime("%Y.%m.%d")


class WindowManager:
    """窗口管理器"""
    
    def __init__(self, main_system):
        self.main_system = main_system
    
    def show_goals_window(self):
        """显示目标管理窗口"""
        from src.gui.goals_window import GoalsWindow
        GoalsWindow(self.main_system)
        
    def show_daily_tasks_window(self):
        """显示计划管理窗口"""
        from src.gui.daily_tasks_window import DailyTasksWindow
        DailyTasksWindow(self.main_system)
        
    def add_daily_task(self):
        """添加计划"""
        from src.gui.daily_tasks_window import DailyTasksWindow
        DailyTasksWindow(self.main_system)
        
    def add_goal(self):
        """添加目标"""
        from src.gui.goals_window import GoalsWindow
        GoalsWindow(self.main_system) 