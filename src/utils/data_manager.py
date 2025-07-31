#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据管理模块
"""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime, date
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.utils.database import execute_query, execute_update, execute_insert
from src.utils.config import EXP_REWARD_CONFIG, MESSAGE_CONFIG, LEVEL_SYSTEM_CONFIG


def format_level_info(level, exp, exp_per_level):
    """格式化等级信息"""
    exp_for_next = calculate_exp_for_next_level(level, exp, exp_per_level)
    progress = (exp % exp_per_level) / exp_per_level * 100
    
    return f"等级 {level} | 经验值 {exp}/{exp + exp_for_next} | 进度 {progress:.1f}%"


def format_level_only(level):
    """只格式化等级信息"""
    return f"{level}"


def calculate_level(exp, exp_per_level):
    """计算等级"""
    return (exp // exp_per_level) + 1


def calculate_exp_for_next_level(level, exp, exp_per_level):
    """计算升级所需经验值"""
    exp_for_current_level = (level - 1) * exp_per_level
    return exp_per_level - (exp - exp_for_current_level)


class DataManager:
    """数据管理类"""
    
    def __init__(self, main_system):
        self.main_system = main_system
        
    def refresh_goals(self):
        """刷新目标列表"""
        # 清空现有数据
        for item in self.main_system.gui.goals_tree.get_children():
            self.main_system.gui.goals_tree.delete(item)
        
        # 获取目标类型
        goal_type = self.main_system.gui.goal_type_var.get()
        
        # 查询数据库 - 只显示未完成的目标
        query = """
        SELECT id, title, description, goal_type, priority, status, 
               deadline, created_at
        FROM goals 
        WHERE goal_type = ? AND status != '已完成'
        ORDER BY priority DESC, created_at DESC
        """
        
        try:
            results = execute_query(query, (goal_type,))
            
            for row in results:
                # 计算完成进度（简化版本，基于状态）
                if row['status'] == '已完成':
                    progress_text = "100%"
                else:
                    progress_text = "0%"
                
                # 格式化截止日期
                deadline = row['deadline']
                if deadline:
                    deadline_date = datetime.strptime(deadline, '%Y-%m-%d').date()
                    today = date.today()
                    if deadline_date < today:
                        deadline_text = f"已逾期 ({deadline})"
                    else:
                        days_left = (deadline_date - today).days
                        deadline_text = f"剩余{days_left}天 ({deadline})"
                else:
                    deadline_text = "无截止日期"
                
                # 设置状态显示
                status = row['status'] or '进行中'
                if status == '已完成':
                    status_text = "✓ 已完成"
                elif status == '进行中':
                    status_text = "✗ 进行中"
                else:
                    status_text = f"? {status}"
                
                # 插入数据
                self.main_system.gui.goals_tree.insert("", "end", values=(
                    row['title'],
                    row['description'] or "",
                    status_text
                ), tags=(row['id'],))
                
        except Exception as e:
            print(f"加载目标失败: {e}")
    
    def refresh_daily_tasks(self):
        """刷新计划列表"""
        # 清空现有数据
        for item in self.main_system.gui.daily_tasks_tree.get_children():
            self.main_system.gui.daily_tasks_tree.delete(item)
            
        try:
            # 查询今日的未完成每日任务
            current_date = datetime.now().strftime("%Y-%m-%d")
            query = "SELECT id, title, description, status, priority, experience_reward FROM daily_tasks WHERE task_date = ? AND status != '已完成' ORDER BY created_at DESC"
            results = execute_query(query, (current_date,))
            
            for row in results:
                # 设置完成状态图标和文本
                status = row['status'] or '未完成'
                if status == '已完成':
                    status_icon = "✓"
                    status_text = "已完成"
                else:
                    status_icon = "✗"
                    status_text = "未完成"
                
                display_status = f"{status_icon} {status_text}"
                
                self.main_system.gui.daily_tasks_tree.insert("", "end", values=(
                    row['title'] or "",
                    row['description'] or "",
                    display_status
                ), tags=(row['id'],))
        except Exception as e:
            print(f"刷新计划列表失败: {e}")
    
    def toggle_goal_completion(self, goal_id):
        """切换目标完成状态"""
        try:
            # 查询当前目标状态和优先级
            query = "SELECT status, title, priority FROM goals WHERE id = ?"
            result = execute_query(query, (goal_id,))
            
            if not result:
                return
            
            current_status = result[0]['status']
            goal_title = result[0]['title']
            goal_priority = result[0]['priority'] or "中"
            
            # 切换状态
            new_status = '已完成' if current_status != '已完成' else '进行中'
            
            # 更新数据库
            update_query = "UPDATE goals SET status = ? WHERE id = ?"
            execute_update(update_query, (new_status, goal_id))
            
            if new_status == '已完成':
                # 目标完成时获取经验值
                exp_gain = EXP_REWARD_CONFIG["goal_completion"]
                print(f"🎉 目标 '{goal_title}' 已完成！获得经验值: {exp_gain}")
                
                # 更新用户等级和经验值
                self.update_user_experience(exp_gain)
                
                messagebox.showinfo("目标完成", MESSAGE_CONFIG["goal_completion"].format(title=goal_title, exp=exp_gain))
            else:
                print(f"目标 '{goal_title}' 状态已更改为进行中")
            
            # 通知所有监听器数据已变更
            print("📢 通知数据变更：目标状态已切换")
            self.main_system.notify_data_changed("goal_changed")
            
        except Exception as e:
            print(f"切换目标状态失败: {e}")
            messagebox.showerror("错误", f"切换目标状态失败: {e}")
    
    def toggle_daily_task_completion(self, task_id):
        """切换计划完成状态"""
        try:
            # 查询当前计划状态
            query = "SELECT status, title, experience_reward FROM daily_tasks WHERE id = ?"
            result = execute_query(query, (task_id,))
            
            if not result:
                return
            
            current_status = result[0]['status']
            task_title = result[0]['title']
            exp_reward = result[0]['experience_reward'] or EXP_REWARD_CONFIG["daily_task_default"]
            
            # 切换状态
            new_status = '已完成' if current_status != '已完成' else '未完成'
            
            # 更新数据库
            update_query = "UPDATE daily_tasks SET status = ?, updated_at = ? WHERE id = ?"
            execute_update(update_query, (new_status, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), task_id))
            
            if new_status == '已完成':
                # 任务完成时获取经验值
                print(f"🎉 每日任务 '{task_title}' 已完成！获得经验值: {exp_reward}")
                
                # 更新用户等级和经验值
                self.update_user_experience(exp_reward)
                
                messagebox.showinfo("任务完成", MESSAGE_CONFIG["task_completion"].format(title=task_title, exp=exp_reward))
            else:
                print(f"每日任务 '{task_title}' 状态已更改为未完成")
            
            # 通知所有监听器数据已变更
            print("📢 通知数据变更：每日任务状态已切换")
            self.main_system.notify_data_changed("daily_task_changed")
            
        except Exception as e:
            print(f"切换每日任务状态失败: {e}")
            messagebox.showerror("错误", f"切换每日任务状态失败: {e}")
    
    def update_user_experience(self, exp_gain):
        """更新用户经验值"""
        try:
            # 获取当前经验值
            query = "SELECT experience FROM basic_info WHERE id = 1"
            result = execute_query(query)
            
            if result:
                current_exp = result[0]['experience'] or 0
                new_exp = current_exp + exp_gain
                
                # 计算新的等级
                
                new_level = calculate_level(new_exp, LEVEL_SYSTEM_CONFIG["exp_per_level"])
                
                # 更新经验值和等级
                update_query = "UPDATE basic_info SET experience = ?, level = ? WHERE id = 1"
                execute_update(update_query, (new_exp, new_level))
                
                print(f"经验值更新: {current_exp} -> {new_exp}, 等级: {new_level}")
            else:
                print("未找到用户基本信息")
                
        except Exception as e:
            print(f"更新经验值失败: {e}")
    
    def refresh_stats_display(self):
        """刷新统计信息显示"""
        try:
            # 清空现有内容
            self.main_system.gui.stats_text.delete(1.0, tk.END)
            
            # 获取目标统计
            goal_stats = self.get_goal_statistics()
            
            # 获取每日任务统计
            daily_task_stats = self.get_daily_task_statistics()
            
            # 获取用户等级信息
            user_level_info = self.get_user_level_info()
            
            # 显示统计信息
            stats_content = f"""
