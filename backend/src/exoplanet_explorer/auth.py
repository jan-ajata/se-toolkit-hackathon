"""API key authentication middleware."""

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from exoplanet_explorer.settings import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str | None = Depends(api_key_header)) -> str:
    """Verify the request contains a valid API key."""
    if api_key is None or api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return api_key
