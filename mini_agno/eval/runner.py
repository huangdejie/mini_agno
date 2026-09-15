from mini_agno.agent import Agent
from mini_agno.eval.case import EvalCase
from mini_agno.eval.judge import JudgeResult, make_judge
from mini_agno.eval.report import CaseResult, EvalReport
from mini_agno.models.base import Model


def run_keyword_case(agent: Agent, case: EvalCase, session_id: str) -> bool:
    resp = agent.run(case.input, session_id=session_id)  # 每个用例独立session
    # all(...) 当括号里所有的结果都为True时，才返回True；只要有一个是False，就返回False。（如果关键词列表是空的，all([])默认返回True）
    return all(k in resp for k in case.keywords or [])


def run_judge_case(
    judge: Agent, case: EvalCase, answer: str, session_id: str
) -> JudgeResult:
    prompt = f"用户问题: {case.input}\n\n待评审的回答: {answer}"
    return judge.run(prompt, session_id=session_id)


def run_eval(
    agent: Agent, cases: list[EvalCase], judge_model: Model | None = None
) -> EvalReport:
    results = []
    for i, case in enumerate(cases):
        if case.mode == "keyword":
            resp = agent.run(case.input, session_id=f"eval-{i}")
            missing = [k for k in (case.keywords or []) if k not in resp]
            results.append(
                CaseResult(
                    case=case,
                    passed=not missing,
                    score=None,
                    answer=resp,
                    feedback=f"缺少关键词:{missing}" if missing else "全部命中",
                )
            )
        elif case.mode == "judge":
            resp = agent.run(case.input, session_id=f"eval-{i}")
            judge = make_judge(case.rubric, model=judge_model)
            judge_result = run_judge_case(judge, case, resp, session_id=f"judge-{i}")
            results.append(
                CaseResult(
                    case=case,
                    passed=None,
                    score=judge_result.score,
                    answer=resp,
                    feedback=judge_result.feedback,
                )
            )
    return EvalReport(results=results)
