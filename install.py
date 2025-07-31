#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LAS 系统安装脚本
极简版安装程序
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python版本过低，需要Python 3.7或更高版本")
        print(f"当前版本: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """安装依赖包"""
    try:
        print("📦 安装依赖包...")
        
        # 检查requirements.txt是否存在
        requirements_file = "requirements.txt"
        if not os.path.exists(requirements_file):
            print("⚠️ requirements.txt文件不存在，跳过依赖安装")
            return True
        
        # 安装依赖
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", requirements_file
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 依赖包安装成功")
            return True
        else:
            print(f"⚠️ 依赖包安装失败: {result.stderr}")
            print("继续安装...")
            return True
            
    except Exception as e:
        print(f"⚠️ 安装依赖包时出错: {e}")
        print("继续安装...")
        return True

def create_directories():
    """创建必要的目录"""
    try:
        print("📁 创建必要目录...")
        
        directories = [
            "doc",
            "src/gui",
            "src/utils"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ 目录已创建: {directory}")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建目录失败: {e}")
        return False

def init_database():
    """初始化数据库"""
    try:
        print("🗄️ 初始化数据库...")
        
        # 导入数据库重置模块
        from reset_database import reset_database
        
        # 重置数据库
        if reset_database():
            print("✅ 数据库初始化成功")
            return True
        else:
            print("❌ 数据库初始化失败")
            return False
            
    except Exception as e:
        print(f"❌ 初始化数据库时出错: {e}")
        return False

def create_launch_script():
    """创建启动脚本"""
    try:
        print("🚀 创建启动脚本...")
        
        system = platform.system()
        
        if system == "Windows":
            # Windows批处理文件
            batch_content = f'''@echo off
echo 正在启动LAS系统...
"{sys.executable}" "{os.path.abspath("main.py")}"
pause
'''
            
            script_path = "启动LAS.bat"
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(batch_content)
            
            print(f"✅ Windows启动脚本已创建: {script_path}")
            
        else:  # macOS/Linux
            # Shell脚本
            script_content = f'''#!/bin/bash
cd "{os.path.abspath(".")}"
"{sys.executable}" "{os.path.abspath("main.py")}"
'''
            
            script_path = "启动LAS.sh"
            with open(script_path, "w") as f:
                f.write(script_content)
            
            os.chmod(script_path, 0o755)
            print(f"✅ {system}启动脚本已创建: {script_path}")
        
        return True
        
    except Exception as e:
        print(f"⚠️ 创建启动脚本失败: {e}")
        return False

def main():
    """主安装流程"""
    print("=" * 50)
    print("LAS 系统安装程序")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        return False
    
    # 创建目录
    if not create_directories():
        return False
    
    # 安装依赖
    install_dependencies()
    
    # 初始化数据库
    if not init_database():
        return False
    
    # 创建启动脚本
    create_launch_script()
    
    print("\n" + "=" * 50)
    print("✅ 安装完成！")
    print("=" * 50)
    print("启动方式:")
    print(f"1. 直接运行: python {os.path.abspath('main.py')}")
    print("2. 使用启动脚本: 双击启动脚本文件")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ 安装被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 安装过程中出现未知错误: {e}")
        sys.exit(1)
