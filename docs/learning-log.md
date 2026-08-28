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

## 2026-08-20（Day 6，模块 6 Step3 收官）

### 完成的事

**模块 6 Step3 · 持久化层落地**
- 新增 `mini_agno/db/base.py`：`BaseDb(ABC)`，两个抽象方法 `get_session(session_id)` / `upsert_session(session)`
- 新增 `mini_agno/db/sqlite_db.py`：`SqliteDb(db_file)`，用标准库 `sqlite3` 建 session 表，整行 JSON 存一个 Session
- `Agent` 加 `db: BaseDb | None = None`，走 cache-aside：内存 `sessions` 是缓存，db 是 source of truth；run 前 load，run 后 upsert
- `Session` 加 `__post_init__` 防御：从 db 读回的 dict 列表自动还原成 `Message` 对象
- 新增 `tests/test_persistence.py`：两个 Agent 实例共享同一 db 文件，第二个实例能读到第一个的对话历史
- 新增 `examples/run_persist_demo.py`：**跨进程验收**——两次独立 python 进程跑同一脚本，第二次能接续第一次的历史
- 更新 `docs/architecture.md`：架构图加入持久化层（db/base.py + db/sqlite_db.py）
- 更新 `.gitignore`：忽略 `*.db` 和 `db/` 目录，避免运行产物污染仓库

### 学到的关键点

**持久化的验收标准**："两个 Agent 实例共享 db 文件能通"只是单进程验证；**跨进程重启还记得**才是持久化的真正分界线。`run_persist_demo.py` 跑两次验证了这个。

**抽象的价值再次验证**：`Agent` 只依赖 `BaseDb` 抽象，不 import `SqliteDb`；换 Postgres 时只需新增一个 `PostgresDb` 子类，Agent 一行不改。这和 `Model(ABC)` 的可插拔是同一个设计思想。

**事务边界**：每个 db 方法自己用 `with conn:` 包事务（成功 commit / 异常 rollback），和 agno 的 `with self.Session() as sess, sess.begin()` 同构。

**存储粒度为什么选"整行 Session JSON"**：agno 也是一行一个 session。理由不是"数据量少"，而是读写模式——ReAct 每次要全量历史，没有分页/单条消息查询需求；session 还包含 agent 状态、summary 等会话级数据，本来就该一起存。

**代码洁癖点**：
- 别让具体实现（`SqliteDb`）漏进 `Agent`——通过 `db: BaseDb | None` 注入
- `BaseDb` 只读/写，不创建 session；创建是 Agent 的应用层决策
- JSON 反序列化必须还原成 `Message` 对象，不能传 dict 列表给主循环

### 当前 mini-agno 状态
- 25 个测试全绿（24 老 + 1 新持久化测试）
- 模块 6 全部完成：会话（内存）+ 持久化（SQLite）
- 已推送到 GitHub：`dc0cffc`

---

## 2026-08-23（Day 7，模块 7 收官）

### 完成的事

**模块 7 · 记忆系统（跨 session）**
- 新增 `mini_agno/memory/manager.py`：`MemoryManager(db)`，封装 `get_memories(user_id)` / `add_memories(user_id, memories)`
- 扩展 `mini_agno/db/base.py`：加 `get_memories` / `add_memory` 抽象方法
- 扩展 `mini_agno/db/sqlite_db.py`：新增 `memory` 表（memory_id/user_id/memory/created_at），实现按 user_id 存取
- `Agent` 加 `memory_manager: MemoryManager | None = None` 和 `run(..., user_id="default")` 参数
- run 前注入：把该 user 的记忆拼成 system 消息塞 messages 最前面（只在 session 为空时注入，避免重复）
- run 后提炼：把本轮 user/tool 消息传给模型，提取持久事实，去重后存入 memory 表
- 新增 `tests/test_memory.py`：同一 user_id 跨 session 共享记忆，不同 user_id 隔离——26 个测试全绿
- 新增 `examples/run_memory.py`：真模型手动验证脚本（不进 pytest）

### 学到的关键点

