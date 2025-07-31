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

def create_spec_file():
    """创建PyInstaller规范文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),
        ('requirements.txt', '.'),
        ('install.py', '.'),
        ('reset_database.py', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'sqlite3',
        'datetime',
        'json',
        'os',
        'sys',
        'pathlib',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LAS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    with open("LAS.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    print("✅ 规范文件已创建: LAS.spec")

def build_executable():
    """构建可执行文件"""
    try:
        print("🔨 开始构建可执行文件...")
        
        # 清理之前的构建
        if os.path.exists("build"):
            shutil.rmtree("build")
        if os.path.exists("dist"):
            shutil.rmtree("dist")
        
        # 使用PyInstaller构建
        result = subprocess.run([
            sys.executable, "-m", "PyInstaller", "LAS.spec", "--clean"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 可执行文件构建成功")
            return True
        else:
            print(f"❌ 构建失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 构建过程中出错: {e}")
        return False

def create_installer():
    """创建安装包"""
    try:
        print("📦 创建安装包...")
        
        # 检查构建结果
        exe_path = os.path.join("dist", "LAS.exe")
        if not os.path.exists(exe_path):
            print("❌ 可执行文件不存在")
            return False
        
        # 创建安装包目录
        installer_dir = "LAS_Installer"
        if os.path.exists(installer_dir):
            shutil.rmtree(installer_dir)
        os.makedirs(installer_dir)
        
        # 复制文件
        shutil.copy2(exe_path, installer_dir)
        
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

注意事项：
- 首次运行会自动创建数据库
- 数据保存在程序目录的doc文件夹中
- 建议定期备份doc文件夹

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
    
    # 创建规范文件
    create_spec_file()
    
    # 构建可执行文件
    if not build_executable():
        return False
    
    # 创建安装包
    create_installer()
    
    print("\n" + "=" * 50)
    print("✅ 构建完成！")
    print("=" * 50)
    print("生成的文件:")
    print("- dist/LAS.exe (可执行文件)")
    print("- LAS_Installer/ (安装包)")
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
