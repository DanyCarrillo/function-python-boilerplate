from abc import ABC, abstractmethod
from typing import List, Optional


class GraphAPIPort(ABC):
    @abstractmethod
    def get_user(self, user_id: str) -> dict:
        pass

    @abstractmethod
    def send_email(self, user_id: str, recipients: List[str], subject: str, body: str) -> None:
        pass

    @abstractmethod
    def list_users(self, filter_query: Optional[str] = None) -> List[dict]:
        pass
