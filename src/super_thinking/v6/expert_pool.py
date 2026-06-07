"""
v6 Expert Pool Module

Dynamic expert pool with hot-swapping support and LLM-driven expert selection.
"""

from __future__ import annotations
import time
import logging
import json
import re
from typing import Protocol, runtime_checkable, TYPE_CHECKING, Any
from .types import (
    Expert, ExpertId, ExpertPool as ExpertPoolProtocol, DebateSession, 
    RosterChange, LLMProvider
)

if TYPE_CHECKING:
    from .types import DebateConfig, MethodologyRegistry, SessionRecorder

logger = logging.getLogger(__name__)


class ExpertPool(ExpertPoolProtocol):
    """Expert pool with registry style and LLM-driven expert selection.
    
    Implements ExpertPoolProtocol with:
    - Registry-based expert management
    - Keyword-based fallback selection (suggest_for)
    - LLM-driven expert selection (select_experts)
    """
    
    def __init__(self, llm_provider: LLMProvider | None = None):
        self._experts: dict[ExpertId, Expert] = {}
        self._session_active: dict[str, set[ExpertId]] = {}
        self._llm_provider = llm_provider
        self._select_experts_cache: dict[str, tuple[ExpertId, ...]] = {}
    
    def set_llm_provider(self, llm_provider: LLMProvider) -> None:
        """Set the LLM provider for select_experts()."""
        self._llm_provider = llm_provider
    
    def register(self, expert: Expert) -> None:
        """Register an expert in the pool."""
        self._experts[expert.id] = expert
        logger.info(f"Registered expert: {expert.id} ({expert.name})")
    
    def unregister(self, expert_id: ExpertId) -> None:
        """Unregister an expert from the pool."""
        if expert_id in self._experts:
            del self._experts[expert_id]
            logger.info(f"Unregistered expert: {expert_id}")
    
    def get(self, expert_id: ExpertId) -> Expert | None:
        """Get an expert by ID."""
        return self._experts.get(expert_id)
    
    def list_registered(self) -> tuple[Expert, ...]:
        """List all registered experts."""
        return tuple(self._experts.values())
    
    def list_active_in_session(self, session: DebateSession) -> tuple[Expert, ...]:
        """List active experts for a given session."""
        active_ids = self._session_active.get(str(session.session_id), set())
        return tuple(self._experts[eid] for eid in active_ids if eid in self._experts)
    
    def suggest_for(self, question: str, *, top_k: int = 5) -> tuple[Expert, ...]:
        """Fallback keyword-based expert suggestion.
        
        Uses trigger_keywords to score and rank experts.
        """
        scored = []
        question_lower = question.lower()
        for expert in self._experts.values():
            score = sum(
                1 for kw in expert.trigger_keywords 
                if kw.lower() in question_lower
            )
            scored.append((score, expert))
        scored.sort(key=lambda x: -x[0])
        return tuple(e for _, e in scored[:top_k])

    
    def select_experts(
        self, 
        question: str, 
        context: dict[str, Any] | None = None,
        min_experts: int = 3,
        max_experts: int = 5
    ) -> tuple[Expert, ...]:
        """LLM-driven expert selection.
        
        Uses LLM to select the most relevant experts based on the question
        and available expert profiles. Falls back to keyword matching if
        LLM is unavailable.
        
        Args:
            question: The user question or problem
            context: Optional context dictionary with additional info
            min_experts: Minimum number of experts to select (default: 3)
            max_experts: Maximum number of experts to select (default: 5)
        
        Returns:
            Tuple of selected Expert objects
        """
        context = context or {}
        
        # If no LLM provider, fall back to keyword matching
        if self._llm_provider is None:
            logger.warning("No LLM provider available, using fallback keyword matching")
            return self._suggest_for_fallback(question, min_experts, max_experts)
        
        try:
            return self._select_experts_with_llm(
                question, context, min_experts, max_experts
            )
        except Exception as e:
            logger.warning(f"LLM selection failed: {e}, falling back to keyword matching")
            return self._suggest_for_fallback(question, min_experts, max_experts)
    
    def _select_experts_with_llm(
        self,
        question: str,
        context: dict[str, Any],
        min_experts: int,
        max_experts: int
    ) -> tuple[Expert, ...]:
        """Internal method to select experts using LLM."""
        # Build candidate prompt with all expert profiles
        candidate_prompt = self._build_candidate_prompt(question, context)
        
        # Call LLM to select experts
        system_prompt = (
            "You are an expert at selecting the most relevant experts for a given question. "
            "Analyze the question and select 3-5 experts that would provide the most "
            "valuable and diverse perspectives. "
            "Return a JSON object with expert_ids array containing the selected expert IDs."
        )
        
        schema = {
            "type": "object",
            "properties": {
                "expert_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of selected expert IDs"
                },
                "reasoning": {
                    "type": "string",
                    "description": "Brief reasoning for the selection"
                }
            },
            "required": ["expert_ids"]
        }
        
        try:
            result = self._llm_provider.complete_json(
                candidate_prompt,
                system=system_prompt,
                schema=schema
            )
        except AttributeError:
            # If complete_json not available, try complete method
            response = self._llm_provider.complete(
                candidate_prompt,
                system=system_prompt,
                temperature=0.2,
                max_tokens=500
            )
            result = self._parse_llm_response(response)
        
        expert_ids = result.get("expert_ids", [])
        
        # Validate and filter expert IDs
        selected = []
        for eid in expert_ids:
            if isinstance(eid, str) and eid in self._experts:
                selected.append(self._experts[eid])
            # Also try without namespace prefix
            for registered_eid in self._experts:
                if str(registered_eid).endswith(eid) or eid.endswith(str(registered_eid)):
                    if self._experts[registered_eid] not in selected:
                        selected.append(self._experts[registered_eid])
                        break
        
        # Ensure we return at least min_experts
        if len(selected) < min_experts:
            logger.info(f"LLM selected only {len(selected)} experts, supplementing with fallback")
            fallback = self._suggest_for_fallback(question, 0, max_experts)
            for expert in fallback:
                if expert not in selected:
                    selected.append(expert)
                if len(selected) >= max_experts:
                    break
        
        # Limit to max_experts
        selected = selected[:max_experts]
        
        logger.info(f"LLM selected {len(selected)} experts: {[e.id for e in selected]}")
        return tuple(selected)

    
    def _build_candidate_prompt(self, question: str, context: dict[str, Any]) -> str:
        """Build prompt containing all candidate expert profiles."""
        lines = [
            "# Question Analysis Task",
            "",
            "## Question",
            question,
            "",
        ]
        
        if context:
            lines.extend([
                "## Context",
                str(context),
                "",
            ])
        
        lines.extend([
            "## Available Experts",
            "",
            "Below are all available experts with their profiles. ",
            "Select the most relevant ones for the question above.",
            ""
        ])
        
        for expert in self._experts.values():
            lines.extend([
                f"### Expert: {expert.name}",
                f"ID: {expert.id}",
                f"Domain: {expert.domain}",
                f"Description: {expert.description}",
                f"Keywords: {', '.join(expert.trigger_keywords)}",
                ""
            ])
        
        lines.extend([
            "## Task",
            "Select between 3 and 5 experts that would provide the most valuable ",
            "and diverse perspectives on the question.",
            "",
            "Return a JSON object with expert_ids array containing the selected expert IDs ",
            "and a brief reasoning for your selection."
        ])
        
        return "\n".join(lines)
    
    def _parse_llm_response(self, response: str) -> dict[str, Any]:
        """Parse LLM response to extract expert IDs."""
        # Try to find JSON in the response
        json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Try to extract expert IDs from text
        expert_ids = []
        for expert_id in self._experts:
            if str(expert_id) in response:
                expert_ids.append(str(expert_id))
        
        if expert_ids:
            return {"expert_ids": expert_ids[:5], "reasoning": "Extracted from text"}
        
        return {"expert_ids": [], "reasoning": "Could not parse response"}
    
    def _suggest_for_fallback(
        self, 
        question: str, 
        min_experts: int = 3,
        max_experts: int = 5
    ) -> tuple[Expert, ...]:
        """Fallback selection using keyword matching."""
        selected = list(self.suggest_for(question, top_k=max_experts))
        
        # Ensure minimum
        if len(selected) < min_experts:
            # Add more experts by domain diversity
            all_experts = list(self._experts.values())
            domains_seen = {e.domain for e in selected}
            
            for expert in all_experts:
                if expert not in selected and expert.domain not in domains_seen:
                    selected.append(expert)
                    domains_seen.add(expert.domain)
                if len(selected) >= min_experts:
                    break
        
        return tuple(selected[:max_experts])
    
    def apply_roster_change(self, session: DebateSession, change: RosterChange) -> bool:
        """Apply a roster change for a session."""
        session_id = str(session.session_id)
        if session_id not in self._session_active:
            self._session_active[session_id] = set()
        
        if change.action == "add":
            expert = self._experts.get(change.expert_id)
            if expert:
                self._session_active[session_id].add(change.expert_id)
                return True
        elif change.action == "remove":
            self._session_active[session_id].discard(change.expert_id)
            return True
        return False
    
    def active_ids(self, session_id: str) -> tuple[ExpertId, ...]:
        """Get active expert IDs for a session."""
        return tuple(self._session_active.get(session_id, set()))
    
    def snapshot(self) -> dict:
        """Get a snapshot of the current pool state."""
        return {
            "registered": [str(eid) for eid in self._experts],
            "sessions": {sid: list(ids) for sid, ids in self._session_active.items()},
        }


__all__ = ["ExpertPool"]
