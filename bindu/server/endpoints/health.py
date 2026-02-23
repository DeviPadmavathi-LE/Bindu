"""Health check endpoint for service monitoring."""

from __future__ import annotations
from datetime import datetime, timezone
from time import time

from starlette.requests import Request
from starlette.responses import JSONResponse

from bindu import __version__
from bindu.server.applications import BinduApplication
from bindu.utils.request_utils import handle_endpoint_errors, get_client_ip
from bindu.utils.logging import get_logger

logger = get_logger("bindu.server.endpoints.health")

_start_time = time()


@handle_endpoint_errors("health check")
async def health_endpoint(app: BinduApplication, request: Request) -> JSONResponse:
    """Health check endpoint for service monitoring.

    Returns service status, uptime, and version information.
    """
    client_ip = get_client_ip(request)
    logger.debug(f"Health check from {client_ip}")

    uptime = round(time() - _start_time, 2)

    # dynamic status (safe improvement)
    status = "ok" if app else "error"

    payload = {
        "status": status,
        "uptime_seconds": uptime,
        "version": __version__,
        "ready": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": app.settings.project.name,  # dynamic instead of hardcoded
        "client_ip": client_ip,  # useful for monitoring/debugging
    }

    return JSONResponse(payload)