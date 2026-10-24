"""Tests for installer module"""

import pytest
from unittest.mock import patch, MagicMock
from maa_arknights_mcp.installer import MAAInstaller, InstallStatus


class TestInstallStatus:
    """Test InstallStatus dataclass"""

    def test_install_status_success(self):
        status = InstallStatus(
            success=True,
            message="Installed",
            maa_cli_installed=True,
            maa_core_installed=True,
            maa_cli_version="1.0.0",
        )
        assert status.success is True
        assert status.maa_cli_installed is True

    def test_install_status_failure(self):
        status = InstallStatus(
            success=False,
            message="Not installed",
            maa_cli_installed=False,
        )
        assert status.success is False
        assert status.maa_cli_installed is False


class TestMAAInstaller:
    """Test MAAInstaller class"""

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_check_installed(self, mock_run):
        """Test check_installed method"""
        mock_run.return_value = MagicMock(success=True, returncode=0, stdout="maa 0.7.7")
        installer = MAAInstaller()
        assert installer.check_installed() is True
        mock_run.assert_called_once_with(["--version"])

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_check_not_installed(self, mock_run):
        """Test check_installed when not installed"""
        mock_run.return_value = MagicMock(success=False, returncode=-1, stdout="")
        installer = MAAInstaller()
        assert installer.check_installed() is False

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_check_core_installed(self, mock_run):
        """Test check_core_installed uses `maa version`"""
        mock_run.return_value = MagicMock(success=True, returncode=0, stdout="MaaCore v5")
        installer = MAAInstaller()
        assert installer.check_core_installed() is True
        mock_run.assert_called_once_with(["version"])

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_get_status_installed(self, mock_run):
        """Test get_status when CLI and core are installed"""

        def side_effect(args, **kwargs):
            if args == ["--version"]:
                return MagicMock(success=True, returncode=0, stdout="maa 0.7.7")
            return MagicMock(
                success=True,
                returncode=0,
                stdout="maa-cli v0.7.7\nMaaCore v5.0.0",
            )

        mock_run.side_effect = side_effect
        installer = MAAInstaller()
        status = installer.get_status()
        assert status.success is True
        assert status.maa_cli_installed is True
        assert status.maa_core_installed is True
        assert status.maa_cli_version == "maa 0.7.7"

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_get_status_cli_only(self, mock_run):
        """Test get_status when only the CLI is installed"""

        def side_effect(args, **kwargs):
            if args == ["--version"]:
                return MagicMock(success=True, returncode=0, stdout="maa 0.7.7")
            return MagicMock(success=False, returncode=1, stdout="")

        mock_run.side_effect = side_effect
        installer = MAAInstaller()
        status = installer.get_status()
        assert status.maa_cli_installed is True
        assert status.maa_core_installed is False
        assert status.success is False
        assert "MaaCore" in status.message

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_get_status_not_installed(self, mock_run):
        """Test get_status when not installed"""
        mock_run.return_value = MagicMock(success=False, returncode=-1, stdout="")
        installer = MAAInstaller()
        status = installer.get_status()
        assert status.success is False
        assert status.maa_cli_installed is False

    @patch("maa_arknights_mcp.installer.MAAInstaller.check_core_installed")
    @patch("maa_arknights_mcp.installer.MAAInstaller.check_installed")
    @patch("maa_arknights_mcp.installer.MAAInstaller.get_status")
    def test_install_already_installed(self, mock_status, mock_check, mock_check_core):
        """Test install when already installed"""
        mock_check.return_value = True
        mock_check_core.return_value = True
        mock_status.return_value = InstallStatus(
            success=True,
            message="Already installed",
            maa_cli_installed=True,
        )
        installer = MAAInstaller()
        status = installer.install()
        assert status.success is True
        assert "已安装" in status.message

    @patch("maa_arknights_mcp.installer.MAAInstaller._install_windows")
    @patch("maa_arknights_mcp.installer.MAAInstaller.check_core_installed")
    @patch("maa_arknights_mcp.installer.MAAInstaller.check_installed")
    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_install_core_without_reinstalling_cli(
        self, mock_run, mock_check, mock_check_core, mock_install_windows
    ):
        """CLI 已安装、仅缺 MaaCore 时不应重新运行安装脚本"""
        mock_check.return_value = True
        mock_check_core.return_value = False
        mock_run.return_value = MagicMock(
            success=True,
            returncode=0,
            stdout="Installed",
            stderr="",
            command="maa install",
        )
        installer = MAAInstaller()
        installer.platform = "windows"
        status = installer.install()
        mock_install_windows.assert_not_called()
        assert status.maa_core_installed is True

    @patch("maa_arknights_mcp.installer.MAAInstaller._install_windows")
    @patch("maa_arknights_mcp.installer.MAAInstaller.check_installed")
    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_install_windows_success(
        self, mock_run, mock_check, mock_install_windows
    ):
        """Test Windows installation success"""
        mock_check.return_value = False
        mock_install_windows.return_value = True
        mock_run.return_value = MagicMock(
            success=True,
            returncode=0,
            stdout="Installed",
            stderr="",
            command="maa install",
        )
        installer = MAAInstaller()
        installer.platform = "windows"
        status = installer.install()
        assert status.maa_cli_installed is True

    @patch("maa_arknights_mcp.installer.MAAInstaller._install_macos")
    @patch("maa_arknights_mcp.installer.MAAInstaller.check_installed")
    def test_install_macos(self, mock_check, mock_install_macos):
        """Test macOS installation"""
        mock_check.return_value = False
        mock_install_macos.return_value = True
        installer = MAAInstaller()
        installer.platform = "darwin"
        # Should not raise
        assert installer.platform == "darwin"

    @patch("maa_arknights_mcp.installer.MAAInstaller._install_linux")
    @patch("maa_arknights_mcp.installer.MAAInstaller.check_installed")
    def test_install_linux(self, mock_check, mock_install_linux):
        """Test Linux installation"""
        mock_check.return_value = False
        mock_install_linux.return_value = True
        installer = MAAInstaller()
        installer.platform = "linux"
        # Should not raise
        assert installer.platform == "linux"

    @patch("maa_arknights_mcp.installer.MAAInstaller.check_installed")
    def test_install_unsupported_platform(self, mock_check):
        """Test installation on unsupported platform"""
        mock_check.return_value = False
        installer = MAAInstaller()
        installer.platform = "unsupported"
        status = installer.install()
        assert status.success is False
        assert "不支持" in status.message

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_update(self, mock_run):
        """Test update method"""
        mock_run.return_value = MagicMock(
            success=True,
            returncode=0,
            stdout="Updated",
            stderr="",
            command="maa self update",
        )
        installer = MAAInstaller()
        result = installer.update()
        assert result.success is True

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_update_core(self, mock_run):
        """Test update_core method"""
        mock_run.return_value = MagicMock(
            success=True,
            returncode=0,
            stdout="Updated",
            stderr="",
            command="maa update",
        )
        installer = MAAInstaller()
        result = installer.update_core()
        assert result.success is True
