"""基建工具模块

提供基建换班、制造、采购、贸易等功能。
"""

import logging
from pathlib import Path
from typing import Optional

from ..cli import MAACLI, CLIResult

logger = logging.getLogger(__name__)


class InfrastructureTools:
    """基建工具类"""

    def __init__(self, cli: MAACLI):
        """
        Args:
            cli: MAA CLI 实例
        """
        self.cli = cli

    def infrast_switch(self, operator: str, room: str) -> CLIResult:
        """基建换班

        Args:
            operator: 干员名称
            room: 房间类型（power, production, trade, control, re, office）

        Returns:
            CLIResult: 执行结果
        """
        logger.info(f"Switching operator {operator} to room {room}")
        return self.cli.run(["infrast", "switch", operator, room])

    def infrast_manage(self, client: str = "Official") -> CLIResult:
        """基建管理（自动换班、制造、采购等）

        Args:
            client: 客户端类型

        Returns:
            CLIResult: 执行结果
        """
        logger.info(f"Managing infrastructure for client: {client}")
        return self.cli.run(["infrast", "manage", client])

    def infrast_production(self, client: str = "Official") -> CLIResult:
        """基建制造（开始制造任务）

        Args:
            client: 客户端类型

        Returns:
            CLIResult: 执行结果
        """
        logger.info(f"Starting infrastructure production for client: {client}")
        return self.cli.run(["infrast", "production", client])

    def infrast_trade(self, client: str = "Official") -> CLIResult:
        """基建贸易（出售物资）

        Args:
            client: 客户端类型

        Returns:
            CLIResult: 执行结果
        """
        logger.info(f"Starting infrastructure trade for client: {client}")
        return self.cli.run(["infrast", "trade", client])

    def infrast_purchase(self, client: str = "Official") -> CLIResult:
        """基建采购（购买物资）

        Args:
            client: 客户端类型

        Returns:
            CLIResult: 执行结果
        """
        logger.info(f"Starting infrastructure purchase for client: {client}")
        return self.cli.run(["infrast", "purchase", client])

    def infrast_energy(self, client: str = "Official") -> CLIResult:
        """基建收取理智

        Args:
            client: 客户端类型

        Returns:
            CLIResult: 执行结果
        """
        logger.info(f"Collecting energy for client: {client}")
        return self.cli.run(["infrast", "energy", client])
