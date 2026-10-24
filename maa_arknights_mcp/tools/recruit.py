"""公招工具模块

提供公开招募、结果获取等功能。
"""

import logging
from pathlib import Path
from typing import Optional

from ..cli import MAACLI, CLIResult

logger = logging.getLogger(__name__)


class RecruitTools:
    """公招工具类"""

    def __init__(self, cli: MAACLI):
        """
        Args:
            cli: MAA CLI 实例
        """
        self.cli = cli

    def recruit_get(self, client: str = "Official") -> CLIResult:
        """获取当前公招结果

        Args:
            client: 客户端类型

        Returns:
            CLIResult: 执行结果
        """
        logger.info(f"Getting recruit results for client: {client}")
        return self.cli.run(["recruit", "get", client])

    def recruit_start(
        self,
        time: int = 7200,
        tags: Optional[str] = None,
        client: str = "Official",
    ) -> CLIResult:
        """开始公招

        Args:
            time: 公招时间（秒），300=30分钟, 1800=30分钟, 7200=2小时, 28800=8小时
            tags: 标签组合，如 "6星 近卫 医疗"，留空随机
            client: 客户端类型

        Returns:
            CLIResult: 执行结果
        """
        args = ["recruit", "start", client]
        if time:
            args.extend(["--time", str(time)])
        if tags:
            args.extend(["--tags", tags])

        logger.info(f"Starting recruit: time={time}, tags={tags}")
        return self.cli.run(args)

    def recruit_collect(self, index: int = 0, client: str = "Official") -> CLIResult:
        """收取公招结果

        Args:
            index: 公招槽位索引（0-3）
            client: 客户端类型

        Returns:
            CLIResult: 执行结果
        """
        logger.info(f"Collecting recruit from slot {index}")
        return self.cli.run(["recruit", "collect", str(index), client])

    def recruit_all(self, client: str = "Official") -> CLIResult:
        """一键收取所有公招结果并开始新的公招

        Args:
            client: 客户端类型

        Returns:
            CLIResult: 执行结果
        """
        logger.info(f"Collecting all recruits for client: {client}")
        return self.cli.run(["recruit", "all", client])
