"""MAA Arknights MCP Server - CLI 入口

作为标准 MCP Server 运行，通过 stdio 与 AI 客户端通信。
支持安装、更新 MAA CLI 及 MaaCore。
"""

import argparse
import logging
import sys
from pathlib import Path

from .installer import MAAInstaller, install_maa
from .server import create_mcp_server


def main():
    """启动 MCP Server"""
    parser = argparse.ArgumentParser(
        description="MAA Arknights MCP Server - Automate Arknights via MAA CLI",
        prog="maa-arknights-mcp",
    )

    # 子命令
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # server 子命令（默认）
    server_parser = subparsers.add_parser("server", help="启动 MCP Server")
    server_parser.add_argument(
        "--maa-cmd",
        type=str,
        default="maa",
        help="MAA CLI command name (default: maa)",
    )
    server_parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Default timeout for MAA CLI commands (default: 600)",
    )
    server_parser.add_argument(
        "--log-dir",
        type=str,
        default=None,
        help="Log directory",
    )
    server_parser.add_argument(
        "--transport",
        type=str,
        choices=["stdio", "http", "sse", "streamable-http"],
        default="stdio",
        help="Transport mode (default: stdio)",
    )
    server_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="HTTP server port (only for http/sse/streamable-http transport)",
    )
    server_parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="HTTP server host (only for http/sse/streamable-http transport)",
    )

    # install 子命令
    install_parser = subparsers.add_parser("install", help="安装 MAA CLI 及 MaaCore")
    install_parser.add_argument(
        "--force",
        action="store_true",
        help="强制重新安装",
    )
    install_parser.add_argument(
        "--maa-cmd",
        type=str,
        default="maa",
        help="MAA CLI command name",
    )

    # check 子命令
    check_parser = subparsers.add_parser("check", help="检查 MAA CLI 安装状态")
    check_parser.add_argument(
        "--maa-cmd",
        type=str,
        default="maa",
        help="MAA CLI command name",
    )

    # update 子命令
    update_parser = subparsers.add_parser("update", help="更新 MAA CLI 或 MaaCore")
    update_parser.add_argument(
        "--type",
        type=str,
        choices=["cli", "core", "all"],
        default="all",
        help="Update type (default: all)",
    )

    args = parser.parse_args()

    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # 处理子命令
    if args.command == "install":
        _handle_install(args)
    elif args.command == "check":
        _handle_check(args)
    elif args.command == "update":
        _handle_update(args)
    else:
        # 默认启动 MCP Server
        _handle_server(args)


def _handle_install(args) -> None:
    """处理安装命令"""
    print("正在安装 MAA CLI 及 MaaCore...")
    print(f"平台：{__import__('platform').system()}")
    print()

    status = install_maa(maa_cmd=args.maa_cmd, force=args.force)

    print()
    if status.success:
        print("✅ 安装成功！")
        if status.maa_cli_installed:
            print(f"   MAA CLI 版本：{status.maa_cli_version}")
        if status.maa_core_installed:
            print(f"   MaaCore 版本：{status.maa_core_version}")
    else:
        print("❌ 安装失败！")
        print(f"   错误信息：{status.message}")
        print()
        print("请尝试手动安装：")
        print("  Windows: winget install maa")
        print("  macOS:   brew install MaaAssistantArknights/tap/maa-cli")
        print("  Linux:   curl -fsSL https://raw.githubusercontent.com/")
        print("           MaaAssistantArknights/maa-cli/main/install.sh | bash")
        sys.exit(1)


def _handle_check(args) -> None:
    """处理检查命令"""
    installer = MAAInstaller(maa_cmd=args.maa_cmd)
    status = installer.get_status()

    print("MAA CLI 安装状态：")
    print(f"  已安装：{'是' if status.maa_cli_installed else '否'}")
    if status.maa_cli_installed:
        print(f"  版本：{status.maa_cli_version}")
    print(f"  消息：{status.message}")


def _handle_update(args) -> None:
    """处理更新命令"""
    installer = MAAInstaller()

    if args.type in ("cli", "all"):
        print("正在更新 MAA CLI...")
        result = installer.update()
        if result.success:
            print("✅ MAA CLI 更新成功")
        else:
            print(f"❌ MAA CLI 更新失败：{result.stderr}")

    if args.type in ("core", "all"):
        print("正在更新 MaaCore 及资源...")
        result = installer.update_core()
        if result.success:
            print("✅ MaaCore 更新成功")
        else:
            print(f"❌ MaaCore 更新失败：{result.stderr}")


def _handle_server(args) -> None:
    """处理服务器命令"""
    # 创建并运行 MCP Server
    # 使用 getattr 提供默认值，兼容无子命令的情况（OpenCode 启动方式）
    log_dir = Path(getattr(args, "log_dir", None)) if getattr(args, "log_dir", None) else None
    mcp = create_mcp_server(
        maa_cmd=getattr(args, "maa_cmd", "maa"),
        timeout=getattr(args, "timeout", 600),
        log_dir=log_dir,
    )

    transport = getattr(args, "transport", "stdio")
    if transport in ("http", "sse", "streamable-http"):
        mcp.run_http_async(
            transport=transport,
            host=getattr(args, "host", "127.0.0.1"),
            port=getattr(args, "port", 8000),
        )
    else:
        # stdio 模式 - MCP 标准协议
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
