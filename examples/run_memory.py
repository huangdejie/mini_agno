from uuid import uuid4


from mini_agno.agent import Agent
from mini_agno.db.sqlite_db import SqliteDb
from mini_agno.memory.manager import MemoryManager
from mini_agno.models.message import ModelResponse
from mini_agno.models.mock import MockModel
from mini_agno.models.openai_model import OpenAIModel


def run_memory():
    db = SqliteDb("test_memory.db")
    mm = MemoryManager(db)

    model = OpenAIModel()
    agent = Agent(model=model, tools=[], memory_manager=mm)
    agent.run("你好，我叫张三", session_id="s1", user_id="u1")

    agent.run("jdk17中日期格式化推荐用什么", session_id="s2", user_id="u1")
    resp = agent.run("我叫什么？", session_id="s3", user_id="u1")
    print(resp)
    assert "张三" in resp
    resp = agent.run("我叫什么？", session_id="s4", user_id="u2")
    assert "张三" not in resp


if __name__ == "__main__":
    from mini_agno.db.sqlite_db import SqliteDb
    from mini_agno.memory.manager import MemoryManager

    db = SqliteDb("mini_agno_memory_test.db")
    mm = MemoryManager(db)
    mm.add_memories("user01", ["我叫张三" + uuid4().hex, "我喜欢喝酒"])
    print(mm.get_memories("user01"))
