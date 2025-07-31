#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库重置脚本
用于删除并重新创建数据库
"""

import os
import sys
import sqlite3
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(os.path.dirname(__file__))

from src.utils.config import DATABASE_NAME, DATABASE_TABLES, DEFAULT_DATA

def reset_database():
    """重置数据库"""
    try:
        print("🔄 开始重置数据库...")
        
        # 删除现有数据库文件
        if os.path.exists(DATABASE_NAME):
            os.remove(DATABASE_NAME)
            print(f"✅ 已删除现有数据库文件: {DATABASE_NAME}")
        
        # 确保数据库目录存在
        os.makedirs(os.path.dirname(DATABASE_NAME), exist_ok=True)
        
        # 创建新的数据库连接
        connection = sqlite3.connect(DATABASE_NAME)
        connection.row_factory = sqlite3.Row
        
        # 创建表
        cursor = connection.cursor()
        for table_name, create_sql in DATABASE_TABLES.items():
            cursor.execute(create_sql)
            print(f"✅ 表 {table_name} 创建成功")
        
        # 初始化默认数据
        cursor.execute("SELECT COUNT(*) FROM basic_info")
        count = cursor.fetchone()[0]
        
        if count == 0:
            from datetime import datetime
            basic_info_data = DEFAULT_DATA["basic_info"]
            cursor.execute("""
                INSERT INTO basic_info (id, start_date, experience, level, created_at, updated_at)
                VALUES (1, ?, ?, ?, ?, ?)
            """, (
                basic_info_data["start_date"],
                basic_info_data["experience"],
                basic_info_data["level"],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            print("✅ 默认数据初始化完成")
        
        connection.commit()
        connection.close()
        
        print("✅ 数据库重置完成！")
        return True
        
    except Exception as e:
        print(f"❌ 数据库重置失败: {e}")
        return False

def verify_database():
    """验证数据库"""
    try:
        print("🔍 验证数据库...")
        
        if not os.path.exists(DATABASE_NAME):
            print("❌ 数据库文件不存在")
            return False
        
        # 尝试连接数据库
        connection = sqlite3.connect(DATABASE_NAME)
        cursor = connection.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = list(DATABASE_TABLES.keys())
        missing_tables = set(expected_tables) - set(tables)
        
        if missing_tables:
            print(f"❌ 缺少表: {missing_tables}")
            return False
        
        # 检查基本数据
        cursor.execute("SELECT COUNT(*) FROM basic_info")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("❌ 缺少基本数据")
            return False
        
        connection.close()
        print("✅ 数据库验证通过")
        return True
        
    except Exception as e:
        print(f"❌ 数据库验证失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("数据库重置工具")
    print("=" * 50)
    
    # 验证当前数据库
    if verify_database():
        print("当前数据库状态正常")
        response = input("是否要重置数据库？(y/N): ")
        if response.lower() != 'y':
            print("取消重置")
            sys.exit(0)
    
    # 重置数据库
    if reset_database():
        print("\n✅ 数据库重置成功！")
        
        # 验证重置结果
        if verify_database():
            print("✅ 数据库重置验证通过")
        else:
            print("❌ 数据库重置验证失败")
    else:
        print("\n❌ 数据库重置失败！")
