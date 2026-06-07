# Agent-Superthinking

> 多维度思考框架：输入问题 → 路由层判断 → 用户选择轨别 → 并行分析 → 冲突检测 → 综合报告。

**面向 AI 框架设计**：模块化、可扩展、按需加载，适合集成到各类 AI Agent 系统。

## 核心架构

```
用户问题
    ↓
┌──────────────────────────────────────┐
│  路由层（Router）                    │
│  - 读取 INDEX_PEOPLE.md（人物索引）  │
│  - 读取 INDEX_METHODS.md（方法论索引）│
│  - 判断涉及哪些专家团                 │
└──────────────────────────────────────┘
    ↓
┌──────────────────────────────────────┐
│  用户选择轨别：                       │
│  [1] 人物型（历史人物视角）          │
│  [2] 方法论型（学术框架视角）        │
│  [3] 双轨组合（最全面）              │
│  [4] 自定义                          │
└──────────────────────────────────────┘
    ↓
被选中的专家/框架并行分析
    ↓
┌──────────────────────────────────────┐
│  融合层（Fusion）                    │
│  - 冲突检测                          │
│  - 共识提炼                          │
│  - 结构化综合报告                     │
└──────────────────────────────────────┘
```

## 双轨专家系统

### 人物型（People）

蒸馏自真实历史人物，捕捉其思维方式。适合：价值观判断、决策启发、人性洞察。

**人物统计：4 位**

| 领域 | 人数 | 代表人物 |
|------|------|---------|
| 文学 | 4 | 但丁、陀思妥耶夫斯基、卡夫卡、鲁迅 |

### 方法论型（Methods）

整合自成熟学术框架/学派，无单一人物代表。适合：分析工具、量化方法、系统建模。

**方法论统计：14 个**

| 类别 | 框架 | 核心贡献 |
|------|------|---------|
| 哲学 | 分析哲学、伦理学、政治哲学、现象学 | 语言分析、正义、悬置 |
| 社会学 | 人类学、社会学、传播学 | 民族志、制度、议程设置 |
| 学科 | 美学、语言学、教育学、管理学 | 美感、语法、SWOT |
| 学科 | 控制论、法理学、运筹学 | 反馈控制、正义、线性规划 |

---

## 跨框架兼容性

### 三种格式支持

| 格式 | 文件 | 用途 |
|------|------|------|
| **SKILL.md** | `experts/*/SKILL.md` | OpenClaw Skill 直接使用 |
| **schema.json** | `experts/*/schema.json` | 任何框架 JSON 解析即用 |
| **INDEX** | `INDEX_PEOPLE.md`, `INDEX_METHODS.md` | 路由层索引 |

### JSON Schema（通用格式）

每个专家同时生成 `schema.json`，任何 AI 框架都能解析：

```json
{
  "name": "socrates-perspective",
  "type": "people",
  "domain": "philosophy",
  "displayName": "苏格拉底",
  "keywords": ["苏格拉底", "辩证法", "自知无知"],
  "models": [...],
  "heuristics": [...],
  "dna": {...},
  "limits": [...],
  "source": {...},
  "version": "1.0.0"
}
```

详细 Schema 定义见 [SCHEMA.md](./SCHEMA.md)

### 框架适配示例

#### OpenClaw（原生支持）
```markdown
> 帮我分析：AI会不会取代人类？
```

#### LangChain
```python
from langchain.tools import Tool
import json

# 加载任意专家
with open("experts/gametheory-perspective/schema.json") as f:
    expert = json.load(f)

tool = Tool(
    name=expert["displayName"],
    func=lambda x: analyze_with_expert(x, expert),
    description=f"Use {expert['displayName']} perspective"
)
```

#### LlamaIndex
```python
from llama_index.tools import FunctionTool
import json

with open("experts/bayesian-perspective/schema.json") as f:
    schema = json.load(f)

tool = FunctionTool.from_defaults(
    fn=analyze_bayesian,
    name=schema["name"],
    description=f"Bayesian reasoning tool"
)
```

#### Claude Code
```bash
# 读取专家 JSON
cat experts/socrates-perspective/schema.json | jq '.models[]'
```

#### 自定义 Agent
```python
import json

def load_expert(name: str):
    with open(f"experts/{name}/schema.json") as f:
        return json.load(f)

socrates = load_expert("socrates-perspective")
for model in socrates["models"]:
    print(f"{model['name']}: {model['summary']}")
```

---

## AI 框架集成

