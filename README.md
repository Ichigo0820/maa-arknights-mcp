# MAA Arknights MCP Server

基于 [MAA (MaaAssistantArknights)](https://github.com/MaaAssistantArknights/MaaAssistantArknights) CLI 的 MCP Server，让 AI 助手能够自动化明日方舟游戏。

## 🎯 项目定位

本项目将 MAA CLI 的自动化能力通过 MCP（Model Context Protocol）协议暴露给 AI 助手，实现：

- **自然语言驱动**：用自然语言告诉 AI 你想做什么，AI 自动调用 MAA CLI 执行
- **预定义任务**：一键刷关卡、自动肉鸽、抄作业等
- **自定义任务**：通过配置文件编排复杂流程
- **跨平台**：支持 Windows/macOS/Linux

## 📦 项目架构

```
maa-arknights-mcp/
├── pyproject.toml              # 项目配置（依赖、入口点）
├── README.md                   # 项目文档
├── maa_arknights_mcp/          # 主包
│   ├── __init__.py             # 包初始化、版本信息
│   ├── __main__.py             # CLI 入口点
│   ├── server.py               # MCP Server 核心（FastMCP 实例、工具注册）
│   ├── cli.py                  # MAA CLI 封装（命令执行、结果解析）
│   ├── tools/                  # 工具模块
│   │   ├── __init__.py         # 工具导出
│   │   ├── game.py             # 游戏控制（启动、关闭、状态）
│   │   ├── combat.py           # 战斗任务（刷关卡、抄作业）
│   │   ├── roguelike.py        # 肉鸽（集成战略、生息演算）
│   │   ├── infrastructure.py   # 基建（换班、制造）
│   │   ├── recruit.py          # 公招
│   │   └── config.py           # 配置管理（初始化、更新、目录）
│   └── utils.py                # 通用工具（日志、路径、异常处理）
├── tests/                      # 测试
│   ├── __init__.py
│   ├── test_cli.py             # CLI 封装测试
│   └── test_tools.py           # 工具模块测试
└── examples/                   # 示例
    ├── daily_task.yaml         # 日常任务示例
    └── roguelike_config.json   # 肉鸽配置示例
```

## 🏗️ 核心设计

### 1. MAA CLI 封装层 (`cli.py`)

```python
class MAACLI:
    """MAA CLI 封装类"""
    
    def __init__(self, cmd: str = "maa"):
        self.cmd = cmd
    
    def run(self, args: list[str], timeout: int = 600) -> CLIResult:
        """执行 MAA CLI 命令"""
        ...
    
    def parse_output(self, stdout: str) -> dict:
        """解析 MAA CLI 输出"""
        ...
```

### 2. MCP 工具层 (`tools/`)

每个工具模块对应一组 MAA CLI 命令：

| 模块 | 对应 CLI 命令 | 功能 |
|------|--------------|------|
| `game.py` | `startup`, `closedown` | 游戏启动/关闭 |
| `combat.py` | `fight`, `copilot`, `sscopilot`, `paradoxcopilot` | 战斗/抄作业 |
| `roguelike.py` | `roguelike`, `reclamation` | 肉鸽/生息演算 |
| `config.py` | `install`, `update`, `init`, `dir`, `version` | 配置管理 |

### 3. MCP Server 层 (`server.py`)

```python
mcp = FastMCP("MAA Arknights")

@mcp.tool()
def maa_fight(stage: str, count: int = 1, ...) -> str:
    """刷关卡"""
    result = cli.fight(stage, count)
    return format_result(result)
```

## 🚀 快速开始

### 安装

```bash
# 方式一：uv（推荐）
uv pip install maa-arknights-mcp

# 方式二：pip
pip install maa-arknights-mcp

# 方式三：从源码
git clone <repo-url>
cd maa-arknights-mcp
uv pip install -e .
```

### 前置条件

1. **安装 MAA CLI**
   ```bash
   # Windows（winget）
   winget install maa
   
   # 或使用安装脚本
   powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/MaaAssistantArknights/maa-cli/main/install.ps1' -OutFile install.ps1; .\install.ps1"
   
   # 安装 MaaCore 及资源
   maa install
   ```

2. **配置 MCP 客户端**
   
   在 Cursor/Claude/Cherry Studio 等中添加：
   ```json
   {
     "mcpServers": {
       "MAA Arknights": {
         "command": "maa-arknights-mcp"
       }
     }
   }
   ```

### 使用示例

**自然语言交互：**

```
用户：帮我刷 BB-7，用 3 个理智药
AI：好的，正在执行...
    → 调用 maa_fight(stage="BB-7", count=3, use_drugs=True)
    → 返回任务结果

用户：帮我打一次肉鸽
AI：好的，正在启动集成战略...
    → 调用 maa_startup(client="Official")
    → 调用 maa_roguelike(theme="Phantom")
    → 返回任务结果
```

## 📋 可用工具

### 游戏控制

| 工具 | 说明 |
|------|------|
| `maa_startup` | 启动游戏 |
| `maa_closedown` | 关闭游戏 |
| `maa_activity` | 获取活动信息 |

### 战斗任务

| 工具 | 说明 |
|------|------|
| `maa_fight` | 刷关卡 |
| `maa_copilot` | 抄作业 |
| `maa_sscopilot` | 保全派驻 |
| `maa_paradoxcopilot` | 悖论模拟 |

### 肉鸽/演算

| 工具 | 说明 |
|------|------|
| `maa_roguelike` | 集成战略 |
| `maa_reclamation` | 生息演算 |

### 配置管理

| 工具 | 说明 |
|------|------|
| `maa_install` | 安装 MaaCore |
| `maa_update` | 更新资源 |
| `maa_init` | 初始化配置 |
| `maa_version` | 查看版本 |
| `maa_dir` | 获取目录路径 |

## 🔧 开发

### 本地开发

```bash
# 克隆仓库
git clone <repo-url>
cd maa-arknights-mcp

# 创建虚拟环境
uv venv

# 安装依赖
uv pip install -e .

# 运行（stdio 模式）
python -m maa_arknights_mcp

# 运行（HTTP 模式）
python -m maa_arknights_mcp --transport http --port 8000
```

### 测试

```bash
uv pip install pytest
pytest tests/
```

## 📝 自定义任务

MAA CLI 支持自定义任务配置文件，可以编排复杂流程：

```yaml
# examples/daily_task.yaml
tasks:
  - name: startup
    command: startup
    params:
      client: Official
  
  - name: fight
    command: fight
    params:
      stage: BB-7
      count: 3
      use_drugs: true
  
  - name: closedown
    command: closedown
```

运行：
```bash
maa run daily_task
```

## 🤝 与 MaaMCP 的区别

| 特性 | MaaMCP | MAA Arknights MCP |
|------|--------|-------------------|
| 底层 | MaaFramework (Python) | MAA CLI (Rust) |
| 精细操作 | ✅ OCR、点击、滑动 | ❌ 仅预定义任务 |
| 后台控制 | ✅ Windows 后台 | ❌ 需要前台 |
| 安装依赖 | Python + maafw | 仅需 maa-cli |
| 适用场景 | 复杂自动化 | 简单任务调度 |

## 📄 许可证

MIT

## 🙏 致谢

- [MaaAssistantArknights](https://github.com/MaaAssistantArknights/MaaAssistantArknights) - MAA 项目
- [MaaFramework](https://github.com/MaaXYZ/MaaFramework) - MAA 框架
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP 服务器框架
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP 协议