**Session 和 Memory 是两层记忆**：Session 是“短期记忆”（按 session_id，存对话原文）；Memory 是“长期记忆”（按 user_id，存提炼事实）。两者正交：Session 负责会话内上下文，Memory 负责跨会话用户画像。

**注入位置**：把记忆拼成 `role="system"` 消息放在 messages 最前面，主模型自然把它当已知事实用。

**提炼时机**：每次 `run()` 结束后提炼，素材是本轮的 user/tool 消息（不含 assistant 自己的话，避免把模型总结误当用户事实）。不是等整个 session 结束再提炼——否则中间 run 看不到新事实。

**记忆爆炸的防御**：db 层做了两件事——
- 去重：完全相同文本不重复插入
- 上限：每个 user 最多保留 50 条，超过删最旧的
语义相似度更新（agno 的做法）先不做，复杂度太高。

**提炼时不要传 tools**：`_extract_facts` 调用模型时不传 `tools`，否则模型可能又去调工具。这是模块 7 最大的坑。

### 当前 mini-agno 状态
- 26 个测试全绿
- 模块 7 完成：跨 session 记忆
- 已具备：短期记忆（Session）+ 长期记忆（Memory）+ 持久化（SQLite）

---

## 2026-08-28（Day 8，模块 8 收官）

### 完成的事

**模块 8 · RAG 知识库**
- 新增 `mini_agno/knowledge/knowledge.py`：`Knowledge(documents)`，L1 简化版——字符串匹配 + 顺序兜底
- `Agent` 加 `knowledge: Knowledge | None = None`，run 前用用户问题做 `knowledge.search()`，把检索结果拼成 system 消息注入
- 注入逻辑和 Memory 一致：只在 session 为空时注入，避免同一 session 内重复
- 新增 `tests/test_knowledge.py`：Knowledge 检索测试 + Agent 接入测试
- 28 个测试全绿

### 学到的关键点

**RAG 的三层能力**：
- L1（字符串匹配）：理解"文档 → 检索 → 塞进 prompt → 回答"闭环
- L2（TF-IDF/余弦相似度）：理解"语义相近"的检索
- L3（embedding + 向量库）：生产级实现

**RAG 和 Memory 的异同**：
- 相同点：都是给模型塞上下文
- 不同点：Memory 按 user_id 全量注入（条数少），Knowledge 按 query 检索注入（文档大）

**Knowledge 注入位置**：放在 messages 最前面的 system 消息里，和 Memory 注入方式一致。

**L1 的局限**：只能匹配 query 字面出现的文档，无法理解同义词。比如问"年假"能匹配"年假"，但问"每年能休几天"就匹配不到。

### 当前 mini-agno 状态
- 28 个测试全绿
- 模块 8 完成：L1 RAG

---

## 明天从哪开始

**模块 9 · 多智能体（Team）**
- 让多个 Agent 分工协作完成一个任务
- 读 agno：`team/team.py` + `team/mode.py`
- 核心模式：Sequential（顺序）/ Router（路由）/ Parallel（并行）
- 验收：两个 agent（一个总结、一个润色）串起来处理输入
- mini 版先实现 Sequential 模式，Team 持有一个 `list[Agent]`，按顺序调用并把前一个输出传给后一个

### 待办（记着）
- [ ] RAG L2/L3 升级（TF-IDF → embedding + 向量库）
- [ ]（可选升级）结构化输出改用 OpenAI 原生 `response_format`
- [ ]（可选）usage / finish_reason 接进 ModelResponse
- [ ]（可选）给 `Function` 加 docstring `Args:` 解析（笔记里标了"待实践"）
- [ ]（可选升级）Memory 语义相似度更新 / 按 topic 分类
- 设计决策：Knowledge 和 Memory 很像但归属不同——Memory 按 user_id（用户画像），Knowledge 按知识库名（公开文档），谁都能查

### 待办（记着）
- [ ]（可选升级）结构化输出改用 OpenAI 原生 `response_format`
- [ ]（可选）usage / finish_reason 接进 ModelResponse
- [ ]（可选）给 `Function` 加 docstring `Args:` 解析（笔记里标了"待实践"）
- [ ]（可选升级）Memory 语义相似度更新 / 按 topic 分类
