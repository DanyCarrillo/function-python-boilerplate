from abc import ABC, abstractmethod
from typing import List, Optional


class AIFoundryPort(ABC):
    @abstractmethod
    def chat_completion(self, messages: List[dict], model: Optional[str] = None, **kwargs) -> str:
        pass
