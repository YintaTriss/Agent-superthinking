# -*- coding: utf-8 -*-
"""Debate command."""

from __future__ import annotations
from typing import Optional, List

import typer

from .render import MockExpertPool, RichRenderer, get_mock_pool, get_renderer

QuestionStr = str
ExpertsList = list[str]

_DEFAULT_EXPERTS = [
    {
        "id": "socrates",
        "name": "苏格拉底",
        "description": "哲学思想 - 辩证法的思维方式",
        "trigger_keywords": ["哲学", "论证", "反思", "辩证", "知识", "思考"],
        "template": "苏格拉底思考：{question}

通过辩证法进行深入提问。",
    },
    {
        "id": "confucius",
        "name": "孔子",
        "description": "中庸思想 - 人情世故",
        "trigger_keywords": ["中庸", "人情", "修身", "治国", "教化", "传承"],
        "template": "孔子教导：{question}

己所不欲，勿施于人。",
    },
    {
        "id": "einstein",
        "name": "爱因斯坦",
        "description": "科学思想 - 科学思维与创造力",
        "trigger_keywords": ["推理", "观察", "偏见", "科学", "实验", "研究"],
        "template": "爱因斯坦观点：{question}

想象力比知识更重要。",
    },
    {
        "id": "musk",
        "name": "马斯克",
        "description": "创业者视角 - 第一性原则思维",
        "trigger_keywords": ["创业", "风险", "企业", "技术", "投资", "市场"],
        "template": "马斯克思维：{question}

应该用第一性原则思考。",
    },
    {
        "id": "charlie",
        "name": "查理·芒格",
        "description": "投资者视角 - 多元思维模型",
        "trigger_keywords": ["投资", "风险", "价值", "会计", "心理", "逆向"],
        "template": "查理·芒格思维：{question}

要学会多种学科的角度看问题。",
    },
]


def debate_cmd(
    question: str,
    experts: Optional[str],
    methods: Optional[str],
    rounds: int,
    mock: bool,
    format: str,
) -> None:
    """Start a multi-expert debate."""
    renderer = get_renderer()
    renderer.print_title("Multi-Expert Debate", "SuperThinking v6")
    print()

    if mock:
        pool = get_mock_pool()
        expert_ids = []
        if experts:
            expert_ids = [e.strip() for e in experts.split(",")]
        else:
            expert_ids = ["socrates", "confucius"]
        
        # Validate experts
        for expert_id in list(expert_ids):
            if pool.get_expert(expert_id) is None:
                renderer.print_warning(f"Expert '{expert_id}' not found, skipping")
                expert_ids.remove(expert_id)
        
        if not expert_ids:
            renderer.print_error("E001", "No valid experts specified")
            raise typer.Exit(code=1)
        
        result = pool.mock_debate(question, expert_ids, renderer, rounds)
        if format == "json":
            renderer.print_json(result)
        return

    # Real LLM mode - simplified
    renderer.print_warning("Real LLM mode not fully implemented, using mock mode")
    pool = get_mock_pool()
    result = pool.mock_debate(question, ["socrates", "confucius"], renderer, rounds)
    if format == "json":
        renderer.print_json(result)


if __name__ == "__main__":
    typer.run(debate_cmd)
