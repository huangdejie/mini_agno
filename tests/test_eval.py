import pytest
from pydantic import ValidationError

from mini_agno.agent import Agent
from mini_agno.eval.case import EvalCase, load_cases
from mini_agno.eval.judge import JudgeResult
from mini_agno.eval.runner import run_judge_case, run_keyword_case
from mini_agno.models.message import ModelResponse
from mini_agno.models.mock import MockModel


def test_eval_keyword():
    pass_agent = Agent(
        model=MockModel(
            id="mock_model",
            response_list=[
                ModelResponse(content="001烤房当前温度38.2度，建议提升火力.")
            ],
        ),
        tools=[],
    )

    assert (
        run_keyword_case(
            pass_agent,
            EvalCase(input="x", mode="keyword", keywords=["提升火力", "38.2"]),
            session_id="test_session_id",
        )
        is True
    )

    fail_agent = Agent(
        model=MockModel(
            id="m2",
            response_list=[
                ModelResponse(content="001烤房状态正常"),  # 两个词都没有
            ],
        ),
        tools=[],
    )
    assert (
        run_keyword_case(
            fail_agent, EvalCase(input="x", mode="keyword", keywords=["提升火力"]), "s2"
        )
        is False
    )


def test_load_cases():
    cases = load_cases("mini_agno/eval/bake_house.yaml")
    assert len(cases) == 4
    assert cases[0].mode == "keyword" and cases[0].keywords == ["提升火力", "38.2"]
    assert cases[1].mode == "keyword" and "保持火力" in (cases[1].keywords or [])
    assert cases[2].mode == "judge" and cases[2].rubric is not None
    assert cases[3].mode == "judge" and "降低火力" in (cases[3].rubric or "")


def _make_mock_judge(judge_id: str, script_content: str) -> Agent:
    """构造 MockModel 裁判：剧本是 JudgeResult 的 JSON 字符串，
    走 output_schema 的 model_validate_json 分支。"""
    return Agent(
        model=MockModel(
            id=judge_id, response_list=[ModelResponse(content=script_content)]
        ),
        tools=[],
        output_schema=JudgeResult,
    )


def test_judge_parses_score():
    # 剧本 7 分 -> run_judge_case 应解析成 JudgeResult（score/feedback 正确映射）
    judge = _make_mock_judge(
        "j1", '{"score": 7, "feedback": "建议符合规则且引用了真实数值"}'
    )
    case = EvalCase(
        input="001烤房温度38.2度，该调多大火力？", mode="judge", rubric="1-10分"
    )
    result = run_judge_case(
        judge, case, answer="温度38.2度，建议提升火力", session_id="j1"
    )
    assert result.score == 7
    assert "规则" in result.feedback


def test_judge_out_of_range():
    # 剧本越界分数 -> Field(ge=1, le=10) 应咬住，抛 ValidationError
    judge = _make_mock_judge("j2", '{"score": 15, "feedback": "满分！"}')
    case = EvalCase(input="x", mode="judge", rubric="1-10分")
    with pytest.raises(ValidationError):
        run_judge_case(judge, case, answer="任意回答", session_id="j2")


def test_run_eval_aggregates():
    """全流程编排 + 聚合：4 用例（2 keyword 一过一败 + 2 judge 7分/4分）。

    被测 agent 和 judge 各用独立 MockModel，剧本按消耗顺序排：
    agent 按 case 顺序消耗 4 条；judge_model 只被 judge 用例消耗 2 条。
    """
    from mini_agno.eval.runner import run_eval

    cases = [
        EvalCase(input="查温度", mode="keyword", keywords=["提升火力", "38.2"]),
        EvalCase(input="总结状态", mode="keyword", keywords=["提升火力"]),
        EvalCase(input="给火力建议", mode="judge", rubric="规则正确性"),
        EvalCase(input="评估回答质量", mode="judge", rubric="规则正确性"),
    ]
    agent = Agent(
        model=MockModel(
            id="under-test",
            response_list=[
                ModelResponse(content="温度38.2度，建议提升火力"),  # case0: 过
                ModelResponse(content="烤房状态正常"),  # case1: 败（缺词）
                ModelResponse(
                    content="温度38.2，建议降低火力"
                ),  # case2: 规则错（judge 给 7？不——剧本 4 分）
                ModelResponse(content="状态良好"),  # case3
            ],
        ),
        tools=[],
    )
    judge_model = MockModel(
        id="judge",
        response_list=[
            ModelResponse(
                content='{"score": 7, "feedback": "引用了真实数值"}'
            ),  # case2 -> 7
            ModelResponse(
                content='{"score": 4, "feedback": "建议不符合规则"}'
            ),  # case3 -> 4
        ],
    )

    report = run_eval(agent, cases, judge_model=judge_model)

    assert report.keyword_pass_count == (1, 2)
    assert report.judge_avg_score == 5.5
    assert report.score_distribution() == {"1-5": 1, "6-8": 1, "9-10": 0}
    fails = report.failures(threshold=6)
    assert len(fails) == 2  # keyword 败的那条 + 4 分的那条
    assert fails[0].case is cases[1]
    assert fails[1].score == 4 and "规则" in fails[1].feedback
