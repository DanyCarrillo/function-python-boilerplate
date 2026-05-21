import logging

from azure.storage.blob import BlobServiceClient

from src.ports.blob_storage_port import BlobStoragePort


class BlobStorageAdapter(BlobStoragePort):
    def __init__(self, connection_string: str):
        self._client = BlobServiceClient.from_connection_string(connection_string)

    def upload(self, container: str, blob_name: str, data: bytes) -> str:
        try:
            blob_client = self._client.get_blob_client(container=container, blob=blob_name)
            blob_client.upload_blob(data, overwrite=True)
            return blob_client.url
        except Exception as e:
            logging.error(f"[BlobStorageAdapter - upload] Error: {e}")
            raise

    def download(self, container: str, blob_name: str) -> bytes:
        try:
            blob_client = self._client.get_blob_client(container=container, blob=blob_name)
            return blob_client.download_blob().readall()
        except Exception as e:
            logging.error(f"[BlobStorageAdapter - download] Error: {e}")
            raise

    def delete(self, container: str, blob_name: str) -> None:
        try:
            blob_client = self._client.get_blob_client(container=container, blob=blob_name)
            blob_client.delete_blob()
        except Exception as e:
            logging.error(f"[BlobStorageAdapter - delete] Error: {e}")
            raise

    def exists(self, container: str, blob_name: str) -> bool:
        try:
            blob_client = self._client.get_blob_client(container=container, blob=blob_name)
            return blob_client.exists()
        except Exception as e:
            logging.error(f"[BlobStorageAdapter - exists] Error: {e}")
            raise
