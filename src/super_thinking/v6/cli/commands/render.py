"""Simple render utilities."""
from typing import Any
import json
import pathlib

try:
    from rich.console import Console
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    Console = None


_EXPERTS_JSON = pathlib.Path(__file__).parent / "experts.json"


def _load_experts() -> list[dict[str, Any]]:
    if _EXPERTS_JSON.exists():
        with open(_EXPERTS_JSON, encoding="utf-8") as f:
            return json.load(f)
    return []


class RichRenderer:
    """Simple renderer."""
    
    def __init__(self):
        if HAS_RICH:
            self._console = Console()
        else:
            self._console = None
    
    def print_title(self, title, subtitle=""):
        if self._console:
            self._console.print(f"[bold cyan]{title}[/]")
        else:
            print(f"=== {title} ===")
    
    def print_header(self, text):
        if self._console:
            self._console.print(f"[bold magenta]{text}[/]")
        else:
            print(f"--- {text} ---")
    
    def print_expert_speech(self, name, content, role=""):
        if self._console:
            self._console.print(f"[yellow]{name}[/] ({role}): {content}")
        else:
            print(f"{name} ({role}): {content}")
    
    def print_warning(self, text):
        if self._console:
            self._console.print(f"[yellow]WARNING:[/] {text}")
        else:
            print(f"WARNING: {text}")
    
    def print_error(self, code, title, detail=""):
        if self._console:
            self._console.print(f"[red]ERROR {code}:[/] {title}")
        else:
            print(f"ERROR {code}: {title}")
    
    def print_json(self, data):
        import json
        print(json.dumps(data, indent=2, ensure_ascii=False))


class MockExpertPool:
    """Mock expert pool loaded from experts.json."""

    def __init__(self):
        self._experts_raw = _load_experts()
        # Build a lookup dict keyed by id
        self._experts = {e["id"]: e for e in self._experts_raw}

    def get_expert(self, expert_id: str) -> dict[str, Any] | None:
        return self._experts.get(expert_id)

    def list_experts(self) -> list[dict[str, Any]]:
        return self._experts_raw

    def mock_debate(self, question: str, expert_ids: list[str], renderer: RichRenderer, rounds: int):
        results = {"question": question, "rounds": [], "experts": []}
        for expert_id in expert_ids:
            expert = self._experts.get(expert_id)
            if expert:
                results["experts"].append({"id": expert_id, "name": expert["name"]})
                template = expert.get("template", "{question}").replace("{question}", question)
                renderer.print_expert_speech(expert["name"], template, role=expert.get("description", ""))
        results["status"] = "completed"
        return results


_renderer = None
_mock_pool = None

def get_renderer():
    global _renderer
    if _renderer is None:
        _renderer = RichRenderer()
    return _renderer

def get_mock_pool():
    global _mock_pool
    if _mock_pool is None:
        _mock_pool = MockExpertPool()
    return _mock_pool
