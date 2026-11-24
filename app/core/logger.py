"""
系统日志配置
作用：配置项目统一日志输出
loguru的好处：开箱即用，输出彩色配置
"""
import sys

from loguru import logger

# 移除loguru默认日志输出配置
logger.remove()

# 重新添加控制台输出
# format: 日志格式 => 时间 | 级别 | 文件名:行号 | 日志内容
logger.add(
    sys.stdout,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    level="INFO",
    rotation="00:00", # 每天0点创建新文件
    retention="7 days", # 日志文件最多保留7天
    encoding="utf-8",
)
