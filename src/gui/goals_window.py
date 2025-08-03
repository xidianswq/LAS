# -*- coding: utf-8 -*-
"""
目标管理窗口模块
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.utils.config import GOAL_CONFIG, WINDOW_CONFIG
from src.utils.database import execute_insert, execute_query, execute_update

class GoalsWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent.root)
        self.window.title(WINDOW_CONFIG["goals_window"]["title"])
        self.window.geometry(WINDOW_CONFIG["goals_window"]["geometry"])
        self.window.resizable(True, True)
        
        # 设置最小窗口大小
        self.window.minsize(WINDOW_CONFIG["goals_window"]["min_width"], WINDOW_CONFIG["goals_window"]["min_height"])
        
        # 注册到主窗口的事件监听器
        if hasattr(parent, 'register_window_for_updates'):
            parent.register_window_for_updates(self)
        
        # 创建界面
        self.create_gui()
        self.refresh_goals()
        
    def create_gui(self):
        """创建目标管理界面"""
        # 标题
        title_label = ttk.Label(self.window, text="目标管理", font=("Arial", 14, "bold"))
        title_label.pack(pady=5)
        
        # 主框架
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # 目标列表区域
        goals_frame = ttk.LabelFrame(main_frame, text="目标列表", padding=5)
        goals_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建目标列表和操作按钮
        self.create_goals_list(goals_frame)
        
        # 添加目标区域 - 移到目标列表下方
        add_goal_frame = ttk.LabelFrame(main_frame, text="添加目标", padding=5)
        add_goal_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.create_goal_form(add_goal_frame)
        
    def create_goal_form(self, parent):
        """创建目标表单"""
        # 创建水平布局框架
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=tk.X)
        
        # 左侧：输入字段
        left_fields = ttk.Frame(form_frame)
        left_fields.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 目标标题
        title_frame = ttk.Frame(left_fields)
        title_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(title_frame, text="标题:").pack(side=tk.LEFT)
        self.title_var = tk.StringVar()
        title_entry = ttk.Entry(title_frame, textvariable=self.title_var, width=30)
        title_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # 目标类型
        type_frame = ttk.Frame(left_fields)
        type_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(type_frame, text="类型:").pack(side=tk.LEFT)
        self.type_var = tk.StringVar(value=GOAL_CONFIG["goal_types"][0])
        self.type_combo = ttk.Combobox(type_frame, textvariable=self.type_var, values=GOAL_CONFIG["goal_types"], state="readonly", width=27)
        self.type_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # 描述
        desc_frame = ttk.Frame(left_fields)
        desc_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(desc_frame, text="描述:").pack(side=tk.LEFT)
        self.description_var = tk.StringVar()
        desc_entry = ttk.Entry(desc_frame, textvariable=self.description_var, width=30)
        desc_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # 优先级
        priority_frame = ttk.Frame(left_fields)
        priority_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(priority_frame, text="优先级:").pack(side=tk.LEFT)
        self.priority_var = tk.StringVar(value=GOAL_CONFIG["priority_levels"][1])  # 默认中等
        priority_combo = ttk.Combobox(priority_frame, textvariable=self.priority_var, values=GOAL_CONFIG["priority_levels"], state="readonly", width=26)
        priority_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # 右侧：按钮
        right_buttons = ttk.Frame(form_frame)
        right_buttons.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        ttk.Button(right_buttons, text="添加目标", command=self.add_goal, width=12).pack(fill=tk.X, pady=(0, 3))
        ttk.Button(right_buttons, text="清空", command=self.clear_form, width=12).pack(fill=tk.X)
        
    def create_goals_list(self, parent):
        """创建目标列表"""
        # 创建水平布局框架
        list_button_frame = ttk.Frame(parent)
        list_button_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧：目标列表
        list_frame = ttk.Frame(list_button_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 创建树形视图
        columns = ("ID", "标题", "类型", "描述", "状态", "优先级", "创建时间")
        self.goals_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        
        # 设置列标题和宽度
        column_widths = {
            "ID": 40,
            "标题": 120,
            "类型": 80,
            "描述": 150,
            "状态": 70,
            "优先级": 50,
            "创建时间": 100
        }
        
        for col in columns:
            self.goals_tree.heading(col, text=col)
            self.goals_tree.column(col, width=column_widths.get(col, 80))
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.goals_tree.yview)
        self.goals_tree.configure(yscrollcommand=scrollbar.set)
        
        self.goals_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定选择事件
        self.goals_tree.bind('<<TreeviewSelect>>', self.on_goal_select)
        
        # 绑定双击事件
        self.goals_tree.bind('<Double-1>', self.on_goal_double_click)
        
        # 右侧：操作按钮
        button_frame = ttk.Frame(list_button_frame)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        ttk.Button(button_frame, text="编辑目标", command=self.edit_selected_goal, width=12).pack(fill=tk.X, pady=(0, 3))
        ttk.Button(button_frame, text="标记完成", command=self.mark_as_completed, width=12).pack(fill=tk.X, pady=(0, 3))
        ttk.Button(button_frame, text="标记进行中", command=self.mark_as_in_progress, width=12).pack(fill=tk.X, pady=(0, 3))
        ttk.Button(button_frame, text="删除目标", command=self.delete_selected_goal, width=12).pack(fill=tk.X, pady=(0, 3))
        ttk.Button(button_frame, text="关闭", command=self.window.destroy, width=12).pack(fill=tk.X)
        
    def add_goal(self):
        """添加目标"""
        title = self.title_var.get().strip()
        goal_type = self.type_var.get().strip()
        description = self.description_var.get().strip()
        priority = self.priority_var.get().strip()
        
        if not title:
            messagebox.showwarning("警告", "请输入目标标题")
            return
            
        if not goal_type:
            messagebox.showwarning("警告", "请选择目标类型")
            return
        
        try:
            # 插入目标
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            query = """
                INSERT INTO goals (title, goal_type, description, status, priority, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            goal_id = execute_insert(query, (
                title, goal_type, description, "进行中", priority,
                current_time, current_time
            ))
            
            if goal_id:
                # 清空表单
                self.clear_form()
                
                # 通知所有监听器数据已变更
                if hasattr(self.parent, 'notify_data_changed'):
                    print("📢 通知数据变更：目标已添加")
                    self.parent.notify_data_changed("goal_added")
                
                # 立即刷新目标列表
                self.refresh_goals()
                
                print("✅ 目标添加成功")
            else:
                messagebox.showerror("错误", "添加目标失败")
                
        except Exception as e:
            messagebox.showerror("错误", f"添加目标失败: {e}")
            
    def clear_form(self):
        """清空表单"""
        self.title_var.set("")
        self.type_var.set(GOAL_CONFIG["goal_types"][0])
        self.description_var.set("")
        self.priority_var.set(GOAL_CONFIG["priority_levels"][1])
        
    def refresh_goals(self):
        """刷新目标列表"""
        try:
            print("🔄 开始刷新目标列表...")
            # 清空现有数据
            for item in self.goals_tree.get_children():
                self.goals_tree.delete(item)
            
            # 查询所有目标
            query = "SELECT * FROM goals ORDER BY created_at DESC"
            goals = execute_query(query)
            
            print(f"📊 查询到 {len(goals)} 个目标")
            
            # 添加到树形视图
            for goal in goals:
                self.goals_tree.insert("", "end", values=(
                    goal['id'],
                    goal['title'],
                    goal['goal_type'],
                    goal['description'],
                    goal['status'],
                    goal['priority'],
                    goal['created_at']
                ))
            
            print("✅ 目标列表刷新完成")
                
        except Exception as e:
            print(f"❌ 刷新目标列表失败: {e}")
            messagebox.showerror("错误", f"加载目标列表失败: {e}")
    
    def on_data_changed(self, event_type="data_changed"):
        """处理数据变更事件"""
        print(f"🎯 目标窗口收到数据变更通知: {event_type}")
        
        if event_type in ["goal_changed", "data_changed"]:
            try:
                # 检查窗口是否仍然存在
                if hasattr(self, 'window') and self.window.winfo_exists():
                    print("🔄 刷新目标列表...")
                    self.refresh_goals()
                    print("✅ 目标列表刷新完成")
                else:
                    print("⚠️ 窗口已不存在，跳过刷新")
            except tk.TclError:
                print("⚠️ 窗口已被销毁，跳过刷新")
            except Exception as e:
                print(f"❌ 刷新目标列表失败: {e}")
                messagebox.showerror("错误", f"刷新目标列表失败: {e}")
    
    def on_goal_select(self, event):
        """处理目标选择事件"""
        selected = self.goals_tree.selection()
        if selected:
            item = self.goals_tree.item(selected[0])
            goal_id = item['values'][0]
            # 可以在这里添加选中目标的详细信息显示
    
    def on_goal_double_click(self, event):
        """处理目标双击事件"""
        selected = self.goals_tree.selection()
        if selected:
            item = self.goals_tree.item(selected[0])
            goal_id = item['values'][0]
            # 打开编辑窗口
            EditGoalWindow(self, goal_id)
    
    def edit_selected_goal(self):
        """编辑选中的目标"""
        selected = self.goals_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个目标")
            return
            
        # 获取选中的目标ID
        item = self.goals_tree.item(selected[0])
        goal_id = item['values'][0]
        
        # 打开编辑窗口
        EditGoalWindow(self, goal_id)
        
    def mark_as_completed(self):
        """标记目标为已完成"""
        selected = self.goals_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个目标")
            return
            
        # 获取选中的目标ID
        item = self.goals_tree.item(selected[0])
        goal_id = item['values'][0]
        goal_title = item['values'][1]
        
        # 根据优先级获取经验值奖励
        goal_priority = item['values'][5]  # 优先级在索引5
        priority_levels = GOAL_CONFIG["priority_levels"]
        experience_rewards = GOAL_CONFIG["experience_reward"]
        
        # 根据优先级获取对应的经验值奖励
        try:
            priority_index = priority_levels.index(goal_priority)
            exp_reward = experience_rewards[priority_index]
        except (ValueError, IndexError):
            # 如果优先级不在列表中或索引超出范围，使用默认值
            exp_reward = experience_rewards[1]  # 默认使用中等优先级奖励

        try:
            # 更新目标状态
            query = "UPDATE goals SET status = '已完成', updated_at = ? WHERE id = ?"
            execute_update(query, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), goal_id))

            # 给予经验值奖励
            if hasattr(self.parent, 'update_user_experience'):
                self.parent.update_user_experience(exp_reward)
                messagebox.showinfo("目标完成", f"恭喜！目标 '{goal_title}' 已完成！\n获得经验值: {exp_reward}")
            
            # 通知所有监听器数据已变更
            if hasattr(self.parent, 'notify_data_changed'):
                print("📢 通知数据变更：目标状态已更新")
                self.parent.notify_data_changed("goal_changed")
            
            # 立即刷新目标列表
            self.refresh_goals()
        except Exception as e:
            messagebox.showerror("错误", f"更新目标状态失败: {e}")
    
    def mark_as_in_progress(self):
        """标记目标为进行中"""
        selected = self.goals_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个目标")
            return
            
        # 获取选中的目标ID
        item = self.goals_tree.item(selected[0])
        goal_id = item['values'][0]

        try:
            # 更新目标状态
            query = "UPDATE goals SET status = '进行中', updated_at = ? WHERE id = ?"
            execute_update(query, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), goal_id))

            # 通知所有监听器数据已变更
            if hasattr(self.parent, 'notify_data_changed'):
                print("📢 通知数据变更：目标状态已更新")
                self.parent.notify_data_changed("goal_changed")
            
            # 立即刷新目标列表
            self.refresh_goals()
        except Exception as e:
            messagebox.showerror("错误", f"更新目标状态失败: {e}")
    
    def delete_selected_goal(self):
        """删除选中的目标"""
        selected = self.goals_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个目标")
            return
            
        # 获取选中的目标ID
        item = self.goals_tree.item(selected[0])
        goal_id = item['values'][0]
        goal_title = item['values'][1]
        
        if messagebox.askyesno("确认", f"确定要删除目标 '{goal_title}' 吗？"):
            try:
                # 删除目标
                query = "DELETE FROM goals WHERE id = ?"
                execute_update(query, (goal_id,))
                
                messagebox.showinfo("成功", "目标已删除！")
                # 通知所有监听器数据已变更
                if hasattr(self.parent, 'notify_data_changed'):
                    print("📢 通知数据变更：目标已删除")
                    self.parent.notify_data_changed("goal_deleted")
                
                # 立即刷新目标列表
                self.refresh_goals()
            except Exception as e:
                messagebox.showerror("错误", f"删除目标失败: {e}")


