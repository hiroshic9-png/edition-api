"""Episode model — raw conversational data (chronicle.md equivalent)."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, JSON
from backend.api.db.database import Base


class Episode(Base):
    __tablename__ = "episodes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=False, index=True)
    session_id = Column(String, nullable=True, index=True)
    content = Column(Text, nullable=False)
    role = Column(String, default="user")  # user / assistant / system
    metadata_ = Column("metadata", JSON, default=dict)
    event_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
