"""游戏控制工具模块

提供游戏启动、关闭、状态查询等功能。
"""

import logging
from pathlib import Path
from typing import Optional

from ..cli import MAACLI, CLIResult

logger = logging.getLogger(__name__)


class GameTools:
    """游戏控制工具类"""

    def __init__(self, cli: MAACLI):
        """
        Args:
            cli: MAA CLI 实例
        """
        self.cli = cli

    def startup(
        self,
        client: str = "Official",
        timeout: int = 120,
    ) -> CLIResult:
        """启动明日方舟游戏并进入主界面

        Args:
            client: 客户端类型，如 "Official"（官服）、"Bilibili"（B 服）等
            timeout: 超时时间（秒）

        Returns:
            CLIResult: 执行结果
        """
        logger.info(f"Starting game with client: {client}")
        return self.cli.run(["startup", client], timeout=timeout)

    def closedown(self, client: str = "Official") -> CLIResult:
        """关闭明日方舟游戏客户端

        Args:
            client: 客户端类型

        Returns:
            CLIResult: 执行结果
        """
        logger.info(f"Closing game with client: {client}")
        return self.cli.run(["closedown", client])

    def activity(self, client: str = "Official") -> CLIResult:
        """获取游戏当前活动信息

        Args:
            client: 客户端类型

        Returns:
            CLIResult: 执行结果
        """
        logger.info(f"Getting activity info for client: {client}")
        return self.cli.run(["activity", client])

    def check_game_running(self, client: str = "Official") -> bool:
        """检查游戏是否正在运行

        Args:
            client: 客户端类型

        Returns:
            游戏是否正在运行
        """
        result = self.cli.run(["activity", client], timeout=10)
        return result.success
