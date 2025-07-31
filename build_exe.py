#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可执行文件打包脚本
使用PyInstaller打包应用程序
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """检查PyInstaller是否已安装"""
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "show", "pyinstaller"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ PyInstaller已安装")
            return True
        else:
            print("❌ PyInstaller未安装")
            return False
            
    except Exception as e:
        print(f"❌ 检查PyInstaller时出错: {e}")
        return False

def install_pyinstaller():
    """安装PyInstaller"""
    try:
        print("📦 安装PyInstaller...")
        
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "pyinstaller"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ PyInstaller安装成功")
            return True
        else:
            print(f"❌ PyInstaller安装失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 安装PyInstaller时出错: {e}")
        return False

def clean_build_files():
    """清理构建文件"""
    print("🧹 清理旧的构建文件...")
    
    # 清理目录
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✅ 已清理: {dir_name}")
    
    # 清理文件
    files_to_clean = ["LAS.spec"]
    for file_name in files_to_clean:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"✅ 已清理: {file_name}")

def cleanup_build_artifacts(build_dir):
    """清理构建过程中的临时文件"""
    print("🧹 清理构建过程中的临时文件...")
    
    try:
        # 清理build目录中的临时文件，但保留dist目录
        temp_dirs = ["build", "__pycache__"]
        for dir_name in temp_dirs:
            temp_dir_path = os.path.join(build_dir, dir_name)
            if os.path.exists(temp_dir_path):
                shutil.rmtree(temp_dir_path)
                print(f"✅ 已清理: {temp_dir_path}")
        
        # 清理临时文件
        temp_files = ["LAS.spec", "main.py", "requirements.txt", "install.py", "reset_database.py"]
        for file_name in temp_files:
            temp_file_path = os.path.join(build_dir, file_name)
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                print(f"✅ 已清理: {temp_file_path}")
        
        # 清理src目录（源代码已打包到exe中）
        src_dir_path = os.path.join(build_dir, "src")
        if os.path.exists(src_dir_path):
            shutil.rmtree(src_dir_path)
            print(f"✅ 已清理: {src_dir_path}")
        
        # 清理build目录下的doc目录（临时创建用于打包）
        build_doc_dir = os.path.join(build_dir, "doc")
        if os.path.exists(build_doc_dir):
            shutil.rmtree(build_doc_dir)
            print(f"✅ 已清理: {build_doc_dir}")
        
        print("✅ 构建临时文件清理完成")
        
    except Exception as e:
        print(f"⚠️ 清理临时文件时出错: {e}")
        # 不中断构建过程，只记录错误

def setup_build_environment():
    """设置构建环境"""
    print("🔧 设置构建环境...")
    
    # 创建build目录
    build_dir = "build"
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
        print(f"✅ 创建构建目录: {build_dir}")
    
    # 复制必要文件到build目录
    files_to_copy = [
        "main.py",
        "requirements.txt", 
        "install.py",
        "reset_database.py"
    ]
    
    for file_name in files_to_copy:
        if os.path.exists(file_name):
            shutil.copy2(file_name, build_dir)
            print(f"✅ 复制文件: {file_name}")
    
    # 复制src目录
    if os.path.exists("src"):
        src_dest = os.path.join(build_dir, "src")
        if os.path.exists(src_dest):
            shutil.rmtree(src_dest)
        shutil.copytree("src", src_dest)
        print("✅ 复制src目录")
    
    # 创建doc目录（用于存放数据库文件）
    doc_dir = os.path.join(build_dir, "doc")
    if not os.path.exists(doc_dir):
        os.makedirs(doc_dir)
        print("✅ 创建doc目录")
    
    return build_dir

