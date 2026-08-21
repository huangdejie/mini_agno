# mini-agno 核心架构（速查笔记）

> 一页看懂 mini-agno 的骨架。配套：知识点见 knowledge.md，进度见 learning-log.md。
> 截至 2026-08-20，代码实际推进到模块 6 Step3（持久化层落地）。

---

## 一、一句话定位

```
mini-agno = Model（大脑） + Tools（手脚） + Loop（主循环） + Session（记忆） + Db（持久化）
```

约 300 行核心代码实现 agno 的骨架，用来理解 agent 框架的设计原理。

## 二、目录结构（代码地图）

```
mini_agno/
├── agent.py            # Agent：主循环（执行引擎，项目核心）
├── session.py          # Session：会话状态（session_id + messages）
├── db/                 # 持久化层
│   ├── base.py         #   BaseDb(ABC) —— 可替换的存储接口
│   └── sqlite_db.py    #   SqliteDb —— 标准库实现，session 整行 JSON 存储
├── models/             # 能力层：模型抽象
│   ├── base.py         #   Model(ABC) —— 可插拔的关键，仅一个抽象方法 invoke()
│   ├── message.py      #   Message / ToolCall / ModelResponse（Pydantic，统一消息模型）
│   ├── openai_model.py #   OpenAIModel —— 真模型，防腐层（双向翻译）
│   └── mock.py         #   MockModel —— 剧本式预设响应，离线测循环逻辑
└── tools/              # 能力层：工具系统
    ├── function.py     #   Function（签名自省→JSON Schema）+ FunctionCall（执行）
    └── decorator.py    #   @tool 装饰器
tests/                  # 按模块对应的测试（MockModel 驱动，不打真 API）
examples/               # 真模型端到端 demo（手动跑）
docs/                   # 学习笔记（本文件 + knowledge.md + learning-log.md）
```

依赖极简：`openai` + `pydantic`，Python 3.12+，uv 管理，pytest 验收。

## 三、Agent 数据结构（领域模型）

```python
@dataclass
class Agent:
    model: Model                          # 策略模式注入，换厂商不改 Agent
    tools: list[Function]
    max_iterations: int = 10              # 循环兜底，防无限调工具
    output_schema: type | None = None     # 传 Pydantic 类→结构化输出；None→自由文本
    sessions: dict[str, Session]          # 按 session_id 存会话（Agent 本身无状态）
    db: BaseDb | None = None              # 可选持久化；None 时退化为内存模式
```

数据流：Session 保存对话历史 → `db.upsert_session()` 落盘 → 新 Agent 实例 `db.get_session()` 加载。
Cache-aside：内存 `sessions` 是缓存，db 是 source of truth；有 db 时 run 结束写回，无 db 时行为与之前完全一致。

## 四、主循环（`agent.py:29` run()，最重要的一张图）

```
用户消息 → 追加进 session.messages
   ↓
┌─ while（上限 max_iterations）──────────────────┐
│  resp = model.invoke(messages, tools)          │
│  追加 assistant 消息（content + tool_calls）    │
│     ↓                                          │
│  if resp.tool_calls:        # A：想调工具       │
│      FunctionCall.execute() → 结果以            │
│      role="tool" + tool_call_id 回填 → 继续循环 │
│  else:                      # B：给最终答案     │
│      有 output_schema → model_validate_json     │
│      否则 → 返回 resp.content                   │
└────────────────────────────────────────────────┘
```

关键认知：
- 模型每轮响应**只有两种**：想调工具 / 给答案，无中间态
- 判断就一行 `if resp.tool_calls:`，没有魔法
- assistant 的 tool_call 请求本身也要 append 进历史（真模型必需）

## 五、一次带工具调用的消息序列（协议实例）

```
messages:                                  tools 参数（每次全量传）:
[ {role:"user",      content:"北京天气"}]    [ {type:"function",
  {role:"assistant", tool_calls:[{id:"1",        function:{name:"get_weather",
                   name:"get_weather",                    parameters:{...}}}] }
                   arguments:{"city":"北京"}}]},
  {role:"tool",      tool_call_id:"1",
                   content:'{"temp":25}'}]
  {role:"assistant", content:"北京 25 度"}    ← 下一轮循环，无 tool_calls，返回
```

口诀：**清单每次带，历史攒起来，动作和结果靠 id 配对**。

## 六、四个关键设计决策

| # | 决策 | 实现 | 收益 |
|---|---|---|---|
| 1 | Model 是 ABC，只约束 `invoke(messages, tools) -> ModelResponse` | `models/base.py:8` | 换厂商 = 加一个子类，Agent 零改动（策略模式） |
| 2 | 内部统一用自己的 Message，只在边界转 OpenAI dict | `openai_model.py:17` `_message_to_openai_dict` | 防腐层：厂商协议变化不污染核心（bug 密度最高处） |
| 3 | 工具靠函数签名自省生成 Schema | `function.py:15` `__post_init__` | 普通函数 + 类型注解 + docstring = 可被模型调用的工具 |
| 4 | 行为（Agent）与状态（Session）分离 | `session.py` + `sessions` 字典 | Agent 无状态化，为持久化层（模块 6 后半）铺路 |

## 七、对照 agno 五层架构的位置

```
领域模型层    Agent / Team / Workflow     ← Agent 已有（声明式 dataclass）
执行引擎层    run 循环                     ← 已有（agent.py 的 run；agno 是抽离的 _run.py）
能力层        Model / Tools / Knowledge   ← Model + Tools 已有；Memory/Knowledge 未做
持久化层      BaseDb / agno_* 表族         ← 仅内存 Session，DB 未做 ⬅️ 当前位置
运行时层      FastAPI + SSE                ← 未做（模块 11）
```

## 八、现状与已知缺口

- **已达成**：M1（会调工具的 agent）、结构化输出、真模型（DeepSeek）打通、多轮会话、Agent 无状态化
- **缺口**：
  - `tools/decorator.py` 的 `@tool` 还是占位（叫 `my_tool`）
  - 结构化输出靠 prompt 约定，未用 OpenAI 原生 `response_format`
  - Session 只在内存，重启即失（模块 6 剩余：DB 持久化）
  - README 的模块状态表滞后于代码（表里写模块 3 进行中，实际到模块 6）
