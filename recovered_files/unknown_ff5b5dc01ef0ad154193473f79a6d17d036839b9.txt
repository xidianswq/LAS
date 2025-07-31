"""
总结文件操作工具
处理总结文件的读写操作，确保格式正确
"""

import os
from datetime import datetime
from typing import Optional


def read_summary_file(file_path: str) -> str:
    """
    读取总结文件内容
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件内容字符串
    """
    if not os.path.exists(file_path):
        return ""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"读取文件失败: {e}")
        return ""


def write_summary_to_file(file_path: str, content: str, title: str = "", date: str = ""):
    """
    将总结内容写入文件，在开头添加新内容，在结尾添加空行
    
    Args:
        file_path: 文件路径
        content: 总结内容
        title: 标题（可选）
        date: 日期（可选）
    """
    # 确保doc文件夹存在
    doc_dir = os.path.dirname(file_path)
    if doc_dir and not os.path.exists(doc_dir):
        os.makedirs(doc_dir)
    
    # 读取现有内容
    existing_content = read_summary_file(file_path)
    
    # 构建新内容
    new_entry = ""
    if date:
        new_entry += f"## {date}\n\n"
    if title:
        new_entry += f"### {title}\n\n"
    new_entry += f"{content}\n\n"
    
    # 写入文件：新内容在开头，现有内容在后面，确保结尾有空行
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_entry + existing_content)
            # 确保文件结尾有空行
            if not existing_content.endswith('\n'):
                f.write('\n')
    except Exception as e:
        print(f"写入文件失败: {e}")


def get_current_date_str() -> str:
    """获取当前日期字符串"""
    return datetime.now().strftime("%Y-%m-%d")


def get_current_time_str() -> str:
    """获取当前时间字符串"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def format_summary_content(content_type: str, content: str, additional_info: dict = None) -> str:
    """
    格式化总结内容
    
    Args:
        content_type: 内容类型（daily）
        content: 主要内容
        additional_info: 额外信息字典
        
    Returns:
        格式化后的内容
    """
    formatted_content = f"**DAILY SUMMARY**\n\n"
    formatted_content += content
    
    if additional_info:
        formatted_content += "\n\n**Additional Info:**\n"
        for key, value in additional_info.items():
            formatted_content += f"- {key}: {value}\n"
    
    return formatted_content 