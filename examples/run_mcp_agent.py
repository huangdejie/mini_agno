import asyncio
from mini_agno.agent import Agent
from mini_agno.models.openai_model import OpenAIModel
from mini_agno.tools.mcp_tools import MCPTools


async def run_agent_with_mcp():
    mcp = MCPTools(command="uv", args=["run", "examples/mcp_server_bake.py"])
    await mcp.connect()
    agent = Agent(model=OpenAIModel(), tools=mcp.get_functions())
    resp = await agent.arun("烤房002的温度是多少")
    print(resp)


asyncio.run(run_agent_with_mcp())
