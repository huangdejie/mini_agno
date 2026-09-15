import asyncio
from mini_agno.agent import Agent
from mini_agno.models.message import Message
from mini_agno.models.openai_model import OpenAIModel
from mini_agno.tools.decorator import my_tool


@my_tool
def query_temperature(bake_house: str):
    """根据烤房名称查询温度"""
    return "38.2"


@my_tool
def query_humidity(bake_house: str):
    """根据烤房名称查询湿度"""
    return "80.1"


async def run_ainvoke():

    openAiModel = OpenAIModel()

    # 第 1 轮：纯文本 —— 看打字机效果（end="" 不换行，flush=True 立刻上屏不攒缓冲）
    print("--- 纯文本轮 ---")
    async for r in openAiModel.ainvoke_stream(
        messages=[Message(role="user", content="用50个字介绍一下你自己")]
    ):
        if r.content:
            print(r.content, end="", flush=True)
    print("\n")

    # 第 2 轮：带工具 —— 看 content 自言自语碎片 + 末尾拼装好的 tool_calls
    print("--- 工具轮 ---")
    async for r in openAiModel.ainvoke_stream(
        messages=[Message(role="user", content="帮我查询001烤房的温湿度")],
        tools=[query_temperature.to_dict(), query_humidity.to_dict()],
    ):
        if r.content:
            print(r.content, end="", flush=True)
        if r.tool_calls:
            print(f"\ntool_calls={r.tool_calls}")
            for call in r.tool_calls:
                print(f"\nid={call.id},name={call.name},arguments={call.arguments}")


async def run_agent_stream():
    model = OpenAIModel()
    try:
        agent = Agent(model=model, tools=[query_temperature, query_humidity])
        async for r in agent.arun_stream(
            "帮我查询001烤房的温湿度,然后根据这个温湿度进行分析"
        ):
            print(r.content, end="", flush=True)
    except Exception as e:
        print(e)
    # finally:
    # await model.aclose()

    print("\n done")


# asyncio.run(run_ainvoke())
asyncio.run(run_agent_stream())
