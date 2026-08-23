from mini_agno.db.base import BaseDb


class MemoryManager:
    def __init__(self, db:BaseDb):
        self.db = db

    def get_memories(self, user_id:str):
        return self.db.get_memories(user_id)

    def add_memories(self, user_id:str, memories:list[str]) -> None:
        for memory in memories:
            self.db.add_memory(user_id, memory)
