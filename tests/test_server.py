"""Tests for server module"""

import asyncio
import json
import re
from pathlib import Path

import pytest
from unittest.mock import patch, MagicMock
from maa_arknights_mcp.server import create_mcp_server

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _load_opencode_config() -> dict:
    """读取 opencode.jsonc（去除行注释后解析）"""
    text = (PROJECT_ROOT / "opencode.jsonc").read_text(encoding="utf-8")
    text = re.sub(r"^\s*//.*$", "", text, flags=re.MULTILINE)
    return json.loads(text)


async def _call_tool(mcp, tool_name, args):
    """Helper to call MCP tools asynchronously"""
    return await mcp.call_tool(tool_name, args)


class TestMCPServer:
    """Test MCP Server creation"""

    def test_create_mcp_server(self):
        """Test MCP server creation"""
        mcp = create_mcp_server(maa_cmd="maa")
        assert mcp is not None
        assert mcp.name == "MAA Arknights"

    def test_mcp_server_tools(self):
        """Test that tools are registered"""
        mcp = create_mcp_server(maa_cmd="maa")
        # Check that server was created successfully
        assert mcp is not None
        assert mcp.name == "MAA Arknights"

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_maa_startup_tool(self, mock_run):
        """Test maa_startup tool"""
        mock_run.return_value = MagicMock(
            success=True,
            returncode=0,
            stdout="Game started",
            stderr="",
            command="maa startup Official",
        )

        mcp = create_mcp_server(maa_cmd="maa")
        result = asyncio.run(_call_tool(mcp, "maa_startup", {"client": "Official"}))
        assert result is not None

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_maa_fight_tool(self, mock_run):
        """Test maa_fight tool"""
        mock_run.return_value = MagicMock(
            success=True,
            returncode=0,
            stdout="Fight completed",
            stderr="",
            command="maa fight BB-7",
        )

        mcp = create_mcp_server(maa_cmd="maa")
        result = asyncio.run(_call_tool(mcp, "maa_fight", {"stage": "BB-7", "count": 3}))
        assert result is not None

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_maa_roguelike_tool(self, mock_run):
        """Test maa_roguelike tool"""
        mock_run.return_value = MagicMock(
            success=True,
            returncode=0,
            stdout="Roguelike started",
            stderr="",
            command="maa roguelike Phantom",
        )

        mcp = create_mcp_server(maa_cmd="maa")
        result = asyncio.run(_call_tool(mcp, "maa_roguelike", {"theme": "Phantom"}))
        assert result is not None

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_maa_infrast_manage_tool(self, mock_run):
        """Test maa_infrast_manage tool"""
        mock_run.return_value = MagicMock(
            success=True,
            returncode=0,
            stdout="Infrastructure managed",
            stderr="",
            command="maa infrast manage Official",
        )

        mcp = create_mcp_server(maa_cmd="maa")
        result = asyncio.run(_call_tool(mcp, "maa_infrast_manage", {"client": "Official"}))
        assert result is not None

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_maa_recruit_all_tool(self, mock_run):
        """Test maa_recruit_all tool"""
        mock_run.return_value = MagicMock(
            success=True,
            returncode=0,
            stdout="Recruits collected",
            stderr="",
            command="maa recruit all Official",
        )

        mcp = create_mcp_server(maa_cmd="maa")
        result = asyncio.run(_call_tool(mcp, "maa_recruit_all", {"client": "Official"}))
        assert result is not None

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_maa_run_tool(self, mock_run):
        """Test maa_run tool（自定义任务，用于基建/公招等 0.7.x 无子命令的任务）"""
        mock_run.return_value = MagicMock(
            success=True,
            returncode=0,
            stdout="Task completed",
            stderr="",
            command="maa run daily",
        )

        mcp = create_mcp_server(maa_cmd="maa")
        result = asyncio.run(
            _call_tool(
                mcp,
                "maa_run",
                {"task": "daily", "addr": "127.0.0.1:58526"},
            )
        )
        assert result is not None
        mock_run.assert_called_once_with(
            ["run", "daily", "-a", "127.0.0.1:58526"], timeout=600
        )

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_maa_version_tool(self, mock_run):
        """Test maa_version tool"""
        mock_run.return_value = MagicMock(
            success=True,
            returncode=0,
            stdout="maa-cli 1.0.0\nMaaCore 1.0.0",
            stderr="",
            command="maa version",
        )

        mcp = create_mcp_server(maa_cmd="maa")
        result = asyncio.run(_call_tool(mcp, "maa_version", {}))
        assert result is not None


class TestToolNaming:
    """工具名必须能在 OpenCode Code Mode 中通过 tools.<server>.<tool> 调用"""

    def test_registered_tool_names_are_identifier_safe(self):
        """注册的工具名只能包含字母、数字和下划线"""
        mcp = create_mcp_server(maa_cmd="maa")
        tools = asyncio.run(mcp.list_tools())
        names = [tool.name for tool in tools]

        assert "maa_check" in names
        for name in names:
            assert re.fullmatch(
                r"[A-Za-z0-9_]+", name
            ), f"工具名 {name!r} 含有非法字符，Code Mode 将无法调用"

    def test_opencode_server_name_is_identifier_safe(self):
        """OpenCode 服务器名不能包含连字符，否则工具名为 tools.maa-arknights_xxx 无法调用"""
        config = _load_opencode_config()
        servers = config["mcp"]["servers"]

        assert servers, "opencode.jsonc 中未配置任何 MCP 服务器"
        for name, server in servers.items():
            assert re.fullmatch(
                r"[A-Za-z0-9_]+", name
            ), f"MCP 服务器名 {name!r} 含有非法字符，请改为下划线命名"
            assert server["type"] == "local"
            assert server["command"], f"MCP 服务器 {name!r} 缺少 command"

    def test_opencode_config_enables_code_mode(self):
        """默认（不写 codemode）走 Code Mode，工具才会出现在 execute 目录中"""
        servers = _load_opencode_config()["mcp"]["servers"]

        for name, server in servers.items():
            assert server.get("codemode", True) is not False, (
                f"MCP 服务器 {name!r} 关闭了 Code Mode，"
                "工具将无法通过 tools.<server>.<tool> 调用"
            )

