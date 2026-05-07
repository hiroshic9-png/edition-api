"""Fact model — structured knowledge extracted from episodes."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Float, DateTime, JSON
from backend.api.db.database import Base


class Fact(Base):
    __tablename__ = "facts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=False, index=True)
    subject = Column(Text, nullable=False)       # e.g. "佐藤部長"
    predicate = Column(Text, nullable=False)     # e.g. "好む"
    object_ = Column("object", Text, nullable=False)  # e.g. "ワイン"
    confidence = Column(Float, default=1.0)
    source_episode_id = Column(String, nullable=True)
    valid_from = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    valid_until = Column(DateTime, nullable=True)  # NULL = currently valid
    metadata_ = Column("metadata", JSON, default=dict)  # social_hierarchy, formality, etc.
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def is_valid(self) -> bool:
        if self.valid_until is None:
            return True
        return datetime.now(timezone.utc) < self.valid_until
