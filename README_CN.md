# 超思考 v6 · 多专家辩论系统

> **与历史上最伟大的头脑对话。** 一个多专家辩论框架，让苏格拉底的辩证法、爱因斯坦的科学精神、孙武的军事谋略、查理·芒格的多元思维模型，在同一个问题下交锋、碰撞、融汇。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![版本: 6.0](https://img.shields.io/badge/版本-6.0-green.svg)]()

**[English](./README.md) | [繁體中文](./README_TW.md)**

---

## 缘起

当一个问题摆在面前，单一视角的回答往往遗漏了最重要的东西——

那些**被默认接受的假设**，那些**与己相异的立场**，那些**意料之外的关联**。

超思考 v6 不给你一个答案，而是召集一群最合适的专家，让他们**真正地辩论**。

不是简单地把各路观点并排陈列，而是让每位专家：
- **陈述**自己的核心论点
- **反驳**他人的薄弱之处
- **回应**被质疑的地方
- 最终由**主持人**检测收敛，**融合层**提炼共识

这才是思考应有的样子。

---

## 核心架构

```
                        ┌─────────────────────────────────────────┐
   用户问题              │            路由层（Router）              │
  ─────────────────────►│  读取 INDEX_PEOPLE.md                  │
                        │  读取 INDEX_METHODS.md                 │
                        │  判断：人物型？方法论型？双轨组合？       │
                        └──────────────────┬────────────────────┘
                                           │
                    ┌───────────────────────┼───────────────────────┐
                    │                       │                       │
                    ▼                       ▼                       ▼
            ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
            │   人物型      │      │   方法论型    │      │   双轨组合    │
            │  （历史人物）  │      │  （学术框架）  │      │  （全面审视）  │
            └──────┬───────┘      └──────┬───────┘      └──────┬───────┘
                   │                     │                     │
                   └─────────────────────┼─────────────────────┘
                                         │
                        ┌────────────────▼────────────────────┐
                        │       辩论编排器（Orchestrator）     │
                        │  ┌──────────────────────────────┐  │
                        │  │      主持人（Moderator）      │  │
                        │  │  • 构建论点菜单               │  │
                        │  │  • 选择下一位发言人            │  │
                        │  │  • 检测共识收敛               │  │
                        │  └──────────────────────────────┘  │
                        │              ▲                     │
                        │              │                     │
                        │  ┌───────────┴───────────────┐     │
                        │  │    专家池（ExpertPool）   │     │
                        │  │  register / unregister   │     │
                        │  └───────────────────────────┘     │
                        └──────────────────┬──────────────────┘
                                           │
                        ┌──────────────────▼──────────────────┐
                        │         融合层（Fusion）            │
                        │  • 冲突检测                        │
                        │  • 共识提炼                        │
                        │  • 结构化综合报告                   │
                        └───────────────────────────────────┘
```

### 核心组件一览

| 组件 | 文件 | 职责 |
|------|------|------|
| `think_v6()` | `entrypoint.py` | 一行调用入口 |
| `convene_v6()` | `entrypoint.py` | 程序化 API |
| `DebateOrchestrator` | `orchestrator.py` | 管理完整辩论生命周期 |
| `Moderator` | `moderator/moderator.py` | 每轮运行，构建论点菜单 |
| `ExpertPool` | `expert_pool.py` | 热插拔专家注册表 |
| `ConvergenceDetector` | `convergence_detector/detector.py` | 检测共识何时达成 |
| `SessionRecorder` | `session_recorder.py` | 11 个事件钩子，可观测性 |
| `MethodologyRegistry` | `methodology.py` | 18 种学术框架 |

---

## 安装

```bash
# 从源码安装
cd agent-superthinking-v6
pip install -e .

# 或者安装已发布的包（上线后）
pip install agent-superthinking
```

### 依赖

仅**两个硬依赖**：

```toml
typer>=0.12.0        # CLI 框架
pydantic>=2.0        # 类型校验
```

`rich` 为可选依赖，装上之后终端输出更美观：

```bash
pip install rich
```

---

## 快速上手

### CLI — 交互式辩论

```bash
# 交互模式（推荐）
super_thinking debate "AI 是否应该拥有法律人格？"

# 指定专家和轮数
super_thinking debate "AI 治理的最佳策略是什么？" \
  --experts socrates,confucius,einstein \
  --rounds 3

# 模拟模式（无需 API Key，基于模板）
super_thinking debate "数字时代隐私还存在吗？" \
  --experts confucius,socrates \
  --mock

# JSON 输出（程序化使用）
super_thinking debate "经济不平等的根源是什么？" \
  --experts keynes,hayek,smith \
  --format json
```

### CLI — 列出所有专家

```bash
super_thinking list
# 或者：super_thinking list --format json
```

### CLI — 单专家咨询

```bash
# 比完整辩论更快——只咨询一位专家
super_thinking consult "时间的本质是什么？" --expert socrates
super_thinking consult "我们应该如何思考创新？" --expert einstein
```

### Python API — 一行调用

```python
from super_thinking import think_v6, DebateConfig

result = think_v6(
    question="应该优先经济发展还是环境保护？",
    selected_experts=["confucius", "hayek", "einstein"],
    config=DebateConfig(max_rounds=2)
)

print(result["final_report"])
```

### Python API — 精细控制

```python
from super_thinking.v6 import convene_v6
from super_thinking.v6.types import DebateConfig
from super_thinking.v6 import ExpertPool

# 自定义专家池
pool = ExpertPool()
pool.register(my_custom_expert)

# 自定义配置
config = DebateConfig(
    max_rounds=3,
    convergence_threshold=0.75,
    temperature=0.7,
)

result = convene_v6(
    question="苦难的意义是什么？",
    selected_experts=["socrates", "buddha", "nietzsche"],
    expert_pool=pool,
    config=config,
)
```

---

## 专家库

超思考 v6 包含 **30+ 位专家**，分为两条路径：

### 人物路径 — 历史巨人

| 领域 | 专家 | 关键词 |
|------|------|--------|
| 哲学 | 苏格拉底、柏拉图、亚里士多德、康德、尼采、笛卡尔、休谟、老子、庄子、维特根斯坦、萨特、马克思 | 辩证法、理念论、德性论、批判、意志、怀疑、经验主义、道家、无为、语言分析、存在主义、唯物史观 |
| 文学 | 但丁、陀思妥耶夫斯基、卡夫卡、鲁迅 | 神曲、复调小说、荒诞、呐喊 |
| 科学 | 爱因斯坦、牛顿、波尔、居里夫人、麦克斯韦、薛定谔、图灵、高斯、欧几里得、哥德尔 | 相对论、重力、量子论、放射学、电磁学、波函数、计算、统计学、几何学、不完备性 |
| 经济 | 亚当·斯密、凯恩斯、哈耶克、稻盛和夫 | 古典自由市场、宏观经济学、奥地利学派、經營哲学 |
| 军事 | 孙子、克劳塞维茨 | 孙子兵法、战争论 |
| 心理 | 弗洛伊德、荣格、埃里克森、罗杰斯、米德、福柯 | 精神分析、集体无意识、发展心理学、来访者中心、社会建构、权力/知识 |
| 宗教 | 佛陀、王阳明 | 八正道、知行合一 |

### 方法论路径 — 学术框架

| 类别 | 框架 |
|------|------|
| 哲学 | 现象学、分析哲学、伦理学、政治哲学 |
| 社会科学 | 人类学、社会学、传播学 |
| 交叉学科 | 美学、语言学、教育学、管理学、控制论、法理学、运筹学 |
| 分析工具 | 贝叶斯推理、批判性思维、设计思维、系统思维 |
| 计算思维 | 信息论、网络理论、复杂性科学、量子思维 |
| 决策科学 | 博弈论、进化心理学 |

---

## JSON Schema — 框架无关的数据格式

每位专家同时生成 `schema.json`，**任何 AI 框架都能解析**：

```python
import json

# 加载任意专家——兼容 LangChain、LlamaIndex 等
with open("experts/philosophy/socrates-perspective/schema.json") as f:
    schema = json.load(f)

print(f"专家：{schema['displayName']}")
print(f"领域：{schema['domain']}")
for model in schema["models"]:
    print(f"  模型：{model['name']} — {model['summary']}")
```

```json
{
  "id": "socrates-perspective",
  "type": "people",
  "domain": "philosophy",
  "displayName": "苏格拉底",
  "keywords": ["苏格拉底", "辩证法", "自知无知", "产婆术", "伦理"],
  "models": [
    {
      "name": "苏格拉底式提问",
      "type": "dialectical",
      "summary": "通过不断追问揭示概念的矛盾，达到更深层的认识"
    }
  ],
  "version": "1.0.0"
}
```

---

## v5 到 v6 迁移指南

```python
# v5（旧版）
from super_thinking import Jury
jury = Jury()
result = jury.think(question, model_names=["socrates", "confucius"])

# v6（当前版）
from super_thinking.v6 import think_v6, DebateConfig
result = think_v6(
    question=question,
    selected_experts=["socrates", "confucius"],
    config=DebateConfig(max_rounds=2)
)

# v6 也提供 v5 兼容适配器（渐进式迁移）
from super_thinking.v6.compat import JuryAdapter
adapter = JuryAdapter()
result = adapter.think(question, model_names=["socrates", "confucius"])
```

---

## CLI 命令参考

| 命令 | 说明 |
|------|------|
| `debate <问题>` | 启动完整多专家辩论 |
| `debate <q> --experts socrates,confucius --rounds 3` | 指定专家和轮数 |
| `debate <q> --mock` | 模拟模式（无需 API Key） |
| `debate <q> --format json` | JSON 输出格式 |
| `list` | 列出所有可用专家 |
| `consult <问题> --expert <id>` | 单专家咨询（快速模式） |
| `--help` | 显示所有选项 |

---

## 高级配置

### 专家池 — 热插拔注册表

```python
from super_thinking.v6 import ExpertPool, Expert

pool = ExpertPool()

# 注册自定义专家
pool.register(Expert(
    id="my_expert",
    name="我的专家",
    domain="custom",
    models=[...],
    heuristics=[...],
))

# 注销
pool.unregister("my_expert")

# 列出所有已注册专家
for expert_id in pool.list_registered():
    print(expert_id)
```

### 会话录制器 — 全链路可观测

```python
from super_thinking.v6 import SessionRecorder

recorder = SessionRecorder()

@recorder.on_round_start
def on_round(session, round_num):
    print(f"第 {round_num} 轮开始...")

@recorder.on_expert_speak
def on_speak(session, expert_id, content):
    print(f"{expert_id} 说：{content[:50]}...")

@recorder.on_convergence
def on_convergence(session, consensus):
    print(f"已收敛：{consensus}")

result = think_v6(question, selected_experts=[...], recorder=recorder)
```

### 自定义 LLM 提供者

```python
from super_thinking.v6.llm import LLMProvider

class MyProvider(LLMProvider):
    def complete(self, messages, **kwargs) -> str:
        # 使用任意 LLM 后端
        return my_llm.call(messages)

pool.set_llm_provider(MyProvider())
```

---

## 设计哲学

### 为什么辩论比单一专家分析更好？

单一 AI 回答是一场**独白**。超思考 v6 创造的是一场**对话**——这才是最有生产力的思维方式。

> "井蛙不可以语于海者，拘于虚也；夏虫不可以语于冰者，笃于时也。" — 庄子

多专家辩论揭示了：
- 每位专家默认接受的**隐藏假设**
- 真正的**分歧所在**（而非虚假共识）
- 遥远领域之间的**意外联系**
- **信心校准**——每位专家的确定程度

### 架构原则

| 原则 | 实现方式 |
|------|----------|
| 专家热插拔 | `ExpertPool.register/unregister` 运行时生效 |
| 全链路可观测 | 11 个事件的 `SessionRecorder` 钩子系统 |
| 类型安全 | 全组件 Pydantic v2 模型 |
| 零魔术 | 无隐藏全局状态，配置对象显式传递 |
| 框架无关 | 每位专家均有 JSON Schema，可对接任意框架 |

---

## 性能基准

在 8 题评估集上的测试结果：

| 操作 | 时间 | 备注 |
|------|------|------|
| 2 轮辩论，3 位专家 | ~15s | 含 API 调用 |
| 1 轮辩论，1 位专家 | ~5s | 最小可用配置 |
| 模拟模式（无 API） | <1s | 基于模板 |

---

## 版本历史

### v6.0.0 — 完整重写
- 完整辩论编排器，含主持人轮次机制
- 热插拔 ExpertPool
- 可配置阈值的共识检测
- 11 事件 SessionRecorder 钩子系统
- 18 种学术框架方法论库
- 30+ 历史人物视角
- 全专家 JSON Schema 导出
- v5 兼容适配器
- CLI：`debate`、`consult`、`list` 命令

### v5.x — 旧版
- 单专家分析配合多视角投票

---

## 贡献指南

### 新增历史人物专家

1. 创建目录：`experts/people/<领域>/<姓名>-perspective/`
2. 编写 `SKILL.md`，定义该人物的思维模型
3. 生成 `schema.json`：`python scripts/sketch_to_json.py`
4. 加入 `INDEX_PEOPLE.md`

### 新增学术框架

1. 创建目录：`experts/methods/<框架名>-perspective/`
2. 编写 `SKILL.md`，定义框架的核心模型和启发式
3. 生成 `schema.json`：`python scripts/sketch_to_json.py`
4. 加入 `INDEX_METHODS.md`

---

## License

MIT License — 可自由使用、修改和分发。

---

*超思考 v6 — 与历史上最伟大的头脑对话。*
