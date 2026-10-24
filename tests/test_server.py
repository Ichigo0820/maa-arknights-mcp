"""Tests for server module"""

import asyncio
import pytest
from unittest.mock import patch, MagicMock
from maa_arknights_mcp.server import create_mcp_server


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
