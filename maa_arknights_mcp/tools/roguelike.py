"""肉鸽/演算工具模块

提供集成战略（肉鸽）、生息演算等功能。
"""

import logging
from pathlib import Path
from typing import Optional

from ..cli import MAACLI, CLIResult

logger = logging.getLogger(__name__)


class RoguelikeTools:
    """肉鸽/演算工具类"""

    def __init__(self, cli: MAACLI):
        """
        Args:
            cli: MAA CLI 实例
        """
        self.cli = cli

    def roguelike(
        self,
        theme: str = "Phantom",
        starts_count: int = 0,
    ) -> CLIResult:
        """自动集成战略（肉鸽）

        Args:
            theme: 集成战略主题，可选 "Phantom"（幻影）、"Mizuki"（水月）、
                   "Sami"（萨米）、"Sarkaz"（萨卡兹）、"JieGarden"（集成战略3）
            starts_count: 开局选择数量（0=默认）

        Returns:
            CLIResult: 执行结果
        """
        args = ["roguelike", theme]
        if starts_count > 0:
            args.extend(["--starts-count", str(starts_count)])

        logger.info(f"Starting roguelike: theme={theme}, starts_count={starts_count}")
        return self.cli.run(args)

    def reclamation(self, theme: str = "Tales") -> CLIResult:
        """自动生息演算

        Args:
            theme: 生息演算主题，目前仅 "Tales" 可用

        Returns:
            CLIResult: 执行结果
        """
        logger.info(f"Starting reclamation: theme={theme}")
        return self.cli.run(["reclamation", theme])
