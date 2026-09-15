import asyncio
import time
from mini_agno.agent import Agent
from mini_agno.models.openai_model import OpenAIModel


async def main():
    agent = Agent(model=OpenAIModel(), tools=[])

    resp = await agent.arun("你好，用一句话介绍你自己", session_id="test_async_demo")
    print(f"响应:{resp}")

    t0 = time.time()
    results = await asyncio.gather(
        agent.arun("你好，用一句话介绍你自己", session_id="test_async_demo"),
        agent.arun("你叫什么名字", session_id="test_async_demo"),
        agent.arun("你叫什么名字", session_id="test_async_demo"),
    )
    print(f"耗时:{time.time() - t0}")
    for result in results:
        print(result)


asyncio.run(main())
