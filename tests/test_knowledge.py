


from mini_agno.agent import Agent
from mini_agno.knowledge.knowledge import Knowledge
from mini_agno.models.message import ModelResponse
from mini_agno.models.mock import MockModel


def test_knowledge_search():
    docs = [
        "我们公司年假15天，入职满一年可用",
        "食堂在3楼，午餐时间是 11:30-13:30"
    ]
    knowledge = Knowledge(docs)
    result = knowledge.search("年假")
    assert "我们公司年假15天，入职满一年可用" in result

def test_knowledge_in_agent():
    docs = [
        "我们公司年假15天，入职满一年可用",
        "食堂在3楼，午餐时间是 11:30-13:30"
    ]
    knowledge = Knowledge(docs)
    mock = MockModel(
        id="mock",
        response_list=[ModelResponse(content="15天")]
    )
    agent = Agent(model=mock, tools=[],knowledge=knowledge)
    resp = agent.run("年假多少天")
    assert "15" in resp
