# Agent-Superthinking v6

> **Think with history's greatest minds.** A multi-expert debate framework that simulates genuine intellectual dialogue between diverse perspectives — from Socratic philosophy to Einstein's scientific rigor, from Sun Tzu's military strategy to Charlie Munger's mental models.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Version: 6.0](https://img.shields.io/badge/Version-6.0-green.svg)]()

**[简体中文](./README_CN.md) | [繁體中文](./README_TW.md)**

---

## What Is This?

Agent-Superthinking v6 is a **multi-expert debate system** for AI agents. Instead of a single AI response, it:

1. **Routes** your question to the most relevant experts (historical figures, academic frameworks, or both)
2. **Convenes** a structured debate — experts present arguments, rebut, and respond
3. **Fuses** conflicting viewpoints into a synthesis report that shows *where* experts agree and *where* they diverge

> "I cannot teach anybody anything. I can only make them think." — Socrates

---

## Architecture

```
                        ┌─────────────────────────────────────────┐
   User Question        │            Router Layer                  │
  ─────────────────────►│  Reads INDEX_PEOPLE.md                 │
                        │  Reads INDEX_METHODS.md                 │
                        │  Classifies: People? Methods? Both?     │
                        └──────────────────┬────────────────────┘
                                           │
                    ┌───────────────────────┼───────────────────────┐
                    │                       │                       │
                    ▼                       ▼                       ▼
            ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
            │   People     │      │   Methods    │      │    Both      │
            │  (History's  │      │  (Academic   │      │   (Full      │
            │   Giants)    │      │   Frames)    │      │   Spectrum)  │
            └──────┬───────┘      └──────┬───────┘      └──────┬───────┘
                   │                     │                     │
                   └─────────────────────┼─────────────────────┘
                                         │
                        ┌────────────────▼────────────────────┐
                        │        DebateOrchestrator          │
                        │  ┌──────────────────────────────┐  │
                        │  │      Moderator               │  │
                        │  │  • BuildArgumentMenu         │  │
                        │  │  • SelectNextSpeaker         │  │
                        │  │  • DetectConvergence         │  │
                        │  └──────────────────────────────┘  │
                        │              ▲                     │
                        │              │                     │
                        │  ┌───────────┴───────────────┐     │
                        │  │     ExpertPool (hot-swap) │     │
                        │  │  register / unregister   │     │
                        │  └───────────────────────────┘     │
                        └──────────────────┬──────────────────┘
                                           │
                        ┌──────────────────▼──────────────────┐
                        │        Fusion Layer                 │
                        │  • Conflict Detection               │
                        │  • Consensus Extraction             │
                        │  • Structured Report                │
                        └───────────────────────────────────┘
```

### Core Components

| Component | File | Responsibility |
|-----------|------|----------------|
| `think_v6()` | `entrypoint.py` | Single-call entry point |
| `convene_v6()` | `entrypoint.py` | Programmatic API |
| `DebateOrchestrator` | `orchestrator.py` | Manages full debate lifecycle |
| `Moderator` | `moderator/moderator.py` | Runs each round, builds menus |
| `ExpertPool` | `expert_pool.py` | Hot-pluggable expert registry |
| `ConvergenceDetector` | `convergence_detector/detector.py` | Detects when consensus is reached |
| `SessionRecorder` | `session_recorder.py` | 11 event hooks for observability |
| `MethodologyRegistry` | `methodology.py` | 18 academic frameworks |

---

## Installation

```bash
# From source
cd agent-superthinking-v6
pip install -e .

# Or install the published package (when available)
pip install agent-superthinking
```

### Dependencies

Only **two hard dependencies**:

```toml
typer>=0.12.0        # CLI framework
pydantic>=2.0        # Type validation
```

`rich` is optional but recommended for beautiful terminal output:

```bash
pip install rich
```

---

## Quick Start

### CLI — Interactive Debate

```bash
# Interactive mode (recommended)
super_thinking debate "Should AI replace human creativity?"

# Specify experts
super_thinking debate "What is the best strategy for AI governance?" \
  --experts socrates,confucius,einstein \
  --rounds 3

# Mock mode (no API key needed, uses templates)
super_thinking debate "Does privacy exist in the digital age?" \
  --experts confucius,socrates \
  --mock

# JSON output (for programmatic use)
super_thinking debate "What causes economic inequality?" \
  --experts keynes,hayek,smith \
  --format json
```

### CLI — List Available Experts

```bash
super_thinking list
# Or: super_thinking list --format json
```

### CLI — Single Expert Consultation

```bash
# Faster than full debate — consult one expert
super_thinking consult "What is the nature of time?" --expert socrates
super_thinking consult "How should we think about innovation?" --expert einstein
```

### Python API

```python
from super_thinking import convene_v6, DebateConfig

# Simple call
result = think_v6(
    question="Should we prioritize economic growth or environmental protection?",
    selected_experts=["confucius", "hayek", "einstein"],
    config=DebateConfig(max_rounds=2)
)

print(result["final_report"])
```

### Python API — Programmatic Control

```python
from super_thinking.v6 import convene_v6
from super_thinking.v6.types import DebateConfig
from super_thinking.v6 import ExpertPool, LLMProvider

# Custom configuration
pool = ExpertPool()
pool.register(my_custom_expert)

config = DebateConfig(
    max_rounds=3,
    convergence_threshold=0.75,
    temperature=0.7,
)
result = convene_v6(
    question="What is the meaning of suffering?",
    selected_experts=["socrates", "buddha", "nietzsche"],
    expert_pool=pool,
    config=config,
)
```

---

## Expert Library

Agent-Superthinking v6 includes **30+ experts** across two tracks:

### People Track — Historical Figures

| Domain | Experts | Keywords |
|--------|---------|----------|
| Philosophy | Socrates, Plato, Aristotle, Kant, Nietzsche, Descartes, Hume, Lao Zi, Zhuangzi, Wittgenstein, Sartre, Marx | Dialectic, Forms, Virtue, Critique, Will, Doubt, Empiricism, Tao, Flow, Language, Existentialism, Materialism |
| Literature | Dante, Dostoevsky, Kafka, Lu Xun | Divine Comedy, Dostoevsky, Absurdity, Archaic Spirit |
| Science | Einstein, Newton, Bohr, Curie, Maxwell, Schrödinger, Turing, Gauss, Euclid, Gödel | Relativity, Gravity, Quantum, Radioactivity, Electromagnetism, Wave Function, Computation, Statistics, Geometry, Incompleteness |
| Economics | Smith, Keynes, Hayek, Inamori | Free Market, Macro, Austrian School,稻盛哲学 |
| Military | Sun Tzu, Clausewitz | Art of War, Total War |
| Psychology | Freud, Jung, Erikson, Rogers, Mead, Foucault | Psychoanalysis, Collective Unconscious, Development, Person-Centered, Symbolic Interaction, Power/Knowledge |
| Religion | Buddha, Wang Yangming | Eightfold Path, Knowing-Action Unity |

### Methods Track — Academic Frameworks

| Category | Frameworks |
|----------|-----------|
| Philosophy | Phenomenology, Analytical Philosophy, Ethics, Political Philosophy |
| Social Science | Anthropology, Sociology, Communication Studies |
| Interdisciplinary | Aesthetics, Linguistics, Pedagogy, Management, Cybernetics, Jurisprudence, Operations Research |
| Analysis | Bayesian Reasoning, Critical Thinking, Design Thinking, Systems Thinking |
| Computation | Information Theory, Network Theory, Complexity Science, Quantum Thinking |
| Decision | Game Theory, Evolutionary Psychology |

---

## JSON Schema — Framework Agnostic

Every expert is also available as a `schema.json` file. Use with **any AI framework**:

```python
import json

# Load any expert as JSON — works with LangChain, LlamaIndex, etc.
with open("experts/philosophy/socrates-perspective/schema.json") as f:
    schema = json.load(f)

print(f"Expert: {schema['displayName']}")
print(f"Domain: {schema['domain']}")
for model in schema["models"]:
    print(f"  Model: {model['name']} — {model['summary']}")
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

## v5 → v6 Migration

```python
# v5 (Legacy)
from super_thinking import Jury
jury = Jury()
result = jury.think(question, model_names=["socrates", "confucius"])

# v6 (Current)
from super_thinking.v6 import think_v6, DebateConfig
result = think_v6(
    question=question,
    selected_experts=["socrates", "confucius"],
    config=DebateConfig(max_rounds=2)
)

# v6 also provides a compatibility adapter
from super_thinking.v6.compat import JuryAdapter
adapter = JuryAdapter()
result = adapter.think(question, model_names=["socrates", "confucius"])
```

---

## CLI Commands Reference

| Command | Description |
|---------|-------------|
| `debate <question>` | Start full multi-expert debate |
| `debate <q> --experts socrates,confucius --rounds 3` | With specific experts and rounds |
| `debate <q> --mock` | Mock mode (no API key needed) |
| `debate <q> --format json` | JSON output |
| `list` | List all available experts |
| `consult <question> --expert <id>` | Single expert consultation |
| `--help` | Show all options |

---

## Advanced Configuration

### ExpertPool — Hot-Swappable Registry

```python
from super_thinking.v6 import ExpertPool, Expert

pool = ExpertPool()

# Register a custom expert
pool.register(Expert(
    id="my_expert",
    name="My Expert",
    domain="custom",
    models=[...],
    heuristics=[...],
))

# Unregister
pool.unregister("my_expert")

# List all registered
for expert_id in pool.list_registered():
    print(expert_id)
```

### SessionRecorder — Full Observability

```python
from super_thinking.v6 import SessionRecorder

recorder = SessionRecorder()

@recorder.on_round_start
def on_round(session, round_num):
    print(f"Round {round_num} starting...")

@recorder.on_expert_speak
def on_speak(session, expert_id, content):
    print(f"{expert_id} said: {content[:50]}...")

@recorder.on_convergence
def on_convergence(session, consensus):
    print(f"Converged: {consensus}")

result = think_v6(question, selected_experts=[...], recorder=recorder)
```

### Custom LLM Provider

```python
from super_thinking.v6.llm import LLMProvider

class MyProvider(LLMProvider):
    def complete(self, messages, **kwargs) -> str:
        # Use any LLM backend
        return my_llm.call(messages)

pool.set_llm_provider(MyProvider())
```

---

## Design Philosophy

### Why Debate Over Single-Expert Analysis?

A single AI response is a **monologue**. Agent-Superthinking v6 creates a **dialogue** — the most productive form of reasoning.

> "The两根稻草在不同角度看到的世界完全不同。" — Zhuangzi

Multi-expert debate surfaces:
- **Hidden assumptions** each expert takes for granted
- **Genuine disagreement** vs. false consensus
- **Unexpected connections** between distant domains
- **Confidence calibration** — how certain is each expert?

### Architecture Principles

| Principle | Implementation |
|-----------|---------------|
| Hot-swap experts | `ExpertPool.register/unregister` at runtime |
| Observable | 11-event `SessionRecorder` hook system |
| Type-safe | Full Pydantic v2 models for all types |
| Zero magic | No hidden global state, explicit config objects |
| Framework agnostic | JSON Schema for every expert |

---

## Performance

Benchmarked on a 8-question evaluation set:

| Operation | Time (s) | Notes |
|-----------|-----------|-------|
| 2-round debate, 3 experts | ~15s | With API calls |
| 1-round debate, 1 expert | ~5s | Minimum viable |
| Mock mode (no API) | <1s | Template-based |

---

## Changelog

### v6.0.0 — Complete Rewrite
- Full debate orchestrator with moderator rounds
- Hot-swappable ExpertPool
- Convergence detection with configurable threshold
- 11-event SessionRecorder
- 18-methodology academic framework library
- 30+ historical figure perspectives
- JSON Schema export for all experts
- v5 compatibility adapter
- CLI with `debate`, `consult`, `list` commands

### v5.x — Legacy
- Single-expert analysis with multiple perspectives
- Jury-based voting

---

## Contributing

### Adding a New Historical Figure

1. Create directory: `experts/people/<domain>/<name>-perspective/`
2. Write `SKILL.md` with the expert's thinking model
3. Generate `schema.json`: `python scripts/sketch_to_json.py`
4. Add to `INDEX_PEOPLE.md`

### Adding a New Academic Framework

1. Create directory: `experts/methods/<name>-perspective/`
2. Write `SKILL.md` with the framework's core models and heuristics
3. Generate `schema.json`: `python scripts/sketch_to_json.py`
4. Add to `INDEX_METHODS.md`

---

## License

MIT License — free to use, modify, and distribute.

---

*Agent-Superthinking — Think with the greatest minds in history.*
