
from mini_agno.agent import Agent
from mini_agno.db.sqlite_db import SqliteDb
from mini_agno.memory.manager import MemoryManager
from mini_agno.models.message import ModelResponse
from mini_agno.models.mock import MockModel


def test_memory(tmp_path):
    db_file = tmp_path / "memory.db"
    db = SqliteDb(str(db_file))
    mm = MemoryManager(db)

    # 4 次 run，每次 = 1 次主循环 + 1 次提炼，共 8 个响应
    model = MockModel(
        id="memory_mock",
        response_list=[
            ModelResponse(content="你好张三"),                # run 1 主循环
            ModelResponse(content="用户叫张三"),               # run 1 提炼
            ModelResponse(content="JDK17 推荐用 java.time"),  # run 2 主循环
            ModelResponse(content=""),                         # run 2 提炼（无新事实）
            ModelResponse(content="你叫张三"),                 # run 3 主循环（读到记忆）
            ModelResponse(content=""),                         # run 3 提炼（无新事实）
            ModelResponse(content="我不知道你叫什么"),          # run 4 主循环（u2 无记忆）
            ModelResponse(content=""),                         # run 4 提炼（无新事实）
        ],
    )
    agent = Agent(model=model, tools=[], memory_manager=mm)
    agent.run("你好，我叫张三", session_id="s1", user_id="u1")

    agent.run("jdk17中日期格式化推荐用什么", session_id="s2", user_id="u1")
    resp = agent.run("我叫什么？", session_id="s3", user_id="u1")
    assert "张三" in resp
    resp = agent.run("我叫什么？", session_id="s4", user_id="u2")
    assert "张三" not in resp
