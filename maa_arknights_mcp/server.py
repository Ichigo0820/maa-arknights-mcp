"""MCP Server 核心

定义 FastMCP 实例并注册所有工具。
"""

import json
import logging
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

from .cli import MAACLI
from .tools.game import GameTools
from .tools.combat import CombatTools
from .tools.roguelike import RoguelikeTools
from .tools.infrastructure import InfrastructureTools
from .tools.recruit import RecruitTools

logger = logging.getLogger(__name__)


def create_mcp_server(
    maa_cmd: str = "maa",
    timeout: int = 600,
    log_dir: Optional[Path] = None,
) -> FastMCP:
    """创建 MCP Server 实例

    Args:
        maa_cmd: MAA CLI 命令名
        timeout: 默认超时时间（秒）
        log_dir: 日志目录

    Returns:
        FastMCP 实例
    """
    mcp = FastMCP(
        name="MAA Arknights",
        instructions=(
            "MAA Arknights MCP Server - 明日方舟自动化助手。"
            "通过 MAA CLI 自动化游戏操作，包括刷关卡、肉鸽、基建、公招等。"
        ),
    )

    # 创建 MAA CLI 实例
    cli = MAACLI(cmd=maa_cmd, timeout=timeout, log_dir=log_dir)

    # 创建工具实例
    game_tools = GameTools(cli)
    combat_tools = CombatTools(cli)
    roguelike_tools = RoguelikeTools(cli)
    infrastructure_tools = InfrastructureTools(cli)
    recruit_tools = RecruitTools(cli)

    # 注册游戏控制工具
    _register_game_tools(mcp, game_tools)

    # 注册战斗任务工具
    _register_combat_tools(mcp, combat_tools)

    # 注册肉鸽/演算工具
    _register_roguelike_tools(mcp, roguelike_tools)

    # 注册基建工具
    _register_infrastructure_tools(mcp, infrastructure_tools)

    # 注册公招工具
    _register_recruit_tools(mcp, recruit_tools)

    # 注册配置管理工具
    _register_config_tools(mcp, cli)

    return mcp


def _register_game_tools(mcp: FastMCP, game: GameTools) -> None:
    """注册游戏控制工具"""

    @mcp.tool()
    def maa_startup(
        client: str = "Official",
        timeout: int = 120,
    ) -> str:
        """启动明日方舟游戏并进入主界面

        Args:
            client: 客户端类型，如 "Official"（官服）、"Bilibili"（B 服）等
            timeout: 超时时间（秒）
        """
        result = game.startup(client=client, timeout=timeout)
        return _format_result(result)

    @mcp.tool()
    def maa_closedown(client: str = "Official") -> str:
        """关闭明日方舟游戏客户端

        Args:
            client: 客户端类型
        """
        result = game.closedown(client=client)
        return _format_result(result)

    @mcp.tool()
    def maa_activity(client: str = "Official") -> str:
        """获取游戏当前活动信息

        Args:
            client: 客户端类型
        """
        result = game.activity(client=client)
        return _format_result(result)


def _register_combat_tools(mcp: FastMCP, combat: CombatTools) -> None:
    """注册战斗任务工具"""

    @mcp.tool()
    def maa_fight(
        stage: str = "",
        mode: int = 1,
        count: int = 1,
        use_drugs: bool = False,
        drug_limit: int = 0,
        copilot: bool = False,
        copilot_uri: str = "",
    ) -> str:
        """运行战斗任务（刷关卡）

        Args:
            stage: 关卡名称，如 "1-7"、"BB-7"、"E8-2" 等，留空使用上次关卡
            mode: 模式（1=普通，2=自动战斗）
            count: 刷取次数
            use_drugs: 是否使用理智药
            drug_limit: 理智药使用上限（0=不限制）
            copilot: 是否使用抄作业
            copilot_uri: 作业 URI（maa://xxx 或本地文件路径）
        """
        result = combat.fight(
            stage=stage,
            mode=mode,
            count=count,
            use_drugs=use_drugs,
            drug_limit=drug_limit,
            copilot=copilot,
            copilot_uri=copilot_uri,
        )
        return _format_result(result)

    @mcp.tool()
    def maa_copilot(maa_uris: str) -> str:
        """自动抄作业

        Args:
            maa_uris: 作业 URI，多个用空格分隔，可以是 maa://xxx 或本地文件路径
        """
        result = combat.copilot(maa_uris=maa_uris)
        return _format_result(result)

    @mcp.tool()
    def maa_sscopilot(maa_uri: str) -> str:
        """自动保全派驻

        Args:
            maa_uri: 保全派驻作业 URI
        """
        result = combat.sscopilot(maa_uri=maa_uri)
        return _format_result(result)

    @mcp.tool()
    def maa_paradoxcopilot(maa_uris: str) -> str:
        """自动悖论模拟

        Args:
            maa_uris: 悖论模拟作业 URI，多个用空格分隔
        """
        result = combat.paradoxcopilot(maa_uris=maa_uris)
        return _format_result(result)


