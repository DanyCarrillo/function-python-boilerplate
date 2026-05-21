from src.adapters.ai_foundry_adapter import AIFoundryAdapter
from src.adapters.ai_search_adapter import AISearchAdapter
from src.adapters.blob_storage_adapter import BlobStorageAdapter
from src.adapters.communication_service_adapter import CommunicationServiceAdapter
from src.adapters.cosmosdb_adapter import CosmosdbAdapter
from src.adapters.document_intelligence_adapter import DocumentIntelligenceAdapter
from src.adapters.graph_api_adapter import GraphAPIAdapter
from src.adapters.openai_adapter import OpenAIAdapter
from src.application.boilerplate_service import BoilerplateService
from src.infrastructure.config import Config


class Container:
    """Lazy dependency injection container — adapters are instantiated on first access."""

    def __init__(self, config: Config):
        self._config = config
        self._blob_storage: BlobStorageAdapter | None = None
        self._cosmosdb: CosmosdbAdapter | None = None
        self._ai_search: AISearchAdapter | None = None
        self._openai: OpenAIAdapter | None = None
        self._document_intelligence: DocumentIntelligenceAdapter | None = None
        self._ai_foundry: AIFoundryAdapter | None = None
        self._communication_service: CommunicationServiceAdapter | None = None
        self._graph_api: GraphAPIAdapter | None = None
        self._boilerplate_service: BoilerplateService | None = None

    @property
    def blob_storage(self) -> BlobStorageAdapter:
        if self._blob_storage is None:
            self._blob_storage = BlobStorageAdapter(
                connection_string=self._config.blob_connection_string,
            )
        return self._blob_storage

    @property
    def cosmosdb(self) -> CosmosdbAdapter:
        if self._cosmosdb is None:
            self._cosmosdb = CosmosdbAdapter(
                connection_string=self._config.cosmos_connection_string,
                database_name=self._config.cosmos_database,
                container_name=self._config.cosmos_container,
            )
        return self._cosmosdb

    @property
    def ai_search(self) -> AISearchAdapter:
        if self._ai_search is None:
            self._ai_search = AISearchAdapter(
                endpoint=self._config.search_endpoint,
                api_key=self._config.search_api_key,
                index_name=self._config.search_index,
            )
        return self._ai_search

    @property
    def openai(self) -> OpenAIAdapter:
        if self._openai is None:
            self._openai = OpenAIAdapter(
                endpoint=self._config.openai_endpoint,
                api_key=self._config.openai_api_key,
                api_version=self._config.openai_api_version,
                chat_model=self._config.openai_chat_model,
                embedding_model=self._config.openai_embedding_model,
            )
        return self._openai

    @property
    def document_intelligence(self) -> DocumentIntelligenceAdapter:
        if self._document_intelligence is None:
            self._document_intelligence = DocumentIntelligenceAdapter(
                endpoint=self._config.doc_intelligence_endpoint,
                api_key=self._config.doc_intelligence_api_key,
            )
        return self._document_intelligence

    @property
    def ai_foundry(self) -> AIFoundryAdapter:
        if self._ai_foundry is None:
            self._ai_foundry = AIFoundryAdapter(
                endpoint=self._config.ai_foundry_endpoint,
                api_key=self._config.ai_foundry_api_key,
                model_name=self._config.ai_foundry_model,
            )
        return self._ai_foundry

    @property
    def communication_service(self) -> CommunicationServiceAdapter:
        if self._communication_service is None:
            self._communication_service = CommunicationServiceAdapter(
                connection_string=self._config.acs_connection_string,
            )
        return self._communication_service

    @property
    def graph_api(self) -> GraphAPIAdapter:
        if self._graph_api is None:
            self._graph_api = GraphAPIAdapter(
                tenant_id=self._config.graph_tenant_id,
                client_id=self._config.graph_client_id,
                client_secret=self._config.graph_client_secret,
            )
        return self._graph_api

    @property
    def boilerplate_service(self) -> BoilerplateService:
        if self._boilerplate_service is None:
            self._boilerplate_service = BoilerplateService(
                blob_storage=self.blob_storage,
                cosmosdb=self.cosmosdb,
                ai_search=self.ai_search,
                openai=self.openai,
                document_intelligence=self.document_intelligence,
                ai_foundry=self.ai_foundry,
                communication_service=self.communication_service,
                graph_api=self.graph_api,
            )
        return self._boilerplate_service
