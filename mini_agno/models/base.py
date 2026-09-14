from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass

from mini_agno.models.message import Message, ModelResponse


@dataclass
class Model(ABC):
    id: str

    @abstractmethod
    def invoke(
        self, messages: list[Message], tools: list[dict] | None = None
    ) -> ModelResponse:
        """Invoke the model with a list of messages."""
        pass

    @abstractmethod
    async def ainvoke(
        self, messages: list[Message], tools: list[dict] | None = None
    ) -> ModelResponse:
        """Invoke the model asynchronously with a list of messages."""
        pass

    @abstractmethod
    def ainvoke_stream(
        self, messages: list[Message], tools: list[dict] | None = None
    ) -> AsyncIterator[ModelResponse]:
        """Stream the model response: yields content fragments as they arrive,
        then one final ModelResponse carrying fully-assembled tool_calls (if any)."""
        pass

    async def aclose(self) -> None:
        """释放模型持有的资源；无资源子类（如 MockModel）不用覆写。"""
        pass
