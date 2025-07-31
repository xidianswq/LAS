#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库管理模块
提供数据库连接、查询和更新功能
"""

import sqlite3
import os
from datetime import datetime
from src.utils.config import DATABASE_NAME, DATABASE_TABLES

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path=None):
        self.db_path = db_path or DATABASE_NAME
        self.connection = None
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        try:
            # 确保数据库目录存在
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # 检查数据库文件是否损坏
            if os.path.exists(self.db_path):
                try:
                    # 尝试连接数据库
                    test_conn = sqlite3.connect(self.db_path)
                    test_conn.execute("SELECT 1")
                    test_conn.close()
                except sqlite3.DatabaseError:
                    print(f"数据库文件损坏，正在删除并重新创建: {self.db_path}")
                    os.remove(self.db_path)
            
            # 连接数据库
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # 使查询结果可以通过列名访问
            
            # 创建表
            self.create_tables()
            
            # 初始化默认数据
            self.init_default_data()
            
            print(f"✅ 数据库初始化完成: {self.db_path}")
            
        except Exception as e:
            print(f"❌ 数据库初始化失败: {e}")
            raise
    
    def create_tables(self):
        """创建数据库表"""
        try:
            cursor = self.connection.cursor()
            
            # 创建所有表
            for table_name, create_sql in DATABASE_TABLES.items():
                cursor.execute(create_sql)
                print(f"✅ 表 {table_name} 创建成功")
            
            self.connection.commit()
            
        except Exception as e:
            print(f"❌ 创建表失败: {e}")
            raise
    
    def init_default_data(self):
        """初始化默认数据"""
        try:
            cursor = self.connection.cursor()
            
            # 检查是否已有基本数据
            cursor.execute("SELECT COUNT(*) FROM basic_info")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # 插入默认数据
                from src.utils.config import DEFAULT_DATA
                
                for table_name, data in DEFAULT_DATA.items():
                    if table_name == "basic_info":
                        cursor.execute("""
                            INSERT INTO basic_info (id, start_date, experience, level, created_at, updated_at)
                            VALUES (1, ?, ?, ?, ?, ?)
                        """, (
                            data["start_date"],
                            data["experience"],
                            data["level"],
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        ))
                
                self.connection.commit()
                print("✅ 默认数据初始化完成")
            
        except Exception as e:
            print(f"❌ 初始化默认数据失败: {e}")
    
    def execute_query(self, query, params=None):
        """执行查询语句"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall()
            return [dict(row) for row in results]
            
        except Exception as e:
            print(f"❌ 查询执行失败: {e}")
            return []
    
    def execute_update(self, query, params=None):
        """执行更新语句"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.connection.commit()
            return True
            
        except Exception as e:
            print(f"❌ 更新执行失败: {e}")
            return False
    
    def execute_insert(self, query, params=None):
        """执行插入语句并返回插入的ID"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.connection.commit()
            return cursor.lastrowid
            
        except Exception as e:
            print(f"❌ 插入执行失败: {e}")
            return None
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()


# 全局数据库管理器实例
_db_manager = None

def get_database_manager():
    """获取数据库管理器实例"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager

def execute_query(query, params=None):
    """执行查询语句"""
    db_manager = get_database_manager()
    return db_manager.execute_query(query, params)

def execute_update(query, params=None):
    """执行更新语句"""
    db_manager = get_database_manager()
    return db_manager.execute_update(query, params)

def execute_insert(query, params=None):
    """执行插入语句"""
    db_manager = get_database_manager()
    return db_manager.execute_insert(query, params)
