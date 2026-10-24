# MAA Arknights MCP Server Skill

## 概述

这是一个用于自动化明日方舟游戏的 MCP Server，通过 MAA CLI 实现游戏操作的自动化。AI 助手可以通过自然语言理解玩家意图，并调用相应的工具执行游戏操作。

## 核心功能

> **在 OpenCode 中调用**：本 Server 以 `maa_arknights` 为名注册，Code Mode 中的路径为
> `tools.maa_arknights.<工具名>`（例如 `tools.maa_arknights.maa_check()`）。
> 不要使用 `tools.maa-arknights_maa_check`，连字符会导致工具名无法解析。

### 0. 安装与更新（自动集成 MAA CLI）

- **检查状态**：`maa_check` - 检查 MAA CLI 是否已安装及版本信息
- **安装 MAA**：`maa_install_cli` - 自动安装 MAA CLI 及 MaaCore（支持跨平台）
- **更新 CLI**：`maa_update_cli` - 更新 MAA CLI
- **更新 Core**：`maa_update_core` - 更新 MaaCore 及资源

> **无需手动安装 MAA CLI！** 项目已集成安装器，首次使用时 AI 会自动检测并安装。

### 1. 游戏控制

- **启动游戏**：`maa_startup` - 启动明日方舟并进入主界面
- **关闭游戏**：`maa_closedown` - 关闭游戏客户端
- **活动查询**：`maa_activity` - 获取当前活动信息

### 2. 战斗任务

- **刷关卡**：`maa_fight` - 刷指定关卡，支持理智药、抄作业
- **抄作业**：`maa_copilot` - 自动抄作业
- **保全派驻**：`maa_sscopilot` - 自动保全派驻
- **悖论模拟**：`maa_paradoxcopilot` - 自动悖论模拟

### 3. 肉鸽/演算

- **集成战略**：`maa_roguelike` - 自动肉鸽（支持多个主题）
- **生息演算**：`maa_reclamation` - 自动生息演算

### 4. 基建管理

> **注意**：maa-cli 0.7.x 没有 `infrast` / `recruit` 子命令，以下工具直接调用会失败。
> 请使用 `maa_run` 工具 + 自定义任务文件来执行基建/公招操作。

- **基建管理**：`maa_infrast_manage` - 自动换班、制造、采购（需通过 `maa_run` 执行）
- **基建制造**：`maa_infrast_production` - 开始制造任务（需通过 `maa_run` 执行）
- **基建贸易**：`maa_infrast_trade` - 出售物资（需通过 `maa_run` 执行）
- **基建采购**：`maa_infrast_purchase` - 购买物资（需通过 `maa_run` 执行）
- **收取理智**：`maa_infrast_energy` - 收取基建理智（需通过 `maa_run` 执行）
- **基建换班**：`maa_infrast_switch` - 手动换班（需通过 `maa_run` 执行）

### 5. 公招系统

> **注意**：maa-cli 0.7.x 没有 `recruit` 子命令，以下工具直接调用会失败。
> 请使用 `maa_run` 工具 + 自定义任务文件来执行公招操作。

- **获取结果**：`maa_recruit_get` - 查看当前公招结果（需通过 `maa_run` 执行）
- **开始公招**：`maa_recruit_start` - 开始新的公招（需通过 `maa_run` 执行）
- **收取公招**：`maa_recruit_collect` - 收取指定槽位（需通过 `maa_run` 执行）
- **一键收取**：`maa_recruit_all` - 收取所有并重新开始（需通过 `maa_run` 执行）

### 6. 配置管理

- **安装**：`maa_install` - 安装 MaaCore 及资源
- **更新**：`maa_update` - 更新资源
- **版本**：`maa_version` - 查看版本信息
- **目录**：`maa_dir` - 获取 MAA 目录路径
- **自定义任务**：`maa_run` - 运行自定义任务（基建/公招等）

## 使用指南

### 首次使用

项目已集成 MAA CLI 安装器，首次使用时 AI 会自动检测并安装：

```
用户：我想玩明日方舟
AI：好的，检测到您尚未安装 MAA CLI，正在为您安装...
    → 调用 maa_install_cli()
    → 返回安装结果
    → 继续执行游戏操作
```

