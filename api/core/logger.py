"""
优雅的日志系统

使用 Loguru + Rich 实现结构化、彩色的终端日志
"""

import sys
from pathlib import Path
from loguru import logger as _logger
from rich.console import Console
from rich.theme import Theme


# 创建 Rich Console
console = Console(theme=Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red bold",
    "success": "green bold",
}))


class LoggerWrapper:
    """
    Logger 包装器，提供 bind() 方法兼容性
    """
    
    def __init__(self, logger_instance):
        self._logger = logger_instance
        self._context = {}
    
    def bind(self, **kwargs):
        """
        绑定上下文信息（兼容方法，实际不改变日志行为）
        返回自身以支持链式调用
        """
        # 创建新的包装器实例，保存上下文
        new_wrapper = LoggerWrapper(self._logger)
        new_wrapper._context = {**self._context, **kwargs}
        return new_wrapper
    
    def _format_message(self, message):
        """格式化消息，添加上下文信息"""
        if self._context:
            context_str = " | ".join(f"{k}={v}" for k, v in self._context.items())
            return f"{message} [{context_str}]"
        return message
    
    def debug(self, message, *args, **kwargs):
        """Debug 级别日志"""
        self._logger.debug(self._format_message(message), *args, **kwargs)
    
    def info(self, message, *args, **kwargs):
        """Info 级别日志"""
        self._logger.info(self._format_message(message), *args, **kwargs)
    
    def success(self, message, *args, **kwargs):
        """Success 级别日志"""
        self._logger.success(self._format_message(message), *args, **kwargs)
    
    def warning(self, message, *args, **kwargs):
        """Warning 级别日志"""
        self._logger.warning(self._format_message(message), *args, **kwargs)
    
    def error(self, message, *args, **kwargs):
        """Error 级别日志"""
        self._logger.error(self._format_message(message), *args, **kwargs)
    
    def critical(self, message, *args, **kwargs):
        """Critical 级别日志"""
        self._logger.critical(self._format_message(message), *args, **kwargs)
    
    def exception(self, message, *args, **kwargs):
        """Exception 级别日志（包含堆栈跟踪）"""
        self._logger.exception(self._format_message(message), *args, **kwargs)
    
    def __getattr__(self, name):
        """代理其他方法到原始 logger"""
        return getattr(self._logger, name)


# 移除默认的 logger
_logger.remove()

# 日志目录
LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 终端日志格式 - 简洁美观
TERMINAL_FORMAT = (
    "<green>{time:HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan> | "
    "<level>{message}</level>"
)

# 文件日志格式 - 详细完整
FILE_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
    "{level: <8} | "
    "{name}:{function}:{line} | "
    "{message}"
)

# 添加终端输出 - 彩色、结构化
_logger.add(
    sys.stderr,
    format=TERMINAL_FORMAT,
    level="INFO",  # 保持 INFO 级别
    colorize=True,
    backtrace=True,
    diagnose=True,
)

# 添加文件输出 - 所有日志
_logger.add(
    LOG_DIR / "app.log",
    format=FILE_FORMAT,
    level="DEBUG",
    rotation="10 MB",  # 日志轮转
    retention="7 days",  # 保留7天
    compression="zip",  # 压缩旧日志
    encoding="utf-8",
    backtrace=True,
    diagnose=True,
)

# 添加错误日志文件 - 只记录错误
_logger.add(
    LOG_DIR / "error.log",
    format=FILE_FORMAT,
    level="ERROR",
    rotation="10 MB",
    retention="30 days",  # 错误日志保留30天
    compression="zip",
    encoding="utf-8",
    backtrace=True,
    diagnose=True,
)

# 创建包装后的 logger
logger = LoggerWrapper(_logger)

# 导出
__all__ = ["logger", "console"]
