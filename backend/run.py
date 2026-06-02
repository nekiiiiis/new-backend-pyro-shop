"""Punto de entrada de desarrollo: `python run.py`.

Para producción se recomienda lanzar uvicorn directamente, por ejemplo:

    uvicorn app.main:app --host 0.0.0.0 --port 3000
"""
from __future__ import annotations

import uvicorn

from app.core.config import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
        log_level=settings.log_level,
    )


if __name__ == "__main__":
    main()
