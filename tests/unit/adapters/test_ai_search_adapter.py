import pytest
from unittest.mock import MagicMock, patch

from src.adapters.ai_search_adapter import AISearchAdapter


@pytest.fixture
def adapter():
    with patch("src.adapters.ai_search_adapter.SearchClient") as mock_cls:
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        instance = AISearchAdapter("https://endpoint", "api_key", "index_name")
        instance._client = mock_client
        yield instance, mock_client


class TestAISearchAdapter:
    def test_search_returns_results(self, adapter):
        instance, mock_client = adapter
        mock_client.search.return_value = [{"id": "1", "content": "doc"}]

        result = instance.search("query", top=5)

        assert result == [{"id": "1", "content": "doc"}]
        mock_client.search.assert_called_once_with(search_text="query", filter=None, top=5)

    def test_search_with_filter(self, adapter):
        instance, mock_client = adapter
        mock_client.search.return_value = []

        instance.search("query", filter_query="type eq 'pdf'")

        mock_client.search.assert_called_once_with(
            search_text="query", filter="type eq 'pdf'", top=10
        )

    def test_search_raises_on_error(self, adapter):
        instance, mock_client = adapter
        mock_client.search.side_effect = Exception("search error")

        with pytest.raises(Exception, match="search error"):
            instance.search("query")

    def test_upload_documents(self, adapter):
        instance, mock_client = adapter
        docs = [{"id": "1"}, {"id": "2"}]

        instance.upload_documents(docs)

        mock_client.upload_documents.assert_called_once_with(documents=docs)

    def test_upload_documents_raises_on_error(self, adapter):
        instance, mock_client = adapter
        mock_client.upload_documents.side_effect = Exception("upload error")

        with pytest.raises(Exception, match="upload error"):
            instance.upload_documents([{"id": "1"}])

    def test_delete_documents(self, adapter):
        instance, mock_client = adapter

        instance.delete_documents(["1", "2"])

        mock_client.delete_documents.assert_called_once_with(
            documents=[{"id": "1"}, {"id": "2"}]
        )

    def test_delete_documents_raises_on_error(self, adapter):
        instance, mock_client = adapter
        mock_client.delete_documents.side_effect = Exception("delete error")

        with pytest.raises(Exception, match="delete error"):
            instance.delete_documents(["1"])
