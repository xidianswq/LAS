#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件
包含系统的各种配置参数
"""

import os
import sys
from pathlib import Path

def get_app_path():
    """获取应用程序路径，支持exe打包后的路径"""
    if getattr(sys, 'frozen', False):
        # 如果是exe打包后的环境
        return Path(sys._MEIPASS)
    else:
        # 如果是开发环境
        return Path(__file__).parent.parent.parent

# ==================== 数据库配置 ====================
DATABASE_NAME = os.path.join(get_app_path(), "doc", "las_database.db")

# ==================== 窗口配置 ====================
WINDOW_CONFIG = {
    # 主窗口配置
    "main_window": {
        "title": "LAS",
        "geometry": "800x375",
        "min_width": 400,
        "min_height": 375,
        "resizable": True
    },
    # 目标管理窗口配置
    "goals_window": {
        "title": "目标管理",
        "geometry": "900x550",
        "min_width": 700,
        "min_height": 400,
        "edit_geometry": "400x320"
    },
    # 每日任务窗口配置
    "daily_tasks_window": {
        "title": "计划管理",
        "geometry": "900x550",
        "min_width": 700,
        "min_height": 400,
        "edit_geometry": "400x300"
    }
}

# ==================== 等级系统配置 ====================
LEVEL_SYSTEM_CONFIG = {
    "exp_per_level": 100,  # 每级需要的经验值
    "min_level": 1,         # 最小等级
    "max_level": None,      # 最大等级（None表示无上限）
    "default_level": 1,     # 默认等级
    "default_exp": 0        # 默认经验值
}

# ==================== 经验值奖励配置 ====================
EXP_REWARD_CONFIG = {
    "goal_completion": 500,     # 目标完成奖励经验值
    "daily_task_default": 10,   # 每日任务默认奖励经验值
    "summary_completion": 5     # 总结完成奖励经验值
}

# ==================== 目标配置 ====================
GOAL_CONFIG = {
    "goal_types": ["月计划", "年计划"],
    "priority_levels": ["高", "中", "低"],
    "status_options": ["进行中", "已完成", "已暂停"],
    "experience_reward": [1000, 300, 100],  # 对应高、中、低优先级
    "default_status": "进行中",
    "default_priority": "中"
}

# ==================== 每日任务配置 ====================
DAILY_TASK_CONFIG = {
    "priority_levels": ["高", "中", "低"],
    "status_options": ["未完成", "已完成"],
    "experience_reward": [30,20,10],
    "default_status": "未完成",
    "default_priority": "中",
    "auto_reset_hour": 0,  # 每天0点自动重置
    "enable_daily_reset": True
}

# ==================== 总结配置 ====================
SUMMARY_CONFIG = {
    "auto_save": True,
    "max_content_length": 10000  # 最大内容长度
}

# ==================== 界面配置 ====================
UI_CONFIG = {
    "padding": 5,
    "sidebar_width": 200,
    "tree_height": 200,
    "text_height": 150,
    "refresh_interval": 1000,  # 24小时刷新间隔（毫秒）
    "time_format": "%Y.%m.%d %H:%M:%S",
    "date_format": "%Y-%m-%d"
}

# ==================== 数据库表配置 ====================
DATABASE_TABLES = {
    "basic_info": '''
        CREATE TABLE IF NOT EXISTS basic_info (
            id INTEGER PRIMARY KEY,
            start_date TEXT,
            experience INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            created_at TEXT,
            updated_at TEXT
        )
    ''',
    "goals": '''
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            goal_type TEXT,
            description TEXT,
            status TEXT DEFAULT '进行中',
            priority TEXT DEFAULT '中',
            deadline TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''',
    "daily_tasks": '''
        CREATE TABLE IF NOT EXISTS daily_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            priority TEXT DEFAULT '中',
            status TEXT DEFAULT '未完成',
            experience_reward INTEGER DEFAULT 10,
            task_date TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''',

}

# ==================== 默认数据配置 ====================
DEFAULT_DATA = {
    "basic_info": {
        "start_date": "2025-07-30",
        "experience": 0,
        "level": 1
    }
}

# ==================== 消息配置 ====================
MESSAGE_CONFIG = {
    "goal_completion": "恭喜！目标 '{title}' 已完成！\n获得经验值: {exp}",
    "task_completion": "恭喜！每日任务 '{title}' 已完成！\n获得经验值: {exp}",
    "error_prefix": "错误",
    "warning_prefix": "警告",
    "info_prefix": "信息"
} 