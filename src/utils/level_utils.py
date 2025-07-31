"""
等级计算工具
提供统一的等级计算功能，无等级上限，等级增长均匀
"""

from src.utils.config import LEVEL_SYSTEM_CONFIG

def calculate_level(experience: int) -> int:
    """
    根据经验值计算等级
    使用线性增长公式：每{exp_per_level}经验值升一级
    
    Args:
        experience: 当前经验值
        
    Returns:
        当前等级
    """
    if experience <= 0:
        return LEVEL_SYSTEM_CONFIG["min_level"] - 1
    
    exp_per_level = LEVEL_SYSTEM_CONFIG["exp_per_level"]
    # 线性增长：每{exp_per_level}经验值升一级
    level = experience // exp_per_level
    return max(LEVEL_SYSTEM_CONFIG["min_level"] - 1, level)


def calculate_exp_to_next_level(current_exp: int) -> int:
    """
    计算距离下一级还需要多少经验值
    
    Args:
        current_exp: 当前经验值
        
    Returns:
        距离下一级还需要的经验值
    """
    current_level = calculate_level(current_exp)
    exp_per_level = LEVEL_SYSTEM_CONFIG["exp_per_level"]
    next_level_exp = (current_level + 1) * exp_per_level
    
    return max(0, next_level_exp - current_exp)


def get_level_progress(current_exp: int) -> float:
    """
    获取当前等级进度百分比
    
    Args:
        current_exp: 当前经验值
        
    Returns:
        进度百分比 (0.0 - 1.0)
    """
    current_level = calculate_level(current_exp)
    exp_per_level = LEVEL_SYSTEM_CONFIG["exp_per_level"]
    level_start_exp = current_level * exp_per_level
    level_end_exp = (current_level + 1) * exp_per_level
    
    if level_end_exp == level_start_exp:
        return 1.0
    
    progress = (current_exp - level_start_exp) / (level_end_exp - level_start_exp)
    return min(1.0, max(0.0, progress))


def format_level_info(experience: int) -> dict:
    """
    格式化等级信息
    
    Args:
        experience: 当前经验值
        
    Returns:
        包含等级信息的字典
    """
    current_level = calculate_level(experience)
    exp_to_next = calculate_exp_to_next_level(experience)
    progress = get_level_progress(experience)
    
    return {
        'level': current_level,
        'experience': experience,
        'exp_to_next': exp_to_next,
        'progress': progress,
        'progress_percent': progress * 100
    } 