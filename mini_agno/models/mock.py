import asyncio
import json
import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass

from mini_agno.models.base import Model
from mini_agno.models.message import Message, ModelResponse
from mini_agno.models.stream import ToolCallAccumulator


class MockModel(Model):

    def __init__(self, id: str, response_list: list[ModelResponse]):
        super().__init__(id)
        self.response_list = response_list
        self.idx = 0
        self.response = None

    def _next(self) -> ModelResponse:
        if self.idx >= len(self.response_list):
            raise RuntimeError("MockModel response_list exhausted (剧本不够)")
        self.response = self.response_list[self.idx]
        self.idx += 1
        return self.response

    def invoke(
        self, messages: list[Message], tools: list[dict] | None = None
    ) -> ModelResponse:
        """Invoke the model with a list of messages."""
        msg = ""
        for message in messages:
            msg += message.content or ""
        logging.debug(f"正在调用模型{self.id}...,消息:{msg}")
        resp = self._next()
        logging.debug(f"模型{self.id}返回:{resp}")
        return resp

    async def ainvoke(
        self, messages: list[Message], tools: list[dict] | None = None
    ) -> ModelResponse:
        """异步版 mock 不分同步异步，直接复用 invoke 的剧本逻辑。"""
        return self.invoke(messages, tools)

    async def ainvoke_stream(
        self, messages: list[Message], tools: list[dict] | None = None
    ) -> AsyncIterator[ModelResponse]:
        """流式版 mock：一次调用消耗一个剧本响应（对应模型一轮）。

        扮演供应商的碎片线况：
        - content 按 5 字符一片吐，片间 sleep 让流式肉眼可见
        - tool_calls 的 arguments 先 json.dumps 还原成线上形态（JSON 字符串），
          刀两半模拟供应商碎片，再喂给 ToolCallAccumulator 拼回，
          按"拼好才发"的协议 yield——剁碎和拼装都在 mock 内闭环，
          离线复现线上全程。
        """
        resp = self._next()
        if resp.content:
            for i in range(0, len(resp.content), 5):
                yield ModelResponse(content=resp.content[i : i + 5])
                await asyncio.sleep(0.01)
        if resp.tool_calls:
            acc = ToolCallAccumulator()
            for index, tc in enumerate(resp.tool_calls):
                args_str = json.dumps(tc.arguments)
                half = max(1, len(args_str) // 2)  # 防空串/极短串切出 0
                acc.add_fragment(
                    index=index, id=tc.id, name=tc.name, arguments=args_str[:half]
                )
                acc.add_fragment(
                    index=index, id=None, name=None, arguments=args_str[half:]
                )
            calls = acc.finalize()
            if calls:
                yield ModelResponse(tool_calls=calls)
