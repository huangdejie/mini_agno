from abc import ABC, abstractmethod
from mini_agno.session import Session


class BaseDb(ABC):

    @abstractmethod
    def get_session(self, session_id: str) -> Session | None:
        pass

    @abstractmethod
    def upsert_session(self, session: Session) -> None:
        pass

    @abstractmethod
    def get_memories(self, user_id: str) -> list[str]:
        pass

    @abstractmethod
    def add_memory(self, user_id: str, memory: str) -> None:
        pass
