# main.py
# 导入所有必要的模块
import astrbot.api.message_components as Comp
from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, MessageEventResult, filter
from astrbot.api.star import Context, Star, register


@register(
    "astrbot_plugin_llmquotetool",  # 插件名称
    "xSapientia",                   # 插件作者
    "提供一个可供LLM调用的QQ引用回复消息工具",  # 插件描述
    "0.0.1",                       # 插件版本
    "https://github.com/xSapientia/astrbot_plugin_llmquotetool"  # 插件仓库地址
)
class LlmQuoteToolPlugin(Star):
    """
    一个实现了LLM函数调用(Function Calling)的QQ引用回复消息工具插件。
    允许LLM根据对话上下文，智能地决定何时以及如何引用回复一条指定的消息。
    """

    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        
        # 将传入的config对象保存为实例属性，以便在插件的其他方法中使用
        self.config = config
        
        # 使用 self.config.get() 方法安全地读取配置项，如果用户未配置则使用默认值
        self.is_tool_enabled = self.config.get("enable_quote_tool", True)
        self.reply_prefix = self.config.get("reply_prefix_message", "")
        self.auto_at_sender = self.config.get("auto_at_sender", False)
        
        # 在日志中打印加载的配置，方便调试
        logger.info("LLM QQ引用回复工具插件已加载。")
        logger.info(f" - 工具启用状态: {self.is_tool_enabled}")
        logger.info(f" - 回复消息前缀: '{self.reply_prefix}'")
        logger.info(f" - 自动@原消息发送者: {self.auto_at_sender}")
        
        if not self.is_tool_enabled:
            logger.warning("LLM QQ引用回复工具当前已被禁用，将不会注册函数工具。")

    @filter.llm_tool(name="quote_user")
    async def quote_user_tool(self, event: AstrMessageEvent, message_id: str, reply_message: str, at_original_sender: bool = None) -> MessageEventResult:
        """
        当需要引用回复某条特定消息时，调用此工具来回复该消息并发送内容。
        
        Args:
            message_id (string): 需要引用回复的消息ID。
            reply_message (string): 回复的文本内容。
            at_original_sender (boolean): 可选，是否在回复中@原消息发送者，不填则使用配置默认值。
        """
        # 每次调用工具时，都检查配置中是否启用了该工具
        if not self.is_tool_enabled:
            logger.warning(f"LLM尝试调用已禁用的 quote_user 工具。调用者: {event.get_sender_name()}")
            return event.plain_result("抱歉，QQ引用回复工具当前不可用。")

        # 验证message_id是否存在
        if not message_id or not message_id.strip():
            logger.error("quote_user工具调用失败：未提供有效的message_id。")
            return event.plain_result("工具调用失败：消息ID不能为空。")

        # 验证reply_message是否存在
        if not reply_message or not reply_message.strip():
            logger.error("quote_user工具调用失败：未提供有效的回复内容。")
            return event.plain_result("工具调用失败：回复内容不能为空。")

        # 确定是否需要@原消息发送者
        should_at_sender = at_original_sender if at_original_sender is not None else self.auto_at_sender

        logger.info(f"LLM 正在调用 quote_user 工具：引用消息ID {message_id}，回复内容：'{reply_message}'，是否@发送者：{should_at_sender}")

        # 构建消息链 (MessageChain)
        message_chain = []

        # 1. 添加引用回复组件
        message_chain.append(Comp.Reply(id=message_id))

        # 2. 如果需要@原消息发送者，添加@组件
        if should_at_sender:
            # 尝试从当前事件中获取发送者ID作为@目标
            # 注意：这里假设我们要@的是当前对话中的某个用户
            # 在实际使用中，可能需要根据message_id查找原消息的发送者
            sender_id = event.get_sender_id()
            if sender_id and sender_id.isdigit():
                message_chain.append(Comp.At(qq=int(sender_id)))
                message_chain.append(Comp.Plain(text=" "))

        # 3. 添加前缀文本（如果配置了）和主要回复消息
        full_message = f"{self.reply_prefix}{reply_message}" if self.reply_prefix else reply_message
        message_chain.append(Comp.Plain(text=full_message))

        # 4. 使用 chain_result 返回最终要发送给用户的完整消息链
        return event.chain_result(message_chain)

    @filter.llm_tool(name="get_recent_messages")
    async def get_recent_messages_tool(self, event: AstrMessageEvent, count: int = 5) -> MessageEventResult:
        """
        获取当前对话中最近的几条消息信息，用于LLM了解上下文以便进行引用回复。
        
        Args:
            count (number): 要获取的最近消息数量，默认为5条，最多不超过20条。
        """
        # 每次调用工具时，都检查配置中是否启用了该工具
        if not self.is_tool_enabled:
            logger.warning(f"LLM尝试调用已禁用的 get_recent_messages 工具。调用者: {event.get_sender_name()}")
            return event.plain_result("抱歉，获取消息工具当前不可用。")

        # 限制获取的消息数量
        count = max(1, min(count, 20))
        
        logger.info(f"LLM 正在调用 get_recent_messages 工具：获取最近 {count} 条消息")

        # 由于AstrBot API限制，我们无法直接获取历史消息
        # 这里返回一个说明性的消息，实际使用中可能需要其他方式实现
        info_message = f"由于API限制，无法直接获取历史消息。当前消息ID：{event.message_obj.message_id}，发送者：{event.get_sender_name()}，内容：{event.message_str[:50]}..."
        
        return event.plain_result(info_message)

    async def terminate(self):
        """
        插件停用时调用的函数，用于释放资源。
        """
        logger.info("LLM QQ引用回复工具插件已卸载。")
        pass
