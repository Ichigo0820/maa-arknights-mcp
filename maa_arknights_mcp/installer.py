"""MAA CLI 安装器模块

自动检测、安装和更新 MAA CLI 及 MaaCore。
支持 Windows、macOS、Linux 平台。
"""

import logging
import platform
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .cli import MAACLI, CLIResult

logger = logging.getLogger(__name__)


@dataclass
class InstallStatus:
    """安装状态"""

    success: bool
    message: str
    maa_cli_installed: bool = False
    maa_core_installed: bool = False
    maa_cli_version: Optional[str] = None
    maa_core_version: Optional[str] = None


class MAAInstaller:
    """MAA CLI 安装器

    自动检测、安装和更新 MAA CLI 及 MaaCore。

    Usage:
        installer = MAAInstaller()
        status = installer.install()
        if status.success:
            print(f"MAA CLI 版本：{status.maa_cli_version}")
    """

    def __init__(self, maa_cmd: str = "maa"):
        """
        Args:
            maa_cmd: MAA CLI 命令名
        """
        self.maa_cmd = maa_cmd
        self.platform = platform.system().lower()  # windows, darwin, linux
        self.cli = MAACLI(cmd=maa_cmd)

    def check_installed(self) -> bool:
        """检查 MAA CLI 是否可用（不要求 MaaCore 已安装）"""
        return self.cli.run(["--version"]).success

    def check_core_installed(self) -> bool:
        """检查 MaaCore 及资源是否已安装

        `maa version` 会同时输出 maa-cli 与 MaaCore 版本，
        未安装 MaaCore 时该命令返回非 0。
        """
        return self.cli.run(["version"]).success

    def get_status(self) -> InstallStatus:
        """获取当前安装状态"""
        maa_cli_installed = self.check_installed()
        maa_cli_version = None
        maa_core_installed = False
        maa_core_version = None

        if maa_cli_installed:
            cli_version = self.cli.run(["--version"])
            maa_cli_version = cli_version.stdout.strip() or None

            version_result = self.cli.run(["version"])
            maa_core_installed = version_result.success
            if maa_core_installed:
                maa_core_version = version_result.stdout.strip() or None

        if not maa_cli_installed:
            message = "MAA CLI 未安装"
        elif maa_core_installed:
            message = "MAA CLI 及 MaaCore 已安装"
        else:
            message = "MAA CLI 已安装，但 MaaCore/资源未安装，请运行 maa_install"

        return InstallStatus(
            success=maa_cli_installed and maa_core_installed,
            message=message,
            maa_cli_installed=maa_cli_installed,
            maa_core_installed=maa_core_installed,
            maa_cli_version=maa_cli_version,
            maa_core_version=maa_core_version,
        )

    def install(
        self,
        force: bool = False,
        maa_cmd: Optional[str] = None,
    ) -> InstallStatus:
        """安装 MAA CLI 及 MaaCore

        Args:
            force: 强制重新安装
            maa_cmd: 自定义 MAA CLI 命令名

        Returns:
            InstallStatus: 安装状态
        """
        if maa_cmd:
            self.maa_cmd = maa_cmd
            self.cli = MAACLI(cmd=maa_cmd)

        # 检查是否已安装
        cli_ready = self.check_installed()
        core_ready = self.check_core_installed() if cli_ready else False

        if cli_ready and core_ready and not force:
            status = self.get_status()
            status.message = "MAA CLI 及 MaaCore 已安装，使用 --force 强制重新安装"
            return status

        # CLI 已安装且只是缺少 MaaCore 时，跳过 CLI 安装步骤
        if not cli_ready or force:
            logger.info(f"开始安装 MAA CLI (平台：{self.platform})")

            # 根据平台选择安装方式
            if self.platform == "windows":
                success = self._install_windows()
            elif self.platform == "darwin":
                success = self._install_macos()
            elif self.platform == "linux":
                success = self._install_linux()
            else:
                return InstallStatus(
                    success=False,
                    message=f"不支持的平台：{self.platform}",
                )

            # 安装脚本失败时，若 CLI 实际已可用则继续安装 MaaCore
            if not success and not self.check_installed():
                return InstallStatus(
                    success=False,
                    message="MAA CLI 安装失败，请手动安装",
                )

        # 安装 MaaCore
        logger.info("安装 MaaCore 及资源...")
        core_result = self.cli.run(["install"])

        if core_result.success:
            logger.info("MAA CLI 及 MaaCore 安装成功")
            return InstallStatus(
                success=True,
                message="MAA CLI 及 MaaCore 安装成功",
                maa_cli_installed=True,
                maa_core_installed=True,
                maa_cli_version=self.cli.get_version(),
            )
        else:
            logger.warning(f"MaaCore 安装失败：{core_result.stderr}")
            return InstallStatus(
                success=False,
                message=f"MaaCore 安装失败：{core_result.stderr}",
                maa_cli_installed=True,
            )

    def _install_windows(self) -> bool:
        """Windows 平台安装"""
        logger.info("Windows 平台：使用安装脚本安装")

        # 提示安装 VC++ runtime
        logger.info("提示：请确保已安装 VC++ 运行库")
        logger.info("运行：winget install \"Microsoft.VCRedist.2015+.x64\"")

        try:
            # 使用 PowerShell 安装脚本
            script = (
                'Invoke-WebRequest -Uri "https://raw.githubusercontent.com/'
                'MaaAssistantArknights/maa-cli/main/install.ps1" '
                '-OutFile "maa_install.ps1"; .\\maa_install.ps1'
            )
            subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", script],
                check=True,
                capture_output=True,
                text=True,
                timeout=300,
            )
            logger.info("MAA CLI 安装脚本执行完成")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"安装脚本执行失败：{e.stderr}")
            return False
        except subprocess.TimeoutExpired:
            logger.error("安装脚本执行超时")
            return False
        except Exception as e:
            logger.error(f"安装失败：{e}")
            return False

    def _install_macos(self) -> bool:
        """macOS 平台安装"""
        logger.info("macOS 平台：尝试使用 Homebrew 安装")

        # 检查 Homebrew 是否可用
        try:
            subprocess.run(
                ["brew", "--version"],
                check=True,
                capture_output=True,
                text=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("Homebrew 未安装，尝试使用安装脚本")
            return self._install_script()

        # 尝试安装
        try:
            result = subprocess.run(
                ["brew", "install", "MaaAssistantArknights/tap/maa-cli"],
                check=True,
                capture_output=True,
                text=True,
                timeout=300,
            )
            logger.info("MAA CLI 安装成功")
            return True
        except subprocess.CalledProcessError:
            logger.error("Homebrew 安装失败，尝试使用安装脚本")
            return self._install_script()

    def _install_linux(self) -> bool:
        """Linux 平台安装"""
        logger.info("Linux 平台：尝试使用包管理器安装")

        # 检查包管理器
        if self._try_install_arch():
            return True
        if self._try_install_nix():
            return True

        logger.info("包管理器安装失败，尝试使用安装脚本")
        return self._install_script()

    def _try_install_arch(self) -> bool:
        """尝试通过 AUR 安装（Arch Linux）"""
        try:
            # 检查 paru 或 yay
            for pkg_manager in ["paru", "yay"]:
                try:
                    subprocess.run(
                        [pkg_manager, "-S", "maa-cli", "--noconfirm"],
                        check=True,
                        capture_output=True,
                        text=True,
                        timeout=300,
                    )
                    logger.info(f"通过 {pkg_manager} 安装成功")
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
        except Exception as e:
            logger.debug(f"AUR 安装失败：{e}")
        return False

    def _try_install_nix(self) -> bool:
        """尝试通过 Nix 安装"""
        try:
            subprocess.run(
                ["nix", "run", "nixpkgs#maa-cli"],
                check=True,
                capture_output=True,
                text=True,
            )
            logger.info("通过 Nix 安装成功")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _install_script(self) -> bool:
        """使用安装脚本安装（通用）"""
        try:
            result = subprocess.run(
                ["curl", "-fsSL",
                 "https://raw.githubusercontent.com/"
                 "MaaAssistantArknights/maa-cli/main/install.sh"],
                check=True,
                capture_output=True,
                text=True,
            )
            # 管道输出到 bash
            subprocess.run(
                ["bash"],
                input=result.stdout,
                check=True,
                capture_output=True,
                text=True,
                timeout=300,
            )
            logger.info("MAA CLI 安装脚本执行完成")
            return True
        except Exception as e:
            logger.error(f"安装脚本执行失败：{e}")
            return False

    def update(self) -> CLIResult:
        """更新 MAA CLI"""
        logger.info("更新 MAA CLI...")
        return self.cli.run(["self", "update"])

    def update_core(self) -> CLIResult:
        """更新 MaaCore 及资源"""
        logger.info("更新 MaaCore 及资源...")
        return self.cli.run(["update"])


def install_maa(
    maa_cmd: str = "maa",
    force: bool = False,
) -> InstallStatus:
    """便捷函数：安装 MAA CLI

    Args:
        maa_cmd: MAA CLI 命令名
        force: 强制重新安装

    Returns:
        InstallStatus: 安装状态
    """
    installer = MAAInstaller(maa_cmd=maa_cmd)
    return installer.install(force=force)


def check_maa_available(maa_cmd: str = "maa") -> bool:
    """便捷函数：检查 MAA CLI 是否可用

    Args:
        maa_cmd: MAA CLI 命令名

    Returns:
        是否可用
    """
    installer = MAAInstaller(maa_cmd=maa_cmd)
    return installer.check_installed()
