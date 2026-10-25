"""MAA CLI 封装层

提供 MAA CLI 命令的执行、结果解析、错误处理等功能。
"""

import json
import re
import subprocess
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# 源石（至纯源石）是付费资源，本 MCP 一律禁止消耗。
# 该策略在 CLI 封装层兜底：任何工具（含未来新增的）传入 --stone 都会被剥离。
FORBIDDEN_CLI_ARGS = ("--stone",)

# 自定义任务文件里若写了 stone = N（N > 0）也视为违规
_STONE_IN_TASK = re.compile(r'\bstone\b\s*[=:]\s*["\']?(\d+)', re.IGNORECASE)


def strip_forbidden_args(args: list[str]) -> list[str]:
    """移除被策略禁止的 CLI 参数（如 --stone 及其取值）

    Args:
        args: 原始参数列表

    Returns:
        list[str]: 过滤后的参数列表
    """
    cleaned: list[str] = []
    dropped: list[str] = []
    skip_next = False

    for arg in args:
        if skip_next:
            skip_next = False
            dropped.append(arg)
            continue
        if arg in FORBIDDEN_CLI_ARGS:
            dropped.append(arg)
            skip_next = True
            continue
        if any(arg.startswith(f"{flag}=") for flag in FORBIDDEN_CLI_ARGS):
            dropped.append(arg)
            continue
        cleaned.append(arg)

    if dropped:
        logger.warning(
            "已屏蔽源石相关参数（本 MCP 禁止消耗源石）: %s", " ".join(dropped)
        )
    return cleaned


def check_task_file_for_stone(path: Path) -> Optional[str]:
    """检查自定义任务文件是否要求消耗源石

    Args:
        path: 任务文件路径

    Returns:
        Optional[str]: 违规说明；None 表示未使用源石（或文件不存在/无法读取）
    """
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None

    for match in _STONE_IN_TASK.finditer(text):
        try:
            if int(match.group(1)) > 0:
                return (
                    f"任务文件 {path.name} 中设置了 stone = {match.group(1)}，"
                    "本 MCP 禁止消耗源石，已拒绝执行"
                )
        except ValueError:
            continue
    return None


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
        args = strip_forbidden_args(list(args))
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

    def resolve_task_path(self, task: str) -> Optional[Path]:
        """解析自定义任务文件路径

        支持直接传文件路径，或传 config/tasks 目录下的任务名（不含扩展名）。

        Args:
            task: 任务名或文件路径

        Returns:
            Optional[Path]: 找到的任务文件；找不到返回 None
        """
        candidate = Path(task)
        if candidate.is_file():
            return candidate
        if candidate.suffix:
            return None

        result = self.run(["dir", "config"])
        config_dir = result.stdout.strip() if result.success else ""
        if config_dir and Path(config_dir).is_dir():
            for ext in (".toml", ".json"):
                file_path = Path(config_dir) / "tasks" / f"{task}{ext}"
                if file_path.is_file():
                    return file_path
        return None

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
