# AgentSuperthinking v6 — v5 兼容层审查报告

> **审查范围**：`src/super_thinking/v6/compat.py`
> **审查日期**：2026-06-07
> **审查者**：technical-writer
> **关联任务**：派单规范 2.1-E（v5 兼容层）

---

## 一、目标与现状

### 1.1 兼容层定位

`compat.py` 自述：
> "v6 v5 兼容层。提供 v5 到 v6 的适配器，确保 v5 `Jury().think()` 行为不变。通过 `SUPER_THINKING_LEGACY=1` 环境变量控制。"

### 1.2 v5 与 v6 关键类型对照

| 维度 | v5 真实定义 | v6 真实定义 | compat.py 声明 |
|------|-------------|-------------|---------------|
| 结果容器 | `dataclass JuryResult` | `dataclass DebateSession` | `V5JuryResult`（手写类） |
| `outputs` 类型 | `dict[str, PerspectiveOutput]` | `tuple[ExpertStatement, ...]`（在 `Round.statements`） | `list`（**类型不符**） |
| `errors` 类型 | `dict[str, str]`（perspective_id → 错误消息） | 分散在 `ExpertStatement.warnings` | `list`（**类型不符**） |
| `routing_result` | `RoutingResult`（包含激活/未激活的 perspective_id） | 无对应概念，由 `DebateMode` 替代 | `Any = None`（**信息丢失**） |
| `Jury.think()` 签名 | `think(input, context=None, mode="auto", selective_ids=None)` | `orchestrator.run(input_text, context)` | `JuryAdapter.think(input_text, context, mode, selective_ids)`（**context 变为必填**） |
| 单条输出类 | `dataclass PerspectiveOutput` 字段：`perspective_id / perspective_name / analysis / confidence / key_points / tags / warnings / metadata` | `dataclass ExpertStatement` 字段：`expert_id / expert_name / role / content / confidence / ...` | `V5CompatibleOutput` 字段：`id / name / content / confidence / role / warnings`（**字段名错位**） |

> 注：v5 定义来自 `src/super_thinking/core/jury.py` 与 `src/super_thinking/perspectives/_interface.py`；v6 定义来自 `src/super_thinking/v6/types.py`。

---

## 二、关键缺陷（按严重度）

### 🔴 P0-01：`V5JuryResult.outputs` 类型与 v5 不一致

**位置**：`compat.py:32-72`

**v5 真实定义**（`jury.py:31`）：
```python
outputs: dict[str, PerspectiveOutput]  # perspective_id -> output
```

**compat.py 实际实现**：
```python
def __init__(self, outputs: list, errors: list, ...):
    self.outputs = outputs  # ❌ 应为 dict[str, PerspectiveOutput]
```

**影响**：
- 所有 v5 调用方调用 `result.outputs['darwin_perspective']` 时会抛 `TypeError: list indices must be integers or slices`。
- `get_outputs()` 返回 `list(outputs.values())` 行为不再成立。
- 文档"100% 保留 v5 字段集"的承诺**实际不成立**。

**修复建议**：
```python
class V5JuryResult:
    def __init__(self, outputs: dict, errors: dict, ...):
        self.outputs = outputs              # dict[str, PerspectiveOutput]
        self.errors = errors                # dict[str, str]
        ...
```

---

### 🔴 P0-02：`V5JuryResult.errors` 类型与 v5 不一致

**位置**：`compat.py:51-58`

**v5 真实定义**（`jury.py:32`）：
```python
errors: dict[str, str]  # perspective_id -> error message
```

**compat.py 实际实现**：
```python
self.errors = errors  # ❌ 应为 dict[str, str]，当前是 list
```

**影响**：v5 调用方 `result.errors['darwin_perspective']` 抛 `KeyError` 或 `TypeError`。

---

### 🔴 P0-03：`wrap_v5_perspective_output` 字段映射全部错位

**位置**：`compat.py:213-228`

**v5 PerspectiveOutput 真实字段**（`_interface.py:33-43`）：
```python
@dataclass
class PerspectiveOutput:
    perspective_id: str
    perspective_name: str
    analysis: str
    confidence: float = 0.5
    key_points: list[str]
    tags: list[str]
    warnings: list[str]
    metadata: dict[str, Any]
```

**compat.py wrap 函数实际读取**：
```python
def wrap_v5_perspective_output(output: Any) -> ExpertStatement:
    expert_id   = getattr(output, 'id', 'unknown')           # ❌ 字段是 perspective_id
    expert_name = getattr(output, 'name', 'Unknown Expert')  # ❌ 字段是 perspective_name
    content     = getattr(output, 'content', str(output))    # ❌ 字段是 analysis
    ...
    return ExpertStatement(
        expert_id=ExpertId(expert_id),  # ❌ 永远是字符串 "unknown"
        expert_name=expert_name,         # ❌ 永远是 "Unknown Expert"
        role=SpeakRole.INITIAL,
        content=content,                # ❌ 永远是 str(output) 全文
        confidence=getattr(output, 'confidence', 0.5),  # ✅
        raw=output,
    )
```

