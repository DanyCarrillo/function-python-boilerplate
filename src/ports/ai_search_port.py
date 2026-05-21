from abc import ABC, abstractmethod
from typing import List, Optional


class AISearchPort(ABC):
    @abstractmethod
    def search(self, query: str, filter_query: Optional[str] = None, top: int = 10) -> List[dict]:
        pass

    @abstractmethod
    def upload_documents(self, documents: List[dict]) -> None:
        pass

    @abstractmethod
    def delete_documents(self, document_ids: List[str]) -> None:
        pass
