#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
总结管理模块
提供总结的保存、加载和管理功能
"""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime, date
import os
from src.utils.database import execute_query, execute_insert, execute_update
from src.utils.config import SUMMARY_CONFIG, EXP_REWARD_CONFIG
from src.utils.summary_utils import write_summary_to_file


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
    
    def load_summary_from_md(self, summary_date):
        """从md文件加载总结"""
        try:
            # 获取应用程序路径
            app_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            doc_dir = os.path.join(app_path, "doc")
            
            # 根据年份获取md文件路径
            year = summary_date.split('-')[0]
            md_file_path = os.path.join(doc_dir, f"{year}.md")
            
            if not os.path.exists(md_file_path):
                return ""
            
            # 读取文件内容并查找对应日期的总结
            with open(md_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单的查找逻辑，可以根据需要优化
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip() == f"## {summary_date}":
                    # 找到日期，收集后续内容直到下一个日期或文件结束
                    summary_content = []
                    j = i + 1
                    while j < len(lines) and not lines[j].strip().startswith('##'):
                        summary_content.append(lines[j])
                        j += 1
                    return '\n'.join(summary_content).strip()
            
            return ""
                
        except Exception as e:
            print(f"从md文件加载总结失败: {e}")
            return ""
    
    def get_summary_list_from_md(self, limit=50):
        """从md文件获取总结列表"""
        try:
            # 获取应用程序路径
            app_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            doc_dir = os.path.join(app_path, "doc")
            
            summaries = []
            
            # 遍历doc目录下的所有md文件
            for filename in os.listdir(doc_dir):
                if filename.endswith('.md'):
                    md_file_path = os.path.join(doc_dir, filename)
                    with open(md_file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 简单的解析逻辑，可以根据需要优化
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if line.strip().startswith('## '):
                            date_str = line.strip()[3:]  # 去掉 "## "
                            # 收集该日期的总结内容
                            summary_content = []
                            j = i + 1
                            while j < len(lines) and not lines[j].strip().startswith('##'):
                                summary_content.append(lines[j])
                                j += 1
                            
                            summaries.append({
                                'content': '\n'.join(summary_content).strip(),
                                'summary_date': date_str,
                                'created_at': date_str  # 使用日期作为创建时间
                            })
            
            # 按日期排序并限制数量
            summaries.sort(key=lambda x: x['summary_date'], reverse=True)
            return summaries[:limit]
            
        except Exception as e:
            print(f"从md文件获取总结列表失败: {e}")
            return []
    
    def delete_summary_from_md(self, summary_date):
        """从md文件删除总结"""
        try:
            # 获取应用程序路径
            app_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            doc_dir = os.path.join(app_path, "doc")
            
            # 根据年份获取md文件路径
            year = summary_date.split('-')[0]
            md_file_path = os.path.join(doc_dir, f"{year}.md")
            
            if not os.path.exists(md_file_path):
                messagebox.showwarning("警告", "未找到对应的md文件")
                return False
            
            # 读取文件内容
            with open(md_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 删除指定日期的总结
            lines = content.split('\n')
            new_lines = []
            skip_section = False
            
            for line in lines:
                if line.strip() == f"## {summary_date}":
                    skip_section = True
                    continue
                elif line.strip().startswith('## ') and skip_section:
                    skip_section = False
                    new_lines.append(line)
                elif not skip_section:
                    new_lines.append(line)
            
            # 写回文件
            with open(md_file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            
            messagebox.showinfo("成功", "总结已从md文件删除！")
            return True
                
        except Exception as e:
            messagebox.showerror("错误", f"从md文件删除总结失败: {e}")
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
            # 获取应用程序路径
            app_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            doc_dir = os.path.join(app_path, "doc")
            
            if not os.path.exists(doc_dir):
                return "暂无总结数据"
            
            total_count = 0
            meaningful_count = 0
            
            # 遍历doc目录下的所有md文件
            for filename in os.listdir(doc_dir):
                if filename.endswith('.md'):
                    md_file_path = os.path.join(doc_dir, filename)
                    with open(md_file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 统计总结数量
                    lines = content.split('\n')
                    for line in lines:
                        if line.strip().startswith('## '):
                            total_count += 1
                            # 检查是否有有意义的内容（简单判断）
                            # 这里可以根据需要优化判断逻辑
                            meaningful_count += 1
            
            if total_count > 0:
                return f"总结统计: 总计{total_count}个, 有意义{meaningful_count}个"
            else:
                return "暂无总结数据"
            
        except Exception as e:
            print(f"获取总结统计失败: {e}")
            return f"获取总结统计失败: {e}"
    
    def write_summary_to_md_file(self, content, summary_date):
        """将总结写入md文件"""
        try:
            # 获取应用程序路径
            app_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            doc_dir = os.path.join(app_path, "doc")
            
            # 确保doc目录存在
            if not os.path.exists(doc_dir):
                os.makedirs(doc_dir)
            
            # 根据年份创建md文件
            year = summary_date.split('-')[0]
            md_file_path = os.path.join(doc_dir, f"{year}.md")
            
            # 写入md文件
            write_summary_to_file(md_file_path, content, "", summary_date)
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
