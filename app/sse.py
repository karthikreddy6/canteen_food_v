import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional


class SSESubscription:
    def __init__(self, queue: asyncio.Queue, user_id: str, client_ip: str = ""):
        self.queue = queue
        self.user_id = user_id
        self.client_ip = client_ip
        self.subscribed_at = datetime.now(timezone.utc)
        self._subscribed_perf = time.perf_counter()

    @property
    def duration_seconds(self) -> float:
        return round(time.perf_counter() - self._subscribed_perf, 1)

    def __eq__(self, other):
        if isinstance(other, asyncio.Queue):
            return self.queue == other
        if isinstance(other, SSESubscription):
            return self.queue == other.queue
        return False


class SSEConnectionManager:
    def __init__(self):
        # Maps user_id to a list of SSESubscription instances
        self.active_connections: Dict[str, List[SSESubscription]] = {}

    async def subscribe(self, user_id: str, client_ip: str = "") -> asyncio.Queue:
        queue = asyncio.Queue()
        sub = SSESubscription(queue, user_id, client_ip)
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(sub)
        return queue

    def unsubscribe(self, user_id: str, queue: asyncio.Queue):
        if user_id in self.active_connections:
            self.active_connections[user_id] = [
                s for s in self.active_connections[user_id] if s.queue != queue
            ]
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def broadcast_to_user(self, user_id: str, event_type: str, data: dict):
        """Pushes an event payload onto all queues registered for user_id."""
        if user_id in self.active_connections:
            serialized_data = json.dumps(data)
            payload = {
                "event": event_type,
                "data": serialized_data,
            }
            for sub in list(self.active_connections[user_id]):
                await sub.queue.put(payload)

    def get_stats(self) -> dict:
        """Returns structured information about active SSE stream subscribers."""
        total_connections = 0
        users_list = []

        for uid, subs in self.active_connections.items():
            count = len(subs)
            total_connections += count
            latest_sub = subs[-1] if subs else None

            users_list.append({
                "user_id": uid,
                "connections_count": count,
                "client_ip": latest_sub.client_ip if latest_sub else "",
                "subscribed_at": latest_sub.subscribed_at.isoformat() if latest_sub else "",
                "duration_seconds": latest_sub.duration_seconds if latest_sub else 0,
            })

        return {
            "total_connections": total_connections,
            "active_users_count": len(self.active_connections),
            "users": users_list,
        }


# Global connection manager instance
sse_manager = SSEConnectionManager()