### 方式一：OpenClaw Skill（推荐）

```markdown
> 帮我分析：AI会不会取代人类？

[路由器展示路由结果]
→ 用户选择轨别和粒度
→ 系统自动加载对应专家 SKILL.md
→ 并行分析 → 融合报告
```

触发词：`思考`、`分析`、`深度分析`、`多视角`

### 方式二：Python 包

```bash
pip install agent-superthinking
```

```python
from super_thinking import Router, Fusion, Registry

# 初始化
router = Router()
registry = Registry()
fusion = Fusion()

# 1. 路由
question = "AI会不会取代人类？"
routes = router.route(question)  # 返回涉及哪些专家团

# 2. 用户选择后，加载专家
selected = ["philosophy", "gametheory", "complexity"]
experts = registry.load(selected)  # 按需加载，不全量

# 3. 并行分析（各框架自行分析）
results = [expert.analyze(question) for expert in experts]

# 4. 融合报告
report = fusion.fuse(results)
print(report)
```

### 方式三：JSON Schema（任意框架）

```python
import json
from pathlib import Path

# 遍历所有专家
for schema_path in Path("experts").rglob("schema.json"):
    expert = json.loads(schema_path.read_text())
    print(f"{expert['displayName']}: {len(expert['models'])} models")
```

---

## 目录结构

```
Agent-superthinking/
├── SKILL.md                    # OpenClaw Skill 入口
├── INDEX_PEOPLE.md            # 人物索引（路由层读取）
├── INDEX_METHODS.md            # 方法论索引（路由层读取）
├── SCHEMA.md                  # JSON Schema 定义
├── README.md                  # 本文件
├── LICENSE                    # MIT
├── pyproject.toml             # Python 包配置
├── scripts/
│   └── sketch_to_json.py     # SKILL.md → JSON 转换脚本
├── src/super_thinking/        # Python 包源码
│   ├── __init__.py
│   ├── core/
│   │   ├── router.py         # 路由层
│   │   ├── registry.py        # 专家注册
│   │   └── jury.py            # 评审层
│   ├── fusion/
│   │   ├── conflict.py        # 冲突检测
│   │   ├── consensus.py       # 共识提炼
│   │   └── formatter.py       # 报告格式化
│   └── experts/               # 内置专家实现
│       └── ...
├── experts/
│   ├── people/                # 人物型专家（4位）
│   │   └── literature/        # 文学人物：但丁、陀思妥耶夫斯基、卡夫卡、鲁迅
│   │       └── <name>-perspective/
│   │           ├── SKILL.md       # OpenClaw Skill
│   │           └── schema.json    # JSON Schema（跨框架）
│   └── methods/               # 方法论型框架（14个）
│       ├── aesthetics/            # 美学
│       ├── analyticphilosophy/    # 分析哲学
│       ├── anthropology/          # 人类学
│       ├── communication/          # 传播学
│       ├── cybernetics/            # 控制论
│       ├── ethics/                 # 伦理学
│       ├── jurisprudence/         # 法理学
│       ├── linguistics/            # 语言学
│       ├── management/             # 管理学
│       ├── operationsresearch/     # 运筹学
│       ├── pedagogy/               # 教育学
│       ├── phenomenology/          # 现象学
│       ├── politicalphilosophy/   # 政治哲学
│       └── sociology/              # 社会学
└── tests/
```

---

## 贡献指南

### 新增人物专家

1. 使用 nuwa-skill 蒸馏流程：
   ```bash
   # 安装女娲
   npm install -g @huashu/nuwa-skill
   
   # 蒸馏新人物
   nuwa distill <人物名>
   ```

2. 将生成的 SKILL.md 放入 `experts/people/<领域>/`
3. 运行转换脚本生成 JSON：
   ```bash
   python scripts/sketch_to_json.py
   ```
4. 更新 `INDEX_PEOPLE.md`

### 新增方法论框架

1. 在 `experts/methods/<name>-perspective/` 下创建 `SKILL.md`
2. 格式：见 [SCHEMA.md](./SCHEMA.md)
3. 运行转换脚本生成 JSON：
   ```bash
   python scripts/sketch_to_json.py
   ```
4. 更新 `INDEX_METHODS.md`

---

## 版本历史

| 版本 | 更新内容 |
|------|---------|
| v2.0 | 双轨系统上线：4人物 + 14方法论 + JSON Schema 跨框架支持 |
| v1.0 | 初始版本：18视角 |

---

## License

MIT

---

Agent-Superthinking_
