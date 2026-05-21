from abc import ABC, abstractmethod
from typing import List, Optional


class CosmosdbPort(ABC):
    @abstractmethod
    def save(self, data: dict) -> dict:
        pass

    @abstractmethod
    def get_by_id(self, item_id: str, partition_key: str) -> Optional[dict]:
        pass

    @abstractmethod
    def query(self, query: str, parameters: Optional[list] = None) -> List[dict]:
        pass

    @abstractmethod
    def delete(self, item_id: str, partition_key: str) -> None:
        pass
