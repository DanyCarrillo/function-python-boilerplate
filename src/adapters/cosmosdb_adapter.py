import logging
from typing import List, Optional

from azure.cosmos import CosmosClient, exceptions

from src.ports.cosmosdb_port import CosmosdbPort


class CosmosdbAdapter(CosmosdbPort):
    def __init__(self, connection_string: str, database_name: str, container_name: str):
        client = CosmosClient.from_connection_string(connection_string)
        self._container = (
            client
            .get_database_client(database_name)
            .get_container_client(container_name)
        )

    def save(self, data: dict) -> dict:
        try:
            return self._container.upsert_item(data)
        except Exception as e:
            logging.error(f"[CosmosdbAdapter - save] Error: {e}")
            raise

    def get_by_id(self, item_id: str, partition_key: str) -> Optional[dict]:
        try:
            return self._container.read_item(item=item_id, partition_key=partition_key)
        except exceptions.CosmosResourceNotFoundError:
            return None
        except Exception as e:
            logging.error(f"[CosmosdbAdapter - get_by_id] Error: {e}")
            raise

    def query(self, query: str, parameters: Optional[list] = None) -> List[dict]:
        try:
            items = self._container.query_items(
                query=query,
                parameters=parameters or [],
                enable_cross_partition_query=True,
            )
            return list(items)
        except Exception as e:
            logging.error(f"[CosmosdbAdapter - query] Error: {e}")
            raise

    def delete(self, item_id: str, partition_key: str) -> None:
        try:
            self._container.delete_item(item=item_id, partition_key=partition_key)
        except Exception as e:
            logging.error(f"[CosmosdbAdapter - delete] Error: {e}")
            raise