### 日常任务流程

**典型日常任务：**
1. 启动游戏 → 刷关卡 → 基建管理 → 公招收取 → 关闭游戏

**示例对话：**
```
用户：帮我刷 1-7，刷 5 次
AI：好的，正在执行...
    → 调用 maa_startup(client="Official", addr="127.0.0.1:58526")
    → 调用 maa_fight(stage="1-7", count=5, addr="127.0.0.1:58526")
    → 返回任务结果

用户：帮我打一次肉鸽
AI：好的，正在启动集成战略...
    → 调用 maa_startup(client="Official", addr="127.0.0.1:58526")
    → 调用 maa_roguelike(theme="Phantom")
    → 返回任务结果
```

### 参数说明

#### maa_startup（启动游戏）

- `client`: 客户端类型，如 "Official"（官服）、"Bilibili"（B 服）等
- `timeout`: 超时时间（秒），默认 120
- `addr`: ADB 设备地址，如 "127.0.0.1:58526"（WSA）、"127.0.0.1:5555"（模拟器）；留空使用 MAA 配置文件中的地址

#### maa_fight（刷关卡）

- `stage`: 关卡名称，如 "1-7"、"BB-7"、"E8-2"，留空使用上次关卡
- `count`: 刷取次数，0 = 一直刷直到理智耗尽（默认 1）
- `medicine`: 使用理智药（药剂）的数量（默认 0）
- `series`: 连续作战次数（-1~6），留空使用 MAA 默认值
- `addr`: ADB 设备地址，如 "127.0.0.1:58526"；留空使用 MAA 配置文件中的地址
- `client_type`: 关卡崩溃后用于重启的客户端类型
- `timeout`: 超时时间（秒），默认 600

#### maa_roguelike（肉鸽）

- `theme`: 主题，可选 "Phantom"（幻影）、"Mizuki"（水月）、"Sami"（萨米）、"Sarkaz"（萨卡兹）、"JieGarden"（集成战略 3）
- `starts_count`: 开局选择数量（0=默认）

#### maa_recruit_start（公招）

- `time`: 公招时间（秒），300=5 分钟, 1800=30 分钟, 7200=2 小时, 28800=8 小时
- `tags`: 标签组合，如 "6 星 近卫 医疗"，留空随机
- `client`: 客户端类型（默认 "Official"）

#### maa_run（自定义任务）

- `task`: 任务名，即 `config/tasks/` 目录下不含扩展名的文件名
- `addr`: ADB 设备地址，留空使用配置文件中的地址
- `batch`: 批处理模式，跳过任务中的交互式提问
- `timeout`: 超时时间（秒），默认 600

### 客户端类型

- `Official`: 官服
- `Bilibili`: B 服
- `Txwy`: 腾讯渠道服
- `YoStarEN`: 国际服（英文）
- `YoStarJP`: 国际服（日文）
- `YoStarKR`: 国际服（韩文）

## 详细操作步骤

### 步骤 1：检查环境

```
→ 调用 maa_check()
→ 确认 MAA CLI 和 MaaCore 已安装
→ 确认 adb 设备已连接（adb devices）
```

### 步骤 2：配置 ADB 连接

WSA（Windows Subsystem for Android）用户需要创建配置文件：

```toml
# config/profiles/default.toml
[connection]
adb_path = "adb"
address = "127.0.0.1:58526"
config = "General"

[instance_options]
touch_mode = "adb"
```

> **关键**：WSA 没有 `/dev/input` 触摸设备，必须设置 `touch_mode = "adb"`，否则 MAA 会报 `TouchModeNotAvailable` 错误。

### 步骤 3：启动游戏

```
→ 调用 maa_startup(client="Official", addr="127.0.0.1:58526", timeout=180)
→ 等待游戏进入主界面
```

> **注意**：如果游戏已在运行但 MAA 无法识别，先 `maa_closedown` 关闭再重新启动。

### 步骤 4：刷关卡

