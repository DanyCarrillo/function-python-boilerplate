import pytest
from unittest.mock import MagicMock, patch

from src.adapters.openai_adapter import OpenAIAdapter


@pytest.fixture
def adapter():
    with patch("src.adapters.openai_adapter.AzureOpenAI") as mock_cls:
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        instance = OpenAIAdapter(
            endpoint="https://endpoint",
            api_key="api_key",
            api_version="2024-02-01",
            chat_model="gpt-4o",
            embedding_model="text-embedding-3-large",
        )
        instance._client = mock_client
        yield instance, mock_client


class TestOpenAIAdapter:
    def test_chat_completion_returns_content(self, adapter):
        instance, mock_client = adapter
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Hello, world!"
        mock_client.chat.completions.create.return_value = mock_response

        result = instance.chat_completion([{"role": "user", "content": "Hi"}])

        assert result == "Hello, world!"

    def test_chat_completion_uses_default_model(self, adapter):
        instance, mock_client = adapter
        mock_client.chat.completions.create.return_value = MagicMock()

        instance.chat_completion([{"role": "user", "content": "Hi"}])

        kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert kwargs["model"] == "gpt-4o"

    def test_chat_completion_uses_override_model(self, adapter):
        instance, mock_client = adapter
        mock_client.chat.completions.create.return_value = MagicMock()

        instance.chat_completion([{"role": "user", "content": "Hi"}], model="gpt-35-turbo")

        kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert kwargs["model"] == "gpt-35-turbo"

    def test_chat_completion_raises_on_error(self, adapter):
        instance, mock_client = adapter
        mock_client.chat.completions.create.side_effect = Exception("api error")

        with pytest.raises(Exception, match="api error"):
            instance.chat_completion([])

    def test_get_embeddings_returns_vector(self, adapter):
        instance, mock_client = adapter
        mock_response = MagicMock()
        mock_response.data[0].embedding = [0.1, 0.2, 0.3]
        mock_client.embeddings.create.return_value = mock_response

        result = instance.get_embeddings("some text")

        assert result == [0.1, 0.2, 0.3]

    def test_get_embeddings_uses_default_model(self, adapter):
        instance, mock_client = adapter
        mock_client.embeddings.create.return_value = MagicMock()

        instance.get_embeddings("text")

        kwargs = mock_client.embeddings.create.call_args.kwargs
        assert kwargs["model"] == "text-embedding-3-large"

    def test_get_embeddings_raises_on_error(self, adapter):
        instance, mock_client = adapter
        mock_client.embeddings.create.side_effect = Exception("embedding error")

        with pytest.raises(Exception, match="embedding error"):
            instance.get_embeddings("text")
