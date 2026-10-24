"""战斗任务工具模块

提供刷关卡、抄作业、保全派驻、悖论模拟等功能。
"""

import logging
from pathlib import Path
from typing import Optional

from ..cli import MAACLI, CLIResult

logger = logging.getLogger(__name__)


class CombatTools:
    """战斗任务工具类"""

    def __init__(self, cli: MAACLI):
        """
        Args:
            cli: MAA CLI 实例
        """
        self.cli = cli

    def fight(
        self,
        stage: str = "",
        mode: int = 1,
        count: int = 1,
        use_drugs: bool = False,
        drug_limit: int = 0,
        copilot: bool = False,
        copilot_uri: str = "",
    ) -> CLIResult:
        """运行战斗任务（刷关卡）

        Args:
            stage: 关卡名称，如 "1-7"、"BB-7"、"E8-2" 等，留空使用上次关卡
            mode: 模式（1=普通，2=自动战斗）
            count: 刷取次数
            use_drugs: 是否使用理智药
            drug_limit: 理智药使用上限（0=不限制）
            copilot: 是否使用抄作业
            copilot_uri: 作业 URI（maa://xxx 或本地文件路径）

        Returns:
            CLIResult: 执行结果
        """
        args = ["fight"]
        if stage:
            args.append(stage)
        if mode != 1:
            args.extend(["-m", str(mode)])
        if count != 1:
            args.extend(["-c", str(count)])
        if use_drugs:
            args.append("--use-drugs")
        if drug_limit > 0:
            args.extend(["--drug-limit", str(drug_limit)])
        if copilot and copilot_uri:
            args.extend(["--copilot", copilot_uri])

        logger.info(f"Fighting: stage={stage}, count={count}, use_drugs={use_drugs}")
        return self.cli.run(args)

    def copilot(self, maa_uris: str) -> CLIResult:
        """自动抄作业

        Args:
            maa_uris: 作业 URI，多个用空格分隔，可以是 maa://xxx 或本地文件路径

        Returns:
            CLIResult: 执行结果
        """
        uri_list = maa_uris.split()
        logger.info(f"Copilot with URIs: {uri_list}")
        return self.cli.run(["copilot"] + uri_list)

    def sscopilot(self, maa_uri: str) -> CLIResult:
        """自动保全派驻

        Args:
            maa_uri: 保全派驻作业 URI

        Returns:
            CLIResult: 执行结果
        """
        logger.info(f"SS Copilot with URI: {maa_uri}")
        return self.cli.run(["sscopilot", maa_uri])

    def paradoxcopilot(self, maa_uris: str) -> CLIResult:
        """自动悖论模拟

        Args:
            maa_uris: 悖论模拟作业 URI，多个用空格分隔

        Returns:
            CLIResult: 执行结果
        """
        uri_list = maa_uris.split()
        logger.info(f"Paradox Copilot with URIs: {uri_list}")
        return self.cli.run(["paradoxcopilot"] + uri_list)
