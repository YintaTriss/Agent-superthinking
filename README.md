# Agent-Superthinking v6

> **与历史上最伟大的头脑一起思考。** 一个多专家辩论框架，模拟不同视角之间的真实思想交锋——从苏格拉底的辩证法到爱因斯坦的科学严谨，从孙子的军事战略到芒格的心智模型。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Version: 6.0](https://img.shields.io/badge/Version-6.0-green.svg)]()

**[简体中文](./README.md) | [繁體中文](./README_TW.md)**

---

## 核心特性

| 特性 | 说明 |
|------|------|
| **多专家辩论** | 不是单专家分析，而是多轮真实交锋：发言 → 反驳 → 回应 |
| **并行发言** | 每轮专家同时发言（ADR-005：ThreadPoolExecutor + 字典序排序） |
| **收敛判断** | `score = 0.4·overlap + 0.4·(1−new_arg_density) + 0.2·(1−drift)`，阈值 0.65 |
| **动态专家池** | 热插拔：辩论中途加入或离开专家（ADR-001） |
| **11 个 Recorder Hook** | 全链路可观察：轮次/发言/收敛/结论全部可监听 |
| **双轨论点解析** | LLM 语义评估 + 结构化解析器机械过滤（ADR-002） |
| **外部咨询** | 同步阻塞，每轮最多 2 次，单次超时 30s（ADR-004） |
| **v5 兼容** | `Jury().think()` 委托 v6 单轮退化模式，不破坏 I1（ADR-003） |

---

## 架构总览

```
                        ┌─────────────────────────────────────────┐
   User Question        │            Router Layer                  │
  ─────────────────────►│  读取 INDEX_PEOPLE.md / INDEX_METHODS.md │
                        │  分类：人物？方法论？混合？               │
                        └──────────────────┬──────────────────────┘
                                           │
                    ┌───────────────────────┼───────────────────────┐
                    ▼                       ▼                       ▼
            ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
            │   人物轨道    │      │  方法论轨道   │      │   混合模式   │
            │   (People)   │      │  (Methods)   │      │   (Both)    │
            └──────┬───────┘      └──────┬───────┘      └──────┬───────┘
                   │                     │                     │
                   └─────────────────────┼─────────────────────┘
                                         │
                        ┌────────────────▼────────────────────┐
                        │     DebateOrchestrator（编排器）      │
                        │                                      │
                        │  ┌────────────────────────────────┐ │
                        │  │  Moderator（主持人）            │ │
                        │  │  • execute_round()            │ │
                        │  │  • build_argument_menu()      │ │
                        │  │  • detect_convergence()       │ │
                        │  │  • decide() — 轮次决策          │ │
                        │  └────────────────────────────────┘ │
                        │              ▲                     │
                        │              │                     │
                        │  ┌───────────┴───────────────┐     │
                        │  │  ExpertPool（热插拔）      │     │
                        │  │  register / unregister   │     │
                        │  └───────────────────────────┘     │
                        └──────────────────┬──────────────────┘
                                           │
                        ┌──────────────────▼──────────────────┐
                        │       Fusion Layer（融合层）          │
                        │  • 冲突检测                          │
                        │  • 共识提取                          │
                        │  • 结构化报告（共识点 + 分歧点 + 行动建议）│
                        └───────────────────────────────────┘
```

### 分层依赖关系

```
entrypoint（外部 API）
  └─ orchestrator（会话/轮次/终态）
       ├─ moderator ← 主持人决策（LLM + 结构化）
       ├─ expert_pool ← 热插拔专家注册表
       ├─ convergence ← 收敛算法
       ├─ recorder ← 11 个事件钩子
       ├─ compat ← v5 JuryAdapter（I1 不变式）
       └─ llm ← Provider 注入（可替换后端）
```

---

## 8 个设计不变式

| # | 不变式 | 说明 |
|---|--------|------|
| **I1** | 向后兼容 | `Jury().think(...)` 调用行为不破坏 |
| **I2** | 纯标准库优先 | 核心仅依赖 Python ≥ 3.10 标准库 |
| **I3** | 可测试性 | 每个决策点 Protocol 注入，纯 mock 可测 |
| **I4** | 可观察性 | 11 个 SessionRecorder 钩子覆盖全链路 |
| **I5** | 可扩展性 | 动态专家池热插拔，注册新专家无需改主持人 |
| **I6** | 可移植性 | 单一 Python 进程，无外部服务依赖 |
| **I7** | 确定性入口 | LLM Provider 注入，离线可注入 DeterministicProvider |
| **I8** | 轮次有界 | 最大 5 轮硬上限，防止无界循环 |

---

## 5 个架构决策（ADR）

| ADR | 决策 | 核心内容 |
|-----|------|---------|
| **ADR-001** | 辩论形式 = 结构化圆桌 | Model C：主持人组织、专家交锋、动态池 |
| **ADR-002** | 双轨论点解析 | 结构化解析器（机械过滤）+ Moderator LLM（语义评估）|
| **ADR-003** | v5 走 v6 单轮退化 | `Jury.think()` 内部委托 `JuryAdapter`，单一代码路径 |
| **ADR-004** | 同步阻塞外部咨询 | ThreadPoolExecutor，每轮 ≤ 2 次，超时 30s |
| **ADR-005** | 并行专家发言 | `ThreadPoolExecutor` 并发调用 `expert.speak()`，字典序排序写入 |

---

## 收敛算法

每轮辩论结束后，主持人计算收敛分数：

```
score = 0.4 × overlap
      + 0.4 × (1 − new_arg_density)
      + 0.2 × (1 − drift)

overlap         = 本轮与上一轮论点重叠度（0~1）
new_arg_density = 新增论点数 / 本轮总论点数的密度
drift           = 专家立场漂移程度（0~1）

判断：score ≥ 0.65 持续 1 轮 → 收敛
```

---

## 核心组件

| 组件 | 文件 | 职责 |
|------|------|------|
| `think_v6()` / `convene_v6()` | `entrypoint.py` | 单次调用入口 / 程序化 API |
| `DebateOrchestrator` | `orchestrator.py` | 管理完整辩论生命周期 |
| `DefaultModerator` | `moderator/moderator.py` | 每轮执行、论点菜单构建、收敛判断 |
| `ExpertPool` | `expert_pool.py` | 热插拔专家注册表 |
| `ConvergenceDetector` | `convergence_detector/detector.py` | 收敛状态检测 |
| `SessionRecorder` | `recorder/recorder.py` | 11 个事件钩子（轮次/发言/收敛/结论）|
| `MethodologyRegistry` | `methodology.py` | 18 个学术框架 |
| `JuryAdapter` | `compat.py` | v5 → v6 兼容适配器（I1 不变式）|
| `LLMProvider` | `llm/` | 可注入的 LLM 后端（openai_compat / deterministic / mock）|

### v6 模块结构

```
src/super_thinking/v6/
├── __init__.py              # 公开 API 导出
├── entrypoint.py            # think_v6() / convene_v6()
├── orchestrator.py           # DebateOrchestrator
├── compat.py                # JuryAdapter（v5 兼容）
├── types.py                 # Pydantic 数据模型
├── expert_pool.py           # ExpertPool
├── argument_menu.py         # ArgumentMenu / ArgumentItem
├── expert_statement.py      # ExpertStatement / ParseResult
├── expert_recommender.py    # 专家推荐
├── methodology.py           # MethodologyRegistry（18 个框架）
├── convergence.py           # 收敛计算
├── convergence_detector/    # 收敛检测器
├── expert/                  # 专家定义
├── interaction/             # 外部咨询
├── llm/                     # LLM Provider
├── moderator/               # 主持人
├── prompts/                # Prompt 模板
└── recorder/               # SessionRecorder
```

---

## 辩论流程

```
用户提问
    │
    ▼
┌─────────────────────────┐
│  Round 1：开场发言       │
│  每位专家并行 speak()     │  ← ADR-005
│  字典序排列写入 Round     │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  主持人：构建论点菜单     │  ← ADR-002 双轨解析
│  选择下一位发言专家       │
│  计算收敛分数            │
└───────────┬─────────────┘
            │ score ≥ 0.65？
      ┌─────┴─────┐
      │  否        │  是
      ▼            ▼
┌──────────┐  ┌─────────────────┐
│ Round 2  │  │ 收敛 → 输出报告   │
│ (反驳)   │  │                 │
└────┬─────┘  │ 共识点           │
      │       │ 分歧点           │
      ▼       │ 未解决矛盾       │
  ...        │ 行动建议          │
             └─────────────────┘
```

---

## 快速开始

### CLI — 辩论模式

```bash
# 交互式辩论（推荐）
super_thinking debate "AI 是否会取代人类创造力？"

# 指定专家和轮次
super_thinking debate "AI 治理的最佳策略是什么？" \
  --experts socrates,confucius,einstein \
  --rounds 3

# Mock 模式（无需 API Key）
super_thinking debate "数字时代的隐私还存在吗？" \
  --experts confucius,socrates \
  --mock

# JSON 输出（程序化使用）
super_thinking debate "经济不平等的根源是什么？" \
  --experts keynes,hayek,smith \
  --format json

# 列出所有专家
super_thinking list

# 单专家咨询（比完整辩论更快）
super_thinking consult "时间的本质是什么？" --expert socrates
```

### Python API

```python
from super_thinking.v6 import think_v6, DebateConfig

# 简单调用
result = think_v6(
    question="应该优先经济发展还是环境保护？",
    selected_experts=["confucius", "hayek", "einstein"],
    config=DebateConfig(max_rounds=2)
)
print(result["final_report"])
```

### Python API — 程序化控制

```python
from super_thinking.v6 import (
    convene_v6, DebateConfig, ExpertPool,
    SessionRecorder, ConvergenceDetector
)
from super_thinking.v6.llm import DeterministicProvider

# 自定义配置
pool = ExpertPool()
pool.register(my_custom_expert)

config = DebateConfig(
    max_rounds=3,
    convergence_threshold=0.75,
    temperature=0.7,
)

# 可观察：使用 SessionRecorder 钩子
recorder = SessionRecorder()

@recorder.on_round_start
def on_round(session, round_num):
    print(f"Round {round_num} 开始")

@recorder.on_statement
def on_statement(stmt):
    print(f"专家 {stmt.expert_id}：{stmt.content[:50]}...")

@recorder.on_convergence
def on_convergence(signal):
    print(f"收敛信号：{signal}")

result = convene_v6(
    question="苦难的意义是什么？",
    selected_experts=["socrates", "buddha", "nietzsche"],
    expert_pool=pool,
    config=config,
    recorder=recorder,
)
```

### v5 → v6 迁移

```python
# v5（遗留）
from super_thinking import Jury
jury = Jury()
result = jury.think(question, model_names=["socrates", "confucius"])

# v6（当前）
from super_thinking.v6 import think_v6, DebateConfig
result = think_v6(
    question=question,
    selected_experts=["socrates", "confucius"],
    config=DebateConfig(max_rounds=2)
)

# v6 兼容模式（JuryAdapter，行为与 v5 完全一致）
from super_thinking.v6.compat import JuryAdapter
adapter = JuryAdapter()
result = adapter.think(question, model_names=["socrates", "confucius"])
```

---

## 专家库（30+ 专家）

### 人物轨道 — 历史人物

| 领域 | 专家 | 关键词 |
|------|------|--------|
| 哲学 | 苏格拉底、柏拉图、亚里士多德、康德、尼采、笛卡尔、休谟、老子、庄子、维特根斯坦、萨特、马克思 | 辩证法、理念论、德性论、批判、意志、怀疑、经验主义、道家、无为、语言哲学、存在主义、唯物主义 |
| 文学 | 但丁、陀思妥耶夫斯基、卡夫卡、鲁迅 | 神曲、复调文学、荒诞、启蒙精神 |
| 科学 | 爱因斯坦、牛顿、波尔、居里夫人、麦克斯韦、薛定谔、图灵、高斯、欧几里得、哥德尔 | 相对论、重力学、量子力学、放射性、电磁学、波函数、计算、统计、几何、不完备性 |
| 经济 | 斯密、凯恩斯、哈耶克、稻盛和夫 | 自由市场、宏观经济学、奥地利学派、稻盛哲学 |
| 军事 | 孙子、克劳塞维茨 | 孙子兵法、总体战 |
| 心理学 | 弗洛伊德、荣格、埃里克森、罗杰斯、米德、福柯 | 精神分析、集体无意识、发展心理学、以人为中心、符号互动、权力/知识 |
| 宗教 | 佛陀、王阳明 | 八正道、知行合一 |

### 方法论轨道 — 学术框架

| 类别 | 框架 |
|------|------|
| 哲学 | 现象学、分析哲学、伦理学、政治哲学 |
| 社会科学 | 人类学、社会学、传播学 |
| 跨学科 | 美学、语言学、教育学、管理学、控制论、法理学、运筹学 |
| 分析方法 | 贝叶斯推理、批判性思维、设计思维、系统思维 |
| 计算 | 信息论、网络理论、复杂科学、量子思维 |
| 决策 | 博弈论、进化心理学 |

---

## SessionRecorder — 11 个事件钩子

```python
recorder = SessionRecorder()

# 会话级
@recorder.on_session_start
def on_session_start(session): ...

@recorder.on_session_end
def on_session_end(session, final_report): ...

# 轮次级
@recorder.on_round_start
def on_round_start(session, round_num): ...

@recorder.on_round_end
def on_round_end(session, round_num, round_obj): ...

# 发言级
@recorder.on_statement
def on_statement(stmt): ...

# 论点菜单级
@recorder.on_menu_built
def on_menu_built(menu): ...

# 收敛级
@recorder.on_convergence
def on_convergence(signal): ...

@recorder.on_divergence
def on_divergence(session): ...

# 决策级
@recorder.on_moderator_decision
def on_decision(decision): ...

# 外部咨询级
@recorder.on_consultation_request
def on_consult(req): ...

@recorder.on_consultation_response
def on_response(resp): ...
```

---

## 自定义 LLM Provider

```python
from super_thinking.v6.llm import LLMProvider

class MyProvider(LLMProvider):
    def complete(self, messages, **kwargs) -> str:
        # 使用任何 LLM 后端
        return my_llm.call(messages)

# 注入到 ExpertPool
pool = ExpertPool()
pool.set_llm_provider(MyProvider())
```

---

## 安装

```bash
# 从源码安装
cd agent-superthinking-v6
pip install -e .

# 可选：美化输出
pip install rich
```

### 核心依赖

```
typer>=0.12.0        # CLI 框架
pydantic>=2.0        # 类型验证
```

---

## 性能基准

| 配置 | 时间 | 备注 |
|------|------|------|
| 2 轮辩论，3 专家 | ~15s | 含 API 调用 |
| 1 轮辩论，1 专家 | ~5s | 最小配置 |
| Mock 模式（无 API）| <1s | 模板响应 |

---

## CLI 命令参考

| 命令 | 说明 |
|------|------|
| `debate <问题>` | 启动多专家辩论 |
| `debate <问题> --experts socrates,confucius --rounds 3` | 指定专家和轮次 |
| `debate <问题> --mock` | Mock 模式（无需 API Key）|
| `debate <问题> --format json` | JSON 输出 |
| `list` | 列出所有可用专家 |
| `consult <问题> --expert <id>` | 单专家咨询 |
| `--help` | 显示所有选项 |

---

## 为什么是多专家辩论？

单 AI 响应是**独白**。Superthinking v6 创造的是**对话**——最高效的推理形式。

多专家辩论能暴露：
- 每个专家默认**隐藏的假设**
- 真正的**分歧** vs 虚假共识
- 远距领域间的**意外联系**
- **信心校准**——每位专家的确定程度

---

## 变更记录

### v6.0.0 — 完整重写

- 多专家辩论编排器（含主持人）
- ADR-005 并行专家发言（ThreadPoolExecutor）
- 热插拔 ExpertPool
- 收敛检测（可配置阈值 0.65）
- 11 个 SessionRecorder 钩子
- 18 个学术框架方法论库
- 30+ 历史人物专家
- JSON Schema 导出（框架无关）
- v5 兼容适配器（I1 不变式）
- CLI（debate / consult / list）

### v5.x — 遗留版本

- 单专家分析（多视角）
- Jury 投票聚合

---

## 许可证

MIT License — 可自由使用、修改和分发。

---

_Agent-Superthinking v6 — 与历史上最伟大的头脑一起思考。_
