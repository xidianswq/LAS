#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安装脚本
用于安装依赖和初始化系统
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
        return False
    print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
    return True

def install_requirements():
    """安装依赖包"""
    try:
        print("📦 安装依赖包...")
        
        # 检查requirements.txt是否存在
        requirements_file = "requirements.txt"
        if not os.path.exists(requirements_file):
            print("❌ requirements.txt文件不存在")
            return False
        
        # 安装依赖
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", requirements_file
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 依赖包安装成功")
            return True
        else:
            print(f"❌ 依赖包安装失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 安装依赖包时出错: {e}")
        return False

def create_directories():
    """创建必要的目录"""
    try:
        print("📁 创建目录...")
        
        directories = [
            "doc",
            "src/gui",
            "src/utils",
            "recovered_files"
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
        from reset_database import reset_database, verify_database
        
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

def create_shortcut():
    """创建快捷方式"""
    try:
        system = platform.system()
        
        if system == "Windows":
            # Windows快捷方式
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, "LAS.lnk")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{os.path.abspath("main.py")}"'
            shortcut.WorkingDirectory = os.path.abspath(".")
            shortcut.IconLocation = sys.executable
            shortcut.save()
            
            print(f"✅ Windows快捷方式已创建: {shortcut_path}")
            
        elif system == "Darwin":  # macOS
            # macOS应用程序包
            app_name = "LAS.app"
            app_path = f"/Applications/{app_name}"
            
            # 创建简单的启动脚本
            script_content = f'''#!/bin/bash
cd "{os.path.abspath(".")}"
"{sys.executable}" "{os.path.abspath("main.py")}"
'''
            
            script_path = "/usr/local/bin/las"
            with open(script_path, "w") as f:
                f.write(script_content)
            
            os.chmod(script_path, 0o755)
            print(f"✅ macOS启动脚本已创建: {script_path}")
            
        else:  # Linux
            # Linux桌面文件
            desktop_file = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=LAS
Comment=人生成就系统
Exec={sys.executable} {os.path.abspath('main.py')}
Path={os.path.abspath('.')}
Icon=utilities-terminal
Terminal=false
Categories=Utility;
"""
            
            desktop_path = os.path.expanduser("~/.local/share/applications/las.desktop")
            with open(desktop_path, "w") as f:
                f.write(desktop_file)
            
            print(f"✅ Linux桌面文件已创建: {desktop_path}")
        
        return True
        
    except Exception as e:
        print(f"⚠️ 创建快捷方式失败: {e}")
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
    if not install_requirements():
        return False
    
    # 初始化数据库
    if not init_database():
        return False
    
    # 创建快捷方式
    create_shortcut()
    
    print("\n" + "=" * 50)
    print("✅ 安装完成！")
    print("=" * 50)
    print("现在可以运行以下命令启动系统:")
    print(f"python {os.path.abspath('main.py')}")
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
