# mini-agno 知识手册（模块 0–5）

> 学习产出的知识沉淀，按「Agent 领域知识 / Python 语言 / 工程实践 / 设计模式」四部分组织。
> 配套：进度见 learning-log.md，学习地图见 agno 仓库 docs/agno-source-code-guide.md。

---

## 一、Agent 框架核心知识

### 1. Agent 的本质公式

```
Agent = Model（大脑） + Tools（手脚） + Loop（循环：调工具→看结果→再决策）
```

去掉所有包装，一个 agent 框架核心就这么多。agno 上万行里，绝大部分是工程化包装（持久化、监控、多模态、边缘处理），核心机制约 300 行。

### 2. ReAct / tool-use 主循环（最重要的一张图）

```
while True:
    resp = model.invoke(messages, tools)
    if resp.tool_calls:              # A：模型想调工具
        执行工具 → 结果 append 回 messages → 继续循环
    else:                            # B：模型给最终答案
        return resp.content
```

关键认知：
- 模型每轮响应**只有两种**：想调工具 / 给答案。**没有中间态**。
- 循环判断就一行 `if resp.tool_calls:`，没有更多魔法
- 循环要有 `max_iterations` 兜底，防止模型无限调工具

### 3. 消息协议（三种 role + 一个参数）

| 位置 | 是什么 | 语义 |
|---|---|---|
| `tools` 参数（不在 messages 里） | 工具清单（JSON Schema） | **能力声明**："你有哪些工具"，每次调用**全量传** |
| `assistant` 消息带 `tool_calls` | 模型上轮的输出 append 进历史 | **动作记录**："我决定调 add(1,2)" |
| `tool` 消息带 `tool_call_id` | 工具执行结果 | **结果回链**："add 返回 3"，用 id 和动作配对（≈ correlationId） |
| `user` / `assistant`(纯文本) | 普通对话 | 提问 / 回答 |

记忆口诀：**清单每次带，历史攒起来，动作和结果靠 id 配对**。

### 4. 模型无状态（为什么每次都重传全部）

模型不记得任何上一轮——每次 invoke 都是独立请求。所以：
- 对话历史要**每次全量**作为 messages 传回
- 工具清单要**每次全量**作为 tools 传
- "多轮对话"是客户端循环 + 重放历史造成的**假象**

### 5. 工具系统（Function → Schema → 执行）

- `Function`：包装一个普通函数，用 `inspect.signature` + `get_type_hints` 反射提取签名，生成 JSON Schema（name/description/parameters）
- `FunctionCall`：一次具体调用，`fn(**arguments)` 按名解包执行
- `@my_tool` 装饰器：普通函数 → `Function` 实例，注册即工具
- 工具的 docstring 就是给模型看的说明书，**写清楚=模型用得对**

### 6. 结构化输出（output_schema）

- 传 Pydantic 类 → 模型吐符合 schema 的 JSON → `output_schema.model_validate_json(content)` 还原成强类型对象
- 现在是"prompt 约定 + 客户端 parse"；OpenAI 原生 `response_format` 是更严的升级路线（待做）
- 注意：模型吐的 JSON 不合 schema 时 `model_validate_json` 会抛 ValidationError，生产要有容错

### 7. 模型抽象（可插拔的关键）

`Model(ABC)` 只有一个抽象方法：`invoke(messages, tools) -> ModelResponse`。
- MockModel：剧本驱动（response_list 按顺序吐预设响应），离线测循环逻辑
- OpenAIModel：真调用，核心是**双向翻译**（见下）
- 换厂商 = 加一个子类，Agent 一行不改——策略模式的标准收益

### 8. 协议转换的五个坑（OpenAIModel 实战提炼）

1. `arguments` 出站 `json.dumps`（dict→JSON 字符串）、入站 `json.loads`（JSON 字符串→dict），**方向必须对称**
2. tool_calls 元素必须带 `"type": "function"`（固定字符串，不是变量）
3. `content=None` 的消息**别放 content 这个 key**（很多厂商对 null 报错）
4. `tool` 消息的 `tool_call_id` 必须有，否则 API 直接报错
5. 转换逻辑按 **role 分流**、字段**各自独立的 if**，不是嵌套条件链（tool_calls 和 tool_call_id 是两种消息上的字段，从不同时出现）

---

## 二、Python 语言知识（Java 转译对照）

### 语法与惯用法

| Python | Java 对应 | 备注 |
|---|---|---|
| `@dataclass` | Lombok `@Data` / record | 自动生成 `__init__`/`__repr__`/`__eq__` |
| `@dataclass` + `ABC` 叠加 | 抽象类带字段 | 子类 dataclass 自动继承父类字段 |
| `__post_init__` | `@PostConstruct` | dataclass 构造后自动跑的钩子 |
| `field(default_factory=list)` | `new ArrayList<>()`（每实例独立） | **`=[]` 是类级共享，所有实例同一个 list，经典大坑** |
| `**dict` 解包调用 | 反射 `Method.invoke` 但更直接 | `fn(**{"a":1})` ≡ `fn(a=1)`，按名传参 |
| `==` / `is` | `equals` / `==` | **和 Java 正好相反**：Python `==` 比值，`is` 比引用 |
| `str.rstrip(chars)` | — | 按**字符集**删不是删子串；删子串用 `removesuffix()` |
| 装饰器 `@xxx` | 注解 + 处理器 | Python 装饰器是**真包装函数**（高阶函数），不只是元数据 |

