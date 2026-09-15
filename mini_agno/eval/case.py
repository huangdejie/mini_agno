from dataclasses import dataclass
import yaml


@dataclass
class EvalCase:
    input: str
    mode: str
    keywords: list[str] | None = None  # keyword模式：输出必须含这些词
    rubric: str | None = None  # judege 模式：评分细则


def load_cases(path: str) -> list[EvalCase]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return [EvalCase(**case) for case in data["cases"]]
