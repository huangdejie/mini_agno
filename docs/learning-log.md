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
| 5 | 结构化输出 | ✅ 完成 | 2026-08-14 |
| 6 | 会话与持久化 | 🔧 进行中（⬅️ 下一个：Step3 持久化） | 2026-08-14 |
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

## 2026-08-13（Day 3，接续）

### 进度对齐（补记 Day 2 之后实际做的事）

上次日志记到 Day 2 结束（M1 达成），但之后其实又推进了三块，只是没写日志。现状：

**`@tool` 装饰器（模块 3 补完）**
- 实现 `mini_agno/tools/decorator.py`：`tool(func)` → 包一层 `Function(entrypoint=func)` 返回
- 这样 `@tool` 装饰普通函数即可注册工具（之前只能手动 `Function(entrypoint=...)`）
- 测试 `test_decorator.py` 通过

**结构化输出（模块 5 主体）**
- `Agent` 加 `output_schema: type | None` 字段
- `run()` 收尾分支：`else` 分支里 `if output_schema: return output_schema.model_validate_json(resp.content)`，否则返回 `resp.content`
- 测试 `test_structured_output.py`：MockModel 返回 `Weather` 的 JSON → agent 还原成 `Weather` 实例。通过
- **注意**：现在是「靠 prompt 让模型自己吐符合 schema 的 JSON，然后客户端 parse」。还没用上 OpenAI 原生的 `response_format`/structured output 功能（那是接真模型时该升级的点）

**接真模型（模块 5 前置/模块 2 补完）**
- 新增 `mini_agno/models/openai_model.py`（用 openai SDK，默认接 deepseek-chat，base_url 指向 deepseek）
- `pyproject.toml` 加 `openai>=3.0.0` 依赖（已 `uv sync`，uv.lock 已更新）
- `invoke()` **还没实现**——只写了签名和注释，转换逻辑待写

**Day 2 待办完成情况**
- [x] tool 结果消息加 `tool_call_id` 字段（Message 已有 `tool_call_id`，agent.py 已正确回链 `tool_call_id=tool_call.id`）✓
- [ ] 接真模型时的消息协议转换（openai_model.invoke 待写）

### 当前 mini-agno 状态（16 个测试全绿）
- `models/`：message.py（含 tool_call_id）、base.py（Model ABC）、mock.py（MockModel）、openai_model.py（骨架，invoke 未实现）
- `tools/`：function.py（Function/FunctionCall）、decorator.py（@tool）
- `agent.py`：ReAct 主循环 + output_schema 结构化输出分支
- `tests/`：16 个全过

### Day 3 收尾要做的（模块 5 真正完成）
1. **写完 `OpenAIModel.invoke()`**：mini-agno 的 `Message` 列表 ↔ OpenAI SDK 的 `dict` 列表互转，调 `client.chat.completions.create(...)`，把返回翻回 `ModelResponse`
2. **接真模型跑通一次**：需要 `DEEPSEEK_API_KEY`（现在 shell 里没设）。用 `.env` 或 `export`
3. （可选升级）结构化输出用真模型时，改用 OpenAI 原生的 `response_format` 而非纯靠 prompt

---

## 2026-08-14（Day 4，模块 5 收官）

### 完成的事

**`OpenAIModel.invoke()` 写完 + 真模型端到端打通 🎯**
- 写完 `_message_to_openai_dict()`（Message → OpenAI dict，按 role 分流：user/assistant/tool 三类，`content` 为 None 不放 key）
- 写完 `invoke()`：出站转 dict → 组 kwargs → `client.chat.completions.create(**kwargs)` → 入站把 `choice.message` 翻回 `ModelResponse`
- **5 项离线 mock 自测全过**：tool 结果消息 / assistant 带 tool_calls / 普通 user 消息 / invoke 纯文本 / invoke 带 tool_calls 入站翻译（arguments JSON 字符串 → dict）
- **真 deepseek API 打通**（export DEEPSEEK_API_KEY 后 `Agent(model=OpenAIModel()).run(...)` 真能回话）

### Day 4 学到的关键点

**概念：`tools`（参数）vs messages 里的 `tool_calls`——最易混的一对**
- `tools` = **工具清单/能力声明**（"我有哪些工具"），每次调模型**全量传**，**从不在 messages 里**
- messages 里的 `tool_calls` = **历史动作记录**（"模型上轮决定调了啥"），模型自己生成，append 进历史
- messages 里 `role="tool"` + `tool_call_id` = **历史结果**（"工具执行返回了啥"），用 `tool_call_id` 和上面的动作配对（≈ correlationId）
- 为什么要每次重传 `tools`：**模型无状态**，每次调用独立，不记得上一轮的工具清单