```
→ 调用 maa_fight(stage="1-7", count=5, addr="127.0.0.1:58526", timeout=1200)
→ 返回结果包含每关掉落明细
```

> **性能提示**：WSA + ADB 输入模式下，每关约 1 分 45 秒。降低 WSA 显示分辨率（如 1920×1080）可提升截图和识别速度。

### 步骤 5：基建/公招（通过自定义任务）

maa-cli 0.7.x 没有 `infrast` / `recruit` 子命令，需要创建自定义任务文件：

```toml
# config/tasks/daily.toml
[[tasks]]
type = "StartUp"
params = { client_type = "Official" }

[[tasks]]
type = "Infrast"

[[tasks]]
type = "Recruit"
```

```
→ 调用 maa_run(task="daily", addr="127.0.0.1:58526", batch=true, timeout=600)
```

### 步骤 6：关闭游戏

```
→ 调用 maa_closedown(client="Official", addr="127.0.0.1:58526")
```

## 注意事项

1. **自动安装**：项目已集成 MAA CLI 安装器，首次使用时会自动检测并安装
   - 如自动安装失败，可使用 `maa_install_cli(force=True)` 强制安装
   - 或手动安装：Windows: `winget install maa`

2. **VC++ 运行库**：Windows 用户需要安装 VC++ 运行库
   - 运行：`winget install "Microsoft.VcRedist.2015+.x64"`

3. **超时设置**：游戏操作可能需要较长时间，默认超时 600 秒
   - 刷关卡建议 `timeout=1200`（5 次 × 约 100 秒/次）
   - 肉鸽建议 `timeout=1800`（可能持续 20-30 分钟）

4. **客户端匹配**：确保使用的客户端类型与实际安装的客户端一致

5. **作业 URI**：抄作业需要有效的 maa:// URI 或本地文件路径

6. **理智药使用**：使用理智药时建议设置 `medicine` 参数避免过度使用

7. **WSA 分辨率**：WSA 默认分辨率 2560×1440 会导致截图和识别较慢，建议调整为 1920×1080

8. **热更新**：启动时可能报 `Network error`（热更新失败），重试即可通过

## 错误处理

所有工具返回统一的 JSON 格式结果：

```json
{
  "success": true/false,
  "returncode": 0,
  "message": "执行结果",
  "command": "maa xxx"
}
```

- `success`: 操作是否成功
- `returncode`: 返回码，0 表示成功
- `message`: 详细消息
- `command`: 执行的命令

### 常见错误

| 错误 | 原因 | 解决方法 |
|------|------|----------|
| `TouchModeNotAvailable` | WSA 没有触摸设备 | 设置 `touch_mode = "adb"` |
| `connect failed` | ADB 未连接 | 检查 `adb devices`，确认 WSA 开发人员模式已开启 |
| `screencap failed` | 游戏画面被黑边包围 | 调整 WSA 显示大小使游戏铺满屏幕 |
| `Network error` | 热更新失败 | 重试，或检查网络连接 |
| `unrecognized subcommand` | 使用了不存在的子命令 | 基建/公招改用 `maa_run` + 任务文件 |

## 自定义任务

MAA CLI 支持自定义任务配置文件（TOML/JSON 格式），可以编排复杂流程：

```toml
# config/tasks/daily.toml
[[tasks]]
type = "StartUp"
params = { client_type = "Official" }

[[tasks]]
type = "Fight"
params = { stage = "1-7", times = 5 }

[[tasks]]
type = "Infrast"

[[tasks]]
type = "Recruit"

[[tasks]]
type = "Closedown"
```

运行：`maa_run(task="daily", addr="127.0.0.1:58526", batch=true)`

## 与 MaaMCP 的区别

| 特性 | MaaMCP | MAA Arknights MCP |
|------|--------|-------------------|
| 底层 | MaaFramework (Python) | MAA CLI (Rust) |
| 精细操作 | ✅ OCR、点击、滑动 | ❌ 仅预定义任务 |
| 后台控制 | ✅ Windows 后台 | ❌ 需要前台 |
| 安装依赖 | Python + maafw | 仅需 maa-cli |
| 适用场景 | 复杂自动化 | 简单任务调度 |
