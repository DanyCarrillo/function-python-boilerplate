import pytest
from unittest.mock import MagicMock, patch

from src.adapters.ai_foundry_adapter import AIFoundryAdapter


@pytest.fixture
def adapter():
    with patch("src.adapters.ai_foundry_adapter.ChatCompletionsClient") as mock_cls:
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        instance = AIFoundryAdapter("https://endpoint", "api_key", "Phi-3")
        instance._client = mock_client
        yield instance, mock_client


class TestAIFoundryAdapter:
    def test_chat_completion_returns_content(self, adapter):
        instance, mock_client = adapter
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "AI response"
        mock_client.complete.return_value = mock_response

        result = instance.chat_completion([{"role": "user", "content": "Hello"}])

        assert result == "AI response"

    def test_chat_completion_maps_system_and_user_messages(self, adapter):
        instance, mock_client = adapter
        mock_client.complete.return_value = MagicMock()

        instance.chat_completion([
            {"role": "system", "content": "You are a bot"},
            {"role": "user", "content": "Hello"},
        ])

        call_kwargs = mock_client.complete.call_args.kwargs
        messages = call_kwargs["messages"]
        assert len(messages) == 2

    def test_chat_completion_uses_default_model(self, adapter):
        instance, mock_client = adapter
        mock_client.complete.return_value = MagicMock()

        instance.chat_completion([{"role": "user", "content": "Hi"}])

        kwargs = mock_client.complete.call_args.kwargs
        assert kwargs["model"] == "Phi-3"

    def test_chat_completion_uses_override_model(self, adapter):
        instance, mock_client = adapter
        mock_client.complete.return_value = MagicMock()

        instance.chat_completion([{"role": "user", "content": "Hi"}], model="Llama-3")

        kwargs = mock_client.complete.call_args.kwargs
        assert kwargs["model"] == "Llama-3"

    def test_chat_completion_raises_on_error(self, adapter):
        instance, mock_client = adapter
        mock_client.complete.side_effect = Exception("foundry error")

        with pytest.raises(Exception, match="foundry error"):
            instance.chat_completion([])
