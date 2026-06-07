"""Main CLI entry point."""
import sys
from typing import Optional

import typer

app = typer.Typer(help="SuperThinking v6 - Multi-Expert Debate System")


@app.command()
def debate(
    question: str = typer.Argument(..., help="Question to analyze"),
    experts: Optional[str] = typer.Option(None, "--experts", "-e", help="Comma-separated expert IDs"),
    methods: Optional[str] = typer.Option(None, "--methods", "-m", help="Comma-separated method IDs"),
    rounds: int = typer.Option(2, "--rounds", "-r", help="Number of debate rounds"),
    mock: bool = typer.Option(False, "--mock", help="Use mock mode (no LLM required)"),
    format: str = typer.Option("text", "--format", "-f", help="Output format: text/json"),
) -> None:
    """Start a multi-expert debate."""
    from .commands.debate import debate_cmd
    debate_cmd(question, experts, methods, rounds, mock, format)


@app.command()
def consult(
    question: str = typer.Argument(..., help="Question to consult on"),
    expert: str = typer.Option("socrates", "--expert", help="Expert ID to consult"),
    mock: bool = typer.Option(False, "--mock", help="Use mock mode (no LLM required)"),
) -> None:
    """Consult a single expert (faster than full debate)."""
    from .commands.consult_cmd import consult_cmd
    consult_cmd(question, expert, mock)


@app.command("list")
def list_experts(
    format: str = typer.Option("text", "--format", "-f", help="Output format: text/json"),
) -> None:
    """List available experts."""
    from .commands import load_experts_json
    experts = load_experts_json()
    if format == "json":
        import json
        print(json.dumps(experts, indent=2, ensure_ascii=False))
        return
    renderer = __import__(".commands", fromlist=["get_renderer"]).get_renderer()
    renderer.print_title("Available Experts")
    for exp in experts:
        tags = ", ".join(exp.get("keywords", [])[:5])
        print(f"  [{exp['id']}] {exp['name']} — {exp.get('description', '')}")
        print(f"       Keywords: {tags}")


if __name__ == "__main__":
    app()
