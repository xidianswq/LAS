#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
总结管理模块
提供总结的保存、加载和管理功能
"""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime, date
from src.utils.database import execute_query, execute_insert, execute_update
from src.utils.config import SUMMARY_CONFIG, EXP_REWARD_CONFIG


class SummaryManager:
    """总结管理器"""
    
    def __init__(self, main_system):
        self.main_system = main_system
        
    def save_summary(self, summary_type, content, summary_date):
        """保存总结"""
        try:
            if not content.strip():
                messagebox.showwarning("警告", "请输入总结内容")
                return False
            
            # 检查是否已存在该日期的总结
            existing_query = "SELECT id FROM summaries WHERE summary_type = ? AND summary_date = ?"
            existing_result = execute_query(existing_query, (summary_type, summary_date))
            
            if existing_result:
                # 更新现有总结
                update_query = """
                    UPDATE summaries 
                    SET content = ?, updated_at = ?
                    WHERE summary_type = ? AND summary_date = ?
                """
                success = execute_update(update_query, (
                    content,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    summary_type,
                    summary_date
                ))
                
                if success:
                    messagebox.showinfo("成功", "总结已更新！")
                    # 给予经验值奖励
                    self.give_summary_reward()
                    return True
                else:
                    messagebox.showerror("错误", "更新总结失败")
                    return False
            else:
                # 插入新总结
                insert_query = """
                    INSERT INTO summaries (summary_type, content, summary_date, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """
                summary_id = execute_insert(insert_query, (
                    summary_type,
                    content,
                    summary_date,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))
                
                if summary_id:
                    messagebox.showinfo("成功", "总结已保存！")
                    # 给予经验值奖励
                    self.give_summary_reward()
                    return True
                else:
                    messagebox.showerror("错误", "保存总结失败")
                    return False
                    
        except Exception as e:
            messagebox.showerror("错误", f"保存总结失败: {e}")
            return False
    
    def load_summary(self, summary_type, summary_date):
        """加载总结"""
        try:
            query = "SELECT content FROM summaries WHERE summary_type = ? AND summary_date = ?"
            result = execute_query(query, (summary_type, summary_date))
            
            if result:
                return result[0]['content']
            else:
                return ""
                
        except Exception as e:
            print(f"加载总结失败: {e}")
            return ""
    
    def get_summary_list(self, summary_type=None, limit=50):
        """获取总结列表"""
        try:
            if summary_type:
                query = """
                    SELECT summary_type, content, summary_date, created_at 
                    FROM summaries 
                    WHERE summary_type = ?
                    ORDER BY created_at DESC 
                    LIMIT ?
                """
                results = execute_query(query, (summary_type, limit))
            else:
                query = """
                    SELECT summary_type, content, summary_date, created_at 
                    FROM summaries 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """
                results = execute_query(query, (limit,))
            
            return results
            
        except Exception as e:
            print(f"获取总结列表失败: {e}")
            return []
    
    def delete_summary(self, summary_type, summary_date):
        """删除总结"""
        try:
            query = "DELETE FROM summaries WHERE summary_type = ? AND summary_date = ?"
            success = execute_update(query, (summary_type, summary_date))
            
            if success:
                messagebox.showinfo("成功", "总结已删除！")
                return True
            else:
                messagebox.showerror("错误", "删除总结失败")
                return False
                
        except Exception as e:
            messagebox.showerror("错误", f"删除总结失败: {e}")
            return False
    
    def give_summary_reward(self):
        """给予总结完成奖励"""
        try:
            exp_reward = EXP_REWARD_CONFIG["summary_completion"]
            
            if hasattr(self.main_system, 'data_manager'):
                self.main_system.data_manager.update_user_experience(exp_reward)
                print(f"📝 总结完成奖励经验值: {exp_reward}")
            
        except Exception as e:
            print(f"给予总结奖励失败: {e}")
    
    def get_summary_statistics(self):
        """获取总结统计信息"""
        try:
            query = """
                SELECT 
                    summary_type,
                    COUNT(*) as total_count,
                    COUNT(CASE WHEN LENGTH(content) > 10 THEN 1 END) as meaningful_count
                FROM summaries 
                GROUP BY summary_type
            """
            results = execute_query(query)
            
            stats_text = ""
            for row in results:
                summary_type = row['summary_type']
                total_count = row['total_count']
                meaningful_count = row['meaningful_count']
                
                stats_text += f"{summary_type}: 总计{total_count}个, 有意义{meaningful_count}个\n"
            
            return stats_text if stats_text else "暂无总结数据"
            
        except Exception as e:
            print(f"获取总结统计失败: {e}")
            return f"获取总结统计失败: {e}"
    
    def clear_summary_form(self):
        """清空总结表单"""
        try:
            # 清空日期输入
            if hasattr(self.main_system, 'gui') and hasattr(self.main_system.gui, 'summary_date_var'):
                self.main_system.gui.summary_date_var.set(self.main_system.get_current_date_str())
            
            # 清空内容输入
            if hasattr(self.main_system, 'gui') and hasattr(self.main_system.gui, 'summary_content_text'):
                self.main_system.gui.summary_content_text.delete(1.0, tk.END)
                
        except Exception as e:
            print(f"清空总结表单失败: {e}")
