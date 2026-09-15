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
| 6 | 会话与持久化 | ✅ 完成 | 2026-08-20 |
| 7 | 记忆系统 | ✅ 完成 | 2026-08-23 |
| 8 | RAG 知识库 | ✅ 完成 | 2026-08-28 |
| 9 | 多智能体（Team） | ✅ 完成 | 2026-09-09 |
| 10 | 工作流（Workflow） | ✅ 完成 | 2026-09-09 |
| 11 | 运行时 API 化（里程碑 M4） | ✅ 完成 | 2026-09-10 |
| 12 | 流式输出 + async（计划外首推） | ✅ 完成 | 2026-09-10~14 |
| 13 | MCP 协议（计划外·工具生态） | ✅ 完成 | 2026-09-15 |
| 14 | eval（计划外·质量度量） | ✅ 完成 | 2026-09-15 |

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

## 2026-09-09（Day 7，模块 9 收官）

### 完成的事

**模块 9 · 多智能体（Team）**
- `Agent` 加 `name` + `description` + `instructions` 三个字段（都可选，不破坏现有调用处）
- `Function.__post_init__` 从"无条件覆盖"改成"**没显式传才自动提取**"——支持手动指定 name/description
- `team.py` 支持两种模式并存：
  - `sequential`（之前已有）：代码写死 A→B→C 顺序链
  - `coordinate`（新增）：Team 在 `__post_init__` 里现造一个 Leader Agent，把"调用下属"做成 Leader 手里的 `delegate_task_to_member(member_id, task)` 工具
- `_validate_coordinate` 校验：leader_model 非空、成员都有 name+description、name 不重名
- `_build_leader_instructions`：把成员的 name+description 拼进 Leader 的 system prompt
- `leader: Agent = field(init=False)`，coordinate 时才造
- 真模型端到端验收 `examples/run_team.py`：temperatureAgent（带 query_temperature 工具）+ analysisAgent，Leader 自主派活
- 修了两个过期测试断言（见下坑点），31 个测试全绿

### 学到的关键点

**agno 的 TeamMode 是四种，且没有"顺序链"**：`coordinate`（默认，主管派活）/ `route`（路由直通）/ `broadcast`（同一任务群发）/ `tasks`（任务清单驱动）。我一开始凭印象说的 Sequential/Router/Parallel 是通用编排概念，不是 agno 的实现——**agno 的 Team 全是"Leader-下属"结构，顺序不是写死的链，是 Leader 现场决定的**。mini 版先做的 sequential 在 agno 里根本没有对应模式。

**coordinate 的本质：Team 不干活，只是造了个 Leader Agent**。Leader 是普通 Agent，跑标准 ReAct 循环；Team 唯一做的是给它塞一件 `delegate_task_to_member` 工具 + 一段列出下属的 system prompt。**Agent 调工具 → 工具里又是一个 Agent.run()——这就是"递归 Agent"**。编排逻辑由 Leader 的 LLM 决定，不是代码。

**下属间上下文全靠 Leader 传话（最关键认知）**：每个下属是独立 Agent、独立 session，互相看不到对话。`delegate_task_to_member` 返回字符串到 Leader 的 messages，Leader 第二次派活时必须**把上一个人的结果写进 task 参数**里（如"温度是45.5度，请分析"）。这和 sequential（数据自动流向下一个）是本质区别。真模型验收时 Leader 做到了——分析建议基于真实查到的温度，说明上下文传递真的发生了。

**description 是给 Leader 看的"岗位职责"**：Leader 派活的唯一依据就是 system prompt 里的成员名单（name+description）。没有 description，Leader 只能靠名字瞎猜。职责要分清：description = "这个成员擅长什么"（一句话，进 Leader prompt）；具体业务规则该放成员自己的 instructions，别塞 description（否则 Leader prompt 又臭又长，且 Leader 可能自己去执行规则而不是派活）。

### 坑 & 易错点

