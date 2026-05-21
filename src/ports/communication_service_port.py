from abc import ABC, abstractmethod
from typing import List, Optional


class CommunicationServicePort(ABC):
    @abstractmethod
    def send_email(
        self,
        sender: str,
        recipients: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None,
    ) -> str:
        pass

    @abstractmethod
    def send_sms(self, from_number: str, to_number: str, message: str) -> str:
        pass
