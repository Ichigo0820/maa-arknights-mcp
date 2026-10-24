"""MAA Arknights MCP Server - CLI 入口

作为标准 MCP Server 运行，通过 stdio 与 AI 客户端通信。
"""

import argparse
import logging
import sys
from pathlib import Path

from .server import create_mcp_server


def main():
    """启动 MCP Server"""
    parser = argparse.ArgumentParser(
        description="MAA Arknights MCP Server - Automate Arknights via MAA CLI",
        prog="maa-arknights-mcp",
    )
    parser.add_argument(
        "--maa-cmd",
        type=str,
        default="maa",
        help="MAA CLI command name (default: maa)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Default timeout for MAA CLI commands (default: 600)",
    )
    parser.add_argument(
        "--log-dir",
        type=str,
        default=None,
        help="Log directory",
    )
    parser.add_argument(
        "--transport",
        type=str,
        choices=["stdio", "http", "sse", "streamable-http"],
        default="stdio",
        help="Transport mode (default: stdio)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="HTTP server port (only for http/sse/streamable-http transport)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="HTTP server host (only for http/sse/streamable-http transport)",
    )

    args = parser.parse_args()

    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # 创建并运行 MCP Server
    log_dir = Path(args.log_dir) if args.log_dir else None
    mcp = create_mcp_server(
        maa_cmd=args.maa_cmd,
        timeout=args.timeout,
        log_dir=log_dir,
    )

    if args.transport in ("http", "sse", "streamable-http"):
        mcp.run_http_async(
            transport=args.transport,
            host=args.host,
            port=args.port,
        )
    else:
        # stdio 模式 - MCP 标准协议
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
