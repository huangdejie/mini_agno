"""eval 入口：加载用例集 -> 跑被测 agent -> 输出报告。

用法：
    uv run python examples/run_eval.py            # 正常跑（用当前 agent 配置）
    uv run python examples/run_eval.py --mutate   # 突变模式：故意把规则写反，验证 eval 有牙齿

真模型跑一轮会消耗若干次 API 调用（每条用例 1 次被测 + judge 用例再加 1 次裁决）。
"""

import sys

from mini_agno.agent import Agent
from mini_agno.eval.case import load_cases
from mini_agno.eval.runner import run_eval
from mini_agno.models.openai_model import OpenAIModel

# 正常规则 vs 突变规则（故意写反）——对比两轮报告，分数跌 = 尺子有效
RULES = (
    "火力规则：温度<40 建议提升火力；40<=温度<50 建议保持火力；温度>=50 建议降低火力。"
)
RULES_MUTATED = (
    "火力规则：温度<40 建议降低火力；40<=温度<50 建议保持火力；温度>=50 建议提升火力。"
)


def main(mutated: bool = False) -> None:
    rules = RULES_MUTATED if mutated else RULES
    label = "突变（规则故意写反）" if mutated else "基线"
    print(f"=== Eval 跑分：{label} ===\n")

    agent = Agent(
        model=OpenAIModel(),
        tools=[],
        instructions=(
            "你是烤房管理助手，根据用户提供的烤房温度湿度数据给出火力操作建议。"
            f"{rules}建议必须引用用户给出的真实数值，说明理由。"
        ),
    )

    cases = load_cases("mini_agno/eval/bake_house.yaml")
    report = run_eval(agent, cases)
    report.print_summary()


if __name__ == "__main__":
    main(mutated="--mutate" in sys.argv)
