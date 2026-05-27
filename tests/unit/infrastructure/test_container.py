import pytest
from unittest.mock import patch

from src.application.boilerplate_service import BoilerplateService
from src.infrastructure.config import Config
from src.infrastructure.container import Container

_ADAPTERS_TO_PATCH = [
    "src.infrastructure.container.BlobStorageAdapter",
    "src.infrastructure.container.CosmosdbAdapter",
    "src.infrastructure.container.AISearchAdapter",
    "src.infrastructure.container.OpenAIAdapter",
    "src.infrastructure.container.DocumentIntelligenceAdapter",
    "src.infrastructure.container.AIFoundryAdapter",
    "src.infrastructure.container.CommunicationServiceAdapter",
    "src.infrastructure.container.GraphAPIAdapter",
]


@pytest.fixture
def config():
    return Config(
        blob_connection_string="blob-conn",
        cosmos_connection_string="cosmos-conn",
        cosmos_database="db",
        cosmos_container="container",
        search_endpoint="https://search",
        search_api_key="search-key",
        search_index="index",
        openai_endpoint="https://openai",
        openai_api_key="openai-key",
        openai_api_version="2024-02-01",
        openai_chat_model="gpt-4o",
        openai_embedding_model="text-embedding-3-large",
        doc_intelligence_endpoint="https://doc-intel",
        doc_intelligence_api_key="doc-key",
        ai_foundry_endpoint="https://foundry",
        ai_foundry_api_key="foundry-key",
        ai_foundry_model="Phi-3",
        acs_connection_string="acs-conn",
        graph_tenant_id="tenant-id",
        graph_client_id="client-id",
        graph_client_secret="client-secret",
    )


class TestContainer:
    def test_blob_storage_is_singleton(self, config):
        with patch("src.infrastructure.container.BlobStorageAdapter") as Mock:
            container = Container(config)
            assert container.blob_storage is container.blob_storage
            Mock.assert_called_once()

    def test_cosmosdb_is_singleton(self, config):
        with patch("src.infrastructure.container.CosmosdbAdapter") as Mock:
            container = Container(config)
            assert container.cosmosdb is container.cosmosdb
            Mock.assert_called_once()

    def test_ai_search_is_singleton(self, config):
        with patch("src.infrastructure.container.AISearchAdapter") as Mock:
            container = Container(config)
            assert container.ai_search is container.ai_search
            Mock.assert_called_once()

    def test_openai_is_singleton(self, config):
        with patch("src.infrastructure.container.OpenAIAdapter") as Mock:
            container = Container(config)
            assert container.openai is container.openai
            Mock.assert_called_once()

    def test_document_intelligence_is_singleton(self, config):
        with patch("src.infrastructure.container.DocumentIntelligenceAdapter") as Mock:
            container = Container(config)
            assert container.document_intelligence is container.document_intelligence
            Mock.assert_called_once()

    def test_ai_foundry_is_singleton(self, config):
        with patch("src.infrastructure.container.AIFoundryAdapter") as Mock:
            container = Container(config)
            assert container.ai_foundry is container.ai_foundry
            Mock.assert_called_once()

    def test_communication_service_is_singleton(self, config):
        with patch("src.infrastructure.container.CommunicationServiceAdapter") as Mock:
            container = Container(config)
            assert container.communication_service is container.communication_service
            Mock.assert_called_once()

    def test_graph_api_is_singleton(self, config):
        with patch("src.infrastructure.container.GraphAPIAdapter") as Mock:
            container = Container(config)
            assert container.graph_api is container.graph_api
            Mock.assert_called_once()

    def test_boilerplate_service_is_singleton(self, config):
        with patch("src.infrastructure.container.BlobStorageAdapter"), \
             patch("src.infrastructure.container.CosmosdbAdapter"), \
             patch("src.infrastructure.container.AISearchAdapter"), \
             patch("src.infrastructure.container.OpenAIAdapter"), \
             patch("src.infrastructure.container.DocumentIntelligenceAdapter"), \
             patch("src.infrastructure.container.AIFoundryAdapter"), \
             patch("src.infrastructure.container.CommunicationServiceAdapter"), \
             patch("src.infrastructure.container.GraphAPIAdapter"):
            container = Container(config)
            assert container.boilerplate_service is container.boilerplate_service

    def test_boilerplate_service_is_instance_of_correct_class(self, config):
        with patch("src.infrastructure.container.BlobStorageAdapter"), \
             patch("src.infrastructure.container.CosmosdbAdapter"), \
             patch("src.infrastructure.container.AISearchAdapter"), \
             patch("src.infrastructure.container.OpenAIAdapter"), \
             patch("src.infrastructure.container.DocumentIntelligenceAdapter"), \
             patch("src.infrastructure.container.AIFoundryAdapter"), \
             patch("src.infrastructure.container.CommunicationServiceAdapter"), \
             patch("src.infrastructure.container.GraphAPIAdapter"):
            container = Container(config)
            assert isinstance(container.boilerplate_service, BoilerplateService)

    def test_blob_storage_receives_correct_connection_string(self, config):
        with patch("src.infrastructure.container.BlobStorageAdapter") as Mock:
            container = Container(config)
            _ = container.blob_storage
            Mock.assert_called_once_with(connection_string="blob-conn")

    def test_cosmosdb_receives_correct_params(self, config):
        with patch("src.infrastructure.container.CosmosdbAdapter") as Mock:
            container = Container(config)
            _ = container.cosmosdb
            Mock.assert_called_once_with(
                connection_string="cosmos-conn",
                database_name="db",
                container_name="container",
            )