**最严重的失败模式**：
```python
from super_thinking.perspectives.darwin_perspective import DarwinPerspective
from super_thinking.v6.compat import wrap_v5_perspective_output

v5_output = DarwinPerspective().think(
    "如何理解适者生存？",
    {"mode": "analysis"}
)
# v5_output 实际有: perspective_id, perspective_name, analysis, ...

v6_stmt = wrap_v5_perspective_output(v5_output)
print(v6_stmt.expert_id)        # 输出: "unknown"  ❌ 应该是 "darwin_perspective"
print(v6_stmt.expert_name)      # 输出: "Unknown Expert"  ❌ 应该是 "Darwin"
print(v6_stmt.content[:80])     # 输出: "<PerspectiveOutput object at 0x...>"  ❌ 应该是分析正文
```

**修复建议**：
```python
def wrap_v5_perspective_output(output: Any) -> ExpertStatement:
    """将 v5 PerspectiveOutput 包装为 v6 ExpertStatement。"""
    from .types import ExpertId
    return ExpertStatement(
        expert_id=ExpertId(getattr(output, 'perspective_id', 'unknown')),
        expert_name=getattr(output, 'perspective_name', 'Unknown Expert'),
        role=SpeakRole.INITIAL,
        content=getattr(output, 'analysis', str(output)),
        confidence=float(getattr(output, 'confidence', 0.5)),
        warnings=tuple(getattr(output, 'warnings', [])),
        raw=output,
    )
```

---

### 🔴 P0-04：`JuryAdapter._convert_statement_to_v5` 反向映射同样错位

**位置**：`compat.py:174-197`

**问题**：在 v6 → v5 反向适配时，`V5CompatibleOutput` 暴露的是 `id / name / content / role`，但 v5 端代码期望 `perspective_id / perspective_name / analysis`（且 `JuryResult` 字典化存储）。**两边都拿不到正确数据**。

**修复建议**：统一为 v5 真实字段命名：
```python
def _convert_statement_to_v5(self, stmt):
    class V5PerspectiveOutput:
        def __init__(self, stmt):
            self.perspective_id   = str(stmt.expert_id)
            self.perspective_name = stmt.expert_name
            self.analysis         = stmt.content
            self.confidence       = stmt.confidence
            self.key_points       = []
            self.tags             = []
            self.warnings         = list(stmt.warnings)
            self.metadata         = {"v6_role": str(stmt.role)}
    return V5PerspectiveOutput(stmt)
```

---

### 🟠 P1-05：`JuryAdapter.think()` 签名 `context` 必填，破坏向后兼容

**位置**：`compat.py:113-116`

**v5 真实签名**（`jury.py:89`）：
```python
def think(
    self,
    input: str,
    context: Optional[dict[str, Any]] = None,  # ✅ 有默认值
    mode: str = "auto",
    selective_ids: Optional[list[str]] = None,
) -> JuryResult:
```

**compat.py JuryAdapter.think**：
```python
def think(
    self,
    input_text: str,
    context: dict | None,           # ❌ 失去默认值
    mode: str,
    selective_ids: list[str] | None,
) -> V5JuryResult:
```

**影响**：v5 调用方常见的 `jury.think("xxx")` 模式在 v6 兼容层会因 `TypeError: missing 3 required positional arguments` 而崩溃。

**修复建议**：
```python
def think(
    self,
    input_text: str,
    context: dict | None = None,    # ✅ 补回默认值
    mode: str = "auto",
    selective_ids: list[str] | None = None,
) -> V5JuryResult:
```

---

### 🟠 P1-06：缺少 Round / 多轮数据迁移路径

**v5 模型**：单轮 `JuryResult`，所有 `PerspectiveOutput` 在同一个字典中。

**v6 模型**：多轮 `DebateSession.rounds[].statements[]`。

**compat.py 现状**：仅实现"v6 单轮 → v5 单结果"，未实现：
- v5 单结果 → v6 单轮 `DebateSession` 的"数据导入"路径（用于历史 v5 案例回放）
- v6 多轮 → v5 多 `JuryResult` 列表的"批量导出"路径（用于 v5 报告工具消费 v6 数据）

**影响**：
- 历史 v5 案例库无法迁移到 v6 进行复盘/对照实验。
- v5 时代开发的报告/审计工具无法消费 v6 输出。

**修复建议**（建议性 v5→v6 迁移示例）：
```python
# === 推荐: v5 → v6 历史数据迁移工具 ===

def migrate_v5_result_to_v6_session(
    v5_result: "JuryResult",          # v5 类型，仅类型注解
    user_question: str,
) -> "DebateSession":
    """
    将 v5 单次 JuryResult 迁移为 v6 单轮 DebateSession。
    
    用于: 历史 v5 案例库导入 v6 复盘系统。
    """
    from .types import (
        DebateSession, Round, RoundNumber, SessionId,
        SessionStatus, DebateConfig, DebateMode,
    )
    from .types import ExpertId
    from datetime import datetime

    statements = tuple(
        wrap_v5_perspective_output(v5_output)
        for v5_output in v5_result.outputs.values()
    )
    round_obj = Round(
        number=RoundNumber(1),
        role_speaker=SpeakRole.INITIAL,
        statements=statements,
        started_at=datetime.utcnow().isoformat(),
    )
    return DebateSession(
        session_id=SessionId(f"migrated-{datetime.utcnow().timestamp()}"),
        user_question=user_question,
        config=DebateConfig(mode=DebateMode.NON_DEBATE, max_rounds=1),
