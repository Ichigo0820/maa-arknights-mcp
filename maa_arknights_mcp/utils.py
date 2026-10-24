"""MAA Arknights MCP Server - 通用工具"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
) -> None:
    """配置日志

    Args:
        level: 日志级别
        log_file: 日志文件路径
    """
    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )


def get_default_log_dir() -> Path:
    """获取默认日志目录"""
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", ""))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".local" / "share"

    return base / "MAA-Arknights-MCP" / "logs"


def ensure_maa_available(maa_cmd: str = "maa") -> bool:
    """检查 MAA CLI 是否可用

    Args:
        maa_cmd: MAA CLI 命令名

    Returns:
        是否可用
    """
    import subprocess

    try:
        result = subprocess.run(
            [maa_cmd, "version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return False


def format_error(message: str, command: str = "", returncode: int = -1) -> str:
    """格式化错误信息

    Args:
        message: 错误消息
        command: 命令
        returncode: 返回码

    Returns:
        格式化的错误信息
    """
    import json

    return json.dumps(
        {
            "success": False,
            "returncode": returncode,
            "message": message,
            "command": command,
        },
        ensure_ascii=False,
        indent=2,
    )
