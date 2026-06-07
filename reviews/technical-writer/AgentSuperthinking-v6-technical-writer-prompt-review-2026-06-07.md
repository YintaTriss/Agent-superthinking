# AgentSuperthinking v6 — Prompt 完整性审查报告

> **审查范围**：`src/super_thinking/v6/prompts/` 目录下所有 Prompt 模板
> **审查日期**：2026-06-07
> **审查者**：technical-writer
> **关联任务**：派单规范 2.1-D（Prompt 完整性）

---

## 一、文件清单与基线检查

### 1.1 数量核对

派单规范要求"prompts/ 目录下所有 .md 模板都存在且非空（共 15 个 .md）"。

**实际盘点结果**：11 个 .md 文件，**与规范差异 -4**。

| # | 文件名 | 字节数 | 行数 | 用途定位 | 状态 |
|---|--------|--------|------|----------|------|
| 1 | `CONVERGENCE_CHECK.md` | 2195 | 86 | 收敛判断（每轮调用） | ✅ 存在且非空 |
| 2 | `expert_final.md` | 1276 | 53 | 专家最终陈述（最终轮） | ✅ 存在且非空 |
| 3 | `expert_initial.md` | 1124 | 41 | 专家独立陈述（第1轮） | ✅ 存在且非空 |
| 4 | `expert_rebuttal.md` | 1365 | 49 | 专家针对发言（中间轮） | ✅ 存在且非空 |
| 5 | `EXPERT_SYSTEM.md` | 2418 | 92 | 专家系统 Prompt | ✅ 存在且非空 |
| 6 | `EXPERT_USER_QUESTION.md` | 1842 | 69 | 专家向用户提问 | ✅ 存在且非空 |
| 7 | `external_consult.md` | 1282 | 52 | 外部专家咨询 | ✅ 存在且非空 |
| 8 | `FINAL_SYNTHESIS.md` | 2733 | 157 | 最终综合结论 | ✅ 存在且非空 |
| 9 | `menu_extraction.md` | 1556 | 51 | 论点菜单抽取 | ✅ 存在且非空 |
| 10 | `MODERATOR_SYSTEM.md` | 2072 | 71 | 主持人系统 Prompt | ✅ 存在且非空 |
| 11 | `ROUND_SUMMARY.md` | 1681 | 86 | 轮次摘要 | ✅ 存在且非空 |
| — | **缺失（应15个）** | — | — | 4 个未识别 | ⚠️ 见 §1.2 |

### 1.2 与规范数量差异分析

派单规范声明 15 个，实际仅 11 个。可能原因：

1. **规范过期**：规范基于早期版本，当前 v6-implementation-clean 已收敛至 11 个。需 Leader 确认目标版本。
2. **缺失文件类型**（基于代码交叉对比推测）：
   - 缺少 `EXPERT_*_PROFILE.md` 系列（专家画像注入模板，目前可能由 `EXPERT_SYSTEM.md` 合并承担）
   - 缺少 `DEBATE_OPENING.md`（开篇白板/题目陈述）
   - 缺少 `JUDGE_BREAKTIE.md`（同票裁决 prompt）
   - 缺少 `CONTEXT_RECAP.md`（长辩论上下文重述）

**建议行动**：以代码实际 `prompts/loader.py` 加载的清单为准更新规范；若 4 个缺失文件确属规划，则需补齐（见 P1-01）。

---

## 二、5 个核心 Prompt 评分（1-5 分）

### 2.1 `MODERATOR_SYSTEM.md` — **4 / 5**

**核心作用**：定义主持人在辩论中的角色、收敛判断、决策输出。

| 评估维度 | 得分 | 说明 |
|----------|------|------|
| 角色定义清晰度 | 5/5 | "中立引导/流程控制/收敛判断/决策生成"四职责清单明确，且附"不提供观点/仅必要时介入/保护少数意见/透明决策"四条行为约束。 |
| 收敛算法可执行性 | 5/5 | 软/硬收敛双轨制，权重公式 `0.4/0.4/0.2` 显式给出，指标取值范围 [0,1] 清晰。 |
| 输出格式可机器解析 | 4/5 | 三类 JSON（轮次发言/收敛检测/决策）字段齐整。`action` 枚举值 `continue/converge/enter_final/ask_user/abort` 完整。 |
| 异常场景兜底 | 2/5 | **缺失**：未定义"专家全部静默/全部超时/全部拒绝发言"时的降级决策模板；未规定"用户问题超长"如何裁剪。 |
| 用户可读性 | 3/5 | 收敛检测 JSON 含 `reason` 字段，但未提供"如何把内部信号翻译给终端用户"的措辞模板。 |

**改进建议**：
- 新增"异常决策"章节：覆盖 `all_silent` / `all_timeout` / `conflicts_too_high` 三种场景的默认 `action`。
- 新增 `decision.user_facing_reason: str` 字段，将"reason"分为内部日志与面向用户两版。

