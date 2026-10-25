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
        count: int = 1,
        medicine: int = 0,
        expiring_medicine: int = 0,
        series: Optional[int] = None,
        addr: Optional[str] = None,
        client_type: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> CLIResult:
        """运行战斗任务（刷关卡）

        注意：本 MCP 不提供「使用源石（至纯源石）补充理智」的能力，
        因此不会向 maa-cli 传递 --stone 参数（等价于 stone=0，永不碎石）。

        Args:
            stage: 关卡名称，如 "1-7"、"BB-7"、"E8-2" 等，留空使用上次关卡
            count: 刷取次数（0 = 一直刷，直到理智耗尽或手动停止）
            medicine: 使用（普通）理智药的数量
            expiring_medicine: 使用临期理智药的数量
            series: 连续作战次数（-1~6），留空使用 MAA 默认值
            addr: ADB 设备地址，如 "127.0.0.1:5555"；留空使用 MAA 配置/默认设备
            client_type: 关卡崩溃后用于重启的客户端类型
            timeout: 超时时间（秒），留空使用默认值

        Returns:
            CLIResult: 执行结果
        """
        args = ["fight"]
        if stage:
            args.append(stage)
        if count > 0:
            args.extend(["--times", str(count)])
        if medicine > 0:
            args.extend(["-m", str(medicine)])
        if expiring_medicine > 0:
            args.extend(["--expiring-medicine", str(expiring_medicine)])
        # 刻意不传 --stone：源石接口对本 MCP 关闭，避免误消耗至纯源石
        if series is not None:
            args.extend(["--series", str(series)])
        if client_type:
            args.extend(["--client-type", client_type])
        if addr:
            args.extend(["-a", addr])

        logger.info(
            f"Fighting: stage={stage}, times={count}, medicine={medicine}, "
            f"expiring_medicine={expiring_medicine}, addr={addr}"
        )
        return self.cli.run(args, timeout=timeout)

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
