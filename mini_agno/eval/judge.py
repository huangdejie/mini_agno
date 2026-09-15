from pydantic import BaseModel, ConfigDict, Field

from mini_agno.agent import Agent
from mini_agno.models.base import Model
from mini_agno.models.openai_model import OpenAIModel


class JudgeResult(BaseModel):
    """裁判输出。真模型的字段名会漂移（爱写 reason 而不是 feedback），
    用别名两个都收，内部统一叫 feedback。"""

    model_config = ConfigDict(populate_by_name=True)

    score: int = Field(ge=1, le=10)
    feedback: str = Field(alias="reason")


def make_judge(rubric: str, model: Model | None = None) -> Agent:
    """裁判工厂：rubric 进 instructions，输出结构化成 JudgeResult。

    model 可注入（离线测试传 MockModel）；不传默认真模型。
    """
    return Agent(
        model=model or OpenAIModel(),
        tools=[],  # 裁判不许调工具
        instructions=(
            "你是质量评审员，只依据下面的评分细则打分。"
            '只输出一个 JSON 对象，键为 "score"（1-10 的整数）和 "reason"（评审理由）。\n'
            f"细则:{rubric}"
        ),
        output_schema=JudgeResult,
    )
