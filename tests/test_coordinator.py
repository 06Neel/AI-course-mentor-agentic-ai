import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.coordinator import CoordinatorAgent


class TestCoordinator:
    def test_intent_classification(self):
        coordinator = CoordinatorAgent.__new__(CoordinatorAgent)
        coordinator.llm = None
        coordinator.retriever = None
        coordinator.agents = {}

        from unittest.mock import MagicMock
        coordinator.llm = MagicMock()
        coordinator.llm.generate.return_value = '{"intent": "quiz_generation", "topic": "machine learning", "confidence": 0.9}'

        from rag.retriever import Retriever
        coordinator.retriever = MagicMock(spec=Retriever)
        coordinator.retriever.is_available = False

        result = coordinator.classify_intent("Generate 10 MCQs on machine learning")
        assert result["intent"] == "quiz_generation"
        assert "machine learning" in result["topic"].lower()

    def test_intent_policy_query(self):
        coordinator = CoordinatorAgent.__new__(CoordinatorAgent)
        from unittest.mock import MagicMock
        coordinator.llm = MagicMock()
        coordinator.llm.generate.return_value = '{"intent": "policy_query", "topic": "attendance", "confidence": 0.85}'
        coordinator.retriever = MagicMock()
        coordinator.retriever.is_available = False

        result = coordinator.classify_intent("What is the attendance policy?")
        assert result["intent"] == "policy_query"


if __name__ == "__main__":
    test = TestCoordinator()
    test.test_intent_classification()
    test.test_intent_policy_query()
    print("All coordinator tests passed!")
