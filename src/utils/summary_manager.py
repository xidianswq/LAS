#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
总结管理模块
提供总结的保存、加载和管理功能
"""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import os
from src.utils.database import execute_query, execute_update
from src.utils.config import EXP_REWARD_CONFIG


def read_summary_file(file_path: str) -> str:
    """
    读取总结文件内容
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件内容字符串
    """
    if not os.path.exists(file_path):
        return ""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"读取文件失败: {e}")
        return ""


def write_summary_to_file(file_path: str, content: str, date: str = ""):
    """
    将总结内容写入文件，在开头添加新内容，在结尾添加空行
    
    Args:
        file_path: 文件路径
        content: 总结内容
        date: 日期（可选）
    """
    # 确保doc文件夹存在
    doc_dir = os.path.dirname(file_path)
    if doc_dir and not os.path.exists(doc_dir):
        os.makedirs(doc_dir, exist_ok=True)
    
    # 读取现有内容
    existing_content = read_summary_file(file_path)
    
    # 构建新内容，使用Markdown格式
    new_entry = ""
    if date:
        new_entry += f"{date}\n"
    new_entry += f"{content}\n"
    new_entry += '\n\n\n'
    
    # 确保文件结尾有空行
    if not existing_content.endswith('\n'):
        new_entry += '\n'
    
    # 写入文件：新内容在开头，现有内容在后面，确保结尾有空行
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_entry + existing_content)
    except Exception as e:
        print(f"写入文件失败: {e}")


class SummaryManager:
    """总结管理器"""
    
    def __init__(self, main_system):
        self.main_system = main_system
        
    def save_summary(self, content, summary_date):
        """保存总结到md文件"""
        try:
            if not content.strip():
                messagebox.showwarning("警告", "请输入总结内容")
                return False
            
            # 直接写入md文件
            self.write_summary_to_md_file(content, summary_date)
            messagebox.showinfo("成功", "总结已保存到md文件！")
            # 给予经验值奖励
            self.give_summary_reward()
            return True
                    
        except Exception as e:
            messagebox.showerror("错误", f"保存总结失败: {e}")
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

    def write_summary_to_md_file(self, content, summary_date):
        """将总结写入md文件"""
        try:
            # 使用正确的路径配置获取应用程序路径
            from src.utils.config import get_app_path
            app_path = get_app_path()
            doc_dir = os.path.join(app_path, "doc")
            
            # 确保doc目录存在
            if not os.path.exists(doc_dir):
                os.makedirs(doc_dir)
            
            # 根据年份创建md文件
            year = summary_date.split('-')[0]
            md_file_path = os.path.join(doc_dir, f"{year}.md")
            
            # 确保文件存在，如果不存在则创建
            if not os.path.exists(md_file_path):
                open(md_file_path, 'w', encoding='utf-8')
            # 写入md文件
            write_summary_to_file(md_file_path, content, summary_date)
            print(f"总结已写入md文件: {md_file_path}")
            
        except Exception as e:
            print(f"写入md文件失败: {e}")
    
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
    
    def save_summary_with_validation(self):
        """保存总结（包含验证）"""
        try:
            # 获取表单数据
            summary_date = self.main_system.gui.summary_date_var.get().strip()
            content = self.main_system.gui.summary_content_text.get(1.0, tk.END).strip()
            
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
            success = self.save_summary(content, formatted_date)
            
            if success:
                # 清空表单
                self.clear_summary_form()
                
                # 通知数据变更
                self.main_system.notify_data_changed("summary_added")
                
        except Exception as e:
            messagebox.showerror("错误", f"保存总结失败: {e}")
