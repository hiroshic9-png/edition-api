"""API key authentication."""
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.api.db.database import get_db
from backend.api.models.tenant import Tenant


async def verify_api_key(
    authorization: str = Header(..., description="Bearer <api_key>"),
    db: Session = Depends(get_db),
) -> Tenant:
    """Extract and verify API key from Authorization header."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format. Use: Bearer <api_key>")

    api_key = authorization[7:]
    tenant = db.query(Tenant).filter(Tenant.api_key == api_key).first()
    if not tenant:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return tenant
