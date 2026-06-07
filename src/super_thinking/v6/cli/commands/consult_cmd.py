"""Consult command - single expert consultation."""
from ..v6.types import DebateConfig
from ..v6 import think_v6


def consult_cmd(question: str, expert: str, mock: bool) -> None:
    """Consult a single expert (no debate, just one perspective)."""
    from . import get_renderer, get_mock_pool

    renderer = get_renderer()
    renderer.print_title(f"Consulting: {expert}")

    if mock:
        pool = get_mock_pool()
        exp = pool.get_expert(expert)
        if not exp:
            renderer.print_error("404", f"Expert '{expert}' not found")
            return
        renderer.print_header("Perspective")
        template = exp.get("template", "{question}").replace("{question}", question)
        renderer.print_expert_speech(exp["name"], template, role=exp.get("description", ""))
        return

    # Real LLM mode
    try:
        result = think_v6(
            question=question,
            selected_experts=[expert],
            config=DebateConfig(max_rounds=1),
        )
        renderer.print_header("Analysis")
        print(result.get("final_report", str(result)))
    except Exception as e:
        renderer.print_error("500", f"Consult failed: {e}")
