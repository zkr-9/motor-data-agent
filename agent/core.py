"""Agent 核心循环 — OpenAI Function Calling ReAct 模式"""

import json
from openai import OpenAI
import config
from agent.prompts import SYSTEM_PROMPT
from agent.tools import TOOLS, execute_tool


class MotorExperimentAgent:
    """电机实验数据智能处理与可视化 Agent"""

    def __init__(self):
        self.client = OpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL,
        )
        self.model = config.OPENAI_MODEL
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.max_tool_calls = config.MAX_TOOL_CALLS

    def chat(self, user_input: str) -> str:
        """处理用户输入，返回 Agent 回复"""
        self.messages.append({"role": "user", "content": user_input})

        for _ in range(self.max_tool_calls):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=TOOLS,
                temperature=config.TEMPERATURE,
            )
            choice = response.choices[0]

            # 如果 LLM 直接回复文本（无需工具调用）
            if choice.finish_reason == "stop" and choice.message.content:
                self.messages.append({"role": "assistant", "content": choice.message.content})
                return choice.message.content

            # 如果 LLM 要调用工具
            if choice.message.tool_calls:
                assistant_msg = {
                    "role": "assistant",
                    "content": choice.message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            }
                        }
                        for tc in choice.message.tool_calls
                    ]
                }
                self.messages.append(assistant_msg)

                for tc in choice.message.tool_calls:
                    tool_name = tc.function.name
                    try:
                        arguments = json.loads(tc.function.arguments)
                    except json.JSONDecodeError:
                        arguments = {}

                    print(f"  🔧 调用工具: {tool_name}({arguments})")
                    result = execute_tool(tool_name, arguments)

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result,
                    })

            # 如果 LLM 完成回复
            elif choice.finish_reason == "stop":
                content = choice.message.content or ""
                self.messages.append({"role": "assistant", "content": content})
                return content

        # 超过最大工具调用次数
        content = "已达到最大工具调用次数，请优化你的问题。"
        self.messages.append({"role": "assistant", "content": content})
        return content

    def reset(self):
        """重置对话历史"""
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
