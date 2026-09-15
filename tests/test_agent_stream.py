import asyncio

from mini_agno.agent import Agent
from mini_agno.models.message import ModelResponse, ToolCall
from mini_agno.models.mock import MockModel
from mini_agno.tools.decorator import my_tool


@my_tool
def query_temperature(bake_house: str):
    """查询烤房温度"""
    return "38.2"


def test_agent_stream_tool_round_and_history():
    """流式主循环：工具轮 + 文本轮；历史里每轮恰好记录本轮产出。

    第一幕剧本故意让自言自语和 tool_calls 同幕出现——这是跨轮污染
    （full_content 没按轮清零）的触发条件，屏幕上看不出来，只有
    断言历史才能抓住。
    """

    async def collect():
        model = MockModel(
            id="m",
            response_list=[
                # 第一幕：自言自语 + 工具调用（同一幕）
                ModelResponse(
                    content="我来查一下",
                    tool_calls=[
                        ToolCall(
                            id="c1",
                            name="query_temperature",
                            arguments={"bake_house": "001"},
                        )
                    ],
                ),
                # 第二幕：纯文本终答
                ModelResponse(content="001烤房温度38.2度"),
            ],
        )
        agent = Agent(model=model, tools=[query_temperature])
        frames = []
        async for r in agent.arun_stream("查一下001烤房温度"):
            frames.append(r)
        return agent, frames

    agent, frames = asyncio.run(collect())
    history = agent.sessions["default"].messages

    # 1) 转发轨道：收到的所有 content 帧拼起来 = 两轮文本之和
    assert (
        "".join(f.content for f in frames if f.content) == "我来查一下001烤房温度38.2度"
    )

    # 2) 历史结构：user -> assistant(自言自语+tool_calls) -> tool(结果) -> assistant(终答)
    assert [m.role for m in history] == ["user", "assistant", "tool", "assistant"]

    # 3) 自言自语挂在第一轮的 assistant 消息上（和 tool_calls 同一条）
    assert history[1].content == "我来查一下"
    assert [t.name for t in history[1].tool_calls] == ["query_temperature"]

    # 4) 工具真实执行，返回值进了 tool 消息
    assert "38.2" in history[2].content

    # 5) 终答干净：恰好是第二轮产出，不含上一轮的自言自语
    #    （full_content 每轮清零的验收——本测试的核心断言）
    assert history[3].content == "001烤房温度38.2度"
