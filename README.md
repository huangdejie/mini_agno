# mini-agno

> 我边读 agno 源码、边自己从头实现的迷你 agent 框架。
> 目的：通过"造轮子"吃透 agent 框架的设计原理，而不是只会调用 agno 的 API。

---

## 这是什么

参照 [agno](https://github.com/agno-agi/agno)（`libs/agno/agno/`）的设计，自己动手实现一个简化版 agent 框架。每个核心机制的学法都一样：

```
1. 读 agno 源码  →  理解它怎么设计、为什么这么设计
2. 在这里实现   →  自己写一个简化版
3. 写测试跑通   →  用验收标准证明实现了
```

完整学习地图见 agno 仓库的 `docs/agno-source-code-guide.md`。

---

## 五层架构（对照 agno）

```
领域模型层    Agent / Team / Workflow      —— 声明式配置 + 数据
    ↓ 委托执行
执行引擎层    run 循环 / 事件 / HITL        —— 命令式，真正干活的地方
    ↓ 调用
能力层        Model（可插拔）/ Tools / Knowledge / Memory
    ↓ 存取
持久化层      BaseDb / agno_* 表族 / VectorDB
    ↓ 暴露
运行时层      FastAPI REST + SSE            —— 把 agent 变成服务
```

mini-agno 会按这五层逐步搭建。

---

## 12 个模块路线

| # | 模块 | 对应 agno 源码 | 状态 |
|---|---|---|---|
| 0 | 全局架构 + 项目骨架 | `libs/agno/agno/` 顶层、`agent/agent.py`、`run/` | ✅ 完成 |
| 1 | 核心数据模型（Message/Response） | `models/message.py`、`models/response.py` | ✅ 完成 |
| 2 | Model 抽象（多厂商可插拔） | `models/base.py:130` | ✅ 完成 |
| 3 | 工具系统（@tool/Function/FunctionCall） | `tools/decorator.py`、`tools/function.py` | ✅ 完成 |
| 4 | **Agent 主循环**（里程碑 M1） | `agent/agent.py` 的 `run`、`run/` | ✅ 完成（M1 达成） |
| 5 | 结构化输出 | `agent.py` 的 `output_schema` | ✅ 完成（含真模型接入） |
| 6 | 会话与持久化 | `db/base.py`、`db/schemas/` | ✅ 完成（模块 6 Step3：BaseDb + SqliteDb） |
| 7 | 记忆系统（跨会话） | `memory/manager.py` | 🔧 进行中（⬅️ 下一个） |
| 8 | RAG 知识库 | `knowledge/knowledge.py` | 未开始 |
| 9 | 多智能体（Team） | `team/team.py`、`team/mode.py` | 未开始 |
| 10 | 工作流（Workflow） | `workflow/step.py`、`workflow/types.py` | 未开始 |
| 11 | 运行时 API 化（里程碑 M4） | `os/`（FastAPI + SSE） | 未开始 |

**里程碑**：M1（模块 4 后，能跑带工具的 agent）· M4（模块 11 后，能 API 化）

---

## 怎么跑

```bash
uv sync          # 安装依赖（pydantic + pytest）
uv run pytest    # 跑测试（当前 24 个测试全绿）
```
