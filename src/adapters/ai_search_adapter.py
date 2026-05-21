import logging
from typing import List, Optional

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

from src.ports.ai_search_port import AISearchPort


class AISearchAdapter(AISearchPort):
    def __init__(self, endpoint: str, api_key: str, index_name: str):
        self._client = SearchClient(
            endpoint=endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(api_key),
        )

    def search(self, query: str, filter_query: Optional[str] = None, top: int = 10) -> List[dict]:
        try:
            results = self._client.search(search_text=query, filter=filter_query, top=top)
            return [dict(r) for r in results]
        except Exception as e:
            logging.error(f"[AISearchAdapter - search] Error: {e}")
            raise

    def upload_documents(self, documents: List[dict]) -> None:
        try:
            self._client.upload_documents(documents=documents)
        except Exception as e:
            logging.error(f"[AISearchAdapter - upload_documents] Error: {e}")
            raise

    def delete_documents(self, document_ids: List[str]) -> None:
        try:
            docs = [{"id": doc_id} for doc_id in document_ids]
            self._client.delete_documents(documents=docs)
        except Exception as e:
            logging.error(f"[AISearchAdapter - delete_documents] Error: {e}")
            raise
