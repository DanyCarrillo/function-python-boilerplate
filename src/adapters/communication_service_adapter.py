import logging
from typing import List, Optional

from azure.communication.email import EmailClient
from azure.communication.sms import SmsClient

from src.ports.communication_service_port import CommunicationServicePort


class CommunicationServiceAdapter(CommunicationServicePort):
    def __init__(self, connection_string: str):
        self._email_client = EmailClient.from_connection_string(connection_string)
        self._sms_client = SmsClient.from_connection_string(connection_string)

    def send_email(
        self,
        sender: str,
        recipients: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None,
    ) -> str:
        try:
            content = {"subject": subject, "plainText": body}
            if html_body:
                content["html"] = html_body

            message = {
                "senderAddress": sender,
                "recipients": {"to": [{"address": r} for r in recipients]},
                "content": content,
            }
            poller = self._email_client.begin_send(message)
            return poller.result()["id"]
        except Exception as e:
            logging.error(f"[CommunicationServiceAdapter - send_email] Error: {e}")
            raise

    def send_sms(self, from_number: str, to_number: str, message: str) -> str:
        try:
            response = self._sms_client.send(
                from_=from_number,
                to=to_number,
                message=message,
            )
            return response.message_id
        except Exception as e:
            logging.error(f"[CommunicationServiceAdapter - send_sms] Error: {e}")
            raise