- **`'Function' object is not iterable`**：`Agent.tools` 声明是 `list[Function]`，但 Python dataclass **运行时不强制类型检查**——误传单个 `Function` 也照收，直到 `for t in self.tools` 才爆。错误延迟到使用点才出现，不在创建点。**Java 是编译期挡住，Python 是运行期才炸**，类型注解只是提示不挡错。
- **测试断言过期**：改完 `__post_init__` 校验顺序和报错文案后，旧测试还断言"Only sequential mode is supported for now"。**改实现要同步改测试**。
- **`try/except` 写测试是假阳性**：没抛异常会静默通过。该用 `pytest.raises(ValueError, match="...")`——`match` 是正则子串匹配，比 `str(e) == "..."` 抗文案微调，且不抛异常会明确失败。

### 当前 mini-agno 状态
- 31 个测试全绿
- 模块 9 完成：sequential + coordinate 两种模式
- 已具备：单 Agent 全部能力 + 多 Agent 协作（顺序链 + Leader 委派）

---

## 2026-09-09（Day 7 续，模块 10 收官）

### 完成的事

**模块 10 · 工作流（Workflow）**
- 新增 `mini_agno/workflow/`：`step.py`（Step）+ `workflow.py`（Workflow 顺序管道）+ `condition.py`（Condition 条件分支）
- `Step`：统一包装两种执行者——`agent: Agent | None` 或 `func: Callable | None`，`__post_init__` 校验互斥（都传/都不传报错），name 缺省取 `func.__name__` 或 `agent.name`
- `Workflow(steps).run(input)`：朴素 for 循环，`current = step.run(current)` 数据下流——和 sequential Team 同构（故意的）
- `Condition(Step)`：**继承 Step** 实现组合模式；`run()` 里算 condition → 走 then/else 分支 → 分支内数据同样下流 → 返回末步输出；空分支 = input 原样透传
- 测试方法论三连改：补 assert（之前纯 print 永远过）/ MockModel 替真模型（离线可复现）/ 60 行新闻挪成模块级常量 `NEWS_TEXT`
- then/else 两条分支都有精确断言；33 个测试全绿

### 学到的关键点

**Workflow vs Team 的本质**：Team 是"LLM 现场决定怎么协作"（自主编排，流程运行期产生）；Workflow 是"开发者提前写死流程"（确定性编排，流程声明期固定）。Java 类比：Workflow ≈ Spring Batch/Camunda BPMN（声明步骤图，引擎照图执行）；Team ≈ 给项目经理配团队（说目标，他自己派活）。**之前做的 sequential Team 其实是 Workflow 的活**——agno 里顺序链（`Steps`）归 Workflow 管，Team 管自主协作，A2 并存的对照组现在兑现了。

