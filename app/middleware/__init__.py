"""
OnFood Server Behavior Tracking Middleware Package.

This package provides modular middleware components to monitor and log
all server behavior including latency, errors, resource usage, and metrics.
"""

import logging
import logging.handlers
import os

# ─── Re-register the onfood.exceptions logger ─────────────────────────────────
# The general exception handler in app/exceptions.py logs unhandled 500s via
# logging.getLogger("onfood.exceptions").  The file handler for this logger was
# previously wired in app/main.py; since that wiring has been removed during the
# middleware refactor, we re-register it here so errors.log continues to work.

_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
os.makedirs(_LOG_DIR, exist_ok=True)

_exc_logger = logging.getLogger("onfood.exceptions")
if not _exc_logger.handlers:
    _exc_handler = logging.handlers.RotatingFileHandler(
        os.path.join(_LOG_DIR, "errors.log"),
        maxBytes=10_000_000,   # 10 MB per file
        backupCount=5,
        encoding="utf-8",
    )
    _exc_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    _exc_logger.addHandler(_exc_handler)
    _exc_logger.setLevel(logging.ERROR)
    _exc_logger.propagate = False