---

### 2.2 `expert_initial.md` — **5 / 5**

**核心作用**：第 1 轮专家独立陈述。

| 评估维度 | 得分 | 说明 |
|----------|------|------|
| 角色定位 | 5/5 | "第 1 轮、各自独立、不针对任何人"三个边界条件清晰。 |
| 发言要求 | 5/5 | 观点明确 / 理由充分 / 格式规范 / 长度适中（300-500 字）四项要求齐全。 |
| 格式可解析 | 5/5 | 输出模板"我认为 / 理由 / 局限性"三段式与 `ExpertStatement.content + confidence` 字段对应。 |
| 抗诱导 | 5/5 | "不要提及其他专家 / 不要用'问题很复杂' / 信息不足需明示"三条禁忌。 |
| 异常兜底 | 4/5 | 唯一瑕疵：未规定"专家拒绝回答/不输出"时的回退（如要求 3 句话最低占位）。 |

**改进建议**：
- 末尾追加最低占位要求："若无法形成观点，输出 `[REFUSED] 原因：...`"以便 Moderator 决策。

---

### 2.3 `expert_rebuttal.md` — **4 / 5**

**核心作用**：第 2 轮及之后的专家针对发言。

| 评估维度 | 得分 | 说明 |
|----------|------|------|
| 引用机制 | 5/5 | `[A1]/[A2]` 编号强制引用，避免"无对象反驳"。 |
| 立场表达 | 5/5 | "支持 / 反对 / 补充"三分类 + 模板示例，逻辑可追溯。 |
| 长度控制 | 5/5 | 200-400 字 + 禁止重复第 1 轮发言，避免循环辩论。 |
| 上下文衔接 | 4/5 | 提供 `previous_statement` 与 `menu_content` 两个占位符。 |
| 异常兜底 | 2/5 | **缺失**：当 `menu_content` 为空（第 2 轮菜单生成失败）时未给出降级策略；未规定"全部支持/全部反对"极端分布的处理。 |

**改进建议**：
- 显式处理 `menu_content` 为空分支："若菜单为空，请直接给出你的补充观点并标注 `[NO_MENU]`"。

---

### 2.4 `expert_final.md` — **5 / 5**

**核心作用**：辩论最终轮的专家立场综合。

| 评估维度 | 得分 | 说明 |
|----------|------|------|
| 综合导向 | 5/5 | "不再针对个人"清晰切分与 rebuttal 的边界。 |
| 多维输出 | 5/5 | 共识 / 分歧 / 建议三段式覆盖决策全要素。 |
| 可操作性 | 5/5 | "下一步建议"明确要求"可执行、可验证"。 |
| 与下游衔接 | 5/5 | 输出字段与 `FINAL_SYNTHESIS.md` 的 `consensus_points / divergence_points / suggestions` 一一对应。 |
| 异常兜底 | 4/5 | 唯一瑕疵：未规定"专家在最终轮选择保持沉默/拒绝表态"时的兜底。 |

**改进建议**：
- 末段加一句："若你仍拒绝表态，输出 `[ABSTAIN] 原因：...`，由主持人决定是否计入共识。"。

---

### 2.5 `CONVERGENCE_CHECK.md` — **4 / 5**

**核心作用**：每轮结束后判断是否收敛。

| 评估维度 | 得分 | 说明 |
|----------|------|------|
| 算法可复现 | 5/5 | 综合得分公式 + 权重 + 三指标定义 + 软硬阈值，可直接编程。 |
| 输出可解析 | 5/5 | 含 `consecutive_count`，便于主持人追踪软收敛连续轮次。 |
| 软/硬双轨 | 5/5 | `converged` 与 `hard_converged` 分离，给主持人弹性。 |
| 上下文衔接 | 4/5 | 含 `prev_convergence_signal` 占位符。 |
| 异常兜底 | 2/5 | **缺失**：`prev_convergence_signal` 缺失（首轮）时模板未给出"视为空"或"视为未收敛"指令；`overlap`/`density`/`drift` 任一缺失时（如专家未输出）未规定 fallback。 |

**改进建议**：
- 显式声明：`{prev_convergence_signal}` 缺省 = `{"converged": false, "consecutive_count": 0}`。
- 当 `num_experts=0` 时，`score` 应直接置 0 并返回 `converged: false`（仅在 `convergence.py` 中实现，prompt 端需说明）。

---

### 2.6 附：`FINAL_SYNTHESIS.md` — **5 / 5**（虽未列入"5 个核心"清单，但属于必查项）

**核心作用**：多轮辩论结束后生成最终综合结论。

