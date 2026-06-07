# 超思考 v6 · 多專家辯論系統

> **與歷史上最偉大的頭腦對話。** 一個多專家辯論框架，讓蘇格拉底的辯證法、愛因斯坦的科學精神、孫武的軍事謀略、查理·芒格的多元思維模型，在同一個問題下交鋒、碰撞、融匯。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![版本: 6.0](https://img.shields.io/badge/版本-6.0-green.svg)]()

**[English](./README.md) | [简体中文](./README_CN.md)**

---

## 緣起

當一個問題擺在面前，單一視角的回答往往遺漏了最重要的東西——

那些**被默認接受的假設**，那些**與己相異的立場**，那些**意料之外的關聯**。

超思考 v6 不給你一個答案，而是召集一群最合適的專家，讓他們**真正地辯論**。

不是簡單地把各路觀點並排陳列，而是讓每位專家：
- **陳述**自己的核心論點
- **反駁**他人的薄弱之處
- **回應**被質疑的地方
- 最終由**主持人**檢測收斂，**融合層**提煉共識

這才是思考應有的樣子。

---

## 核心架構

```
                        ┌─────────────────────────────────────────┐
   用戶問題              │            路由層（Router）              │
  ─────────────────────►│  讀取 INDEX_PEOPLE.md                  │
                        │  讀取 INDEX_METHODS.md                 │
                        │  判斷：人物型？方法論型？雙軌組合？       │
                        └──────────────────┬────────────────────┘
                                           │
                    ┌───────────────────────┼───────────────────────┐
                    │                       │                       │
                    ▼                       ▼                       ▼
            ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
            │   人物型      │      │   方法論型    │      │   雙軌組合    │
            │  （歷史人物）  │      │  （學術框架）  │      │  （全面審視）  │
            └──────┬───────┘      └──────┬───────┘      └──────┬───────┘
                   │                     │                     │
                   └─────────────────────┼─────────────────────┘
                                         │
                        ┌────────────────▼────────────────────┐
                        │       辯論編排器（Orchestrator）     │
                        │  ┌──────────────────────────────┐  │
                        │  │      主持人（Moderator）      │  │
                        │  │  • 構建論點選單               │  │
                        │  │  • 選擇下一位發言人            │  │
                        │  │  • 檢測共識收斂               │  │
                        │  └──────────────────────────────┘  │
                        │              ▲                     │
                        │              │                     │
                        │  ┌───────────┴───────────────┐     │
                        │  │    專家池（ExpertPool）   │     │
                        │  │  register / unregister   │     │
                        │  └───────────────────────────┘     │
                        └──────────────────┬──────────────────┘
                                           │
                        ┌──────────────────▼──────────────────┐
                        │         融合層（Fusion）            │
                        │  • 衝突檢測                        │
                        │  • 共識提煉                        │
                        │  • 結構化綜合報告                   │
                        └───────────────────────────────────┘
```

### 核心組件一覽

| 組件 | 檔案 | 職責 |
|------|------|------|
| `think_v6()` | `entrypoint.py` | 一行呼叫入口 |
| `convene_v6()` | `entrypoint.py` | 程式化 API |
| `DebateOrchestrator` | `orchestrator.py` | 管理完整辯論生命週期 |
| `Moderator` | `moderator/moderator.py` | 每輪運行，構建論點選單 |
| `ExpertPool` | `expert_pool.py` | 熱插拔專家註冊表 |
| `ConvergenceDetector` | `convergence_detector/detector.py` | 檢測共識何時達成 |
| `SessionRecorder` | `session_recorder.py` | 11 個事件鉤子，可觀測性 |
| `MethodologyRegistry` | `methodology.py` | 18 種學術框架 |

---

## 安裝

```bash
# 從源碼安裝
cd agent-superthinking-v6
pip install -e .
```

### 依賴

僅**兩個硬依賴**：`typer>=0.12.0` 和 `pydantic>=2.0`。`rich` 為可選依賴。

---

## 快速上手

### CLI — 互動式辯論

```bash
super_thinking debate "AI 是否應該擁有法律人格？"
super_thinking debate "AI 治理策略" --experts socrates,confucius,einstein --rounds 3
super_thinking debate "數位時代隱私" --experts confucius,socrates --mock
```

### CLI — 單專家諮詢

```bash
super_thinking consult "時間的本質是什麼？" --expert socrates
```

### Python API

```python
from super_thinking import think_v6, DebateConfig

result = think_v6(
    question="應該優先經濟發展還是環境保護？",
    selected_experts=["confucius", "hayek", "einstein"],
    config=DebateConfig(max_rounds=2)
)
print(result["final_report"])
```

---

## 專家庫

**30+ 位專家**，兩條路徑：

### 人物路徑

哲學：蘇格拉底、柏拉圖、亞里士多德、康德、尼采、笛卡爾、休謨、老子、莊子、維特根斯坦、薩特、馬克思
文學：但丁、陀思妥耶夫斯基、卡夫卡、魯迅
科學：愛因斯坦、牛頓、波爾、居禮夫人、麥克斯韋、薛丁格、圖靈、高斯、歐幾里得、哥德爾
經濟：亞當·斯密、凱恩斯、哈耶克、稻盛和夫
軍事：孫子、克勞塞維茨
心理：弗洛伊德、榮格、埃里克森、羅傑斯、米德、福柯
宗教：佛陀、王陽明

### 方法論路徑

哲學：現象學、分析哲學、倫理學、政治哲學
社會科學：人類學、社會學、傳播學
交叉學科：美學、語言學、教育學、管理學、控制論、法理學、運籌學
分析工具：貝葉斯推理、批判性思維、設計思維、系統思維
計算思維：資訊理論、網路理論、複雜性科學、量子思維
決策科學：博弈論、進化心理學

---

## JSON Schema

每個專家都有對應的 `schema.json`，可被任何框架解析：

```python
import json
with open("experts/philosophy/socrates-perspective/schema.json") as f:
    schema = json.load(f)
```

---

## v5 到 v6 遷移

```python
# v5
from super_thinking import Jury
result = Jury().think(q, model_names=["socrates", "confucius"])

# v6
from super_thinking.v6 import think_v6, DebateConfig
result = think_v6(question=q, selected_experts=["socrates", "confucius"], config=DebateConfig(max_rounds=2))
```

---

## CLI 命令

| 命令 | 說明 |
|------|------|
| `debate <問題>` | 啟動完整多專家辯論 |
| `list` | 列出所有可用專家 |
| `consult <問題> --expert <id>` | 單專家諮詢（快速模式） |
| `--mock` | 模擬模式（無需 API Key） |
| `--format json` | JSON 輸出格式 |

---

## License

MIT License

---

*超思考 v6 — 與歷史上最偉大的頭腦對話。*
