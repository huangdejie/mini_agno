from dataclasses import dataclass, field


@dataclass
class Knowledge:
    documents: list[str] = field(default_factory=list)

    def search(self, query: str, top_k: int = 3) -> list[str]:
        """
        L1 简化实现：字符串匹配 + 顺序兜底
        返回最相关的 top_k 个文档片段。
        """
        # 先找包含 query 关键词的
        matched = [doc for doc in self.documents if query in doc]

        # 如果匹配不够，用剩下的文档按顺序补齐
        if len(matched) < top_k:
            others = [doc for doc in self.documents if doc not in matched]
            matched.extend(others[: top_k - len(matched)])
        return matched[:top_k]
