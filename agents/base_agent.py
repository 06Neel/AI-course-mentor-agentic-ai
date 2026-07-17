from abc import ABC, abstractmethod

from llm.groq_provider import GroqProvider
from config.settings import Settings


class BaseAgent(ABC):
    def __init__(self, api_key: str = None, model: str = None):
        self.llm = GroqProvider(api_key=api_key, model=model)
        self.settings = Settings()

    @abstractmethod
    def run(self, query: str, context: str = "", **kwargs) -> str:
        pass
