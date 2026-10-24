"""Tests for CLI module"""

import pytest
from unittest.mock import patch, MagicMock
from maa_arknights_mcp.cli import MAACLI, CLIResult


class TestCLIResult:
    """Test CLIResult dataclass"""

    def test_cli_result_success(self):
        result = CLIResult(
            success=True,
            returncode=0,
            stdout="Success",
            stderr="",
            command="maa fight",
        )
        assert result.success is True
        assert result.returncode == 0

    def test_cli_result_failure(self):
        result = CLIResult(
            success=False,
            returncode=1,
            stdout="",
            stderr="Error",
            command="maa fight",
        )
        assert result.success is False
        assert result.returncode == 1


class TestMAACLI:
    """Test MAACLI class"""

    @patch("subprocess.run")
    def test_run_success(self, mock_run):
        """Test successful command execution"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Success output",
            stderr="",
        )

        cli = MAACLI(cmd="maa")
        result = cli.run(["fight", "BB-7"])

        assert result.success is True
        assert result.stdout == "Success output"
        assert "maa fight BB-7" in result.command

    @patch("subprocess.run")
    def test_run_failure(self, mock_run):
        """Test failed command execution"""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Error output",
        )

        cli = MAACLI(cmd="maa")
        result = cli.run(["fight", "invalid"])

        assert result.success is False
        assert result.returncode == 1

    @patch("subprocess.run")
    def test_run_timeout(self, mock_run):
        """Test command timeout"""
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd=["maa", "fight"],
            timeout=60,
        )

        cli = MAACLI(cmd="maa", timeout=60)
        result = cli.run(["fight", "BB-7"], timeout=60)

        assert result.success is False
        assert "timed out" in result.stderr.lower()

    @patch("subprocess.run")
    def test_run_file_not_found(self, mock_run):
        """Test command not found"""
        mock_run.side_effect = FileNotFoundError()

        cli = MAACLI(cmd="nonexistent-cli")
        result = cli.run(["version"])

        assert result.success is False
        assert "not found" in result.stderr.lower()

    @patch("subprocess.run")
    def test_parse_output_json(self, mock_run):
        """Test JSON output parsing"""
        import json

        mock_output = json.dumps({"key": "value"})
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=mock_output,
            stderr="",
        )

        cli = MAACLI(cmd="maa")
        result = cli.run(["list"])

        assert result.data == {"key": "value"}

    def test_get_maa_cmd(self):
        """Test get_maa_cmd method"""
        cli = MAACLI(cmd="maa-cli")
        assert cli.get_maa_cmd() == "maa-cli"

    def test_check_available(self):
        """Test check_available method"""
        cli = MAACLI(cmd="nonexistent-cli-for-test")
        assert cli.check_available() is False

    def test_get_version(self):
        """Test get_version method"""
        cli = MAACLI(cmd="nonexistent-cli-for-test")
        assert cli.get_version() is None

    def test_get_dir(self):
        """Test get_dir method"""
        cli = MAACLI(cmd="nonexistent-cli-for-test")
        assert cli.get_dir("config") is None
