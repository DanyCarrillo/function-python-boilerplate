import logging
from typing import List, Optional

from openai import AzureOpenAI

from src.ports.openai_port import OpenAIPort


class OpenAIAdapter(OpenAIPort):
    def __init__(
        self,
        endpoint: str,
        api_key: str,
        api_version: str,
        chat_model: str,
        embedding_model: str,
    ):
        self._client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
        )
        self._chat_model = chat_model
        self._embedding_model = embedding_model

    def chat_completion(self, messages: List[dict], model: Optional[str] = None, **kwargs) -> str:
        try:
            response = self._client.chat.completions.create(
                model=model or self._chat_model,
                messages=messages,
                **kwargs,
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"[OpenAIAdapter - chat_completion] Error: {e}")
            raise

    def get_embeddings(self, text: str, model: Optional[str] = None) -> List[float]:
        try:
            response = self._client.embeddings.create(
                model=model or self._embedding_model,
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            logging.error(f"[OpenAIAdapter - get_embeddings] Error: {e}")
            raise
