from __future__ import annotations
import uvicorn

from src.common.env import config  # Get variables from centralized environment config

# Enable hot reload only when config.debug is True
DEBUG: bool = bool(config.debug)

if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=8000,
        reload=DEBUG,
        reload_dirs=["src"] if DEBUG else None,
    )
