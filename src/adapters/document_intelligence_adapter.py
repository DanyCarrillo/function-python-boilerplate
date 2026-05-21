import logging
from typing import Optional

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

from src.ports.document_intelligence_port import DocumentIntelligencePort


class DocumentIntelligenceAdapter(DocumentIntelligencePort):
    def __init__(self, endpoint: str, api_key: str):
        self._client = DocumentIntelligenceClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(api_key),
        )

    def analyze_document(
        self,
        document_url: Optional[str] = None,
        document_bytes: Optional[bytes] = None,
        model_id: str = "prebuilt-document",
    ) -> dict:
        try:
            if document_url:
                poller = self._client.begin_analyze_document(
                    model_id=model_id,
                    analyze_request={"urlSource": document_url},
                )
            elif document_bytes:
                poller = self._client.begin_analyze_document(
                    model_id=model_id,
                    analyze_request=document_bytes,
                    content_type="application/octet-stream",
                )
            else:
                raise ValueError("Either document_url or document_bytes must be provided.")
            return poller.result().as_dict()
        except ValueError:
            raise
        except Exception as e:
            logging.error(f"[DocumentIntelligenceAdapter - analyze_document] Error: {e}")
            raise
