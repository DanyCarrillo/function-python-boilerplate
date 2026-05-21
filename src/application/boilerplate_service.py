import logging

from src.domain.entities.document_entity import DocumentEntity
from src.domain.exceptions.domain_exceptions import IntegrationException
from src.ports.ai_foundry_port import AIFoundryPort
from src.ports.ai_search_port import AISearchPort
from src.ports.blob_storage_port import BlobStoragePort
from src.ports.communication_service_port import CommunicationServicePort
from src.ports.cosmosdb_port import CosmosdbPort
from src.ports.document_intelligence_port import DocumentIntelligencePort
from src.ports.graph_api_port import GraphAPIPort
from src.ports.openai_port import OpenAIPort


class BoilerplateService:
    def __init__(
        self,
        blob_storage: BlobStoragePort,
        cosmosdb: CosmosdbPort,
        ai_search: AISearchPort,
        openai: OpenAIPort,
        document_intelligence: DocumentIntelligencePort,
        ai_foundry: AIFoundryPort,
        communication_service: CommunicationServicePort,
        graph_api: GraphAPIPort,
    ):
        self._blob_storage = blob_storage
        self._cosmosdb = cosmosdb
        self._ai_search = ai_search
        self._openai = openai
        self._document_intelligence = document_intelligence
        self._ai_foundry = ai_foundry
        self._communication_service = communication_service
        self._graph_api = graph_api

    def process_document(self, document_url: str, document_id: str) -> DocumentEntity:
        """Analyse a document, generate embeddings, and persist to CosmosDB + AI Search."""
        try:
            analysis = self._document_intelligence.analyze_document(document_url=document_url)
            content = analysis.get("content", "")

            embeddings = self._openai.get_embeddings(text=content[:8000])

            entity = DocumentEntity(id=document_id, content=content)
            self._cosmosdb.save({**entity.to_dict(), "embeddings": embeddings})

            self._ai_search.upload_documents([{
                "id": document_id,
                "content": content,
                "embeddings": embeddings,
            }])

            logging.info(f"[BoilerplateService - process_document] Document {document_id} processed.")
            return entity
        except Exception as e:
            logging.error(f"[BoilerplateService - process_document] Error: {e}")
            raise IntegrationException(str(e)) from e
