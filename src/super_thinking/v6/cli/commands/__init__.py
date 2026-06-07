"""CLI commands."""
import json
import pathlib
from typing import Any

from .debate import debate_cmd
from .render import get_mock_pool, get_renderer, MockExpertPool, RichRenderer

__all__ = ["debate_cmd", "get_mock_pool", "get_renderer", "MockExpertPool", "RichRenderer", "load_experts_json"]

_EXPERTS_JSON_PATH = pathlib.Path(__file__).parent / "experts.json"


def load_experts_json() -> list[dict[str, Any]]:
    """Load experts from the bundled JSON file."""
    if _EXPERTS_JSON_PATH.exists():
        with open(_EXPERTS_JSON_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []
