import pytest
from unittest.mock import MagicMock, patch

from src.adapters.document_intelligence_adapter import DocumentIntelligenceAdapter


@pytest.fixture
def adapter():
    with patch("src.adapters.document_intelligence_adapter.DocumentIntelligenceClient") as mock_cls:
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        instance = DocumentIntelligenceAdapter("https://endpoint", "api_key")
        instance._client = mock_client
        yield instance, mock_client


class TestDocumentIntelligenceAdapter:
    def test_analyze_from_url_returns_dict(self, adapter):
        instance, mock_client = adapter
        mock_result = MagicMock()
        mock_result.as_dict.return_value = {"content": "extracted text"}
        mock_client.begin_analyze_document.return_value.result.return_value = mock_result

        result = instance.analyze_document(document_url="https://example.com/doc.pdf")

        assert result == {"content": "extracted text"}
        call_kwargs = mock_client.begin_analyze_document.call_args.kwargs
        assert call_kwargs["analyze_request"] == {"urlSource": "https://example.com/doc.pdf"}

    def test_analyze_from_bytes_returns_dict(self, adapter):
        instance, mock_client = adapter
        mock_result = MagicMock()
        mock_result.as_dict.return_value = {"content": "text from bytes"}
        mock_client.begin_analyze_document.return_value.result.return_value = mock_result

        result = instance.analyze_document(document_bytes=b"PDF content")

        assert result == {"content": "text from bytes"}

    def test_analyze_raises_when_no_source(self, adapter):
        instance, _ = adapter

        with pytest.raises(ValueError, match="Either document_url or document_bytes must be provided."):
            instance.analyze_document()

    def test_analyze_raises_on_client_error(self, adapter):
        instance, mock_client = adapter
        mock_client.begin_analyze_document.side_effect = Exception("service error")

        with pytest.raises(Exception, match="service error"):
            instance.analyze_document(document_url="https://example.com/doc.pdf")

    def test_analyze_uses_custom_model_id(self, adapter):
        instance, mock_client = adapter
        mock_result = MagicMock()
        mock_result.as_dict.return_value = {}
        mock_client.begin_analyze_document.return_value.result.return_value = mock_result

        instance.analyze_document(document_url="https://example.com/doc.pdf", model_id="prebuilt-invoice")

        call_kwargs = mock_client.begin_analyze_document.call_args.kwargs
        assert call_kwargs["model_id"] == "prebuilt-invoice"
