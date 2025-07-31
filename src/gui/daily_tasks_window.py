# -*- coding: utf-8 -*-
"""
每日计划管理窗口模块
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.utils.config import DAILY_TASK_CONFIG, WINDOW_CONFIG
from src.utils.database import execute_insert, execute_query, execute_update

class DailyTasksWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent.root)
        self.window.title(WINDOW_CONFIG["daily_tasks_window"]["title"])
        self.window.geometry(WINDOW_CONFIG["daily_tasks_window"]["geometry"])
        self.window.resizable(True, True)
        
        # 设置最小窗口大小
        self.window.minsize(WINDOW_CONFIG["daily_tasks_window"]["min_width"], WINDOW_CONFIG["daily_tasks_window"]["min_height"])
        
        # 注册到主窗口的事件监听器
        if hasattr(parent, 'register_window_for_updates'):
            parent.register_window_for_updates(self)
        
        # 创建界面
        self.create_gui()
        self.refresh_tasks()
        
    def create_gui(self):
        """创建每日计划管理界面"""
        # 标题
        title_label = ttk.Label(self.window, text="每日计划管理", font=("Arial", 14, "bold"))
        title_label.pack(pady=5)
        
        # 主框架
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # 任务列表区域
        tasks_frame = ttk.LabelFrame(main_frame, text="今日任务列表", padding=5)
        tasks_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建任务列表和操作按钮
        self.create_tasks_list(tasks_frame)
        
        # 添加任务区域 - 移到任务列表下方
        add_task_frame = ttk.LabelFrame(main_frame, text="添加每日任务", padding=5)
        add_task_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.create_task_form(add_task_frame)
        
        
    def create_task_form(self, parent):
        """创建任务表单"""
        # 创建水平布局框架
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=tk.X)
        
        # 左侧：输入字段
        left_fields = ttk.Frame(form_frame)
        left_fields.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 任务标题
        title_frame = ttk.Frame(left_fields)
        title_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(title_frame, text="标题:").pack(side=tk.LEFT)
        self.title_var = tk.StringVar()
        title_entry = ttk.Entry(title_frame, textvariable=self.title_var, width=30)
        title_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # 任务描述
        desc_frame = ttk.Frame(left_fields)
        desc_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(desc_frame, text="描述:").pack(side=tk.LEFT)
        self.description_var = tk.StringVar()
        desc_entry = ttk.Entry(desc_frame, textvariable=self.description_var, width=30)
        desc_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # 优先级
        priority_exp_frame = ttk.Frame(left_fields)
        priority_exp_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(priority_exp_frame, text="优先级:").pack(side=tk.LEFT)
        self.priority_var = tk.StringVar(value="中")
        priority_combo = ttk.Combobox(priority_exp_frame, textvariable=self.priority_var, 
                                     values=["高", "中", "低"], state="readonly", width=26)
        priority_combo.pack(side=tk.LEFT, padx=(5, 10))

        
        # 右侧：按钮
        right_buttons = ttk.Frame(form_frame)
        right_buttons.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        ttk.Button(right_buttons, text="添加任务", command=self.add_task, width=12).pack(fill=tk.X, pady=(0, 3))
        ttk.Button(right_buttons, text="清空", command=self.clear_form, width=12).pack(fill=tk.X)
        
    def create_tasks_list(self, parent):
        """创建任务列表"""
        # 创建水平布局框架
        list_button_frame = ttk.Frame(parent)
        list_button_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧：任务列表
        list_frame = ttk.Frame(list_button_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 创建树形视图
        columns = ("ID", "标题", "描述", "优先级", "状态")
        self.tasks_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        
        # 设置列标题和宽度
        column_widths = {
            "ID": 10,
            "标题": 200,
            "描述": 200,
            "优先级": 10,
            "状态": 20
        }
        
        for col in columns:
            self.tasks_tree.heading(col, text=col)
            self.tasks_tree.column(col, width=column_widths.get(col, 80))
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tasks_tree.yview)
        self.tasks_tree.configure(yscrollcommand=scrollbar.set)
        
        self.tasks_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定选择事件
        self.tasks_tree.bind('<<TreeviewSelect>>', self.on_task_select)
        
        # 绑定双击事件
        self.tasks_tree.bind('<Double-1>', self.on_task_double_click)
        
        # 右侧：操作按钮区域 - 竖向排列
        button_frame = ttk.Frame(list_button_frame)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        # 竖向排列的按钮
        ttk.Button(button_frame, text="编辑任务", command=self.edit_selected_task, width=12).pack(fill=tk.X, pady=(0, 3))
        ttk.Button(button_frame, text="标记完成", command=self.mark_as_completed, width=12).pack(fill=tk.X, pady=(0, 3))
        ttk.Button(button_frame, text="标记未完成", command=self.mark_as_incomplete, width=12).pack(fill=tk.X, pady=(0, 3))
        ttk.Button(button_frame, text="删除任务", command=self.delete_selected_task, width=12).pack(fill=tk.X, pady=(0, 3))
        ttk.Button(button_frame, text="关闭", command=self.window.destroy, width=12).pack(fill=tk.X, pady=(0, 3))
        
    def add_task(self):
        """添加任务"""
        title = self.title_var.get().strip()
        description = self.description_var.get().strip()
        priority = self.priority_var.get().strip()
        
        if not title:
            messagebox.showwarning("警告", "请输入任务标题")
            return
        
        try:
            # 插入任务
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            # 根据优先级计算经验值奖励
            priority_levels = DAILY_TASK_CONFIG["priority_levels"]
            experience_rewards = DAILY_TASK_CONFIG["experience_reward"]
            try:
                priority_index = priority_levels.index(priority)
                exp_reward = experience_rewards[priority_index]
            except (ValueError, IndexError):
                exp_reward = experience_rewards[1]  # 默认使用中等优先级奖励
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            query = """
                INSERT INTO daily_tasks (title, description, status, priority, task_date, 
                                       experience_reward, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            task_id = execute_insert(query, (
                title, description, "未完成", priority, current_date,
                exp_reward, current_time, current_time
            ))
            
            if task_id:
                # 清空表单
                self.clear_form()
                
                # 通知所有监听器数据已变更
                if hasattr(self.parent, 'notify_data_changed'):
                    print("📢 通知数据变更：每日任务已添加")
                    self.parent.notify_data_changed("daily_task_added")
                
                # 立即刷新任务列表
                self.refresh_tasks()
                
                print("✅ 每日任务添加成功")
            else:
                messagebox.showerror("错误", "添加任务失败")
                
        except Exception as e:
            messagebox.showerror("错误", f"添加任务失败: {e}")
            
    def clear_form(self):
        """清空表单"""
        self.title_var.set("")
        self.description_var.set("")
        self.priority_var.set("中")
        
    def refresh_tasks(self):
        """刷新任务列表"""
        try:
            print("🔄 开始刷新每日任务列表...")
            # 清空现有数据
            for item in self.tasks_tree.get_children():
                self.tasks_tree.delete(item)
            
            # 查询今日任务
            current_date = datetime.now().strftime("%Y-%m-%d")
            query = "SELECT * FROM daily_tasks WHERE task_date = ? ORDER BY created_at DESC"
            tasks = execute_query(query, (current_date,))
            
            print(f"📊 查询到 {len(tasks)} 个今日任务")
            
            # 添加到树形视图
            for task in tasks:
                status_icon = "✓" if task['status'] == "已完成" else "✗"
                status_text = f"{status_icon} {task['status']}"
                
                self.tasks_tree.insert("", "end", values=(
                    task['id'],
                    task['title'],
                    task['description'],
                    task['priority'],
                    status_text
                ))
            
            print("✅ 每日任务列表刷新完成")
                
        except Exception as e:
            print(f"❌ 刷新每日任务列表失败: {e}")
            messagebox.showerror("错误", f"加载任务列表失败: {e}")
    
    def on_data_changed(self, event_type="data_changed"):
        """处理数据变更事件"""
        print(f"📅 每日任务窗口收到数据变更通知: {event_type}")
        
        if event_type in ["daily_task_changed", "data_changed"]:
            try:
                # 检查窗口是否仍然存在
                if hasattr(self, 'window') and self.window.winfo_exists():
                    print("🔄 刷新每日任务列表...")
                    self.refresh_tasks()
                    print("✅ 每日任务列表刷新完成")
                else:
                    print("⚠️ 窗口已不存在，跳过刷新")
            except tk.TclError:
                print("⚠️ 窗口已被销毁，跳过刷新")
            except Exception as e:
                print(f"❌ 刷新每日任务列表失败: {e}")
                messagebox.showerror("错误", f"刷新每日任务列表失败: {e}")
    
    def on_task_select(self, event):
        """处理任务选择事件"""
        selected = self.tasks_tree.selection()
        if selected:
            item = self.tasks_tree.item(selected[0])
            task_id = item['values'][0]
            # 可以在这里添加选中任务的详细信息显示
    
    def on_task_double_click(self, event):
        """处理任务列表的双击事件"""
        selected = self.tasks_tree.selection()
        if selected:
            item = self.tasks_tree.item(selected[0])
            task_id = item['values'][0]
            self.edit_selected_task()
    
    def edit_selected_task(self):
        """编辑选中的任务"""
        selected = self.tasks_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个任务")
            return
            
        # 获取选中的任务ID
        item = self.tasks_tree.item(selected[0])
        task_id = item['values'][0]
        
        # 打开编辑窗口
        EditDailyTaskWindow(self, task_id)
        
    def mark_as_completed(self):
        """标记任务为已完成"""
        selected = self.tasks_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个任务")
            return
            
        # 获取选中的任务ID
        item = self.tasks_tree.item(selected[0])
        task_id = item['values'][0]
        task_title = item['values'][1]
        # 根据优先级获取经验值奖励
        task_priority = item['values'][3]  # 优先级在索引3
        priority_levels = DAILY_TASK_CONFIG["priority_levels"]
        experience_rewards = DAILY_TASK_CONFIG["experience_reward"]
        
        # 根据优先级获取对应的经验值奖励
        try:
            priority_index = priority_levels.index(task_priority)
            exp_reward = experience_rewards[priority_index]
        except (ValueError, IndexError):
            # 如果优先级不在列表中或索引超出范围，使用默认值
            exp_reward = DAILY_TASK_CONFIG["experience_reward"][1]  # 默认使用中等优先级奖励

        try:
            # 更新任务状态
            query = "UPDATE daily_tasks SET status = '已完成', completed_at = ?, updated_at = ? WHERE id = ?"
            execute_update(query, (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                task_id
            ))

            # 给予经验值奖励
            if hasattr(self.parent, 'update_user_experience'):
                self.parent.update_user_experience(exp_reward)
                messagebox.showinfo("任务完成", f"恭喜！任务 '{task_title}' 已完成！\n获得经验值: {exp_reward}")
            
            # 通知所有监听器数据已变更
            if hasattr(self.parent, 'notify_data_changed'):
                print("📢 通知数据变更：每日任务已完成")
                self.parent.notify_data_changed("daily_task_changed")
            
            # 立即刷新任务列表
            self.refresh_tasks()
        except Exception as e:
            messagebox.showerror("错误", f"更新任务状态失败: {e}")
    
    def mark_as_incomplete(self):
        """标记任务为未完成"""
        selected = self.tasks_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个任务")
            return
            
        # 获取选中的任务ID
        item = self.tasks_tree.item(selected[0])
        task_id = item['values'][0]

        try:
            # 更新任务状态
            query = "UPDATE daily_tasks SET status = '未完成', updated_at = ? WHERE id = ?"
            execute_update(query, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), task_id))

            # 通知所有监听器数据已变更
            if hasattr(self.parent, 'notify_data_changed'):
                print("📢 通知数据变更：每日任务状态已更新")
                self.parent.notify_data_changed("daily_task_changed")
            
            # 立即刷新任务列表
            self.refresh_tasks()
        except Exception as e:
            messagebox.showerror("错误", f"更新任务状态失败: {e}")
    
    def delete_selected_task(self):
        """删除选中的任务"""
        selected = self.tasks_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个任务")
            return
            
        # 获取选中的任务ID
        item = self.tasks_tree.item(selected[0])
        task_id = item['values'][0]
        task_title = item['values'][1]
        
        if messagebox.askyesno("确认", f"确定要删除任务 '{task_title}' 吗？"):
            try:
                # 删除任务
                query = "DELETE FROM daily_tasks WHERE id = ?"
                execute_update(query, (task_id,))
                
                messagebox.showinfo("成功", "任务已删除！")
                # 通知所有监听器数据已变更
                if hasattr(self.parent, 'notify_data_changed'):
                    print("📢 通知数据变更：每日任务已删除")
                    self.parent.notify_data_changed("daily_task_deleted")
                
                # 立即刷新任务列表
                self.refresh_tasks()
            except Exception as e:
                messagebox.showerror("错误", f"删除任务失败: {e}")


