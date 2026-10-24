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
        addr: Optional[str] = None,
    ) -> CLIResult:
        """启动明日方舟游戏并进入主界面

        Args:
            client: 客户端类型，如 "Official"（官服）、"Bilibili"（B 服）等
            timeout: 超时时间（秒）
            addr: ADB 设备地址，如 "127.0.0.1:5555"；留空使用 MAA 配置/默认设备

        Returns:
            CLIResult: 执行结果
        """
        args = ["startup", client]
        if addr:
            args.extend(["-a", addr])
        logger.info(f"Starting game with client: {client}, addr: {addr}")
        return self.cli.run(args, timeout=timeout)

    def closedown(self, client: str = "Official", addr: Optional[str] = None) -> CLIResult:
        """关闭明日方舟游戏客户端

        Args:
            client: 客户端类型
            addr: ADB 设备地址

        Returns:
            CLIResult: 执行结果
        """
        args = ["closedown", client]
        if addr:
            args.extend(["-a", addr])
        logger.info(f"Closing game with client: {client}, addr: {addr}")
        return self.cli.run(args)

    def activity(self, client: str = "Official", addr: Optional[str] = None) -> CLIResult:
        """获取游戏当前活动信息

        Args:
            client: 客户端类型
            addr: ADB 设备地址

        Returns:
            CLIResult: 执行结果
        """
        args = ["activity", client]
        if addr:
            args.extend(["-a", addr])
        logger.info(f"Getting activity info for client: {client}, addr: {addr}")
        return self.cli.run(args)

    def check_game_running(self, client: str = "Official") -> bool:
        """检查游戏是否正在运行

        Args:
            client: 客户端类型

        Returns:
            游戏是否正在运行
        """
        result = self.cli.run(["activity", client], timeout=10)
        return result.success