def _register_roguelike_tools(mcp: FastMCP, roguelike: RoguelikeTools) -> None:
    """注册肉鸽/演算工具"""

    @mcp.tool()
    def maa_roguelike(
        theme: str = "Phantom",
        starts_count: int = 0,
    ) -> str:
        """自动集成战略（肉鸽）

        Args:
            theme: 集成战略主题，可选 "Phantom"（幻影）、"Mizuki"（水月）、
                   "Sami"（萨米）、"Sarkaz"（萨卡兹）、"JieGarden"（集成战略 3）
            starts_count: 开局选择数量（0=默认）
        """
        result = roguelike.roguelike(theme=theme, starts_count=starts_count)
        return _format_result(result)

    @mcp.tool()
    def maa_reclamation(theme: str = "Tales") -> str:
        """自动生息演算

        Args:
            theme: 生息演算主题，目前仅 "Tales" 可用
        """
        result = roguelike.reclamation(theme=theme)
        return _format_result(result)


def _register_infrastructure_tools(mcp: FastMCP, infrast: InfrastructureTools) -> None:
    """注册基建工具"""

    @mcp.tool()
    def maa_infrast_manage(client: str = "Official") -> str:
        """基建管理（自动换班、制造、采购等）

        Args:
            client: 客户端类型
        """
        result = infrast.infrast_manage(client=client)
        return _format_result(result)

    @mcp.tool()
    def maa_infrast_production(client: str = "Official") -> str:
        """基建制造（开始制造任务）

        Args:
            client: 客户端类型
        """
        result = infrast.infrast_production(client=client)
        return _format_result(result)

    @mcp.tool()
    def maa_infrast_trade(client: str = "Official") -> str:
        """基建贸易（出售物资）

        Args:
            client: 客户端类型
        """
        result = infrast.infrast_trade(client=client)
        return _format_result(result)

    @mcp.tool()
    def maa_infrast_purchase(client: str = "Official") -> str:
        """基建采购（购买物资）

        Args:
            client: 客户端类型
        """
        result = infrast.infrast_purchase(client=client)
        return _format_result(result)

    @mcp.tool()
    def maa_infrast_energy(client: str = "Official") -> str:
        """基建收取理智

        Args:
            client: 客户端类型
        """
        result = infrast.infrast_energy(client=client)
        return _format_result(result)

    @mcp.tool()
    def maa_infrast_switch(operator: str, room: str) -> str:
        """基建换班

        Args:
            operator: 干员名称
            room: 房间类型（power, production, trade, control, re, office）
        """
        result = infrast.infrast_switch(operator=operator, room=room)
        return _format_result(result)


def _register_recruit_tools(mcp: FastMCP, recruit: RecruitTools) -> None:
    """注册公招工具"""

    @mcp.tool()
    def maa_recruit_get(client: str = "Official") -> str:
        """获取当前公招结果

        Args:
            client: 客户端类型
        """
        result = recruit.recruit_get(client=client)
        return _format_result(result)

    @mcp.tool()
    def maa_recruit_start(
        time: int = 7200,
        tags: Optional[str] = None,
        client: str = "Official",
    ) -> str:
        """开始公招

        Args:
            time: 公招时间（秒），300=5 分钟, 1800=30 分钟, 7200=2 小时, 28800=8 小时
            tags: 标签组合，如 "6 星 近卫 医疗"，留空随机
            client: 客户端类型
        """
        result = recruit.recruit_start(time=time, tags=tags, client=client)
        return _format_result(result)

    @mcp.tool()
    def maa_recruit_collect(index: int = 0, client: str = "Official") -> str:
        """收取公招结果

        Args:
            index: 公招槽位索引（0-3）
            client: 客户端类型
        """
        result = recruit.recruit_collect(index=index, client=client)
        return _format_result(result)

    @mcp.tool()
    def maa_recruit_all(client: str = "Official") -> str:
        """一键收取所有公招结果并开始新的公招

        Args:
            client: 客户端类型
        """
        result = recruit.recruit_all(client=client)
        return _format_result(result)


