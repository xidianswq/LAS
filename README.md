# LAS (Life Achievement System) - 人生成就系统

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

## 📖 项目简介

LAS (Life Achievement System) 是一个基于Python开发的轻量级桌面应用程序，旨在帮助用户管理人生目标、日常任务和个人成长。系统采用经验值等级机制，通过完成目标和任务来获得经验值，激励用户持续进步。项目依赖极少，主要使用Python内置模块，安装简单，运行稳定。

## ✨ 主要功能

### 🎯 目标管理
- **目标分类**: 支持月计划、年计划等不同类型的目标
- **优先级设置**: 高、中、低三个优先级等级
- **状态跟踪**: 进行中、已完成、已暂停等状态管理
- **经验值奖励**: 根据优先级获得不同经验值奖励

### 📅 每日任务管理
- **任务创建**: 快速创建和管理日常任务
- **优先级设置**: 支持高、中、低优先级
- **完成状态**: 实时跟踪任务完成情况
- **自动重置**: 支持每日自动重置未完成任务

### 📊 数据统计与总结
- **经验值系统**: 通过完成任务获得经验值
- **等级系统**: 基于经验值的等级提升机制
- **数据可视化**: 直观的统计图表展示
- **总结功能**: 支持每日总结和反思

### 🎮 游戏化元素
- **经验值奖励**: 完成目标获得经验值
- **等级提升**: 累积经验值提升等级
- **成就系统**: 激励用户持续进步

## 🚀 快速开始

### 系统要求

- **操作系统**: Windows 7+, macOS 10.12+, Linux
- **Python版本**: 3.7 或更高版本（内置tkinter和sqlite3）
- **内存**: 至少 256MB RAM
- **存储空间**: 至少 50MB 可用空间

### 安装方法

#### 方法一：使用安装脚本（推荐）

```bash
# 1. 克隆或下载项目
git clone https://github.com/xidianswq/LAS.git
cd LAS

# 2. 运行安装脚本
python install.py
```

#### 方法二：直接运行

```bash
# 1. 初始化数据库（首次运行）
python reset_database.py

# 2. 运行程序
python main.py
```

#### 方法三：使用可执行文件

```bash
# 1. 构建可执行文件
python build_exe.py

# 2. 运行生成的exe文件
# Windows: build/dist/LAS.exe
# 或使用安装包: build/LAS_Installer/
```

## 📁 项目结构

```
LAS/
├── main.py                 # 主程序入口
├── requirements.txt        # 依赖包列表
├── install.py             # 安装脚本
├── build_exe.py          # 可执行文件构建脚本
├── reset_database.py     # 数据库重置脚本
├── README.md             # 项目说明文档
├── doc/                  # 文档和数据目录
│   ├── las_database.db  # SQLite数据库文件
│   └── 2025.md         # 年度总结文档
└── src/                 # 源代码目录
    ├── gui/            # 图形界面模块
    │   ├── main_window.py
    │   ├── goals_window.py
    │   └── daily_tasks_window.py
    └── utils/          # 工具模块
        ├── config.py
        ├── database.py
        ├── data_manager.py
        ├── event_manager.py
        ├── summary_manager.py
        └── system_manager.py
```

## 🎮 使用指南

### 启动系统

```bash
python main.py
```

### 基本操作

1. **创建目标**
   - 点击"目标管理"按钮
   - 选择目标类型（月计划/年计划）
   - 设置优先级和描述
   - 保存目标

2. **管理每日任务**
   - 点击"计划管理"按钮
   - 添加新的每日任务
   - 设置优先级和完成状态
   - 系统会自动计算经验值

3. **查看统计**
   - 在主界面查看当前等级和经验值
   - 查看目标完成情况
   - 查看每日任务统计

4. **数据备份**
   - 定期备份 `doc/las_database.db` 文件
   - 备份整个 `doc` 目录以确保数据安全

## ⚙️ 配置说明

### 系统配置

主要配置文件位于 `src/utils/config.py`：

- **窗口配置**: 主窗口、目标管理窗口、任务管理窗口的尺寸和属性
- **等级系统**: 经验值计算规则和等级提升机制
- **奖励配置**: 不同类型任务的经验值奖励
- **界面配置**: UI元素的样式和布局

### 数据库配置

- **数据库文件**: `doc/las_database.db`
- **数据表**: 目标表、任务表、经验值表等
- **备份建议**: 定期备份数据库文件

## 🔧 开发指南

### 环境搭建

```bash
# 1. 克隆项目
git clone https://github.com/xidianswq/LAS.git
cd LAS

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 3. 安装开发依赖（可选）
pip install -r requirements.txt

# 4. 运行开发版本
python main.py
```

### 代码结构

- **GUI模块** (`src/gui/`): 负责用户界面和交互
- **工具模块** (`src/utils/`): 核心业务逻辑和数据处理
- **配置管理**: 系统配置和参数管理
- **事件系统**: 组件间通信和事件处理

### 添加新功能

1. **创建新的GUI窗口**:
   - 在 `src/gui/` 目录下创建新的窗口类
   - 继承自 `tkinter.Toplevel`
   - 实现必要的界面元素和事件处理

2. **添加新的数据模型**:
   - 在 `src/utils/database.py` 中定义数据表
   - 在 `src/utils/data_manager.py` 中实现数据操作
   - 更新配置文件和事件处理

3. **扩展功能模块**:
   - 在 `src/utils/` 目录下创建新的管理器类
   - 实现相应的业务逻辑
   - 集成到主系统中

## 🐛 故障排除

### 常见问题

1. **程序无法启动**
   - 检查Python版本是否为3.7+
   - 确认Python内置tkinter模块可用
   - 检查数据库文件权限

2. **数据库错误**
   - 运行 `python reset_database.py` 重置数据库
   - 检查 `doc` 目录是否存在且有写入权限

3. **界面显示异常**
   - 检查系统DPI设置
   - 尝试调整窗口大小
   - 确认tkinter正常工作

4. **数据丢失**
   - 检查是否有数据库备份
   - 查看 `doc` 目录中的数据库文件
   - 考虑从备份恢复数据

### 日志和调试

- 程序运行日志会输出到控制台
- 数据库操作日志可在 `doc` 目录查看
- 使用 `python -v main.py` 获取详细调试信息

## 📝 更新日志

### v1.0.0 (2024-01-01)
- ✨ 初始版本发布
- 🎯 实现目标管理功能
- 📅 实现每日任务管理
- 📊 实现经验值等级系统
- 🎮 添加游戏化元素

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目！

### 贡献方式

1. **报告Bug**: 在GitHub Issues中报告问题
2. **功能建议**: 提出新功能或改进建议
3. **代码贡献**: 提交Pull Request
4. **文档改进**: 帮助完善文档

### 开发规范

- 遵循PEP 8代码风格
- 添加适当的注释和文档字符串
- 确保新功能有相应的测试
- 更新相关文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和用户！

---

**LAS - 让生活更有目标，让成长更有动力！** 🚀 