def build_executable(build_dir):
    """构建可执行文件"""
    try:
        print("🔨 开始构建可执行文件...")
        
        # 切换到build目录
        original_dir = os.getcwd()
        os.chdir(build_dir)
        
        try:
            # 使用PyInstaller直接构建，不创建spec文件
            result = subprocess.run([
                sys.executable, "-m", "PyInstaller",
                "--onefile",           # 打包成单个文件
                "--windowed",          # 无控制台窗口
                "--name=LAS",          # 可执行文件名称
                "--add-data=src;src",  # 包含src目录
                "--add-data=doc;doc",  # 包含doc目录
                "--add-data=requirements.txt;.",  # 包含requirements.txt
                "--add-data=install.py;.",       # 包含install.py
                "--add-data=reset_database.py;.", # 包含reset_database.py
                "--hidden-import=tkinter",
                "--hidden-import=tkinter.ttk",
                "--hidden-import=tkinter.messagebox",
                "--hidden-import=tkinter.filedialog",
                "--hidden-import=sqlite3",
                "--hidden-import=datetime",
                "--hidden-import=json",
                "--hidden-import=os",
                "--hidden-import=sys",
                "--hidden-import=pathlib",
                "main.py"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ 可执行文件构建成功")
                return True
            else:
                print(f"❌ 构建失败: {result.stderr}")
                return False
                
        finally:
            # 切换回原目录
            os.chdir(original_dir)
            
    except Exception as e:
        print(f"❌ 构建过程中出错: {e}")
        return False

def create_simple_installer(build_dir):
    """创建简单的安装包"""
    try:
        print("📦 创建安装包...")
        
        # 检查构建结果
        build_exe_path = os.path.join(build_dir, "dist", "LAS.exe")
        if not os.path.exists(build_exe_path):
            print("❌ 可执行文件不存在")
            return False
        
        # 创建安装包目录（在build目录内）
        installer_dir = os.path.join(build_dir, "LAS_Installer")
        if os.path.exists(installer_dir):
            shutil.rmtree(installer_dir)
        os.makedirs(installer_dir)
        
        # 复制可执行文件
        shutil.copy2(build_exe_path, installer_dir)
        
        # 复制doc目录（用于存放数据库文件）
        doc_src = os.path.join(build_dir, "doc")
        doc_dest = os.path.join(installer_dir, "doc")
        if os.path.exists(doc_src):
            if os.path.exists(doc_dest):
                shutil.rmtree(doc_dest)
            shutil.copytree(doc_src, doc_dest)
            print("✅ 复制doc目录")
        
        # 创建启动脚本
        batch_content = '''@echo off
echo 正在启动LAS系统...
LAS.exe
pause
'''
        
        with open(os.path.join(installer_dir, "启动LAS.bat"), "w", encoding="utf-8") as f:
            f.write(batch_content)
        
        # 创建README
        readme_content = '''LAS 人生成就系统

安装说明：
1. 双击 "LAS.exe" 直接运行
2. 或双击 "启动LAS.bat" 运行

系统要求：
- Windows 7 或更高版本
- 无需安装Python环境

数据存储：
- 数据保存在程序目录的doc文件夹中
- 数据库文件：doc/las_database.db
- 建议定期备份doc文件夹

注意事项：
- 首次运行会自动创建数据库
- 请确保程序有写入doc目录的权限
- 不要删除或移动doc目录

技术支持：
如有问题，请查看项目文档或联系开发者。
'''
        
        with open(os.path.join(installer_dir, "README.txt"), "w", encoding="utf-8") as f:
            f.write(readme_content)
        
        print(f"✅ 安装包已创建: {installer_dir}")
        return True
        
    except Exception as e:
        print(f"❌ 创建安装包时出错: {e}")
        return False

def main():
    """主构建流程"""
    print("=" * 50)
    print("LAS 可执行文件构建工具")
    print("=" * 50)
    
    # 检查PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            return False
    
    # 清理旧的构建文件
    clean_build_files()
    
    # 设置构建环境
    build_dir = setup_build_environment()
    
    # 构建可执行文件
    if not build_executable(build_dir):
        return False
    
    # 创建安装包
    create_simple_installer(build_dir)
    
    # 清理构建过程中的临时文件
    cleanup_build_artifacts(build_dir)
    
    print("\n" + "=" * 50)
    print("✅ 构建完成！")
    print("=" * 50)
    print("生成的文件:")
    print("- build/dist/LAS.exe (可执行文件)")
    print("- build/LAS_Installer/ (安装包)")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ 构建被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 构建过程中出现未知错误: {e}")
        sys.exit(1)
