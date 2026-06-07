"""
List experts/methods subcommand for superthink CLI.

Usage: superthink list experts [OPTIONS]
       superthink list methods [OPTIONS]
"""

from __future__ import annotations

from typing import Optional

from ..render import MockExpertPool, RichRenderer, get_mock_pool, get_renderer


def list_cmd(
    category: str,
    domain: Optional[str] = None,
    search: Optional[str] = None,
    format: str = "text",
) -> None:
    """
    List available experts or methods.
    
    Examples:
    
        superthink list_experts experts
        superthink list_experts methods
        superthink list_experts experts --domain philosophy
        superthink list_experts experts --search 辩证
    """
    renderer: RichRenderer = get_renderer()
    pool: MockExpertPool = get_mock_pool()
    
    if category == "experts":
        if search:
            results = pool.search_experts(search)
            if not results:
                renderer.print_warning(f"No experts found matching '{search}'")
                return
            renderer.print_expert_table(results, f"Search Results: {search}")
        elif domain:
            results = pool.list_experts(domain=domain)
            if not results:
                renderer.print_warning(f"No experts found in domain '{domain}'")
                return
            renderer.print_expert_table(results, f"Experts in {domain}")
        else:
            results = pool.list_experts()
            renderer.print_expert_table(results, f"Available Experts ({len(results)})")
        
        if format == "json":
            renderer.print_json(results)
    
    elif category == "methods":
        results = pool.list_methods()
        renderer.print_method_table(results, f"Available Methods ({len(results)})")
        
        if format == "json":
            renderer.print_json(results)
    
    else:
        renderer.print_error("E006", f"Unknown category '{category}'",
                           "Use 'experts' or 'methods'")
