from abc import ABC, abstractmethod
from typing import Optional


class DocumentIntelligencePort(ABC):
    @abstractmethod
    def analyze_document(
        self,
        document_url: Optional[str] = None,
        document_bytes: Optional[bytes] = None,
        model_id: str = "prebuilt-document",
    ) -> dict:
        pass
