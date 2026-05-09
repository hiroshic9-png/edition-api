"""API Request Log model — telemetry for all incoming requests."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Float, Integer
from backend.api.db.database import Base


class ApiRequestLog(Base):
    __tablename__ = "api_request_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    method = Column(String, nullable=False)
    path = Column(String, nullable=False, index=True)
    query_text = Column(String, nullable=True)
    status_code = Column(Integer, nullable=False)
    latency_ms = Column(Float, nullable=False)
    user_agent = Column(String, nullable=True)
    agent_name = Column(String, nullable=True, index=True)
    ip_address = Column(String, nullable=True)
    api_key_prefix = Column(String(8), nullable=True)
    domain = Column(String, nullable=True, index=True)
