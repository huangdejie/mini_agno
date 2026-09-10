from dataclasses import dataclass
from mini_agno.models.base import Model
from mini_agno.models.message import Message, ModelResponse
import logging


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
