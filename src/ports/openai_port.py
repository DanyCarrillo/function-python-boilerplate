from abc import ABC, abstractmethod
from typing import List, Optional


class OpenAIPort(ABC):
    @abstractmethod
    def chat_completion(self, messages: List[dict], model: Optional[str] = None, **kwargs) -> str:
        pass

    @abstractmethod
    def get_embeddings(self, text: str, model: Optional[str] = None) -> List[float]:
        pass
