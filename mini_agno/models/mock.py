from dataclasses import dataclass
from mini_agno.models.base import Model
from mini_agno.models.message import Message, ModelResponse


@dataclass
class MockModel(Model):
    response: str

    def invoke(self, messages: list[Message]) -> ModelResponse:
        """Invoke the model with a list of messages."""
        msg = ""
        for message in messages:
            msg += message.content
        print(f"正在调用模型{self.id}...,消息:{msg}")
        return ModelResponse(content=self.response)
