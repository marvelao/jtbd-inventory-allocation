"""
工具函数模块
"""


def format_number(value, decimal_places=2):
    """
    格式化数字
    
    Args:
        value: 数字值
        decimal_places: 小数位数
        
    Returns:
        格式化后的字符串
    """
    try:
        return f"{float(value):.{decimal_places}f}"
    except (ValueError, TypeError):
        return "0.00"


def format_percentage(value, decimal_places=2):
    """
    格式化百分比
    
    Args:
        value: 百分比值
        decimal_places: 小数位数
        
    Returns:
        格式化后的字符串（带%符号）
    """
    try:
        return f"{float(value):.{decimal_places}f}%"
    except (ValueError, TypeError):
        return "0.00%"


def validate_positive_integer(value, min_value=1, max_value=100000):
    """
    验证正整数
    
    Args:
        value: 待验证的值
        min_value: 最小值
        max_value: 最大值
        
    Returns:
        验证是否通过
    """
    try:
        num = int(value)
        return min_value <= num <= max_value
    except (ValueError, TypeError):
        return False


def validate_material_code(code):
    """
    验证物料编码
    
    Args:
        code: 物料编码
        
    Returns:
        验证是否通过
    """
    if not code or not isinstance(code, str):
        return False
    return len(code.strip()) > 0
