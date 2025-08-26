# astrbot_plugin_llmquotetool

<div align="center">

[![Version](https://img.shields.io/badge/version-0.0.1-blue.svg)](https://github.com/xSapientia/astrbot_plugin_llmquotetool)
[![AstrBot](https://img.shields.io/badge/AstrBot-%3E%3D3.4.0-green.svg)](https://github.com/Soulter/AstrBot)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

提供一个可供LLM调用的QQ引用回复消息工具，支持智能引用回复和消息上下文获取

</div>

## ✨ 功能特性

- 🔗 **智能引用回复**: LLM可以调用工具对特定消息进行引用回复
- 👤 **自动@发送者**: 支持在引用回复时自动@原消息发送者
- 🎯 **灵活配置**: 可自定义回复前缀、@行为等多种选项
- 📝 **上下文获取**: 提供获取最近消息的功能（基础版本）
- 🛡️ **安全控制**: 支持启用/禁用工具功能，确保使用安全
- 📊 **详细日志**: 记录工具调用情况，便于调试和监控

## 🎯 使用方法

### LLM函数工具

本插件为LLM提供以下可调用的函数工具：

#### 1. quote_user - QQ引用回复工具

```python
# LLM可以调用此工具进行引用回复
quote_user(
    message_id="消息ID",           # 必需：要引用的消息ID
    reply_message="回复内容",       # 必需：回复的文本内容
    at_user_id="用户ID"            # 可选：要@的用户ID，可以是原消息发送者或其他任何用户
)
```

**使用场景示例：**
- 用户询问"刚才那个问题的答案是什么？" - LLM可以引用之前的问题消息进行回复
- 需要针对特定消息进行澄清或补充说明，并@相关用户
- 在群聊中回复特定用户的消息时，可以@原发送者或其他相关用户
- LLM可以根据上下文智能判断是否需要@人以及@谁

#### 2. get_recent_messages - 获取最近消息

```python
# LLM可以调用此工具了解对话上下文
get_recent_messages(
    count=5                        # 可选：获取消息数量，默认5条，最多20条
)
```

**使用场景示例：**
- LLM需要了解当前对话的上下文信息
- 确定需要引用回复的具体消息
- 分析对话流程以提供更准确的回复

## ⚙️ 配置说明

插件支持在 AstrBot 管理面板中进行可视化配置：

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `enable_quote_tool` | bool | true | 启用QQ引用回复工具 |
| `reply_prefix_message` | string | "" | 回复消息前缀文本 |
| `auto_at_sender` | bool | false | 自动@原消息发送者 |
| `tool_usage_log` | bool | true | 记录工具使用日志 |

### 配置详解

**启用QQ引用回复工具 (enable_quote_tool)**
- 控制LLM是否可以调用引用回复功能
- 关闭后所有相关工具调用都会被拒绝

**回复消息前缀 (reply_prefix_message)**
- 在引用回复的消息前添加的前缀文本
- 例如设置为"回复："，则所有引用回复都会以"回复："开头
- 留空则不添加任何前缀

**自动@原消息发送者 (auto_at_sender)**
- 当LLM没有指定@对象时，是否自动@当前消息的发送者
- 启用后在LLM未指定at_user_id参数时会自动@发送消息的用户
- LLM可以通过at_user_id参数来覆盖此设置，实现更灵活的@控制

**记录工具使用日志 (tool_usage_log)**
- 是否在日志中详细记录LLM工具的调用情况
- 有助于调试和监控工具使用情况

## 🔧 技术实现

### 消息链构建

插件使用AstrBot的消息链(MessageChain)技术构建引用回复：

```python
# 消息链组成示例
message_chain = [
    Comp.Reply(id=message_id),          # 引用回复组件
    Comp.At(qq=user_id),                # @用户组件（可选）
    Comp.Plain(text=" "),               # 空格分隔
    Comp.Plain(text=reply_message)      # 回复文本内容
]
```

### 平台适配

目前支持的平台：
- ✅ QQ个人号(aiocqhttp) - 完全支持引用回复功能
- ❓ 其他平台 - 取决于平台对Reply组件的支持程度

## 📊 使用示例

### 对话场景1：回答历史问题

```
用户A: 今天天气怎么样？
机器人: 今天是晴天，温度25度。
用户B: 刚才那个天气问题的详细预报能给一下吗？
机器人: [调用quote_user工具，引用"今天天气怎么样？"这条消息]
      ↳ 详细天气预报：今天晴天，温度22-28度，湿度60%，微风...
```

### 对话场景2：澄清误解

```
用户: 你说的那个方法我试了不行
机器人: [调用get_recent_messages了解上下文，然后使用quote_user]
      ↳ 关于这个解决方案，我补充一下具体步骤...
```

## 🐛 故障排除

### 工具无法调用
1. 检查 `enable_quote_tool` 配置是否开启
2. 确认LLM提供商支持Function Calling功能
3. 查看AstrBot日志中的错误信息

### 引用回复不显示
1. 确认当前平台支持Reply消息组件
2. 检查message_id是否有效
3. 验证消息ID格式是否正确

### @功能不工作
1. 检查 `auto_at_sender` 配置
2. 确认用户ID格式是否为纯数字
3. 验证当前平台是否支持At消息组件

## 📝 更新日志

### v0.0.1 (2024-12-27)
- ✅ 实现基础的QQ引用回复功能
- ✅ 添加LLM函数工具 `quote_user`
- ✅ 添加消息上下文获取工具 `get_recent_messages`
- ✅ 支持自动@原消息发送者
- ✅ 实现可视化配置界面
- ✅ 添加详细的使用日志记录
- ✅ 完善错误处理和参数验证

### 计划中的功能
- 🔄 增强的历史消息获取功能
- 🔄 支持批量引用回复
- 🔄 消息内容智能分析
- 🔄 更多平台适配支持

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发指南

1. Fork 本仓库
2. 创建新的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

### 代码规范

- 使用中文注释
- 遵循AstrBot插件开发规范
- 添加适当的错误处理
- 保持代码简洁高效

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 👨‍💻 作者

- **xSapientia** - *Initial work* - [GitHub](https://github.com/xSapientia)

## 🙏 致谢

- 感谢 [AstrBot](https://github.com/Soulter/AstrBot) 项目提供的优秀框架
- 参考了 [astrbot_plugin_llmattool](https://github.com/oyxning/astrbot_plugin_llmAtTool) 的实现思路
- 感谢所有提出建议和反馈的用户

## 📞 支持

如果在使用过程中遇到问题：

1. 查看本文档的故障排除部分
2. 检查AstrBot日志文件
3. 在GitHub上提交Issue
4. 加入AstrBot交流群寻求帮助

---

<div align="center">

如果这个插件对你有帮助，请给个 ⭐ Star！

[报告问题](https://github.com/xSapientia/astrbot_plugin_llmquotetool/issues) · [功能建议](https://github.com/xSapientia/astrbot_plugin_llmquotetool/issues) · [查看更多插件](https://github.com/xSapientia)

</div>
