import pytest
from unittest.mock import MagicMock, patch

from azure.cosmos import exceptions

from src.adapters.cosmosdb_adapter import CosmosdbAdapter


@pytest.fixture
def adapter():
    with patch("src.adapters.cosmosdb_adapter.CosmosClient") as mock_cls:
        mock_container = MagicMock()
        mock_cls.from_connection_string.return_value \
            .get_database_client.return_value \
            .get_container_client.return_value = mock_container
        instance = CosmosdbAdapter("conn", "db", "container")
        instance._container = mock_container
        yield instance, mock_container


class TestCosmosdbAdapter:
    def test_save_returns_upserted_item(self, adapter):
        instance, mock_container = adapter
        mock_container.upsert_item.return_value = {"id": "1"}

        result = instance.save({"id": "1"})

        assert result == {"id": "1"}

    def test_save_raises_on_error(self, adapter):
        instance, mock_container = adapter
        mock_container.upsert_item.side_effect = Exception("upsert error")

        with pytest.raises(Exception, match="upsert error"):
            instance.save({"id": "1"})

    def test_get_by_id_returns_item(self, adapter):
        instance, mock_container = adapter
        mock_container.read_item.return_value = {"id": "1", "data": "value"}

        result = instance.get_by_id("1", "partition")

        assert result == {"id": "1", "data": "value"}

    def test_get_by_id_returns_none_when_not_found(self, adapter):
        instance, mock_container = adapter
        error_response = MagicMock()
        error_response.status_code = 404
        mock_container.read_item.side_effect = exceptions.CosmosResourceNotFoundError(
            message="Not found", response=error_response
        )

        result = instance.get_by_id("not_exists", "partition")

        assert result is None

    def test_get_by_id_raises_on_other_error(self, adapter):
        instance, mock_container = adapter
        mock_container.read_item.side_effect = Exception("read error")

        with pytest.raises(Exception, match="read error"):
            instance.get_by_id("1", "partition")

    def test_query_returns_list(self, adapter):
        instance, mock_container = adapter
        mock_container.query_items.return_value = [{"id": "1"}, {"id": "2"}]

        result = instance.query("SELECT * FROM c")

        assert result == [{"id": "1"}, {"id": "2"}]

    def test_query_raises_on_error(self, adapter):
        instance, mock_container = adapter
        mock_container.query_items.side_effect = Exception("query error")

        with pytest.raises(Exception, match="query error"):
            instance.query("SELECT * FROM c")

    def test_delete_calls_delete_item(self, adapter):
        instance, mock_container = adapter

        instance.delete("1", "partition")

        mock_container.delete_item.assert_called_once_with(item="1", partition_key="partition")

    def test_delete_raises_on_error(self, adapter):
        instance, mock_container = adapter
        mock_container.delete_item.side_effect = Exception("delete error")

        with pytest.raises(Exception, match="delete error"):
            instance.delete("1", "partition")
