"""
Active User Activity Tracker.

Maintains in-memory state of users who have recently performed authenticated
HTTP requests (via JWT token), providing visibility into which users are actively
using the system even if they don't hold an open WebSocket or SSE connection.
"""

import threading
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional


class ActiveUserTracker:
    def __init__(self, ttl_seconds: int = 900):  # default 15 minutes
        self.ttl_seconds = ttl_seconds
        self._lock = threading.Lock()
        self._users: Dict[str, dict] = {}

    def record_activity(
        self,
        user_id: str,
        role: str = "",
        canteen_id: str = "",
        client_ip: str = "",
        user_agent: str = "",
        path: str = "",
        method: str = "",
    ):
        """Update last seen activity for a user."""
        if not user_id:
            return

        now_utc = datetime.now(timezone.utc)
        now_perf = time.perf_counter()

        with self._lock:
            self._users[user_id] = {
                "user_id": user_id,
                "role": role or "customer",
                "canteen_id": canteen_id or "",
                "client_ip": client_ip,
                "user_agent": user_agent[:120] if user_agent else "",
                "last_path": path,
                "last_method": method,
                "last_seen_at": now_utc.isoformat(),
                "_last_seen_perf": now_perf,
            }

    def get_active_users(self, window_seconds: Optional[int] = None) -> List[dict]:
        """Return list of users active within the given time window (seconds)."""
        limit = window_seconds if window_seconds is not None else self.ttl_seconds
        now_perf = time.perf_counter()

        active = []
        with self._lock:
            # Clean up old and collect active
            expired = []
            for uid, info in self._users.items():
                idle = now_perf - info["_last_seen_perf"]
                if idle <= limit:
                    data = dict(info)
                    data["idle_seconds"] = round(idle, 1)
                    del data["_last_seen_perf"]
                    active.append(data)
                elif idle > self.ttl_seconds * 2:
                    expired.append(uid)

            for uid in expired:
                del self._users[uid]

        # Sort by most recently active first
        active.sort(key=lambda x: x["idle_seconds"])
        return active


active_user_tracker = ActiveUserTracker()
