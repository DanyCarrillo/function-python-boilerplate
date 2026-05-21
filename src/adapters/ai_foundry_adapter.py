import logging
from typing import List, Optional

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

from src.ports.ai_foundry_port import AIFoundryPort


class AIFoundryAdapter(AIFoundryPort):
    def __init__(self, endpoint: str, api_key: str, model_name: str):
        self._client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(api_key),
        )
        self._model_name = model_name

    def chat_completion(self, messages: List[dict], model: Optional[str] = None, **kwargs) -> str:
        try:
            inference_messages = []
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "system":
                    inference_messages.append(SystemMessage(content=content))
                else:
                    inference_messages.append(UserMessage(content=content))

            response = self._client.complete(
                messages=inference_messages,
                model=model or self._model_name,
                **kwargs,
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"[AIFoundryAdapter - chat_completion] Error: {e}")
            raise
