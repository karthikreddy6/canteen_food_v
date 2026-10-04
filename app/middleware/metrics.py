"""
Prometheus metrics collector and /metrics endpoint.

Exposes standard HTTP server metrics in Prometheus text format:
  - http_requests_total          (Counter)    — total requests by method, path, status
  - http_request_duration_seconds (Histogram) — latency distribution
  - http_requests_in_progress    (Gauge)      — currently active requests
  - process_memory_rss_bytes     (Gauge)      — server process memory
  - process_cpu_percent          (Gauge)      — server process CPU usage

Controlled by ENABLE_METRICS config flag — entire module is a no-op when
disabled, and mount_metrics_endpoint() does nothing.

Usage:
    from app.middleware.metrics import metrics, mount_metrics_endpoint
    metrics.record_request("GET", "/api/menu", 200, 0.045)
    # Mount metrics_endpoint on your FastAPI app
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import FastAPI


class PrometheusMetrics:
    """
    Lightweight Prometheus metrics collector.

    Uses prometheus_client if available. Falls back to a no-op implementation
    if the package is not installed or metrics are disabled, so the server
    never crashes due to missing optional monitoring dependencies.
    """

    def __init__(self):
        self._enabled = False
        self._metrics_enabled_config = True
        self._request_counter = None
        self._request_duration = None
        self._in_progress = None
        self._memory_gauge = None
        self._cpu_gauge = None

    def configure(self, enable_metrics: bool = True):
        """Configure whether metrics collection is enabled."""
        self._metrics_enabled_config = enable_metrics
        if enable_metrics and not self._enabled:
            self._initialize()

    def _initialize(self):
        """Try to import prometheus_client and create metric objects."""
        if not self._metrics_enabled_config:
            return
        try:
            from prometheus_client import Counter, Histogram, Gauge

            self._request_counter = Counter(
                "http_requests_total",
                "Total HTTP requests",
                ["method", "path", "status_code"],
            )
            self._request_duration = Histogram(
                "http_request_duration_seconds",
                "HTTP request duration in seconds",
                ["method", "path"],
                buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
            )
            self._in_progress = Gauge(
                "http_requests_in_progress",
                "Number of HTTP requests currently being processed",
            )
            self._memory_gauge = Gauge(
                "process_memory_rss_bytes",
                "Resident Set Size of the server process in bytes",
            )
            self._cpu_gauge = Gauge(
                "process_cpu_percent",
                "CPU usage percentage of the server process",
            )
            self._enabled = True
        except ImportError:
            # prometheus_client not installed — metrics will be no-ops
            pass

    def record_request(
        self,
        method: str,
        path_template: str,
        status_code: int,
        duration_seconds: float,
    ):
        """Record a completed HTTP request in all relevant metrics."""
        if not self._enabled:
            return
        self._request_counter.labels(
            method=method,
            path=path_template,
            status_code=str(status_code),
        ).inc()
        self._request_duration.labels(
            method=method,
            path=path_template,
        ).observe(duration_seconds)

    def set_in_progress(self, count: int):
        """Update the in-progress gauge."""
        if not self._enabled:
            return
        self._in_progress.set(count)

    def set_resources(self, memory_bytes: float, cpu_percent: float):
        """Update process resource gauges."""
        if not self._enabled:
            return
        self._memory_gauge.set(memory_bytes)
        self._cpu_gauge.set(cpu_percent)


# ─── Singleton ────────────────────────────────────────────────────────────────
metrics = PrometheusMetrics()


def mount_metrics_endpoint(app: "FastAPI", enable_metrics: bool = True):
    """
    Add a GET /metrics endpoint to the FastAPI app that serves Prometheus
    text format metrics.

    This endpoint is excluded from authentication via the require_app_client
    bypass list in security.py so that Prometheus can scrape it without
    X-App-Key credentials.

    When enable_metrics is False, this function is a no-op.
    """
    if not enable_metrics:
        return

    # Configure the metrics singleton
    metrics.configure(enable_metrics=enable_metrics)

    try:
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
        from fastapi import APIRouter, Response

        metrics_router = APIRouter(tags=["Monitoring"])

        @metrics_router.get(
            "/metrics",
            summary="Prometheus Metrics",
            description="Returns all server metrics in Prometheus text exposition format.",
            include_in_schema=False,  # Hide from public API docs
        )
        async def prometheus_metrics():
            return Response(
                content=generate_latest(),
                media_type=CONTENT_TYPE_LATEST,
            )

        app.include_router(metrics_router)
    except ImportError:
        # prometheus_client not installed — skip endpoint
        pass
