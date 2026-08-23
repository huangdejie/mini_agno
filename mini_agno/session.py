from dataclasses import dataclass, field
from mini_agno.models.message import Message


@dataclass
class Session:
    session_id: str
    user_id: str
    messages: list[Message] = field(default_factory=list)

    def __post_init__(self):
        self.messages = [
            Message(**msg) if isinstance(msg, dict) else msg for msg in self.messages
        ]
