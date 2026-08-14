from dataclasses import dataclass, field
from mini_agno.models.message import Message


@dataclass
class Session:
    session_id: str
    messages: list[Message] = field(default_factory=list)