**坑 & 易错点**
- `arguments` 出站用 `json.dumps`（dict→JSON 字符串），入站用 `json.loads`（JSON 字符串→dict）——**方向必须对称**，搞反就错
- OpenAI tool_calls 元素必须有 `"type": "function"` 字段（固定字符串，不是变量）
- `content=None` 的消息别放 `"content"` 这个 key（很多厂商对 `content:null` 报错），按需加
- **测试时构造 OpenAIModel 要塞假 key**：`OpenAI()` 在 `__init__` 就校验 key，key 为空直接抛 `OpenAIError`，连 `invoke()` 都走不到——mock 测时记得 `DEEPSEEK_API_KEY="fake" `uv run ...`
- **MockModel 不读 messages**，会掩盖消息协议错误（Day 2 已记）；接真模型后才暴露出 `_message_to_openai_dict` 的嵌套 bug——真模型是验证消息协议的最佳试金石
- **mock MagicMock 时 `MagicMock(name='add')` 会被当实例名吞掉**，要用 `configure_mock(name='add')` 或直接构造 message 属性

### 当前 mini-agno 状态
- `models/`：message.py、base.py（Model ABC）、mock.py（MockModel）、**openai_model.py（invoke 完整，真模型已通）**
- `tools/`：function.py（Function/FunctionCall）、decorator.py（@tool）
- `agent.py`：ReAct 主循环 + output_schema 结构化输出分支
- `tests/`：16 个全过
- **模块 5 完成**：结构化输出 + 真模型接入

### 待办（记着）
- [x] 删草稿 `mini_agno/t.py`（已删）
- [x] 把 openai_model 的 mock 自测固化成 `tests/test_openai_model.py`（已完成）
- [ ]（可选升级）结构化输出改用 OpenAI 原生 `response_format`，而非纯靠 prompt 让模型吐 JSON

---

## 2026-08-14（Day 4 晚间续，模块 6 上半场）

> 补记：Day 4 收官后又推进了模块 6 的"会话"半场（两笔 commit），当天没写日志。

### 完成的事

**模块 6 Step1（commit `c457715`）· 多轮会话记忆**
- Agent 加 `messages` 字段（`field(default_factory=list)`），run() 累积历史，assistant 最终回答也进历史
- 新增 `tests/test_session.py` 初版：历史累积 + 可变默认值不共享
- 真模型多轮验证脚本 `examples/run_session_demo.py`（手动跑，不进 pytest）
- 新增 `docs/knowledge.md`（模块 0-5 知识手册）
- pyproject 加 build-system(hatchling)：uv 改为 editable 安装

**模块 6 Step2（commit `a2f5439`）· 抽离 Session，Agent 无状态化**
- 新增 `mini_agno/session.py`：`Session(session_id, messages)` 独立持有历史
- Agent 无状态化：`sessions: dict[str, Session]` + `_get_or_create_session()`，`run(user_message, session_id="default")`
- 测试三个：历史累积 / 默认值不共享 / 多会话隔离（s1、s2 互不串话）

### 学到的关键点
- **Agent 无状态 + Session 持状态 + 按 session_id 隔离**——对应 agno 的设计（行为与状态分离）
- `=[]` 可变默认值共享坑在实战中防住了：`field(default_factory=list)`，且有回归测试盯着
- Session History 只是"会话内重放原文"，换 session_id 就忘；跨会话记得要靠 Memory（模块 7）——三种"记得"的分界见 Obsidian 笔记《Agent定义》

### 当前 mini-agno 状态
- 24 个测试全绿；模块 6 "会话"半场完成，"持久化"（Step3）未开始

---

## 2026-08-19~20（Day 5，笔记体系整理，无代码）

### 完成的事
- mini-agno 推到 GitHub（`huangdejie/mini_agno`），只留 main 分支
- 知识库分工落地：**日志（本文件）记过程，概念笔记记结论**（家在 Obsidian `30-knowledge/ai/`）
- Obsidian 整理出《Agent定义》（含 Memory 在流程中的位置）+《mini_agno学习》（ReAct 主循环 / 消息协议 / 工具系统 / 模型可插拔）

### 整理笔记时新学到的点
- **防腐层（ACL）吃透了**：`openai_model.py` 整个文件就是防腐层，出站/入站两道关卡；检验标准 = "厂商怪癖被几个文件知道"（mini-agno 是 1 个，满分）
- Model 层翻译的不只是工具信息，是**整份请求 + 整份响应**：出站还有调用参数 / response_format，入站还有 usage / finish_reason / reasoning_content——**这几个 mini-agno 都没接，待办**
- 字段位置三层：usage 在响应顶层（`resp.usage`）、finish_reason 在 `choices[0]`、content 在 `choices[0].message`
- 实测 deepseek：280 个 prompt token 里 256 个缓存命中（前缀缓存，历史全量重传有缓存兜底）；`prompt_cache_hit_tokens` 是 DeepSeek 私有字段——印证"厂商差异必须在 Model 层抹平"
- 参数描述业界做法：载体统一是 JSON Schema 的 description 字段；生产方式 = docstring Args 解析（agno 用 docstring_parser，`tools/function.py:1028`）或 Pydantic `Field(description=...)`
- 工具返回值：JSON 化塞 role=tool 消息；返回结构说明写 docstring Returns 段（随 description 每轮自动送达）；**输入要 schema（模型生成），输出不要（模型只读）**

---

## 明天从哪开始

**模块 6 Step3 · 持久化（模块 6 下半场）**
- 读 agno：`db/base.py:180-232`（get_session / upsert_session / delete_session）+ `db/sqlite/sqlite.py` 怎么建表——按需 grep，别通读
- 实现：`BaseDb(ABC)`（get_session / upsert_session 两个抽象方法）+ `SqliteDb`（标准库 sqlite3，零依赖）+ Agent 挂 `db` 字段，run 前 load、run 后写回
- **验收（灵魂）**：两个独立进程共享同一 db 文件，第一个 `run("我叫张三")`，第二个 `run("我叫什么")` 能答对——"重启还记得"才是持久化
- 两个设计决策：什么时候写库（每条消息后 vs run 结束）？存整条 Session JSON 还是按消息存行？（先选简单的）
- 穿插小待办：usage/finish_reason 接进 ModelResponse；给 Function 加 docstring Args 解析（笔记标了"待实践"）

## 环境备忘

```bash
cd /Users/huangdj/code/mine/mini-agno   # 进项目
uv run pytest                            # 跑所有测试
uv run pytest tests/test_agent.py        # 跑单个文件
uv run python -c "..."                   # 跑小段代码验证
```
