import pytest
from unittest.mock import MagicMock, patch

from src.adapters.communication_service_adapter import CommunicationServiceAdapter


@pytest.fixture
def adapter():
    with patch("src.adapters.communication_service_adapter.EmailClient") as mock_email_cls, \
         patch("src.adapters.communication_service_adapter.SmsClient") as mock_sms_cls:
        mock_email = MagicMock()
        mock_sms = MagicMock()
        mock_email_cls.from_connection_string.return_value = mock_email
        mock_sms_cls.from_connection_string.return_value = mock_sms
        instance = CommunicationServiceAdapter("endpoint=...;accesskey=...")
        instance._email_client = mock_email
        instance._sms_client = mock_sms
        yield instance, mock_email, mock_sms


class TestCommunicationServiceAdapter:
    def test_send_email_returns_id(self, adapter):
        instance, mock_email, _ = adapter
        mock_email.begin_send.return_value.result.return_value = {"id": "msg-123"}

        result = instance.send_email(
            sender="sender@example.com",
            recipients=["to@example.com"],
            subject="Test",
            body="Hello",
        )

        assert result == "msg-123"

    def test_send_email_with_html_body(self, adapter):
        instance, mock_email, _ = adapter
        mock_email.begin_send.return_value.result.return_value = {"id": "msg-456"}

        instance.send_email(
            sender="sender@example.com",
            recipients=["to@example.com"],
            subject="Test",
            body="Plain",
            html_body="<b>Bold</b>",
        )

        call_message = mock_email.begin_send.call_args[0][0]
        assert "html" in call_message["content"]
        assert call_message["content"]["html"] == "<b>Bold</b>"

    def test_send_email_without_html_body(self, adapter):
        instance, mock_email, _ = adapter
        mock_email.begin_send.return_value.result.return_value = {"id": "msg-789"}

        instance.send_email("s@e.com", ["r@e.com"], "Subj", "Body")

        call_message = mock_email.begin_send.call_args[0][0]
        assert "html" not in call_message["content"]

    def test_send_email_raises_on_error(self, adapter):
        instance, mock_email, _ = adapter
        mock_email.begin_send.side_effect = Exception("email error")

        with pytest.raises(Exception, match="email error"):
            instance.send_email("s@e.com", ["r@e.com"], "Subj", "Body")

    def test_send_sms_returns_message_id(self, adapter):
        instance, _, mock_sms = adapter
        mock_response = MagicMock()
        mock_response.message_id = "sms-789"
        mock_sms.send.return_value = mock_response

        result = instance.send_sms("+10000000000", "+19999999999", "Hello")

        assert result == "sms-789"

    def test_send_sms_raises_on_error(self, adapter):
        instance, _, mock_sms = adapter
        mock_sms.send.side_effect = Exception("sms error")

        with pytest.raises(Exception, match="sms error"):
            instance.send_sms("+1", "+2", "msg")
