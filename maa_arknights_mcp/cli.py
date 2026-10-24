"""MAA CLI 封装层

提供 MAA CLI 命令的执行、结果解析、错误处理等功能。
"""

import json
import subprocess
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class CLIResult:
    """MAA CLI 命令执行结果"""

    success: bool
    returncode: int
    stdout: str
    stderr: str
    command: str
    # 解析后的结构化数据（如果可用）
    data: dict = field(default_factory=dict)


class MAACLI:
    """MAA CLI 封装类

    封装 MAA CLI 命令的执行，提供统一的结果解析和错误处理。

    Usage:
        cli = MAACLI()
        result = cli.run(["fight", "BB-7", "-c", "3"])
        if result.success:
            print(result.stdout)
    """

    def __init__(
        self,
        cmd: str = "maa",
        timeout: int = 600,
        log_dir: Optional[Path] = None,
    ):
        """
        Args:
            cmd: MAA CLI 命令名（maa 或 maa-cli）
            timeout: 默认超时时间（秒）
            log_dir: 日志目录
        """
        self.cmd = cmd
        self.timeout = timeout
        self.log_dir = log_dir

    def run(
        self,
        args: list[str],
        timeout: Optional[int] = None,
        log_file: Optional[Path] = None,
    ) -> CLIResult:
        """执行 MAA CLI 命令

        Args:
            args: 命令参数列表
            timeout: 超时时间（秒），None 使用默认值
            log_file: 日志文件路径

        Returns:
            CLIResult: 执行结果
        """
        timeout = timeout or self.timeout
        full_cmd = [self.cmd] + args

        logger.info(f"Executing: {' '.join(full_cmd)}")

        try:
            # 准备环境变量
            env = self._prepare_env(log_file)

            # 执行命令
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
                env=env,
            )

            # 构建结果
            cli_result = CLIResult(
                success=result.returncode == 0,
                returncode=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                command=" ".join(full_cmd),
            )

            # 尝试解析输出
            cli_result.data = self._parse_output(result.stdout)

            # 记录日志
            self._log_result(cli_result, log_file)

            logger.info(
                f"Command completed: success={cli_result.success}, "
                f"returncode={cli_result.returncode}"
            )

            return cli_result

        except subprocess.TimeoutExpired:
            return CLIResult(
                success=False,
                returncode=-1,
                stdout="",
                stderr=f"Command timed out after {timeout}s",
                command=" ".join(full_cmd),
            )

        except FileNotFoundError:
            return CLIResult(
                success=False,
                returncode=-1,
                stdout="",
                stderr=(
                    f"MAA CLI not found: '{self.cmd}'. "
                    "Please install maa-cli first.\n"
                    "Windows: winget install maa\n"
                    "macOS: brew install MaaAssistantArknights/tap/maa-cli"
                ),
                command=" ".join(full_cmd),
            )

        except Exception as e:
            logger.error(f"Command failed: {e}")
            return CLIResult(
                success=False,
                returncode=-1,
                stdout="",
                stderr=str(e),
                command=" ".join(full_cmd),
            )

    def _prepare_env(self, log_file: Optional[Path] = None) -> dict:
        """准备环境变量"""
        env = dict(__import__("os").environ)

        # 设置日志级别
        env.setdefault("MAA_LOG", "Warn")

        # 设置日志文件
        if log_file:
            env["MAA_LOG_FILE"] = str(log_file)

        return env

    def _parse_output(self, stdout: str) -> dict:
        """解析 MAA CLI 输出

        尝试从输出中提取 JSON 数据（如果有的话）
        """
        if not stdout.strip():
            return {}

        # 尝试直接解析 JSON
        try:
            return json.loads(stdout)
        except json.JSONDecodeError:
            pass

        # 尝试提取 JSON 块
        import re

        json_match = re.search(r"\{.*\}", stdout, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        return {}

    def _log_result(
        self, result: CLIResult, log_file: Optional[Path] = None
    ) -> None:
        """记录命令执行结果"""
        if not result.success:
            logger.error(f"Command failed: {result.command}")
            logger.error(f"stderr: {result.stderr}")

        if log_file:
            try:
                log_file.parent.mkdir(parents=True, exist_ok=True)
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"=== {result.command} ===\n")
                    f.write(f"Success: {result.success}\n")
                    f.write(f"ReturnCode: {result.returncode}\n")
                    f.write(f"Stdout: {result.stdout}\n")
                    f.write(f"Stderr: {result.stderr}\n")
                    f.write("\n")
            except Exception as e:
                logger.warning(f"Failed to write log file: {e}")

    # ==================== 便捷方法 ====================

    def get_maa_cmd(self) -> str:
        """获取当前使用的 MAA CLI 命令"""
        return self.cmd

    def check_available(self) -> bool:
        """检查 MAA CLI 是否可用"""
        result = self.run(["version"])
        return result.success

    def get_version(self) -> Optional[str]:
        """获取 MAA CLI 和 MaaCore 版本"""
        result = self.run(["version"])
        if result.success:
            return result.stdout.strip()
        return None

    def get_dir(self, dir_name: str) -> Optional[str]:
        """获取 MAA 目录路径

        Args:
            dir_name: 目录类型（data, library, resource, config, cache, log）

        Returns:
            目录路径，如果失败返回 None
        """
        result = self.run(["dir", dir_name])
        if result.success:
            return result.stdout.strip()
        return None