| 评估维度 | 得分 | 说明 |
|----------|------|------|
| 输出维度 | 5/5 | 六维：共识 / 分歧 / 根本矛盾 / 行动建议 / 开放问题 / 置信度，覆盖决策全要素。 |
| 可操作性 | 5/5 | 行动建议按时序分"短期 1-3 月 / 中期 3-12 月 / 长期 1 年以上"。 |
| 置信度量化 | 5/5 | "结论 / 置信度 / 专家认同度"三列表格，含 `overall_confidence` 数值。 |
| 格式双轨 | 5/5 | Markdown 可读 + JSON 可解析双输出。 |
| 异常兜底 | 4/5 | 唯一瑕疵：`{中间轮次论点摘要}` 字段为自由文本占位，未给出"超过 10 轮如何截断"或"如何挑选代表性发言"的降级规则。 |

**改进建议**：
- 在 `{中间轮次论点摘要}` 后追加："若总轮次 > 10，仅保留分歧度最高的 3 轮"。

---

## 三、跨 Prompt 一致性检查

### 3.1 命名一致性

- 大小写不统一：核心文件 6 个中 2 个全大写（`MODERATOR_SYSTEM.md`、`CONVERGENCE_CHECK.md`、`FINAL_SYNTHESIS.md`、`EXPERT_SYSTEM.md`、`EXPERT_USER_QUESTION.md`），4 个小写（`expert_initial.md`、`expert_rebuttal.md`、`expert_final.md`、`external_consult.md`、`menu_extraction.md`、`ROUND_SUMMARY.md`）。
- 风险：在大小写敏感的文件系统（Linux 部署）会导致 import 失败。**建议统一为小写**（P2-01）。

### 3.2 字段对齐

- `expert_final.md` 输出 ⇄ `FINAL_SYNTHESIS.md` 输入：共识/分歧/建议三段对齐 ✅
- `expert_initial/rebuttal.md` 输出 ⇄ `menu_extraction.md` 输入：未显式约束菜单抽取的最小粒度，存在"专家一句话也被抽成 1 条论点"的过抽取风险。
- `MODERATOR_SYSTEM.md` 决策 JSON ⇄ `orchestrator.py` 行为：未在 prompt 中显式说明 `enter_final` 与 `converge` 的差异（`enter_final` 应跳过后续 rebuttal 轮次）。

### 3.3 字符/长度控制

- `expert_initial.md` 300-500 字 vs `expert_rebuttal.md` 200-400 字 vs `expert_final.md` 无显式长度要求 —— 不一致。建议 `expert_final.md` 显式 400-600 字（P2-02）。

---

## 四、总体评分

| 文件 | 评分 | 关键问题 |
|------|------|----------|
| `MODERATOR_SYSTEM.md` | 4/5 | 缺异常场景决策模板 |
| `expert_initial.md` | 5/5 | 完备 |
| `expert_rebuttal.md` | 4/5 | `menu_content` 空兜底缺失 |
| `expert_final.md` | 5/5 | 完备 |
| `CONVERGENCE_CHECK.md` | 4/5 | 首轮 `prev_signal` 缺省值未声明 |
| `FINAL_SYNTHESIS.md` | 5/5 | 轮次 > 10 时的降级未说明 |
| **其余 5 个** | 待代码交叉验证 | 由 code-reviewer 验证模板加载逻辑 |

**平均分**：4.50 / 5（5 个核心）；4.67 / 5（含 FINAL_SYNTHESIS）

---

## 五、改进建议（按 P0/P1/P2 排序）

### P1 — 应在下个迭代修复

- **P1-01**：与 Leader 确认 15 vs 11 的差异，补齐缺失的 4 个 prompt（若确属规划）。
- **P1-02**：`MODERATOR_SYSTEM.md` 新增"异常决策"章节（`all_silent` / `all_timeout` / `conflict_too_high`）。
- **P1-03**：`CONVERGENCE_CHECK.md` 显式声明首轮 `prev_convergence_signal` 缺省值与"专家为 0"的 fallback。

### P2 — 优化项

- **P2-01**：统一 prompts 目录文件名为小写，避免 Linux 部署问题。
- **P2-02**：`expert_final.md` 显式声明 400-600 字长度。
- **P2-03**：`FINAL_SYNTHESIS.md` 增加"轮次 > 10 时的代表性发言挑选"规则。
- **P2-04**：`expert_rebuttal.md` 显式处理 `menu_content` 为空场景。
- **P2-05**：`MODERATOR_SYSTEM.md` 决策 JSON 增 `user_facing_reason` 字段。

---

## 六、证据链

- 文件清单：`bash ls -la prompts/`
- 字节/行数：`bash wc -c/-l *.md`
- 全文内容：已逐文件 `cat` 完整审阅
- 字段对齐交叉验证：与 `types.py:ExpertStatement` / `types.py:ConvergenceSignal` 字段对照

> 报告完。下一步将完成 E（v5 兼容层）审查。
