import pytest
from unittest.mock import MagicMock, patch

from src.adapters.graph_api_adapter import GraphAPIAdapter


@pytest.fixture
def adapter():
    with patch("src.adapters.graph_api_adapter.ConfidentialClientApplication") as mock_msal:
        mock_app = MagicMock()
        mock_msal.return_value = mock_app
        mock_app.acquire_token_silent.return_value = None
        mock_app.acquire_token_for_client.return_value = {"access_token": "test-token"}
        instance = GraphAPIAdapter("tenant", "client_id", "client_secret")
        instance._app = mock_app
        yield instance, mock_app


class TestGraphAPIAdapter:
    def test_get_access_token_acquires_new_when_cache_empty(self, adapter):
        instance, mock_app = adapter
        mock_app.acquire_token_silent.return_value = None
        mock_app.acquire_token_for_client.return_value = {"access_token": "new-token"}

        token = instance._get_access_token()

        assert token == "new-token"

    def test_get_access_token_uses_cached_token(self, adapter):
        instance, mock_app = adapter
        mock_app.acquire_token_silent.return_value = {"access_token": "cached-token"}

        token = instance._get_access_token()

        mock_app.acquire_token_for_client.assert_not_called()
        assert token == "cached-token"

    def test_get_access_token_raises_when_no_token(self, adapter):
        instance, mock_app = adapter
        mock_app.acquire_token_silent.return_value = None
        mock_app.acquire_token_for_client.return_value = {
            "error": "invalid_client",
            "error_description": "bad credentials",
        }

        with pytest.raises(RuntimeError, match="Failed to acquire token"):
            instance._get_access_token()

    def test_get_user_returns_dict(self, adapter):
        instance, _ = adapter
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "user-1", "displayName": "Test User"}
        mock_response.raise_for_status = MagicMock()

        with patch("src.adapters.graph_api_adapter.requests.get", return_value=mock_response):
            result = instance.get_user("user-1")

        assert result == {"id": "user-1", "displayName": "Test User"}

    def test_get_user_raises_on_error(self, adapter):
        instance, _ = adapter

        with patch("src.adapters.graph_api_adapter.requests.get", side_effect=Exception("http error")):
            with pytest.raises(Exception, match="http error"):
                instance.get_user("user-1")

    def test_send_email_calls_post(self, adapter):
        instance, _ = adapter
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()

        with patch("src.adapters.graph_api_adapter.requests.post", return_value=mock_response) as mock_post:
            instance.send_email("user-1", ["to@example.com"], "Subject", "Body")

        mock_post.assert_called_once()

    def test_send_email_raises_on_error(self, adapter):
        instance, _ = adapter

        with patch("src.adapters.graph_api_adapter.requests.post", side_effect=Exception("post error")):
            with pytest.raises(Exception, match="post error"):
                instance.send_email("user-1", ["to@e.com"], "Subj", "Body")

    def test_list_users_returns_list(self, adapter):
        instance, _ = adapter
        mock_response = MagicMock()
        mock_response.json.return_value = {"value": [{"id": "1"}, {"id": "2"}]}
        mock_response.raise_for_status = MagicMock()

        with patch("src.adapters.graph_api_adapter.requests.get", return_value=mock_response):
            result = instance.list_users()

        assert result == [{"id": "1"}, {"id": "2"}]

    def test_list_users_with_filter_sets_param(self, adapter):
        instance, _ = adapter
        mock_response = MagicMock()
        mock_response.json.return_value = {"value": []}
        mock_response.raise_for_status = MagicMock()

        with patch("src.adapters.graph_api_adapter.requests.get", return_value=mock_response) as mock_get:
            instance.list_users(filter_query="department eq 'IT'")

        call_kwargs = mock_get.call_args.kwargs
        assert call_kwargs["params"]["$filter"] == "department eq 'IT'"

    def test_list_users_raises_on_error(self, adapter):
        instance, _ = adapter

        with patch("src.adapters.graph_api_adapter.requests.get", side_effect=Exception("list error")):
            with pytest.raises(Exception, match="list error"):
                instance.list_users()
