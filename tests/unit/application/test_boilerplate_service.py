import pytest
from unittest.mock import MagicMock

from src.application.boilerplate_service import BoilerplateService
from src.domain.entities.document_entity import DocumentEntity
from src.domain.exceptions.domain_exceptions import IntegrationException


@pytest.fixture
def mocks():
    return {
        "blob_storage": MagicMock(),
        "cosmosdb": MagicMock(),
        "ai_search": MagicMock(),
        "openai": MagicMock(),
        "document_intelligence": MagicMock(),
        "ai_foundry": MagicMock(),
        "communication_service": MagicMock(),
        "graph_api": MagicMock(),
    }


@pytest.fixture
def service(mocks):
    return BoilerplateService(**mocks)


class TestBoilerplateService:
    def test_process_document_returns_entity(self, service, mocks):
        mocks["document_intelligence"].analyze_document.return_value = {"content": "doc text"}
        mocks["openai"].get_embeddings.return_value = [0.1, 0.2, 0.3]

        result = service.process_document("https://doc.url", "doc-001")

        assert isinstance(result, DocumentEntity)
        assert result.id == "doc-001"
        assert result.content == "doc text"

    def test_process_document_saves_to_cosmosdb(self, service, mocks):
        mocks["document_intelligence"].analyze_document.return_value = {"content": "text"}
        mocks["openai"].get_embeddings.return_value = [0.5]

        service.process_document("https://doc.url", "doc-002")

        mocks["cosmosdb"].save.assert_called_once()
        saved = mocks["cosmosdb"].save.call_args[0][0]
        assert saved["id"] == "doc-002"
        assert saved["content"] == "text"
        assert saved["embeddings"] == [0.5]

    def test_process_document_uploads_to_ai_search(self, service, mocks):
        mocks["document_intelligence"].analyze_document.return_value = {"content": "text"}
        mocks["openai"].get_embeddings.return_value = [0.5]

        service.process_document("https://doc.url", "doc-003")

        mocks["ai_search"].upload_documents.assert_called_once()
        docs = mocks["ai_search"].upload_documents.call_args[0][0]
        assert docs[0]["id"] == "doc-003"
        assert docs[0]["embeddings"] == [0.5]

    def test_process_document_truncates_content_for_embeddings(self, service, mocks):
        long_content = "x" * 10000
        mocks["document_intelligence"].analyze_document.return_value = {"content": long_content}
        mocks["openai"].get_embeddings.return_value = [0.1]

        service.process_document("https://doc.url", "doc-004")

        call_args = mocks["openai"].get_embeddings.call_args
        assert len(call_args.kwargs.get("text", call_args[0][0] if call_args[0] else "")) <= 8000

    def test_process_document_raises_integration_exception_on_error(self, service, mocks):
        mocks["document_intelligence"].analyze_document.side_effect = Exception("service down")

        with pytest.raises(IntegrationException):
            service.process_document("https://doc.url", "doc-005")

    def test_process_document_handles_empty_content(self, service, mocks):
        mocks["document_intelligence"].analyze_document.return_value = {}
        mocks["openai"].get_embeddings.return_value = []

        result = service.process_document("https://doc.url", "doc-006")

        assert result.content == ""