def _register_config_tools(mcp: FastMCP, cli: MAACLI) -> None:
    """注册配置管理工具"""

    @mcp.tool()
    def maa_install() -> str:
        """安装 MaaCore 及资源（首次使用需要）"""
        result = cli.run(["install"])
        return _format_result(result)

    @mcp.tool()
    def maa_update() -> str:
        """更新 MaaCore 及资源"""
        result = cli.run(["update"])
        return _format_result(result)

    @mcp.tool()
    def maa_self_update(force: bool = False) -> str:
        """更新 maa-cli 自身"""
        args = ["self", "update"]
        if force:
            args.append("--force")
        result = cli.run(args)
        return _format_result(result)

    @mcp.tool()
    def maa_init(name: Optional[str] = None, force: bool = False) -> str:
        """初始化 MAA 配置"""
        args = ["init"]
        if name:
            args.extend(["--name", name])
        if force:
            args.append("--force")
        result = cli.run(args)
        return _format_result(result)

    @mcp.tool()
    def maa_list() -> str:
        """列出所有可用的预定义任务"""
        result = cli.run(["list"])
        return _format_result(result)

    @mcp.tool()
    def maa_hot_update() -> str:
        """手动更新热更新资源"""
        result = cli.run(["hot-update"])
        return _format_result(result)

    @mcp.tool()
    def maa_remainder(
        divisor: int = 4, timezone: Optional[str] = None
    ) -> str:
        """获取 DayMod 条件的偏移量

        Args:
            divisor: 除数
            timezone: 时区
        """
        args = ["remainder", str(divisor)]
        if timezone:
            args.extend(["--timezone", timezone])
        result = cli.run(args)
        return _format_result(result)

    @mcp.tool()
    def maa_dir(dir_name: str) -> str:
        """获取 MAA 特定目录路径

        Args:
            dir_name: 目录类型，可选 "data"、"library"、"resource"、"hot-update"、
                      "config"、"cache"、"log"
        """
        result = cli.run(["dir", dir_name])
        return _format_result(result)

    @mcp.tool()
    def maa_version() -> str:
        """获取 maa-cli 和 MaaCore 版本信息"""
        result = cli.run(["version"])
        return _format_result(result)

    @mcp.tool()
    def maa_cleanup(targets: str = "") -> str:
        """清除 MAA 缓存

        Args:
            targets: 要清除的缓存类型，多个用空格分隔
        """
        args = ["cleanup"]
        if targets:
            args.extend(targets.split())
        result = cli.run(args)
        return _format_result(result)

    @mcp.tool()
    def maa_convert(
        input_file: str,
        output_file: Optional[str] = None,
        format: str = "",
    ) -> str:
        """转换配置文件格式（JSON/YAML/TOML）

        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径（可选）
            format: 输出格式（json/yaml/toml）
        """
        args = ["convert", input_file]
        if output_file:
            args.append(output_file)
        if format:
            args.extend(["-t", format])
        result = cli.run(args)
        return _format_result(result)

    @mcp.tool()
    def maa_import(file_path: str, type: str = "cli") -> str:
        """导入配置文件

        Args:
            file_path: 配置文件路径
            type: 配置文件类型（cli/profile/infrast 等）
        """
        result = cli.run(["import", file_path, "-t", type])
        return _format_result(result)


def _format_result(result) -> str:
    """格式化 CLI 结果为 JSON 字符串"""
    return json.dumps(
        {
            "success": result.success,
            "returncode": result.returncode,
            "message": (result.stdout or result.stderr).strip(),
            "command": result.command,
        },
        ensure_ascii=False,
        indent=2,
    )
