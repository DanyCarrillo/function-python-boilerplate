import pytest
from unittest.mock import MagicMock, patch

from src.adapters.blob_storage_adapter import BlobStorageAdapter


@pytest.fixture
def adapter():
    with patch("src.adapters.blob_storage_adapter.BlobServiceClient") as mock_cls:
        mock_service = MagicMock()
        mock_cls.from_connection_string.return_value = mock_service
        instance = BlobStorageAdapter(connection_string="DefaultEndpointsProtocol=https;...")
        instance._client = mock_service
        yield instance, mock_service


class TestBlobStorageAdapter:
    def test_upload_returns_url(self, adapter):
        instance, mock_service = adapter
        mock_blob = MagicMock()
        mock_blob.url = "https://example.blob.core.windows.net/container/blob"
        mock_service.get_blob_client.return_value = mock_blob

        result = instance.upload("container", "blob.txt", b"data")

        mock_blob.upload_blob.assert_called_once_with(b"data", overwrite=True)
        assert result == "https://example.blob.core.windows.net/container/blob"

    def test_upload_raises_on_error(self, adapter):
        instance, mock_service = adapter
        mock_blob = MagicMock()
        mock_blob.upload_blob.side_effect = Exception("upload error")
        mock_service.get_blob_client.return_value = mock_blob

        with pytest.raises(Exception, match="upload error"):
            instance.upload("container", "blob.txt", b"data")

    def test_download_returns_bytes(self, adapter):
        instance, mock_service = adapter
        mock_blob = MagicMock()
        mock_blob.download_blob.return_value.readall.return_value = b"file content"
        mock_service.get_blob_client.return_value = mock_blob

        result = instance.download("container", "blob.txt")

        assert result == b"file content"

    def test_download_raises_on_error(self, adapter):
        instance, mock_service = adapter
        mock_blob = MagicMock()
        mock_blob.download_blob.side_effect = Exception("download error")
        mock_service.get_blob_client.return_value = mock_blob

        with pytest.raises(Exception, match="download error"):
            instance.download("container", "blob.txt")

    def test_delete_calls_delete_blob(self, adapter):
        instance, mock_service = adapter
        mock_blob = MagicMock()
        mock_service.get_blob_client.return_value = mock_blob

        instance.delete("container", "blob.txt")

        mock_blob.delete_blob.assert_called_once()

    def test_delete_raises_on_error(self, adapter):
        instance, mock_service = adapter
        mock_blob = MagicMock()
        mock_blob.delete_blob.side_effect = Exception("delete error")
        mock_service.get_blob_client.return_value = mock_blob

        with pytest.raises(Exception, match="delete error"):
            instance.delete("container", "blob.txt")

    def test_exists_returns_true(self, adapter):
        instance, mock_service = adapter
        mock_blob = MagicMock()
        mock_blob.exists.return_value = True
        mock_service.get_blob_client.return_value = mock_blob

        assert instance.exists("container", "blob.txt") is True

    def test_exists_returns_false(self, adapter):
        instance, mock_service = adapter
        mock_blob = MagicMock()
        mock_blob.exists.return_value = False
        mock_service.get_blob_client.return_value = mock_blob

        assert instance.exists("container", "blob.txt") is False

    def test_exists_raises_on_error(self, adapter):
        instance, mock_service = adapter
        mock_blob = MagicMock()
        mock_blob.exists.side_effect = Exception("exists error")
        mock_service.get_blob_client.return_value = mock_blob

        with pytest.raises(Exception, match="exists error"):
            instance.exists("container", "blob.txt")
