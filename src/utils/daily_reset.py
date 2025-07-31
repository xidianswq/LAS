#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日重置管理模块
提供每日任务自动重置功能
"""

import threading
import time
from datetime import datetime, date
from src.utils.database import execute_query, execute_update
from src.utils.config import DAILY_TASK_CONFIG


class DailyResetManager:
    """每日重置管理器"""
    
    def __init__(self, main_system):
        self.main_system = main_system
        self.running = False
        self.thread = None
        
    def start(self):
        """启动每日重置管理器"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            print("🔄 每日重置管理器已启动")
    
    def stop(self):
        """停止每日重置管理器"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("⏹️ 每日重置管理器已停止")
    
    def _run(self):
        """运行重置检查循环"""
        while self.running:
            try:
                current_hour = datetime.now().hour
                
                # 检查是否到了重置时间
                if current_hour == DAILY_TASK_CONFIG["auto_reset_hour"]:
                    self._perform_daily_reset()
                
                # 每小时检查一次
                time.sleep(3600)  # 1小时
                
            except Exception as e:
                print(f"每日重置管理器运行错误: {e}")
                time.sleep(3600)  # 出错时也等待1小时
    
    def _perform_daily_reset(self):
        """执行每日重置"""
        try:
            print("🔄 开始执行每日重置...")
            
            # 获取今天的日期
            today = date.today().strftime("%Y-%m-%d")
            
            # 检查是否已经重置过
            check_query = "SELECT COUNT(*) as count FROM daily_tasks WHERE task_date = ?"
            result = execute_query(check_query, (today,))
            
            if result and result[0]['count'] > 0:
                print("✅ 今日任务已存在，跳过重置")
                return
            
            # 获取昨天的任务作为模板
            yesterday = (date.today() - date.timedelta(days=1)).strftime("%Y-%m-%d")
            template_query = "SELECT title, description, priority FROM daily_tasks WHERE task_date = ? AND status = '已完成'"
            templates = execute_query(template_query, (yesterday,))
            
            if templates:
                print(f"📋 找到 {len(templates)} 个已完成的任务作为模板")
                
                # 根据优先级计算经验值奖励
                priority_levels = DAILY_TASK_CONFIG["priority_levels"]
                experience_rewards = DAILY_TASK_CONFIG["experience_reward"]
                
                for template in templates:
                    try:
                        # 计算经验值奖励
                        priority = template['priority'] or "中"
                        try:
                            priority_index = priority_levels.index(priority)
                            exp_reward = experience_rewards[priority_index]
                        except (ValueError, IndexError):
                            exp_reward = experience_rewards[1]  # 默认使用中等优先级奖励
                        
                        # 插入新任务
                        insert_query = """
                            INSERT INTO daily_tasks (title, description, status, priority, task_date, 
                                                   experience_reward, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """
                        execute_update(insert_query, (
                            template['title'],
                            template['description'],
                            "未完成",
                            priority,
                            today,
                            exp_reward,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        ))
                        
                    except Exception as e:
                        print(f"创建任务失败: {e}")
                
                print("✅ 每日重置完成")
                
                # 通知数据变更
                if hasattr(self.main_system, 'notify_data_changed'):
                    self.main_system.notify_data_changed("daily_reset")
            else:
                print("📝 没有找到可用的任务模板")
                
        except Exception as e:
            print(f"❌ 每日重置失败: {e}")


# 全局每日重置管理器实例
_daily_reset_manager = None

def init_daily_reset_manager(main_system):
    """初始化每日重置管理器"""
    global _daily_reset_manager
    if _daily_reset_manager is None:
        _daily_reset_manager = DailyResetManager(main_system)
        _daily_reset_manager.start()
        print("✅ 每日重置管理器初始化成功")
    return _daily_reset_manager

def get_daily_reset_manager():
    """获取每日重置管理器实例"""
    return _daily_reset_manager 