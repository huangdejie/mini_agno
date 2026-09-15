import random
from mini_agno.agent import Agent
from mini_agno.models.openai_model import OpenAIModel
from mini_agno.team.team import Team
from mini_agno.tools.decorator import my_tool


@my_tool
def query_temperature(bake_house: str) -> str:
    """根据烤房查询烤房的温度"""
    base_temp = 45.5
    fluctuation = 10.0
    random_temp = random.uniform(base_temp - fluctuation, base_temp + fluctuation)
    return f"{random_temp:.1f}"


def run_team():
    members = []
    model = OpenAIModel()

    temp_agent = Agent(
        model=model,
        name="temperatureAgent",
        tools=[query_temperature],
        description="你是一个善于根据工具查询烤房温度的助手",
    )

    analysis_agent = Agent(
        model=model,
        name="analysisAgent",
        tools=[],
        description="你是一个善于根据烤房温度进行分析的助手（不要依赖于其他技术标准仅依赖以下规则）.规则如下：如果烤房小于40度，则建议提升火力；如果烤房温度大于等于40度但小于50度，则建议保持火力；如果烤房温度大于等于50度，则建议降低火力。",
    )
    members.append(analysis_agent)
    members.append(temp_agent)

    team = Team(members=members, leader_model=model, mode="coordinate")
    a = team.run(
        "帮我分析河南平顶山001烤房的温度情况，并给出当前火力操作建议，不要依赖于其他行业标准，并说出用到了哪些工具"
    )
    print(a)


if __name__ == "__main__":
    run_team()
    # print(query_temperature("河南平顶山001烤房"))
