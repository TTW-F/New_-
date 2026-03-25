"""
输入清理和安全防护模块

防止 SQL 注入、XSS 等攻击
"""

import re
import html
import logging
from typing import Any, Dict, List, Union

logger = logging.getLogger(__name__)


class InputSanitizer:
    """输入清理器"""
    
    # SQL 注入危险模式
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|CREATE|TRUNCATE)\b)",
        r"(--|#|/\*|\*/)",
        r"(\bOR\b\s+\d+\s*=\s*\d+)",
        r"(\bAND\b\s+\d+\s*=\s*\d+)",
        r"(;\s*(SELECT|INSERT|UPDATE|DELETE|DROP))",
        r"(\'\s*(OR|AND)\s*\')",
    ]
    
    # XSS 危险模式
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
    ]
    
    @classmethod
    def sanitize_string(cls, value: str, escape_html: bool = True) -> str:
        """
        清理字符串输入
        
        Args:
            value: 输入字符串
            escape_html: 是否转义 HTML
            
        Returns:
            清理后的字符串
        """
        if not isinstance(value, str):
            return value
        
        # 移除空字符
        value = value.replace('\x00', '')
        
        # 转义 HTML 特殊字符
        if escape_html:
            value = html.escape(value)
        
        # 移除多余的空白
        value = ' '.join(value.split())
        
        return value
    
    @classmethod
    def check_sql_injection(cls, value: str) -> bool:
        """
        检查是否包含 SQL 注入模式
        
        Args:
            value: 输入字符串
            
        Returns:
            是否包含危险模式
        """
        if not isinstance(value, str):
            return False
        
        value_upper = value.upper()
        
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_upper, re.IGNORECASE):
                logger.warning(f"检测到潜在的 SQL 注入: {value[:100]}")
                return True
        
        return False
    
    @classmethod
    def check_xss(cls, value: str) -> bool:
        """
        检查是否包含 XSS 模式
        
        Args:
            value: 输入字符串
            
        Returns:
            是否包含危险模式
        """
        if not isinstance(value, str):
            return False
        
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"检测到潜在的 XSS: {value[:100]}")
                return True
        
        return False
    
    @classmethod
    def sanitize_dict(cls, data: Dict[str, Any], escape_html: bool = True) -> Dict[str, Any]:
        """
        清理字典中的所有字符串值
        
        Args:
            data: 输入字典
            escape_html: 是否转义 HTML
            
        Returns:
            清理后的字典
        """
        result = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = cls.sanitize_string(value, escape_html)
            elif isinstance(value, dict):
                result[key] = cls.sanitize_dict(value, escape_html)
            elif isinstance(value, list):
                result[key] = cls.sanitize_list(value, escape_html)
            else:
                result[key] = value
        
        return result
    
    @classmethod
    def sanitize_list(cls, data: List[Any], escape_html: bool = True) -> List[Any]:
        """
        清理列表中的所有字符串值
        
        Args:
            data: 输入列表
            escape_html: 是否转义 HTML
            
        Returns:
            清理后的列表
        """
        result = []
        
        for item in data:
            if isinstance(item, str):
                result.append(cls.sanitize_string(item, escape_html))
            elif isinstance(item, dict):
                result.append(cls.sanitize_dict(item, escape_html))
            elif isinstance(item, list):
                result.append(cls.sanitize_list(item, escape_html))
            else:
                result.append(item)
        
        return result
    
    @classmethod
    def is_safe_input(cls, value: str) -> bool:
        """
        检查输入是否安全
        
        Args:
            value: 输入字符串
            
        Returns:
            是否安全
        """
        if not isinstance(value, str):
            return True
        
        return not (cls.check_sql_injection(value) or cls.check_xss(value))


def sanitize_input(value: Union[str, Dict, List], escape_html: bool = True) -> Union[str, Dict, List]:
    """
    清理输入的便捷函数
    
    Args:
        value: 输入值
        escape_html: 是否转义 HTML
        
    Returns:
        清理后的值
    """
    if isinstance(value, str):
        return InputSanitizer.sanitize_string(value, escape_html)
    elif isinstance(value, dict):
        return InputSanitizer.sanitize_dict(value, escape_html)
    elif isinstance(value, list):
        return InputSanitizer.sanitize_list(value, escape_html)
    else:
        return value
