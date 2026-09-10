from abc import ABC, abstractmethod
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

    async def ainvoke(
        self, messages: list[Message], tools: list[dict] | None = None
    ) -> ModelResponse:
        """Invoke the model with a list of messages."""
        pass
