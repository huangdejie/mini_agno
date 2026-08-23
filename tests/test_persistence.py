from mini_agno.agent import Agent
from mini_agno.db.sqlite_db import SqliteDb
from mini_agno.models.mock import MockModel
from mini_agno.models.message import ModelResponse


def test_session_psersists_across_agent_instances(tmp_path):
    db_file = tmp_path / "test.db"
    db = SqliteDb(str(db_file))

    # 第一个 Agent 实例写入
    a1 = Agent(
        model=MockModel(id="m1", response_list=[ModelResponse(content="你叫张三")]),
        tools=[],
        db=db,
    )
    a1.run("我叫张三", session_id="s1")

    # 第二个全新实例读取
    a2 = Agent(
        model=MockModel(id="m2", response_list=[ModelResponse(content="你叫张三")]),
        tools=[],
        db=db,
    )
    a2.run("我叫什么", session_id="s1")

    assert len(a2.sessions["s1"].messages) == 4  # 两次 run 各两条
    assert a2.sessions["s1"].messages[0].content == "我叫张三"
    assert a2.sessions["s1"].messages[2].content == "我叫什么"
