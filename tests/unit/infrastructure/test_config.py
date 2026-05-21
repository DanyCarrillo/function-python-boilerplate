import pytest
from unittest.mock import patch

from src.infrastructure.config import Config

_REQUIRED_ENV = {
    "BLOB_CONNECTION_STRING": "blob-conn",
    "COSMOS_CONNECTION_STRING": "cosmos-conn",
    "COSMOS_DATABASE": "db",
    "COSMOS_CONTAINER": "container",
    "SEARCH_ENDPOINT": "https://search",
    "SEARCH_API_KEY": "search-key",
    "SEARCH_INDEX": "index",
    "OPENAI_ENDPOINT": "https://openai",
    "OPENAI_API_KEY": "openai-key",
    "OPENAI_API_VERSION": "2024-02-01",
    "OPENAI_CHAT_MODEL": "gpt-4o",
    "OPENAI_EMBEDDING_MODEL": "text-embedding-3-large",
    "DOC_INTELLIGENCE_ENDPOINT": "https://doc-intel",
    "DOC_INTELLIGENCE_API_KEY": "doc-key",
    "AI_FOUNDRY_ENDPOINT": "https://foundry",
    "AI_FOUNDRY_API_KEY": "foundry-key",
    "AI_FOUNDRY_MODEL": "Phi-3",
    "ACS_CONNECTION_STRING": "acs-conn",
    "GRAPH_TENANT_ID": "tenant-id",
    "GRAPH_CLIENT_ID": "client-id",
    "GRAPH_CLIENT_SECRET": "client-secret",
}


class TestConfig:
    def test_from_env_reads_all_values(self):
        with patch.dict("os.environ", _REQUIRED_ENV, clear=True):
            config = Config.from_env()

        assert config.blob_connection_string == "blob-conn"
        assert config.cosmos_connection_string == "cosmos-conn"
        assert config.cosmos_database == "db"
        assert config.cosmos_container == "container"
        assert config.search_endpoint == "https://search"
        assert config.search_api_key == "search-key"
        assert config.search_index == "index"
        assert config.openai_endpoint == "https://openai"
        assert config.openai_api_key == "openai-key"
        assert config.openai_api_version == "2024-02-01"
        assert config.openai_chat_model == "gpt-4o"
        assert config.openai_embedding_model == "text-embedding-3-large"
        assert config.doc_intelligence_endpoint == "https://doc-intel"
        assert config.doc_intelligence_api_key == "doc-key"
        assert config.ai_foundry_endpoint == "https://foundry"
        assert config.ai_foundry_api_key == "foundry-key"
        assert config.ai_foundry_model == "Phi-3"
        assert config.acs_connection_string == "acs-conn"
        assert config.graph_tenant_id == "tenant-id"
        assert config.graph_client_id == "client-id"
        assert config.graph_client_secret == "client-secret"

    def test_from_env_uses_default_api_version_when_not_set(self):
        env_without_version = {k: v for k, v in _REQUIRED_ENV.items() if k != "OPENAI_API_VERSION"}
        with patch.dict("os.environ", env_without_version, clear=True):
            config = Config.from_env()

        assert config.openai_api_version == "2024-02-01"

    def test_from_env_uses_custom_api_version(self):
        env = {**_REQUIRED_ENV, "OPENAI_API_VERSION": "2025-01-01"}
        with patch.dict("os.environ", env, clear=True):
            config = Config.from_env()

        assert config.openai_api_version == "2025-01-01"

    def test_from_env_raises_on_missing_required_var(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(KeyError):
                Config.from_env()

    def test_config_is_immutable(self):
        with patch.dict("os.environ", _REQUIRED_ENV, clear=True):
            config = Config.from_env()

        with pytest.raises((AttributeError, TypeError)):
            config.blob_connection_string = "other"
