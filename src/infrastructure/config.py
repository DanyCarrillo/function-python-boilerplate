import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    # Azure Blob Storage
    blob_connection_string: str

    # Azure CosmosDB
    cosmos_connection_string: str
    cosmos_database: str
    cosmos_container: str

    # Azure AI Search
    search_endpoint: str
    search_api_key: str
    search_index: str

    # Azure OpenAI
    openai_endpoint: str
    openai_api_key: str
    openai_api_version: str
    openai_chat_model: str
    openai_embedding_model: str

    # Azure Document Intelligence
    doc_intelligence_endpoint: str
    doc_intelligence_api_key: str

    # Azure AI Foundry
    ai_foundry_endpoint: str
    ai_foundry_api_key: str
    ai_foundry_model: str

    # Azure Communication Service
    acs_connection_string: str

    # Microsoft Graph API
    graph_tenant_id: str
    graph_client_id: str
    graph_client_secret: str

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            blob_connection_string=os.environ["BLOB_CONNECTION_STRING"],
            cosmos_connection_string=os.environ["COSMOS_CONNECTION_STRING"],
            cosmos_database=os.environ["COSMOS_DATABASE"],
            cosmos_container=os.environ["COSMOS_CONTAINER"],
            search_endpoint=os.environ["SEARCH_ENDPOINT"],
            search_api_key=os.environ["SEARCH_API_KEY"],
            search_index=os.environ["SEARCH_INDEX"],
            openai_endpoint=os.environ["OPENAI_ENDPOINT"],
            openai_api_key=os.environ["OPENAI_API_KEY"],
            openai_api_version=os.environ.get("OPENAI_API_VERSION", "2024-02-01"),
            openai_chat_model=os.environ["OPENAI_CHAT_MODEL"],
            openai_embedding_model=os.environ["OPENAI_EMBEDDING_MODEL"],
            doc_intelligence_endpoint=os.environ["DOC_INTELLIGENCE_ENDPOINT"],
            doc_intelligence_api_key=os.environ["DOC_INTELLIGENCE_API_KEY"],
            ai_foundry_endpoint=os.environ["AI_FOUNDRY_ENDPOINT"],
            ai_foundry_api_key=os.environ["AI_FOUNDRY_API_KEY"],
            ai_foundry_model=os.environ["AI_FOUNDRY_MODEL"],
            acs_connection_string=os.environ["ACS_CONNECTION_STRING"],
            graph_tenant_id=os.environ["GRAPH_TENANT_ID"],
            graph_client_id=os.environ["GRAPH_CLIENT_ID"],
            graph_client_secret=os.environ["GRAPH_CLIENT_SECRET"],
        )