class EditGoalWindow:
    def __init__(self, parent, goal_id):
        self.parent = parent
        self.goal_id = goal_id
        self.window = tk.Toplevel(parent.window)
        self.window.title("编辑目标")
        self.window.geometry(WINDOW_CONFIG["goals_window"]["edit_geometry"])
        
        # 创建界面
        self.create_gui()
        self.load_goal_data()
        
    def create_gui(self):
        """创建编辑目标界面"""
        # 标题
        ttk.Label(self.window, text="编辑目标", font=("Arial", 12, "bold")).pack(pady=5)
        
        # 表单框架
        form_frame = ttk.Frame(self.window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        # 目标信息输入
        ttk.Label(form_frame, text="标题:").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.title_entry = ttk.Entry(form_frame, width=30)
        self.title_entry.grid(row=0, column=1, pady=3, padx=(8, 0))
        
        ttk.Label(form_frame, text="类型:").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.type_var = tk.StringVar(value=GOAL_CONFIG["goal_types"][0])
        type_combo = ttk.Combobox(form_frame, textvariable=self.type_var, values=GOAL_CONFIG["goal_types"], width=27)
        type_combo.grid(row=1, column=1, pady=3, padx=(8, 0))
        
        ttk.Label(form_frame, text="描述:").grid(row=2, column=0, sticky=tk.W, pady=3)
        self.description_entry = ttk.Entry(form_frame, width=30)
        self.description_entry.grid(row=2, column=1, pady=3, padx=(8, 0))
        
        ttk.Label(form_frame, text="状态:").grid(row=3, column=0, sticky=tk.W, pady=3)
        self.status_var = tk.StringVar(value="进行中")
        status_combo = ttk.Combobox(form_frame, textvariable=self.status_var, values=GOAL_CONFIG["status_options"], width=27)
        status_combo.grid(row=3, column=1, pady=3, padx=(8, 0))
        
        ttk.Label(form_frame, text="优先级:").grid(row=4, column=0, sticky=tk.W, pady=3)
        self.priority_var = tk.StringVar(value="中")
        priority_combo = ttk.Combobox(form_frame, textvariable=self.priority_var, values=GOAL_CONFIG["priority_levels"], width=27)
        priority_combo.grid(row=4, column=1, pady=3, padx=(8, 0))
        
        # 按钮
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        ttk.Button(button_frame, text="保存", command=self.save_goal).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(button_frame, text="取消", command=self.window.destroy).pack(side=tk.LEFT)
        
    def load_goal_data(self):
        """加载目标数据"""
        try:
            query = "SELECT * FROM goals WHERE id = ?"
            result = execute_query(query, (self.goal_id,))
            
            if result:
                goal = result[0]
                self.title_entry.insert(0, goal['title'] or "")
                self.type_var.set(goal['goal_type'] or GOAL_CONFIG["goal_types"][0])
                self.description_entry.insert(0, goal['description'] or "")
                self.status_var.set(goal['status'] or "进行中")
                self.priority_var.set(goal['priority'] or "中")
            else:
                messagebox.showerror("错误", "未找到目标信息")
                self.window.destroy()
        except Exception as e:
            messagebox.showerror("错误", f"加载目标数据失败: {e}")
            self.window.destroy()
            
    def save_goal(self):
        """保存目标"""
        title = self.title_entry.get().strip()
        goal_type = self.type_var.get()
        description = self.description_entry.get().strip()
        status = self.status_var.get()
        priority = self.priority_var.get()
        
        if not title:
            messagebox.showwarning("警告", "请输入目标标题")
            return
            
        try:
            # 更新目标
            query = """
                UPDATE goals 
                SET title = ?, goal_type = ?, description = ?, status = ?, 
                    priority = ?, updated_at = ?
                WHERE id = ?
            """
            execute_update(query, (
                title, goal_type, description, status, priority,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.goal_id
            ))
            
            # 通知所有监听器数据已变更
            if hasattr(self.parent, 'parent') and hasattr(self.parent.parent, 'notify_data_changed'):
                print("📢 通知数据变更：目标已编辑")
                self.parent.parent.notify_data_changed("goal_edited")
            elif hasattr(self.parent, 'notify_data_changed'):
                print("📢 通知数据变更：目标已编辑")
                self.parent.notify_data_changed("goal_edited")
            
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("错误", f"保存目标失败: {e}")
