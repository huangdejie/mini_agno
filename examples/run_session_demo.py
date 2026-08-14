"""真模型验证：多轮会话记忆（手动跑，不进 pytest）。

为什么不进 pytest：
- 需要 DEEPSEEK_API_KEY，CI/无网环境必挂
- 真打 API 会花钱、慢
- 模型行为不稳定，断言脆弱

用法：
    export DEEPSEEK_API_KEY="你的key"
    uv run python examples/run_session_demo.py

预期：第二轮能答出"你叫张三、是程序员"——说明历史真的带上了（记住了）。
"""

from mini_agno.agent import Agent
from mini_agno.models.openai_model import OpenAIModel

if __name__ == "__main__":
    agent = Agent(model=OpenAIModel(), tools=[])
    print("第一轮：", agent.run(user_message="我叫张三，是个程序员", session_id="zhen_test"))
    print("第二轮：", agent.run(user_message="我叫谁？职业是什么？", session_id="zhen_test"))
    print("历史消息数：", len(agent.sessions['zhen_test'].messages))  # 预期 4（user+assistant × 2）
