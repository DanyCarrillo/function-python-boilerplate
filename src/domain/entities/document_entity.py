from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class DocumentEntity:
    id: str
    content: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Optional[dict] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }
