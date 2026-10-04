"""
System resource monitor.

Tracks process-level CPU usage, memory (RSS), and concurrent in-flight
request count. Used by the tracker middleware to annotate each request
with resource utilization data.

Controlled by ENABLE_RESOURCE_TRACKING config flag — returns zeroes when
disabled, avoiding the psutil import entirely.
"""

import os
import threading
from dataclasses import dataclass


@dataclass
class ResourceSnapshot:
    """A point-in-time snapshot of process resources."""
    memory_rss_mb: float = 0.0        # Resident Set Size in megabytes
    cpu_percent: float = 0.0          # CPU usage % since last call
    in_flight_requests: int = 0       # Currently active concurrent requests


class ResourceMonitor:
    """
    Thread-safe monitor for server resource utilization.

    Usage:
        monitor = ResourceMonitor()

        # At request start:
        monitor.request_started()
        snapshot = monitor.snapshot()

        # At request end:
        monitor.request_finished()
    """

    def __init__(self):
        self._in_flight = 0
        self._lock = threading.Lock()
        self._process = None  # lazily initialized psutil.Process
        self._resource_tracking_enabled = True

    def configure(self, enable_resource_tracking: bool = True):
        """Configure whether psutil resource tracking is enabled."""
        self._resource_tracking_enabled = enable_resource_tracking

    def _get_process(self):
        """Lazily initialize psutil.Process (avoids import error if psutil missing)."""
        if not self._resource_tracking_enabled:
            return False  # sentinel: disabled
        if self._process is None:
            try:
                import psutil
                self._process = psutil.Process(os.getpid())
                # First call to cpu_percent() returns 0.0 — this primes it
                self._process.cpu_percent()
            except ImportError:
                # psutil not installed — resource tracking will return zeros
                self._process = False  # sentinel: don't retry
        return self._process

    def request_started(self) -> int:
        """Increment in-flight counter. Returns new count."""
        with self._lock:
            self._in_flight += 1
            return self._in_flight

    def request_finished(self) -> int:
        """Decrement in-flight counter. Returns new count."""
        with self._lock:
            self._in_flight = max(0, self._in_flight - 1)
            return self._in_flight

    @property
    def in_flight(self) -> int:
        """Current number of in-flight requests."""
        with self._lock:
            return self._in_flight

    def snapshot(self) -> ResourceSnapshot:
        """
        Take a snapshot of current resource utilization.

        Returns a ResourceSnapshot with memory, CPU, and in-flight count.
        If psutil is not installed or tracking is disabled, memory and CPU
        will be 0.0.
        """
        process = self._get_process()

        memory_mb = 0.0
        cpu_pct = 0.0

        if process and process is not False:
            try:
                mem_info = process.memory_info()
                memory_mb = round(mem_info.rss / (1024 * 1024), 2)
                cpu_pct = round(process.cpu_percent(), 2)
            except Exception:
                pass  # process may have been killed, etc.

        return ResourceSnapshot(
            memory_rss_mb=memory_mb,
            cpu_percent=cpu_pct,
            in_flight_requests=self.in_flight,
        )


# ─── Singleton Instance ──────────────────────────────────────────────────────
# Import and use this single instance across the application.
resource_monitor = ResourceMonitor()
