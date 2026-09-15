from collections.abc import AsyncIterator
from dotenv import load_dotenv

from mini_agno.models.stream import ToolCallAccumulator

load_dotenv()

import json
from openai import AsyncOpenAI, OpenAI
from os import getenv
from mini_agno.models.base import Model
from mini_agno.models.message import Message, ModelResponse, ToolCall
from typing import Any, override


class OpenAIModel(Model):
    def __init__(
        self, id: str = "deepseek-chat", base_url: str = "https://api.deepseek.com"
    ):
        super().__init__(id)
        self.client = OpenAI(base_url=base_url, api_key=getenv("DEEPSEEK_API_KEY"))
        self.aclient = AsyncOpenAI(
            base_url=base_url, api_key=getenv("DEEPSEEK_API_KEY")
        )

    # 将消息转换为openai认可的dict
    def _message_to_openai_dict(self, msg: Message) -> dict:
        msg_dict: dict[str, Any] = {"role": msg.role}
        if msg.content is not None:
            msg_dict["content"] = msg.content
        if msg.tool_call_id is not None:
            msg_dict["tool_call_id"] = msg.tool_call_id
        if msg.tool_calls:
            tool_calls = []
            for tool_call in msg.tool_calls:
                tool = {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.name,
                        "arguments": json.dumps(tool_call.arguments),  # json字符串
                    },
                }
                tool_calls.append(tool)
            msg_dict["tool_calls"] = tool_calls
        return msg_dict

    def invoke(
        self, messages: list[Message], tools: list[dict] | None = None
    ) -> ModelResponse:
        """Invoke the model with a list of messages."""
        # 调用客户端
        resp = self.client.chat.completions.create(
            **self._build_openai_messages(messages, tools)
        )
        return self._parse_response(resp)

    def _build_openai_messages(
        self, messages: list[Message], tools: list[dict] | None = None
    ) -> list[dict]:
        """翻入：你的 Message 列表 → OpenAI 认的 dict 列表"""
        openai_msgs = [self._message_to_openai_dict(msg) for msg in messages]
        kwargs = {"model": self.id, "messages": openai_msgs}
        if tools is not None:
            kwargs["tools"] = tools
        return kwargs

    def _parse_response(self, resp) -> ModelResponse:
        choice = resp.choices[0].message
        tool_calls = []
        if choice.tool_calls is not None:
            for tc in choice.tool_calls:
                tool_call = ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=json.loads(tc.function.arguments),
                )
                tool_calls.append(tool_call)
        return ModelResponse(content=choice.content, tool_calls=tool_calls)

    async def ainvoke(
        self, messages: list[Message], tools: list[dict] | None = None
    ) -> ModelResponse:
        resp = await self.aclient.chat.completions.create(
            **self._build_openai_messages(messages, tools)
        )
        return self._parse_response(resp)

    async def ainvoke_stream(
        self, messages: list[Message], tools: list[dict] | None = None
    ) -> AsyncIterator[ModelResponse]:
        # stream = await self.aclient.chat.completions.create(**self._build_openai_messages(messages, tools),stream=True)
        async with await self.aclient.chat.completions.create(
            **self._build_openai_messages(messages, tools), stream=True
        ) as stream:
            acc = ToolCallAccumulator()
            async for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                if delta.content:
                    yield ModelResponse(content=delta.content)
                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        acc.add_fragment(
                            index=tc.index,
                            id=tc.id,
                            name=tc.function.name,
                            arguments=tc.function.arguments,
                        )
            calls = acc.finalize()
            if calls:
                yield ModelResponse(tool_calls=calls)

    @override
    async def close(self) -> None:
        self.client.close()
        await self.aclient.close()
