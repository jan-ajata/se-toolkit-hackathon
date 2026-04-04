"""Entry point for running the FastAPI server with uvicorn."""

import uvicorn

from exoplanet_explorer.settings import settings

if __name__ == "__main__":
    uvicorn.run(
        "exoplanet_explorer.main:app",
        host=settings.address,
        port=settings.port,
        reload=settings.reload,
    )
