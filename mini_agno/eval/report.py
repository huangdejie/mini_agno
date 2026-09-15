from dataclasses import dataclass
from mini_agno.eval.case import EvalCase


@dataclass
class CaseResult:
    case: EvalCase
    passed: bool | None
    score: int | None
    feedback: str  # judge的理由
    answer: str  # 被测 agent 的原话——失败清单是给人看的，必须带


@dataclass
class EvalReport:
    results: list[CaseResult]

    @property
    def keyword_pass_count(self) -> tuple[int, int]:
        """关键词通过统计"""
        kw = [r for r in self.results if r.case.mode == "keyword"]
        passed = sum(1 for r in kw if r.passed)
        # 返回通过数和总数
        return passed, len(kw)

    @property
    def judge_avg_score(self) -> float | None:
        """judge 用例的平均分；无 judge 用例返回 None"""
        scores = [r.score for r in self.results if r.case.mode == "judge"]
        if not scores:
            return None
        return sum(scores) / len(scores)

    def score_distribution(self) -> dict[str, int]:
        dist = {"1-5": 0, "6-8": 0, "9-10": 0}
        for r in self.results:
            if r.case.mode == "judge" and r.score is not None:
                if r.score <= 5:
                    dist["1-5"] += 1
                elif r.score <= 8:
                    dist["6-8"] += 1
                else:
                    dist["9-10"] += 1
        return dist

    def failures(self, threshold: int = 6) -> list[CaseResult]:
        out = []
        for r in self.results:
            if r.case.mode == "keyword" and r.passed is False:
                out.append(r)
            elif r.case.mode == "judge" and (r.score or 0) < threshold:
                out.append(r)
        return out

    def print_summary(self, threshold: int = 6) -> None:
        print("=" * 50)
        print("Eval 报告")
        print("=" * 50)
        passed, total = self.keyword_pass_count
        print(f"keyword: {passed}/{total} 通过")
        avg = self.judge_avg_score
        if avg is not None:
            judge_total = sum(1 for r in self.results if r.case.mode == "judge")
            dist = self.score_distribution()
            print(f"judge:   平均分 {avg:.1f}（{judge_total} 条）")
            print(
                f"分布:    [1-5]: {dist['1-5']}  [6-8]: {dist['6-8']}  [9-10]: {dist['9-10']}"
            )

        fails = self.failures(threshold)
        if fails:
            print(f"--- 未通过/低分清单（阈值 {threshold}）---")
            for r in fails:
                tag = "keyword 未过" if r.passed is False else f"score={r.score}"
                print(f"[{r.case.input[:30]}...] {tag}")
                print(f"  feedback: {r.feedback[:80]}")
                print(f"  answer:   {r.answer[:80]}")
        else:
            print("全部通过，无低分用例")
