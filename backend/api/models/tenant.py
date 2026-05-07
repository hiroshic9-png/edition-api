"""Tenant model — API consumers."""
import uuid
import secrets
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from backend.api.db.database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    api_key = Column(String, unique=True, nullable=False,
                     default=lambda: f"edition_{secrets.token_urlsafe(32)}")
    plan = Column(String, default="hobby")  # hobby / pro / enterprise
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