=== 目标统计 ===
{goal_stats}

=== 每日任务统计 ===
{daily_task_stats}

=== 用户等级信息 ===
{user_level_info}
"""
            
            self.main_system.gui.stats_text.insert(tk.END, stats_content)
            
        except Exception as e:
            print(f"刷新统计信息显示失败: {e}")
            self.main_system.gui.stats_text.insert(tk.END, f"刷新统计信息失败: {e}")
    
    def get_goal_statistics(self):
        """获取目标统计信息"""
        try:
            query = """
                SELECT 
                    COUNT(*) as total_goals,
                    SUM(CASE WHEN status = '已完成' THEN 1 ELSE 0 END) as completed_goals,
                    SUM(CASE WHEN status = '进行中' THEN 1 ELSE 0 END) as in_progress_goals,
                    goal_type
                FROM goals 
                GROUP BY goal_type
            """
            results = execute_query(query)
            
            stats_text = ""
            for row in results:
                total = row['total_goals'] or 0
                completed = row['completed_goals'] or 0
                in_progress = row['in_progress_goals'] or 0
                goal_type = row['goal_type'] or "未知"
                
                completion_rate = (completed / total) * 100 if total > 0 else 0
                
                stats_text += f"{goal_type}: 总计{total}个, 已完成{completed}个, 进行中{in_progress}个, 完成率{completion_rate:.1f}%\n"
            
            return stats_text if stats_text else "暂无目标数据"
            
        except Exception as e:
            print(f"获取目标统计失败: {e}")
            return f"获取目标统计失败: {e}"
    
    def get_daily_task_statistics(self):
        """获取每日任务统计信息"""
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            query = """
                SELECT 
                    COUNT(*) as total_tasks,
                    SUM(CASE WHEN status = '已完成' THEN 1 ELSE 0 END) as completed_tasks,
                    SUM(CASE WHEN status = '未完成' THEN 1 ELSE 0 END) as in_progress_tasks
                FROM daily_tasks 
                WHERE task_date = ?
            """
            results = execute_query(query, (current_date,))
            
            if results:
                row = results[0]
                total = row['total_tasks'] or 0
                completed = row['completed_tasks'] or 0
                in_progress = row['in_progress_tasks'] or 0
                
                completion_rate = (completed / total) * 100 if total > 0 else 0
                
                return f"今日任务: 总计{total}个, 已完成{completed}个, 未完成{in_progress}个, 完成率{completion_rate:.1f}%"
            else:
                return "今日暂无任务数据"
                
        except Exception as e:
            print(f"获取每日任务统计失败: {e}")
            return f"获取每日任务统计失败: {e}"
    
    def get_user_level_info(self):
        """获取用户等级信息"""
        try:
            query = "SELECT experience FROM basic_info WHERE id = 1"
            result = execute_query(query)
            
            if result:
                experience = result[0]['experience'] or 0
                
                # 计算当前等级
                current_level = calculate_level(experience, LEVEL_SYSTEM_CONFIG["exp_per_level"])
                
                # 使用等级计算工具获取正确的等级信息
                level_info = format_level_info(current_level, experience, LEVEL_SYSTEM_CONFIG["exp_per_level"])
                
                return f"当前等级: {current_level}\n当前经验: {experience}\n"
            else:
                return "未找到用户等级信息"
                
        except Exception as e:
            print(f"获取用户等级信息失败: {e}")
            return f"获取用户等级信息失败: {e}" 