# mini-agno 学习日志

> 这份日志记录每天的学习进度和关键知识点，方便跨天接续。
> 学习地图见 agno 仓库 `docs/agno-source-code-guide.md`。

---

## 总览

- **项目**：mini-agno（自己造的迷你 agent 框架），路径 `/Users/huangdj/code/mine/mini-agno`
- **目标**：读 agno 源码 + 自己实现，吃透 agent 框架的设计原理
- **agno 源码**：`/Users/huangdj/code/open/agno`（`libs/agno/agno/`）
- **方式**：每个模块 = 读 agno 源码 → 自己实现 → 写测试验收。我（Claude）给指令，用户自己动手。
- **任务跟踪**：12 个模块（task #1–#12）

## 模块进度

| # | 模块 | 状态 | 日期 |
|---|---|---|---|
| 0 | 全局架构 + 项目骨架 | ✅ 完成 | 2026-08-05 |
| 1 | 核心数据模型（Message/Response） | ✅ 完成 | 2026-08-05 |
| 2 | Model 抽象（多厂商可插拔） | ⬅️ 下一个 | — |
| 3 | 工具系统 | 未开始 | — |
| 4 | Agent 主循环（里程碑 M1） | 未开始 | — |
| 5 | 结构化输出 | 未开始 | — |
| 6 | 会话与持久化 | 未开始 | — |
| 7 | 记忆系统 | 未开始 | — |
| 8 | RAG 知识库 | 未开始 | — |
| 9 | 多智能体（Team） | 未开始 | — |
| 10 | 工作流（Workflow） | 未开始 | — |
| 11 | 运行时 API 化（里程碑 M4） | 未开始 | — |

---

## 2026-08-05（Day 1）

### 完成的事

**模块 0 · 全局架构 + 项目骨架**
- 用 `uv init mini-agno --python 3.12` 建项目，改造成 `mini_agno` 包 + pytest 环境
- 理解 agno 的 **五层架构**：领域模型 / 执行引擎 / 能力层 / 持久化 / 运行时
- **关键认知**：agno 的 `Agent` 类（`agent/agent.py`）里**没有主循环**——执行逻辑被抽到了 `run/` 目录。这是"是什么（配置）"和"怎么跑（执行）"分离的体现
- 验收：`uv run pytest`，3 个环境测试全绿

**模块 1 · 核心数据模型**
- 读了 agno 的 `models/message.py:55`（`Message` 用 Pydantic BaseModel，核心字段 role + content）
- 在 `mini_agno/message.py` 实现了 `Message` / `ModelResponse` / `RunResponse`（Pydantic）
- 验收：往返序列化测试通过

### 今天学到的关键点

**工具链（uv + pytest）**
- `uv` ≈ Maven Wrapper；`uv run X` = "在项目 venv 里跑命令 X"
- `pytest` 是**测试运行器程序**（≈ JUnit + Surefire），不是测试文件本身
- 跑测试用 `uv run pytest`（启动运行器，它自动发现测试），**不是**直接跑测试文件
- pytest 自动扫描 `test_*.py` 里的 `test_*` 函数；`testpaths`/`pythonpath` 在 `pyproject.toml` 的 `[tool.pytest.ini_options]` 配置

**Python 语法**
- Pydantic `BaseModel` ≈ 带 Jackson + Bean Validation 的 DTO：
  - 构造器自动生成，不用写 `__init__`
  - `model_dump()` → dict（≈ `toJson`）
  - `model_validate(dict)` → 对象（≈ `fromJson`）
- **`==` 比值**（调 `__eq__`，≈ Java `equals`）；**`is` 比引用**（≈ Java `==`）——和 Java 正好相反
- Pydantic 的 `==` 逐字段比较，对象可直接 `==` 比较（嵌套列表也递归比）
- `assert 条件` / `assert 条件, "说明"`；pytest 会"魔法重写" assert，失败时显示两边值对比
- 往返序列化：`obj.model_dump()` → `Cls.model_validate(d)`，值相等（随机默认字段也不影响，因为 dump 时已序列化当前值）

### 当前 mini-agno 状态

- 已实现：`mini_agno/__init__.py`、`mini_agno/message.py`（Message/ModelResponse/RunResponse）
- 测试：`tests/test_setup.py`（环境）、`tests/test_message.py`（数据模型）
- 依赖：pydantic、pytest、black

---

## 明天从哪开始

**模块 2 · Model 抽象（多厂商可插拔）**

- 读 agno `models/base.py:130` 的 `Model(ABC)`，看它的 4 个抽象方法（`invoke` / `ainvoke` / `invoke_stream` / `ainvoke_stream`）
- 读一个具体实现（`models/openai/`），看它怎么把统一契约翻译成厂商 SDK 调用
- 在 mini-agno 实现 `Model(ABC)` + 第一个实现（OpenAI 或先写个 mock 假模型，便于离线测试）
- 验收：`model.invoke(messages) -> ModelResponse`

详细任务卡见 agno 仓库 `docs/agno-source-code-guide.md` 的「模块 2」一节。

## 环境备忘

```bash
cd /Users/huangdj/code/mine/mini-agno   # 进项目
uv run pytest                            # 跑所有测试
uv run pytest tests/test_message.py      # 跑单个文件
uv run python -c "..."                   # 跑小段代码验证
```