**agno Workflow 是小型流程编排 DSL**：`Steps`（顺序）/ `Parallel`（并行）/ `Condition`（if）/ `Router`（switch）/ `Loop`（循环）+ `Step` 可包 Agent/Team/普通函数/**嵌套 Workflow**（`step.py:181-190` 四个 Optional 字段）。确定性骨架 + 局部自主（某步嵌 Team）是生产常见形态。

**组合模式：Condition 也是 Step**。Condition 继承 Step、实现同样的 `run(input) -> str`，所以能直接进 `Workflow.steps` 列表，**Workflow 主循环一行不用改**。分支内部再走一遍"数据下流" for 循环，和主循环同构。选择路由的 `condition` 是普通 Python 函数（确定性判断），不是 LLM——LLM 判断路由是 Team Router 的活，这是两者的分界。

**@override 装饰器**（Python 3.12 `typing.override`）：≈ Java `@Override`，mypy 能查覆写错误。

**覆盖 `__post_init__` = 全盘接管初始化**：Condition 裸 `pass` 覆盖 Step 的 `__post_init__` 后，父类的 name 缺省逻辑也没了（所以 Condition 必须显式传 name）——不是"只跳过互斥校验"。后来补了自己的三字段校验。

### 坑 & 易错点

- **纯 print 没断言 = 假测试**：`test_seq_workflow` 第一版只 `print(resp)`，永远通过。改实现时这种测试不会红。
- **弱断言的漏洞**：`assert "燃油" in resp`——如果 Workflow 丢了 step2 只返回原文新闻，里面也有"燃油"，照样绿。**精确相等才能钉死"最终输出=最后一步输出"**。期望值要写"应该是什么"的又一变体。
- **条件分支要两条路都测**：只测 then 路径，走错分支不红。else 路径补了第二段 run + 精确断言。
- **真模型别进 pytest**：没 key 就挂、花钱、慢、不可复现。pytest 用 MockModel，真模型放 `examples/` 手动跑（沿用 test_memory 的约定）。
- **测试数据内联 60 行把逻辑淹没**：挪成模块级常量；多测试共用再升级 pytest fixture（`@pytest.fixture` ≈ 依赖注入，按参数名匹配注入）。

### 当前 mini-agno 状态
- 33 个测试全绿
- 模块 10 完成：Step + Workflow（顺序管道）+ Condition（条件分支）
- 已具备：单 Agent + 多 Agent（Team）+ 确定性流程编排（Workflow）——三个执行抽象齐了

---

## 2026-09-10（Day 8，模块 11 收官 · M4 达成 🎉）

### 完成的事

**模块 11 · 运行时 API 化（里程碑 M4，12 模块计划收官）**
- 新增 `mini_agno/api.py`（17 行）：Pydantic DTO（RunRequest/RunResponse）+ 模块级 Agent 单例 + `POST /chat` 端点
- 依赖：fastapi + uvicorn + pytest-httpx
- curl 端到端验收通过：uvicorn 起服务，同 session 两问记住"张三"，换 session 隔离，缺字段 body 自动 422
- 离线 TestClient 测试决定不补（记待办）

### 学到的关键点

**库 vs 服务**：前 10 个模块造的是 library（import 后进程内调用），模块 11 变成 service（网络远程调用）。Agent 主循环一行不改，写的只是**协议边界**：HTTP JSON 进 → 调 Agent → JSON 出。Java 类比：api.py = @RestController + DTO，uvicorn = 内嵌 Tomcat（ASGI），FastAPI 路由装饰器 = @PostMapping。

**Agent 模块级单例是铁律**：agent 在模块加载时创建一次、所有请求复用。每个请求 new 一个 = 每次重建会话缓存，状态和性能全乱——这就是 agno CLAUDE.md "Never create agents in loops / 复用 agent" 规矩的由来，这次亲手写服务层才真正理解。

**HTTP 无状态，会话连续性全靠 session_id 穿针引线**：每个请求互相独立，"记得你"不是 HTTP 的能力，是请求体里带着 session_id、服务端用它找回 Session（模块 6 的伏笔在 API 层兑现）。session_id 就是 correlationId。

**Pydantic = 白送的 Bean Validation**：一行校验代码没写，缺 message 字段的 body 自动 422 + 错误详情。DTO 定义即校验规则。

**agno 的服务化层叫 AgentOS**（`agno.os`）：把 FastAPI 包了一层，agent/team/workflow 挂上去自动获得 /agents /teams /workflows 目录 + run 端点 + /config 发现文档。mini 版裸写 FastAPI 学的是同一机制。

### 当前 mini-agno 状态
- 33 个测试全绿（api 层无测试）
- **模块 11 完成，M4 达成——12 模块造轮子计划全部完成** 🎉
- mini-agno 全貌：数据模型 → Model 抽象 → 工具 → ReAct 主循环 → 结构化输出 → Session/持久化 → Memory → RAG(L1) → Team(sequential+coordinate) → Workflow(Step+Condition) → HTTP API

---

## 毕业后方向（12 模块计划外，按建议优先级）

1. **流式输出 + async（首推）**：mini-agno 唯一的结构性短板——所有 run() 都阻塞到整段生成完；token 本来就是流式产出的，打字机效果/取消/并发都建立在这个认知上。也补上"所有公共方法要有 async 变体"的欠债。MCP client、向量库查询都是 async 的，这是后续一切的地基
2. **MCP 协议**：工具生态的 USB-C，接外部工具服务器，工具不用全自己写
3. **RAG L2/L3**：TF-IDF → embedding + 向量库（pgvector），从字符串匹配到语义检索的质变
4. **eval（怎么测 LLM 应用）**：agent_as_judge——传统单测断言对不上非确定性输出，这是 LLM 工程师的分水岭
5. agno 仓库没碰过的地图：guardrails/（PII 脱敏、prompt 注入防护）、reasoning/（思考模型）、approval/（HITL 人审）、scheduler/ + job_queue/（定时/异步）

### 待办（记着）
- [ ] api 层 TestClient 离线测试（本轮跳过，api 改动时补）
- [ ] （模块10遗留）`examples/run_workflow.py` 真模型版没跑
- [ ] （模块10遗留）then/else 拆成两个测试函数（一个测试一个行为）
- [ ] Loop / Parallel / Router 三个控制流原语（agno 有，mini 版没做）
- [ ] Step 支持 team / 嵌套 workflow 执行者
- [ ] coordinate 进阶：`route` / `broadcast` / `tasks` 三种模式
- [ ] description vs instructions 职责：把 run_team.py 里 analysis_agent 的长 description 拆成"短 description + 长 instructions"
- [ ] RAG L2/L3 升级（TF-IDF → embedding + 向量库）
- [ ]（可选升级）结构化输出改用 OpenAI 原生 `response_format`
- [ ]（可选）usage / finish_reason 接进 ModelResponse
- [ ]（可选）给 `Function` 加 docstring `Args:` 解析（笔记里标了"待实践"）
- [ ]（可选升级）Memory 语义相似度更新 / 按 topic 分类
- 设计决策：Knowledge 和 Memory 很像但归属不同——Memory 按 user_id（用户画像），Knowledge 按知识库名（公开文档），谁都能查

---

## 2026-09-10 ~ 09-14（Day 8~11，流式模块 Step 1-3）

> 毕业后首推方向开工：流式输出 + async。四步走：Step1 async 地基 → Step2 Model 层流式 → Step3 Agent 流式主循环 → Step4 SSE 端点（未完）。全程跨度最长、概念密度最高的一程。

### 完成的事

**Step 1（09-10）· async 地基**
- `OpenAIModel`：`AsyncOpenAI` 客户端 + `ainvoke()`；抽取 `_build_openai_messages`/`_parse_response` 供同步/异步共用——同步异步只差中间"调 SDK"一行，出站/入站翻译完全复用（防腐层红利）
- `Agent.arun()`：async 版主循环；抽取 `_prepare_message`/`_execute_tool_calls` 供 run/arun 共用；`_aextract_facts` 异步提炼
- `Model.ainvoke` 标 `@abstractmethod`（契约的牙齿），MockModel.ainvoke 复用 invoke 剧本
- 验收：并发 3 个 arun 0.8s（串行需 2s+）

**Step 2（09-11）· Model 层流式**
- 探针 `see_stream_vs_not.py` 四段对照：非流式一次到位 vs 流式碎片；**工具轮 arguments 被剁成 14 片、id/name 只在首片、双工具 index 分桶、平铺拼接把两个 JSON 焊死**——全部亲眼实证
- `ToolCallAccumulator`：按 index 分桶拼装碎片；6 个单测含突变验证
- `OpenAIModel.ainvoke_stream`：content 碎片即到即 yield，tool_calls 攒齐后一次性 yield（`if calls` 守卫）
- `MockModel.ainvoke_stream`：content 切片吐 + arguments 剁两半再经 accumulator 拼回，剁碎与拼装 mock 内闭环，离线复现线上线况
- `Model.ainvoke_stream` 进 ABC

**Step 3（09-12~14）· Agent 流式主循环**
- `Agent.arun_stream`：while + async for 嵌套；content 碎片**双轨**（攒整段进历史 + 转发碎片给上层）；tool_calls 到手执行工具进下一轮；收尾 upsert + 异步 memory 提炼
- 五行评审修正：`full_content` 每轮清零（自言自语不焊进终答）/ `yield chunk` 信封不拆 / `await _aextract_facts` / `AsyncIterator[ModelResponse]` 注解 / output_schema 显式 raise
- `tests/test_agent_stream.py`：五断言 + 突变校验（挪 full_content 出循环必红）
- 资源两级：`async with stream`（每调用级）+ `Model.aclose()`（应用级，Step 4 FastAPI lifespan 上岗）
- 真模型验收：双工具查询 → 拿真实温湿度流式输出分析

### 学到的关键点

**async 心智模型**：`await` 等的是这一次调用的结果，不等的是这台机器上其他所有活。收益不在单请求变快，在同线程能同时等 N 个 IO。asyncio.sleep（让出）vs time.sleep（焊死线程）；单线程协作式调度 = 无数据竞争 ≠ 无逻辑乱序（同 session 并发 arun 历史被搅乱，防御 = 并发流各用各的 session_id）。

**Python async 的机制细节**：`async def`+函数体有 `yield` = 异步生成器，**不能 await**（TypeError），只能 `async for`——和返回 coroutine 的 `ainvoke` 是两个家族；`await` 只等 HTTP 响应头不等 body；生成器调用时一行不跑，首次迭代才开工（惰性）；签名注解在模块加载期求值（缺 import 全测试文件收集失败）。

**流式线况（探针实证）**：content 碎片独立可用、即到即发；tool_calls 的 arguments 是剁碎的 JSON 片、只有首片带 id/name、按 index 分桶是唯一活路（平铺拼接在双工具时焊死两个 JSON，排队到达都救不了）；usage 包 choices 为空要防；工具轮的 content 是可选自言自语（finish_reason 区分轮型：stop=文本轮，tool_calls=工具轮）。`delta` 每包只装增量。

**协议设计三连问（自己推出来的）**：① 为什么帧是对象不是 str——交付物有几种可能才需要信封（流式帧 N 种且会增长，str 装不下"类型"）；② 为什么 run/arun 返回裸值——终答只有一种可能，歧义为零不需要信封（但模型→Agent 内部仍用信封区分文本/工具轮）；③ Agent 借 ModelResponse 是务实简化（形状刚好够用），agno 真实设计是 Agent 自己的事件族（RunContentEvent），升级触发点=要发工具状态帧/usage 的那天。**帧需要自报身份，成品不需要**。

**yield**：return 交值函数死亡，yield 交值冻结原地等唤醒；生成器=编译器替你写 Iterator 状态机（Java 手写 hasNext/next 的痛，C# 有 yield return）；`for x in` = next 舞蹈自动化。

**资源所有权**：stream 活一次调用（async with，ResultSet）；aclient 活一个应用（aclose，DataSource/连接池）；把 aclose 塞进每次调用 = 第二次调用必炸（两次实证）。同步客户端也要关（aclose 里补 `self.client.close()`）。

### 坑 & 易错点

- **假测试三连**：纯 print 无断言 / 收集到列表就 return 无断言 / 剧本第二幕没被消费——"代码跑完了"≠"代码对了"，**写完自检：故意改坏实现，测试必须红**（突变校验法）
- **单样本会骗，包括老师**：我用一次 /tmp 实验断言"凶手是 aclose"，被用户复现打脸；二分定位每次结论都要可复现验证。最小复现（bare_repro.py）是排查收尾的黄金动作
- **抽取重构三坑**：原处变量名带进新方法（resp NameError）/ 搬代码块丢缩进（knowledge 注入）/ 类型注解未 import
- **批量文本操作的爆炸半径**：一次 sed 想改 arun_stream 的 while，把 run/arun 的同名 while 也炸了——三个 `while True` 长得一模一样，sed 分不清
- **栈噪音止损**：httpcore2 teardown 时"generator didn't stop after athrow()"，非确定性、与代码无关（bare_repro 实证）、升级 openai 3.13.0 后变罕见——**四组实验证明到极限后接受+记录，不再追**。try/except 拦不住它（不经过用户调用栈），且吞真实错误
- **屏幕正常 ≠ 历史干净**：流式观感里自言自语和终答连着流是正常的；full_content 污染只发生在 session 历史，只有断言历史的测试能抓住

### 当前 mini-agno 状态
- 40 个测试全绿
- 流式模块 Step 1-3 完成：ainvoke/arun + ainvoke_stream/arun_stream 全链路，openai 升级 3.13.0
- 剩 Step 4：FastAPI SSE 端点（curl -N 看打字机 + aclose 在 lifespan 上岗）

---

## 下次从哪开始

**流式模块 Step 4 · SSE 端点（最后一站）**
- `api.py` 加 `POST /chat/stream`：async def + StreamingResponse(media_type="text/event-stream")
- 每帧 `f"data: {json.dumps(...)}\n\n"`（两个换行是协议，少一个帧不结束）
- curl -N 验收打字机；TestClient 离线测（iter_lines）
- lifespan shutdown 里 `await agent.model.aclose()`（aclose 正式上岗）

### 待办（记着）
- [ ] demo run_stream.py 里的 try/except 会吞真实错误（保留是自己的决定，排查时先看它）
- [ ] 将来要工具状态帧时：Agent 造自己的事件族（RunContentEvent/ToolRunEvent），不再借 ModelResponse
- [ ] examples/bare_repro.py 留作排查记录（含在本次提交）

---

## 2026-09-14（Day 11 续，Step 4 收官 · 流式模块全剧终 🎉）

### 完成的事

**Step 4 · SSE 端点**
- `api.py`：`POST /chat_stream`（async def + StreamingResponse，`media_type="text/event-stream"`），消费 `agent.arun_stream`，每帧包成 `data: {"content": "..."}\n\n`（`ensure_ascii=False` 保中文可读）
- `/chat`（同步非流式）与 `/chat_stream`（流式）并存——同一个 agent 单例两种交付形态
- **lifespan 正式上岗**：`FastAPI(lifespan=lifespan)`，shutdown 时 `await agent.model.aclose()`——Step 2 定义的应用级关闭点三个 Step 后兑现
- ApiPost 真模型调通：帧级到达、多轮工具流完整

### 学到的关键点

**最后一棒做表示转换**：整条管线前几棒流 ModelResponse 帧（对象），只有 SSE 端点这一棒把帧序列化成 `data: ...\n\n` 文本——"保对象到最后、出门口才转字符串"兑现。

**定义 ≠ 接线**：lifespan 函数写好后忘了 `FastAPI(lifespan=lifespan)`，aclose 永远不执行且**不报错**（不执行≠报错，测试抓不到）——岗位空悬类 bug 的第三次现身（aclose 进每次调用 / aclose 没人调 / lifespan 没挂上）。验证手段：钩子里打 print，亲眼看 shutdown 输出。

**SSE 细节**：`\n\n` 双换行是帧终结符（少一个接收方认为帧没结束）；curl 要 `-N` 关缓冲否则"憋几秒一次蹦出"的假象；`ensure_ascii=False` 否则中文变 `仮`。

**lifespan ≈ Spring `@PreDestroy`**：应用启动后/退出前各一个钩子位，资源关闭的标准居所。

### 当前 mini-agno 状态
- 40 个测试全绿
- **流式模块（模块 12）全部完成**：ainvoke/arun + ainvoke_stream/arun_stream + SSE 端点，从 token 到浏览器全链路打通
- mini-agno 至此：12 个计划模块 + 流式增强，具备真产品形态的完整骨架

---

## 2026-09-15（Day 12，MCP 模块收官）

### 完成的事

**模块 13 · MCP 协议（工具生态的 USB-C）**
- Step 1 手搓体验：`examples/mcp_server_bake.py`（fastmcp `@mcp.tool` 把烤房工具包成 stdio server）+ `mcp_client_bake.py`（裸 client：`list_tools()` 看 server 自报 schema、手动 `call_tool`）——server 自报的 `input_schema` 和自己 `Function.to_dict()` 的 `parameters` 一模一样，两端各有一份 schema 反射逻辑
- Step 2 接入层 `mini_agno/tools/mcp_tools.py`：connect（手动 `__aenter__` 开门 + list_tools + 造 Function）→ get_functions → disconnect；每个工具一个 async 闭包 entrypoint（闭包焊工具名，`**kwargs` 转发）
- Step 3 端到端：`run_mcp_agent.py` 真模型打通——agent 调工具 = JSON-RPC 转发给**另一个进程**执行，"烤房002的温度是38.2"从子进程回来
- 两堵墙都拆了：**墙1** `Function` 加 `skip_auto_schema`（schema 三来源：反射/docstring/**server 自报**，agno 的 `skip_entrypoint_processing` 同款）；**墙2** `FunctionCall.aexecute()` 双模（同步/异步 entrypoint 通吃）+ 同步 `execute()` 误用 async 工具时抛**带修法指引的 TypeError**
- 超出布置的发挥：`_aexecute_tool_calls` 用 **`asyncio.gather` 并发执行**同轮多个工具（gather 保序，消息顺序确定）；`_build_tool_message` 统一消息构造

### 学到的关键点

**MCP 的本质：把工具的"定义"和"执行"从进程内解耦到协议两端**。之前工具是 agent 代码里的函数（schema 靠反射）；MCP 后工具是 server 自报的（name/description/JSON Schema 都由提供方声明），执行转发到 server 进程。**解耦的兑现：烤房团队改温度算法，agent 代码零改动，重发布 server 即可**。

**模块 3 造的 Function 抽象恰好是 MCP 的插槽**：MCPTools 是个薄适配器（生命周期/发现/代理三职责），产出 `list[Function]`，Agent 和主循环**一行不改**——远端工具进 Agent 手里和本地工具无差别。框架设计的正面验证：好的抽象让新接入方变成"胶水"而不是"改造"。

**`async with X:` 的真身**：`await X.__aenter__()` + `await X.__aexit__(None,None,None)` 两句调用。糖管**块级**生命周期；手动调管**对象级**生命周期——MCPTools 的 session 要从 connect 活到 disconnect，没有缩进能罩住，只能手动开关门（合法逃生舱，agno 同款；enter/exit 必须同 task 配对——anyio cancel scope 的要求）。

**schema 的三种来源**（本次理顺）：函数签名反射（本地工具默认）/ docstring Args / server 自报（MCP）。`Function` 从"只会反射"长成"三来源可选"。

**async 工具的执行分家**：entrypoint 是 async 时，同步 `execute()` 拿到的是 coroutine 不是结果——同步/异步执行器分家（`_execute_tool_calls` / `_aexecute_tool_calls`），同步 `run()` 不支持 MCP 工具（协议本身 async-only，诚实限制）。

### 坑 & 易错点

- **`await 同步方法`**：arun_stream 里写成 `await self._execute_tool_calls(...)`（同步版方法名），返回 None 被 await → `TypeError: object NoneType can't be used in 'await' expression`。**这次是全量测试抓住的**——改完全量测试再次实证价值
- **格式化和功能不能混一个 commit**：全仓跑了格式化（逗号空格/两空行），1400 行 diff 里功能改动会被淹没——分"功能 commit + 格式化 commit"
- fastmcp stdio server 用 `uv run` 拉起（command="uv", args=["run", ...]），别直接 python——环境对不上

### 待办（记着）
- [ ] `MCPTools.disconnect` 改名 `aclose`（与 Model.aclose 统一）+ 关完 `self._client = None` + demo 补 try/finally
- [ ] `skip_auto_schema` 的离线单测还没写
- [ ] `connect()` 调两次会重复堆工具（加幂等守卫）
- [ ] MCPTools 也该进 api.py 的 lifespan 管理（服务器形态）

---

## 2026-09-15（Day 12 续，eval 模块收官）

### 完成的事

**模块 14 · eval：给没有标准答案的输出造尺子**
- `mini_agno/eval/`：`case.py`（EvalCase + YAML 用例集加载）、`judge.py`（JudgeResult + make_judge 裁判工厂）、`runner.py`（run_keyword_case / run_judge_case / run_eval 全流程编排）、`report.py`（CaseResult + EvalReport 聚合）
- keyword 模式（L1 软断言：必含关键词）+ judge 模式（L3 LLM-as-judge：裁判 Agent + output_schema 吐 `{score, reason}`）
- **用 mini-agno 评测 mini-agno**：裁判就是自家 Agent，output_schema 复用模块 5
- 5 个离线测试（含 run_eval 全流程聚合：剧本 4 用例断言 `(1,2)`/`5.5`/分布/失败清单），45 全绿
- **压轴突变校验**：基线 10.0 → 规则故意写反 1.5，失败清单的 feedback 精准定位“方向性错误”——尺子有牙齿
- `examples/run_eval.py --mutate` 一键对比

### 学到的关键点

**eval = 给 LLM 输出写的 pytest**。整个模块只有一个新思想：**断言器可以是个 Agent**。其余全是 pytest 结构的重写（yaml 用例集=test 文件、run_eval=运行器、print_summary=末尾那行 42 passed）。乱感的解药是找对照框架——感觉乱往往不是问题难，是缺一个熟悉的心智锚点。

**测试的阶梯**：L0 确定性管道测试（MockModel+精确断言，45 个测试全是）→ L1 软断言（结构性质/关键词）→ L2 参考答案比对 → L3 LLM-as-judge → L4 人工抽检。**分数是统计量**：对分布断言不对单点（平均分/分布/阈值筛选，JMH 的 p99 思想）。

**真模型的结构化输出会漂移**：裁判吐 `{"score":3,"reason":...}` 而 schema 叫 feedback——字段名是契约但模型有自己的偏好。轻修：pydantic `Field(alias="reason")` + `populate_by_name=True` 两个键都收；根治：OpenAI 原生 response_format 强制 schema（老待办又+1 例证）。instructions 里显式写键名也能提高稳定性。

**尺子先量尺子**：第一次基线跑分 judge 给了 1 分——但被抓的是**用例自身的缺陷**（输入没带数据，agent 合理反问被 rubric 判死）。eval 上线第一件事往往是修用例集，不是修 agent：每条用例必须给 agent 展示能力的公平输入。

**`passed is False` vs `not passed`**：judge 用例的 passed 是 None（falsy），`not r.passed` 会误伤；`is False` 精确匹配。None/False 二义性经典雷。

### 坑 & 易错点（三大惯犯在 eval 模块全部再犯，全部被抓住）

- **假测试第四季**：测试调用了 run_keyword_case 但返回值扔了，零断言——写完必须自问“改坏实现它会红吗”
- **编造字段/参数名**：`output_parser=`（Agent 没这字段，构造即炸，我当场引爆）、`ToolCall(args=)`、`MockModel(name=)`——对 API 的记忆模糊时先翻定义，别凭印象写
- **定义≠接线第四次**：`run_eval(judge_mode=...)` 收了参数但从没传给 make_judge——离线测试就做不了
- **写完不跑**：测试文件带着 4 个错（缺 import ×2、编造字段 ×2）直接交付，一条 `uv run pytest` 9ms 全暴露——“写完立刻跑”仍未刻进肌肉

### 当前 mini-agno 状态
- 45 个测试全绿
- **模块 14 完成**：eval 尺子就位，prompt/模型变更从此有涨跌数字
- 14 个模块：12 计划内 + 流式 + MCP + eval

---

## 下次从哪开始（毕业后方向剩余）

1. **MCP 协议**：工具生态的 USB-C，mini-agno 当 MCP client 接外部工具服务器
2. **RAG L2/L3**：TF-IDF → embedding + 向量库（pgvector）
3. **eval**：怎么测 LLM 应用（agent_as_judge）
4. agno 未探索地图：guardrails / reasoning / approval(HITL) / scheduler

### 待办（记着）
- [ ] api 层 TestClient 离线测试（流式端点也缺）
- [ ] demo run_stream.py 里的 try/except 会吞真实错误（保留是自己的决定，排查时先看它）
- [ ] 将来要工具状态帧时：Agent 造自己的事件族（RunContentEvent/ToolRunEvent），不再借 ModelResponse
- [ ] examples/bare_repro.py 留作排查记录（含在 Step 3 提交）