class EditDailyTaskWindow:
    def __init__(self, parent, task_id):
        self.parent = parent
        self.task_id = task_id
        self.window = tk.Toplevel(parent.window)
        self.window.title("编辑每日任务")
        self.window.geometry(WINDOW_CONFIG["daily_tasks_window"]["edit_geometry"])
        
        # 创建界面
        self.create_gui()
        self.load_task_data()
        
    def create_gui(self):
        """创建编辑任务界面"""
        # 标题
        ttk.Label(self.window, text="编辑每日任务", font=("Arial", 12, "bold")).pack(pady=5)
        
        # 表单框架
        form_frame = ttk.Frame(self.window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        # 任务信息输入
        ttk.Label(form_frame, text="标题:").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.title_entry = ttk.Entry(form_frame, width=30)
        self.title_entry.grid(row=0, column=1, pady=3, padx=(8, 0))
        
        ttk.Label(form_frame, text="描述:").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.description_entry = ttk.Entry(form_frame, width=30)
        self.description_entry.grid(row=1, column=1, pady=3, padx=(8, 0))
        
        ttk.Label(form_frame, text="优先级:").grid(row=3, column=0, sticky=tk.W, pady=3)
        self.priority_var = tk.StringVar(value="中")
        priority_combo = ttk.Combobox(form_frame, textvariable=self.priority_var, 
                                     values=["高", "中", "低"], width=27)
        priority_combo.grid(row=3, column=1, pady=3, padx=(8, 0))

        ttk.Label(form_frame, text="状态:").grid(row=2, column=0, sticky=tk.W, pady=3)
        self.status_var = tk.StringVar(value="未完成")
        status_combo = ttk.Combobox(form_frame, textvariable=self.status_var, 
                                   values=["未完成", "已完成"], width=27)
        status_combo.grid(row=2, column=1, pady=3, padx=(8, 0))
        
        # 按钮
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        ttk.Button(button_frame, text="保存", command=self.save_task).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(button_frame, text="取消", command=self.window.destroy).pack(side=tk.LEFT)
        
    def load_task_data(self):
        """加载任务数据"""
        try:
            query = "SELECT * FROM daily_tasks WHERE id = ?"
            result = execute_query(query, (self.task_id,))
            
            if result:
                task = result[0]
                self.title_entry.insert(0, task['title'] or "")
                self.description_entry.insert(0, task['description'] or "")
                self.status_var.set(task['status'] or "未完成")
                self.priority_var.set(task['priority'] or "中")
            else:
                messagebox.showerror("错误", "未找到任务信息")
                self.window.destroy()
        except Exception as e:
            messagebox.showerror("错误", f"加载任务数据失败: {e}")
            self.window.destroy()
            
    def save_task(self):
        """保存任务"""
        title = self.title_entry.get().strip()
        description = self.description_entry.get().strip()
        status = self.status_var.get()
        priority = self.priority_var.get()
        
        if not title:
            messagebox.showwarning("警告", "请输入任务标题")
            return
            
        try:
            # 根据优先级计算经验值奖励
            priority_levels = DAILY_TASK_CONFIG["priority_levels"]
            experience_rewards = DAILY_TASK_CONFIG["experience_reward"]
            try:
                priority_index = priority_levels.index(priority)
                exp_reward = experience_rewards[priority_index]
            except (ValueError, IndexError):
                exp_reward = experience_rewards[1]  # 默认使用中等优先级奖励
            
            # 更新任务
            query = """
                UPDATE daily_tasks 
                SET title = ?, description = ?, status = ?, 
                    priority = ?, experience_reward = ?, updated_at = ?
                WHERE id = ?
            """
            execute_update(query, (
                title, description, status, priority, exp_reward,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.task_id
            ))
            
            # 通知所有监听器数据已变更
            if hasattr(self.parent, 'parent') and hasattr(self.parent.parent, 'notify_data_changed'):
                print("📢 通知数据变更：每日任务已编辑")
                self.parent.parent.notify_data_changed("daily_task_edited")
            elif hasattr(self.parent, 'notify_data_changed'):
                print("📢 通知数据变更：每日任务已编辑")
                self.parent.notify_data_changed("daily_task_edited")
            
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("错误", f"保存任务失败: {e}")
