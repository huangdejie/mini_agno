from mini_agno.agent import Agent
from mini_agno.models.openai_model import OpenAIModel

# demo 工具就在同目录，按文件名导入（executed from repo root via `uv run python examples/...`）
from examples.bake_tools import query_bake_info

if __name__ == "__main__":
    model = OpenAIModel()
    tools = [query_bake_info]
    agent = Agent(model=model, tools=tools)
    v = agent.run(user_message="北京烘烤信息查询")
    print(v)
