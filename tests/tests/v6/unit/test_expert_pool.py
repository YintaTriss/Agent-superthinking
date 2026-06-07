"""
test_expert_pool.py - ExpertPool Unit Tests
"""

import pytest
import time
import json
import sys

sys.path.insert(0, "src")

from super_thinking.v6.expert_pool import ExpertPool
from super_thinking.v6.types import ExpertId, SpeakRole, ExpertStatement


class MockExpert:
    def __init__(self, expert_id="test_expert", name="Test Expert", description="Test desc", domain="Test Domain", trigger_keywords=("test", "expert")):
        self.id = ExpertId(expert_id)
        self.name = name
        self.description = description
        self.domain = domain
        self.trigger_keywords = trigger_keywords
        self.is_methodology = False
        self.speak_count = 0
    
    def speak(self, prompt):
        self.speak_count += 1
        return ExpertStatement(expert_id=self.id, expert_name=self.name, role=SpeakRole.INITIAL, content="[" + self.name + "] speaks", confidence=0.5)


class MockLLMProvider:
    def __init__(self, response_delay=0.01):
        self.response_delay = response_delay
        self.call_history = []
        self.local = {}
    
    def set_response(self, pattern, expert_ids):
        self.local[pattern] = expert_ids
    
    def complete(self, prompt, system=None, temperature=0.2, max_tokens=2000):
        if self.response_delay > 0:
            time.sleep(self.response_delay)
        self.call_history.append({"prompt": prompt})
        for p, ids in self.local.items():
            if p.lower() in prompt.lower():
                return json.dumps({"expert_ids": ids, "reasoning": "Selected"})
        return json.dumps({"expert_ids": ["expert_1", "expert_2", "expert_3"], "reasoning": "Default"})
    
    def complete_json(self, prompt, system=None, schema=None):
        if self.response_delay > 0:
            time.sleep(self.response_delay)
        self.call_history.append({"prompt": prompt, "schema": schema})
        for p, ids in self.local.items():
            if p.lower() in prompt.lower():
                return {"expert_ids": ids, "reasoning": "Selected"}
        return {"expert_ids": ["expert_1", "expert_2", "expert_3"], "reasoning": "Default"}


@pytest.fixture
def mock_experts():
    def _create(count=5):
        experts = []
        for i in range(1, count + 1):
            experts.append(MockExpert("expert_" + str(i), "Expert" + str(i), "Desc" + str(i), "Domain" + str(i), ("expert" + str(i), "domain" + str(i))))
        return experts
    return _create


@pytest.fixture
def mock_llm_provider():
    return MockLLMProvider()


@pytest.fixture
def expert_pool(mock_experts):
    pool = ExpertPool()
    for e in mock_experts(5):
        pool.register(e)
    return pool


@pytest.fixture
def expert_pool_with_llm(mock_experts, mock_llm_provider):
    pool = ExpertPool(llm_provider=mock_llm_provider)
    for e in mock_experts(5):
        pool.register(e)
    return pool


class TestSelectExpertsWithLLM:
    def test_select_experts_returns_tuple(self, expert_pool_with_llm):
        result = expert_pool_with_llm.select_experts("Test question")
        assert isinstance(result, tuple)
        assert 3 <= len(result) <= 5
    
    def test_select_experts_respects_max(self, expert_pool_with_llm):
        result = expert_pool_with_llm.select_experts("Test question", max_experts=2)
        assert len(result) <= 2
    
    def test_select_experts_respects_min(self, expert_pool_with_llm):
        result = expert_pool_with_llm.select_experts("Test question", min_experts=4, max_experts=5)
        assert len(result) >= 4
    
    def test_select_experts_calls_llm(self, expert_pool_with_llm, mock_llm_provider):
        expert_pool_with_llm.select_experts("Test question")
        assert len(mock_llm_provider.call_history) > 0
    
    def test_select_experts_consistency(self, expert_pool_with_llm):
        q = "AI and startup question"
        r1 = expert_pool_with_llm.select_experts(q)
        r2 = expert_pool_with_llm.select_experts(q)
        ids1 = set(e.id for e in r1)
        ids2 = set(e.id for e in r2)
        overlap = len(ids1 & ids2)
        min_count = min(len(r1), len(r2))
        rate = overlap / min_count if min_count > 0 else 0
        print("Overlap rate:", rate)
        assert rate >= 0.5


class TestSelectExpertsFallback:
    def test_fallback_without_llm(self, expert_pool):
        result = expert_pool.select_experts("expert1 domain1 test")
        assert isinstance(result, tuple)
        assert len(result) >= 1
    
    def test_fallback_returns_tuple(self, expert_pool):
        result = expert_pool.select_experts("test question")
        assert isinstance(result, tuple)
    
    def test_fallback_respects_limits(self, expert_pool):
        result = expert_pool.select_experts("test", min_experts=2, max_experts=3)
        assert 2 <= len(result) <= 3


class TestExpertPoolProtocol:
    def test_register_and_get(self, expert_pool, mock_experts):
        e = mock_experts(1)[0]
        expert_pool.register(e)
        assert expert_pool.get(e.id) is not None
    
    def test_list_registered(self, expert_pool, mock_experts):
        for e in mock_experts(3):
            expert_pool.register(e)
        assert len(expert_pool.list_registered()) >= 3
    
    def test_snapshot(self, expert_pool, mock_experts):
        for e in mock_experts(2):
            expert_pool.register(e)
        snap = expert_pool.snapshot()
        assert "registered" in snap


class TestSelectExpertsIntegration:
    def test_full_selection_flow(self, mock_experts, mock_llm_provider):
        pool = ExpertPool(llm_provider=mock_llm_provider)
        for e in mock_experts(10):
            pool.register(e)
        result = pool.select_experts("Business strategy question", min_experts=3, max_experts=5)
        assert 3 <= len(result) <= 5
        assert isinstance(result, tuple)
    
    def test_set_llm_provider_after_init(self, mock_experts, mock_llm_provider):
        pool = ExpertPool()
        for e in mock_experts(3):
            pool.register(e)
        result1 = pool.select_experts("test")
        assert len(result1) >= 1
        pool.set_llm_provider(mock_llm_provider)
        pool.select_experts("test")
        assert len(mock_llm_provider.call_history) > 0
