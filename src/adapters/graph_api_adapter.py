import logging
from typing import List, Optional

import requests
from msal import ConfidentialClientApplication

from src.ports.graph_api_port import GraphAPIPort

_GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"
_SCOPES = ["https://graph.microsoft.com/.default"]


class GraphAPIAdapter(GraphAPIPort):
    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        self._app = ConfidentialClientApplication(
            client_id=client_id,
            client_credential=client_secret,
            authority=f"https://login.microsoftonline.com/{tenant_id}",
        )

    def _get_access_token(self) -> str:
        result = self._app.acquire_token_silent(_SCOPES, account=None)
        if not result:
            result = self._app.acquire_token_for_client(scopes=_SCOPES)
        if "access_token" not in result:
            raise RuntimeError(f"Failed to acquire token: {result.get('error_description')}")
        return result["access_token"]

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self._get_access_token()}"}

    def get_user(self, user_id: str) -> dict:
        try:
            response = requests.get(
                f"{_GRAPH_BASE_URL}/users/{user_id}",
                headers=self._headers(),
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"[GraphAPIAdapter - get_user] Error: {e}")
            raise

    def send_email(self, user_id: str, recipients: List[str], subject: str, body: str) -> None:
        try:
            payload = {
                "message": {
                    "subject": subject,
                    "body": {"contentType": "Text", "content": body},
                    "toRecipients": [{"emailAddress": {"address": r}} for r in recipients],
                }
            }
            response = requests.post(
                f"{_GRAPH_BASE_URL}/users/{user_id}/sendMail",
                headers={**self._headers(), "Content-Type": "application/json"},
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
        except Exception as e:
            logging.error(f"[GraphAPIAdapter - send_email] Error: {e}")
            raise

    def list_users(self, filter_query: Optional[str] = None) -> List[dict]:
        try:
            params = {}
            if filter_query:
                params["$filter"] = filter_query
            response = requests.get(
                f"{_GRAPH_BASE_URL}/users",
                headers=self._headers(),
                params=params,
                timeout=30,
            )
            response.raise_for_status()
            return response.json().get("value", [])
        except Exception as e:
            logging.error(f"[GraphAPIAdapter - list_users] Error: {e}")
            raise
