from mini_agno.agent import Agent
from mini_agno.models.message import ModelResponse, ToolCall
from mini_agno.models.mock import MockModel
from mini_agno.tools.function import Function


def add(a: int, b: int):
    """Add two numbers"""
    print(f"执行啦Adding {a} and {b}")
    return a + b


def weather():
    """Query the weather"""
    return "sunny"


def test_agent():
    add_tool = ToolCall(name="add", arguments={"a": 1, "b": 2})
    weather_tool = ToolCall(name="weather", arguments={})
    mp1 = ModelResponse(
        content="用户让我先计算1+2，然后还要查询天气，我需要看看有哪些工具可以使用。。。太好了，找到了以下可以使用的工具,让我开始调用他们",
        tool_calls=[add_tool, weather_tool],
    )
    mp2 = ModelResponse(content="工具调用结果：1+2=3，天气是晴天。")
    model = MockModel(id="mock", response_list=[mp1, mp2])
    add_func = Function(entrypoint=add)
    weather_func = Function(entrypoint=weather)
    agent = Agent(model=model, tools=[add_func, weather_func])
    res = agent.run("请计算1+2，然后查询天气")
    print("#" * 30)
    print(res)
    assert res == "工具调用结果：1+2=3，天气是晴天。"


def test_agent_multi_turn_tools():
    model = MockModel(
        id="mock",
        response_list=[
            ModelResponse(
                tool_calls=[ToolCall(name="add", arguments={"a": 1, "b": 2})]
            ),  # 第1轮：先算加法
            ModelResponse(
                tool_calls=[ToolCall(name="weather", arguments={})]
            ),  #  第2轮：再查天气
            ModelResponse(content="算完了，也查完了。"),  # 第3轮：给答案
        ],
    )
    agent = Agent(
        model=model, tools=[Function(entrypoint=add), Function(entrypoint=weather)]
    )
    assert agent.run("先算1+2，再查天气") == "算完了，也查完了。"
