# mini-agno 学习日志

> 这份日志记录每天的学习进度和关键知识点，方便跨天接续。
> 学习地图见 agno 仓库 `docs/agno-source-code-guide.md`。

---

## 总览

- **项目**：mini-agno（自己造的迷你 agent 框架），路径 `/Users/huangdj/code/mine/mini-agno`
- **目标**：读 agno 源码 + 自己实现，吃透 agent 框架的设计原理
- **agno 源码**：`/Users/huangdj/code/open/agno`（`libs/agno/agno/`）
- **方式**：每个模块 = 讲清核心机制 → 自己实现最小版 → 写测试验收。Claude 给指令不代劳。
- **任务跟踪**：12 个模块（task #1–#12）

## 模块进度

| # | 模块 | 状态 | 日期 |
|---|---|---|---|
| 0 | 全局架构 + 项目骨架 | ✅ 完成 | 2026-08-05 |
| 1 | 核心数据模型（Message/Response） | ✅ 完成 | 2026-08-05 |
| 2 | Model 抽象（多厂商可插拔） | ✅ 完成 | 2026-08-06 |
| 3 | 工具系统（Function/FunctionCall） | ✅ 完成 | 2026-08-06 |
| 4 | **Agent 主循环**（里程碑 M1）🎯 | ✅ 完成 | 2026-08-06 |
| 5 | 结构化输出 | ⬅️ 下一个 | — |
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
- **关键认知**：agno 的 `Agent` 类（`agent/agent.py`）里**没有主循环**——执行逻辑被抽到了 `agent/_run.py`。这是"是什么（配置）"和"怎么跑（执行）"分离的体现
- 验收：`uv run pytest`，3 个环境测试全绿

**模块 1 · 核心数据模型**
- 读了 agno 的 `models/message.py:55`（`Message` 用 Pydantic BaseModel，核心字段 role + content）
- 在 `mini_agno/models/message.py` 实现了 `Message` / `ModelResponse` / `RunResponse`（Pydantic）
- 验收：往返序列化测试通过

### Day 1 学到的关键点

**工具链（uv + pytest）**
- `uv` ≈ Maven Wrapper；`uv run X` = "在项目 venv 里跑命令 X"
- `pytest` 是**测试运行器程序**（≈ JUnit + Surefire），用原生 `assert`
- 跑测试用 `uv run pytest`（启动运行器），不是直接跑测试文件
- `testpaths`/`pythonpath` 在 `pyproject.toml` 的 `[tool.pytest.ini_options]` 配置

**Python 语法**
- Pydantic `BaseModel` ≈ 带 Jackson + Bean Validation 的 DTO；`model_dump()`/`model_validate()`
- `==` 比值（≈ Java `equals`）；`is` 比引用（≈ Java `==`）——和 Java 相反
- `assert` + pytest 魔法重写报错

---

## 2026-08-06（Day 2）

### 完成的事

**模块 2 · Model 抽象（多厂商可插拔）**
- 读 agno `models/base.py:129` 的 `@dataclass class Model(ABC)`
- 实现 `mini_agno/models/base.py`：`Model(ABC)` + 抽象方法 `invoke(messages, tools) -> ModelResponse`
- 实现 `mini_agno/models/mock.py`：`MockModel`（脚本化，按顺序返回预设响应，支持离线测试）
- 验收：抽象类不可实例化 + MockModel.invoke 正确

**模块 3 · 工具系统**
- agno `tools/function.py`（1388 行）太难读，改为"核心机制 + 自己实现"
- 实现 `mini_agno/tools/function.py`：`Function`（`__post_init__` 自动从函数提取 name/description/parameters，生成 JSON Schema）+ `FunctionCall`（`execute` 用 `**arguments` 解包执行）
- 验收：`add` 函数能生成正确 schema + FunctionCall 执行返回 3

**模块 4 · Agent 主循环（里程碑 M1）🎯**
- 读 agno `agent/_run.py:2144`（while 循环；印证"执行逻辑从 Agent 类抽离"）
- 实现 `mini_agno/agent.py`：`Agent(model, tools)` + `run()` 的 ReAct/tool-use 循环
- **M1 达成**：mini-agno 第一次能跑一个会调用工具的 agent（多轮工具调用测试通过）

### Day 2 学到的关键点

**核心概念：ReAct/tool-use 循环（最重要的认知）**
- 模型每轮响应只有两种：A) 想调工具 → 返回 `tool_calls`；B) 想给最终答案 → 返回 `content`，无 `tool_calls`
- 循环判断极简：`if resp.tool_calls: 执行工具→结果塞回 messages→继续  else: return resp.content`
- **不存在"纯思考、不调工具、不给答案"的中间态**——真实模型每轮要么调工具要么给答案
- 工具结果消息用 `role="tool"`；assistant 的 tool_call 请求也要 append 进 messages（真模型必需）

**Python 语法**
- `@dataclass` + `ABC` 叠加；dataclass 子类自动继承父类字段
- `__post_init__`：dataclass 构造后自动跑的钩子（≈ Java `@PostConstruct`），用于自动提取字段
- `inspect.signature(fn)` + `typing.get_type_hints(fn)`：反射函数签名和类型
- `**dict` 字典解包：`fn(**{"a":1,"b":2})` ≡ `fn(a=1,b=2)`（按名解包，比 Java 反射 `Method.invoke` 更直接）
- `str.rstrip(chars)` 按**字符集**删，不是删子串；删子串用 `removesuffix`（3.9+）

**关键方法论（重要！）**
- **"测试通过 ≠ 代码正确"**：模块 3 把 `return` bug 写进测试期望值、模块 4 用 `:FINISHED` 哨兵让测试过——都被 review 抓出。写测试时期望值要写"应该是什么"，不是"现在输出是什么"
- **agno 生产级源码太难，别通读**：function.py 1388 行、_run.py 4500+ 行充斥边缘处理。主线是"核心机制 + 自己实现最小版"，agno 源码降级为按需 grep 查阅
- MockModel 能验证循环逻辑，但不读 messages，会掩盖"消息协议错误"——接真模型前要补完

### 接真模型前的待办（记着）
- [ ] tool 结果消息加 `tool_call_id` 字段（OpenAI 等协议必需，否则报错）
- [ ] 其他真模型消息协议细节（接真模型时统一补）

### 当前 mini-agno 状态
- 已实现：`models/message.py`（ToolCall/Message/ModelResponse/RunResponse）、`models/base.py`（Model ABC）、`models/mock.py`（MockModel）、`tools/function.py`（Function/FunctionCall）、`agent.py`（Agent + 主循环）
- 测试：test_setup / test_message / test_model / test_tools / test_agent（含多轮工具调用）
- **里程碑 M1 达成**：能跑会调工具的 agent

---

## 明天从哪开始

**模块 5 · 结构化输出**
- 让 agent 返回强类型对象（Pydantic 模型）而不是自由文本
- 对应 agno `agent.py` 的 `output_schema` 参数
- 验收：agent.run 返回某个 Pydantic 模型实例（如 `Weather(city, temp)`）
- 详细任务卡见 agno 仓库 `docs/agno-source-code-guide.md` 的「模块 5」

## 环境备忘

```bash
cd /Users/huangdj/code/mine/mini-agno   # 进项目
uv run pytest                            # 跑所有测试
uv run pytest tests/test_agent.py        # 跑单个文件
uv run python -c "..."                   # 跑小段代码验证
```
