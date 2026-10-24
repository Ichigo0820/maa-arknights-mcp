# MAA Arknights MCP Server Skill

## 概述

这是一个用于自动化明日方舟游戏的 MCP Server，通过 MAA CLI 实现游戏操作的自动化。AI 助手可以通过自然语言理解玩家意图，并调用相应的工具执行游戏操作。

## 核心功能

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
- **基建管理**：`maa_infrast_manage` - 自动换班、制造、采购
- **基建制造**：`maa_infrast_production` - 开始制造任务
- **基建贸易**：`maa_infrast_trade` - 出售物资
- **基建采购**：`maa_infrast_purchase` - 购买物资
- **收取理智**：`maa_infrast_energy` - 收取基建理智
- **基建换班**：`maa_infrast_switch` - 手动换班

### 5. 公招系统
- **获取结果**：`maa_recruit_get` - 查看当前公招结果
- **开始公招**：`maa_recruit_start` - 开始新的公招
- **收取公招**：`maa_recruit_collect` - 收取指定槽位
- **一键收取**：`maa_recruit_all` - 收取所有并重新开始

### 6. 配置管理
- **安装**：`maa_install` - 安装 MaaCore 及资源
- **更新**：`maa_update` - 更新资源
- **版本**：`maa_version` - 查看版本信息
- **目录**：`maa_dir` - 获取 MAA 目录路径

## 使用指南

### 日常任务流程

**典型日常任务：**
1. 启动游戏 → 刷关卡 → 基建管理 → 公招收取 → 关闭游戏

**示例对话：**
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

### 参数说明

#### maa_fight（刷关卡）
- `stage`: 关卡名称，如 "1-7"、"BB-7"、"E8-2"
- `count`: 刷取次数（默认 1）
- `use_drugs`: 是否使用理智药（默认 false）
- `drug_limit`: 理智药使用上限（0=不限制）
- `copilot`: 是否使用抄作业（默认 false）
- `copilot_uri`: 作业 URI（maa://xxx 或本地文件路径）

#### maa_roguelike（肉鸽）
- `theme`: 主题，可选 "Phantom"（幻影）、"Mizuki"（水月）、"Sami"（萨米）、"Sarkaz"（萨卡兹）、"JieGarden"（集成战略 3）
- `starts_count`: 开局选择数量（0=默认）

#### maa_recruit_start（公招）
- `time`: 公招时间（秒），300=5 分钟, 1800=30 分钟, 7200=2 小时, 28800=8 小时
- `tags`: 标签组合，如 "6 星 近卫 医疗"，留空随机
- `client`: 客户端类型（默认 "Official"）

### 客户端类型

- `Official`: 官服
- `Bilibili`: B 服
- 其他自定义客户端

## 注意事项

1. **前置条件**：需要已安装 MAA CLI 和 MaaCore
   - Windows: `winget install maa`
   - macOS: `brew install MaaAssistantArknights/tap/maa-cli`

2. **超时设置**：游戏操作可能需要较长时间，默认超时 600 秒

3. **客户端匹配**：确保使用的客户端类型与实际安装的客户端一致

4. **作业 URI**：抄作业需要有效的 maa:// URI 或本地文件路径

5. **理智药使用**：使用理智药时建议设置 `drug_limit` 避免过度使用

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

## 自定义任务

MAA CLI 支持自定义任务配置文件（YAML 格式），可以编排复杂流程：

```yaml
# daily_task.yaml
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
    params:
      client: Official
```

运行：`maa run daily_task`

## 与 MaaMCP 的区别

| 特性 | MaaMCP | MAA Arknights MCP |
|------|--------|-------------------|
| 底层 | MaaFramework (Python) | MAA CLI (Rust) |
| 精细操作 | ✅ OCR、点击、滑动 | ❌ 仅预定义任务 |
| 后台控制 | ✅ Windows 后台 | ❌ 需要前台 |
| 安装依赖 | Python + maafw | 仅需 maa-cli |
| 适用场景 | 复杂自动化 | 简单任务调度 |