### 类型系统

- 现代写法：`list[Message]`、`dict[str, Any]`、`str | None`（3.10+，不用再 `Optional[str]`）
- 类型注解是**惰性**的：定义时不求值 → `Dict` 没 import 不会在 import 时报错，**调用到那行才 NameError**
- `typing.get_type_hints(fn)` / `inspect.signature(fn)`：反射签名和类型（≈ `Method.getParameterTypes()`）

### Pydantic（≈ Jackson + Bean Validation + 手写 DTO）

| Pydantic | Java 对应 |
|---|---|
| `class X(BaseModel)` | DTO + 校验注解 |
| `model_dump()` / `model_dump_json()` | `writeValueAsString` |
| `model_validate` / `model_validate_json` | `readValue` |
| 校验失败抛 `ValidationError` | `ConstraintViolationException` |
| 类型不匹配自动报错 | 字段类型不对直接拒绝 |

---

## 三、工程与生态

### uv（≈ Maven Wrapper）

- `uv run X` = 在项目 venv 里跑命令 X；`uv add pkg` = 加第三方依赖（改 pyproject + lock）
- **标准库不用装**：`unittest`/`json`/`os` 直接 import；PyPI 上也没有
- 要装的是第三方：pytest、pydantic、openai
- 开发依赖进 `[dependency-groups] dev`（≈ Maven `provided`/test scope 的味道）

### pytest（≈ JUnit + Surefire）

| 需求 | 命令 |
|---|---|
| 跑全部 | `uv run pytest` |
| 只看收集到哪些测试 | `--collect-only` |
| 显示 `print` 输出 | `-s`（= `--capture=no`，默认吞掉、失败才吐） |
| 显示 `logging` 输出 | `--log-cli-level=DEBUG`（logging 走另一通道，`-s` 管不到） |
| 按名过滤 | `-k 关键词` |

- pytest 和 unittest **能混用**：pytest 能跑 `unittest.TestCase`，但写测试用 pytest 风格（裸 `assert`）更顺
- pytest 的 assert 有魔法重写：失败时自动展示操作数双方的值，不用手写 msg
- 配置在 `pyproject.toml` 的 `[tool.pytest.ini_options]`：`testpaths`（扫描范围）、`pythonpath`（导入路径）、`addopts`（默认参数）

### unittest.mock（≈ Mockito）

- `MagicMock()`：全接口可用的假对象，任何属性访问/调用都不报错
- 替换方法：`obj.method = MagicMock(return_value=fake)`（≈ `when(mock.method()).thenReturn(x)`）
- **大坑：`MagicMock(name='add')` 的 name 被 mock 自己吞了当实例名**，设属性要用 `configure_mock(name='add')`
- mock 的验证边界：mock 只能验证「你写的那层逻辑」，**mock 不了协议本身**——所以真模型的端到端验证不可替代

### 测试方法论（本项目最大教训）

1. **期望值写"应该是什么"，不是"现在输出是什么"**——否则是把 bug 固化进测试（模块 3 的 return bug、模块 4 的 `:FINISHED` 哨兵都栽在这）
2. **MockModel 验证循环逻辑，真模型验证消息协议**——MockModel 不读 messages，`_message_to_openai_dict` 的嵌套 bug mock 测全绿、真模型一打就穿
3. **打真 API 的测试别进 pytest**——CI 无 key 必挂、还花钱；真模型验证放 examples/ 手动跑，转换逻辑用 mock 固化成测试
4. 分层验证：单元（mock）→ 集成（mock 客户端转换层）→ 端到端（手动真模型）

---

## 四、设计模式（用 Java 视角看 mini-agno）

| mini-agno 里的实现 | 模式 | Java 世界的对应 |
|---|---|---|
| `Model(ABC)` + Mock/OpenAI 两实现 | 策略模式 | `PaymentService` 接口 + 多渠道 impl |
| `OpenAIModel` 双向翻译 | 防腐层（ACL） | 领域对象 ⟷ 外部 DTO 的 Converter/Mapper |
| `@my_tool` 装饰器 | 装饰器/注册器 | Spring 注解 + BeanPostProcessor |
| `Function.__post_init__` 自动提取 | 惯例优先配置 | `@Autowired` 按约定装配 |
| `Agent`（行为）与 `Session`（状态）分离（模块 6 待做） | 无状态服务 + 会话 | `@Service` 单例 + `HttpSession` |

**防腐层的教训**：边界处的数据要换形态（dict⟷str、None⟷缺 key），这类代码看着枯燥，却是 bug 密度最高的地方——协议的格式约定（`type:"function"`、null 处理、id 回链）没有为什么，只能对着文档抠，靠真模型验证。

---

## 五、一句话卡片（速查）

- Agent 主循环 = `if resp.tool_calls: 执行塞回继续 else: 返回`
- tools 是清单每次带，tool_calls 是历史攒起来
- 模型无状态，多轮是重放历史的假象
- arguments 出站 dumps、入站 loads
- content 为 None 就不放 key
- `=[]` 默认值共享，用 `field(default_factory=list)`
- Python `==` 比值，`is` 比引用（和 Java 相反）
- 类型注解惰性求值，NameError 在调用时才爆
- `MagicMock(name=)` 是坑，`configure_mock` 是路
- 测试期望写应该是什么，不是现在是什么
- Mock 测逻辑，真模型测协议
