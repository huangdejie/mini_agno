from mini_agno.db.sqlite_db import SqliteDb
from mini_agno.models.message import ModelResponse
from mini_agno.models.mock import MockModel
from mini_agno.agent import Agent

DB_FILE = "db/mini_agno_persist_demo.db"

if __name__ == "__main__":
    db = SqliteDb(DB_FILE)
    mock = MockModel(id="mock", response_list=[ModelResponse(content="你叫张三")])
    agent = Agent(db=db, model=mock, tools=[])

    resp = agent.run("我叫什么", session_id="persist_demo")
    print(f"响应:{resp}")
    print("历史消息数：", len(agent.sessions["persist_demo"].messages))
