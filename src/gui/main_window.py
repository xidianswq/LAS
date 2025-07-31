#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口GUI模块
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.utils.database import execute_query, execute_update
from src.utils.data_manager import format_level_info, format_level_only, calculate_level

from src.utils.config import UI_CONFIG


class MainWindowGUI:
    """主窗口GUI类"""
    
    def __init__(self, main_system):
        self.main_system = main_system
        self.root = main_system.root
        
        # GUI组件
        self.time_label = None
        self.system_time_label = None
        self.level_label = None
        self.goals_tree = None
        self.daily_tasks_tree = None
        self.summary_content_text = None
        self.stats_text = None
        self.goal_type_var = None
        self.summary_date_var = None
        
        # 创建界面
        self.create_gui()
        
    def create_gui(self):
        """创建图形界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=UI_CONFIG["padding"], pady=UI_CONFIG["padding"])
        
        # 创建左侧面板
        left_panel = ttk.Frame(main_frame, width=UI_CONFIG["sidebar_width"]) 
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, UI_CONFIG["padding"]))
        left_panel.pack_propagate(False)  # 固定宽度
        
        # 创建右侧主内容区
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 创建左侧面板内容
        self.create_sidebar(left_panel)
        
        # 创建右侧内容区
        self.create_main_content(right_panel)
        
    def create_sidebar(self, parent):
        """创建侧边栏"""
        # 今日时间
        time_frame = ttk.LabelFrame(parent, text="今日时间", padding=UI_CONFIG["padding"])
        time_frame.pack(fill=tk.X, pady=(0, UI_CONFIG["padding"]))
        
        self.time_label = ttk.Label(time_frame, text="")
        self.time_label.pack()
        
        # 系统运行时间
        system_frame = ttk.LabelFrame(parent, text="系统运行时间", padding=UI_CONFIG["padding"])
        system_frame.pack(fill=tk.X, pady=(0, UI_CONFIG["padding"]))
        
        self.system_time_label = ttk.Label(system_frame, text="")
        self.system_time_label.pack()
        
        # 等级
        level_frame = ttk.LabelFrame(parent, text="等级", padding=UI_CONFIG["padding"])
        level_frame.pack(fill=tk.X, pady=(0, UI_CONFIG["padding"]))
        
        self.level_label = ttk.Label(level_frame, text="等级: 1")
        self.level_label.pack()
    
    def create_main_content(self, parent):
        """创建主内容区"""
        # 创建选项卡
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 计划选项卡    
        daily_tasks_frame = ttk.Frame(notebook)
        notebook.add(daily_tasks_frame, text="计划")
        self.create_daily_tasks_tab(daily_tasks_frame)

        # 目标选项卡
        goals_frame = ttk.Frame(notebook)
        notebook.add(goals_frame, text="目标")
        self.create_goals_tab(goals_frame)
        
        # 总结录入选项卡
        summary_frame = ttk.Frame(notebook)
        notebook.add(summary_frame, text="总结录入")
        self.create_summary_tab(summary_frame)
        
        # 数据统计选项卡
        stats_frame = ttk.Frame(notebook)
        notebook.add(stats_frame, text="数据统计")
        self.create_stats_tab(stats_frame)
        
    def create_goals_tab(self, parent):
        """创建目标选项卡"""
        # 目标类型选择
        goal_type_frame = ttk.LabelFrame(parent, text="目标类型选择", padding=5)
        goal_type_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(goal_type_frame, text="目标类型:").pack(side=tk.LEFT)
        self.goal_type_var = tk.StringVar(value="月计划")
        ttk.Radiobutton(goal_type_frame, text="月计划", variable=self.goal_type_var, 
                       value="月计划", command=self.main_system.on_goal_type_changed).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Radiobutton(goal_type_frame, text="年计划", variable=self.goal_type_var, 
                       value="年计划", command=self.main_system.on_goal_type_changed).pack(side=tk.LEFT, padx=(5, 0))
        
        # 目标列表
        goals_list_frame = ttk.LabelFrame(parent, text="目标列表", padding=5)
        goals_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # 创建树形视图
        columns = ("事项", "子项", "量化指标", "完成")
        self.goals_tree = ttk.Treeview(goals_list_frame, columns=columns, show="headings", height=8)
        
        # 设置列宽度，确保内容能够完整显示
        column_widths = {
            "事项": 150,
            "子项": 100,
            "量化指标": 50,
            "完成": 50
        }
        
        for col in columns:
            self.goals_tree.heading(col, text=col)
            self.goals_tree.column(col, width=column_widths.get(col, 100))
        
        # 滚动条
        scrollbar = ttk.Scrollbar(goals_list_frame, orient=tk.VERTICAL, command=self.goals_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.goals_tree.configure(yscrollcommand=scrollbar.set)
        
        self.goals_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # 绑定双击事件
        self.goals_tree.bind('<Double-1>', self.main_system.on_goal_double_click)
        
        # 按钮区域
        goals_button_frame = ttk.Frame(parent)
        goals_button_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        ttk.Button(goals_button_frame, text="目标管理", command=self.main_system.show_goals_window).pack(side=tk.LEFT, padx=(0, 5))
        
    def create_daily_tasks_tab(self, parent):
        """创建计划选项卡"""
        # 计划列表
        tasks_list_frame = ttk.LabelFrame(parent, text="计划列表", padding=5)
        tasks_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # 创建树形视图
        columns = ("事项", "子项", "完成")
        self.daily_tasks_tree = ttk.Treeview(tasks_list_frame, columns=columns, show="headings", height=8)
        
        # 设置列宽度，确保内容能够完整显示
        column_widths = {
            "事项": 180,
            "子项": 130,
            "完成": 80
        }
        
        for col in columns:
            self.daily_tasks_tree.heading(col, text=col)
            self.daily_tasks_tree.column(col, width=column_widths.get(col, 100))
        
        # 滚动条
        scrollbar = ttk.Scrollbar(tasks_list_frame, orient=tk.VERTICAL, command=self.daily_tasks_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.daily_tasks_tree.configure(yscrollcommand=scrollbar.set)
        
        self.daily_tasks_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # 绑定双击事件
        self.daily_tasks_tree.bind('<Double-1>', self.main_system.on_daily_task_double_click)
        
        # 按钮区域
        tasks_button_frame = ttk.Frame(parent)
        tasks_button_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        ttk.Button(tasks_button_frame, text="计划管理", command=self.main_system.add_daily_task).pack(side=tk.LEFT, padx=(0, 5))
        
    def create_summary_tab(self, parent):
        """创建总结录入选项卡"""
        # 日期选择
        date_frame = ttk.LabelFrame(parent, text="总结日期", padding=5)
        date_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(date_frame, text="日期:").pack(side=tk.LEFT)
        self.summary_date_var = tk.StringVar(value=self.main_system.get_current_date_str())
        date_entry = ttk.Entry(date_frame, textvariable=self.summary_date_var, width=12)
        date_entry.pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(date_frame, text="(YYYY.MM.DD)").pack(side=tk.LEFT, padx=(3, 0))
        
        # 内容输入
        content_frame = ttk.LabelFrame(parent, text="总结内容", padding=5)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建文本框和滚动条
        text_frame = ttk.Frame(content_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.summary_content_text = tk.Text(text_frame, wrap=tk.WORD, height=8)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.summary_content_text.yview)
        self.summary_content_text.configure(yscrollcommand=scrollbar.set)
        
        self.summary_content_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 按钮框架
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="保存总结", command=self.main_system.save_summary).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="清空内容", command=self.main_system.clear_summary_form).pack(side=tk.LEFT, padx=(0, 5))
        
    def create_stats_tab(self, parent):
        """创建数据统计选项卡"""
        # 统计信息显示区域
        stats_display_frame = ttk.LabelFrame(parent, text="统计信息", padding=10)
        stats_display_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建统计信息显示
        self.stats_text = tk.Text(stats_display_frame, height=12, wrap=tk.WORD)
        # 滚动条
        scrollbar = ttk.Scrollbar(stats_display_frame, orient=tk.VERTICAL, command=self.stats_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.stats_text.configure(yscrollcommand=scrollbar.set)
        
        self.stats_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
    def update_time_display(self):
        """更新时间显示"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        
        # 计算系统运行时间（使用硬编码的开始日期）
        try:
            # 硬编码系统开始日期
            start_date_str = "2025-07-30"  # 可以根据需要修改这个日期
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            current_date = date.today()
            
            # 计算天数差
            days_diff = (current_date - start_date).days
            
            if days_diff == 0:
                system_time_text = "今天开始"
            elif days_diff == 1:
                system_time_text = "已运行1天"
            else:
                system_time_text = f"已运行{days_diff}天"
                
            self.system_time_label.config(text=system_time_text)
        except Exception as e:
            self.system_time_label.config(text="计算运行时间出错")
            print(f"计算系统运行时间时出错: {e}")
        
        # 每天更新一次
        self.root.after(UI_CONFIG["refresh_interval"], self.update_time_display)
        
    def load_user_level(self):
        """加载用户等级信息"""
        try:
            # 从数据库获取当前经验值
            query = "SELECT experience FROM basic_info WHERE id = 1"
            result = execute_query(query)
            
            if result:
                current_exp = result[0]['experience'] or 0
                # 计算当前等级
                current_level = calculate_level(current_exp, 100)
                level_info = format_level_only(current_level)
                
                # 更新等级显示
                self.level_label.config(text=level_info)

            else:
                # 如果没有找到用户信息，使用默认值
                level_info = format_level_only(1)
                self.level_label.config(text=level_info)
            
        except Exception as e:
            print(f"加载用户等级信息失败: {e}")
            # 使用默认值
            level_info = format_level_only(1)
            self.level_label.config(text=level_info) 