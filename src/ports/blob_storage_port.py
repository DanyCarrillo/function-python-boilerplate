from abc import ABC, abstractmethod


class BlobStoragePort(ABC):
    @abstractmethod
    def upload(self, container: str, blob_name: str, data: bytes) -> str:
        pass

    @abstractmethod
    def download(self, container: str, blob_name: str) -> bytes:
        pass

    @abstractmethod
    def delete(self, container: str, blob_name: str) -> None:
        pass

    @abstractmethod
    def exists(self, container: str, blob_name: str) -> bool:
        pass
