import asyncio
import json
from typing import Dict, List

class SSEConnectionManager:
    def __init__(self):
        # Maps user_id to a list of asyncio.Queues (one queue per active client tab/device)
        self.active_connections: Dict[str, List[asyncio.Queue]] = {}

    async def subscribe(self, user_id: str) -> asyncio.Queue:
        queue = asyncio.Queue()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(queue)
        return queue

    def unsubscribe(self, user_id: str, queue: asyncio.Queue):
        if user_id in self.active_connections:
            if queue in self.active_connections[user_id]:
                self.active_connections[user_id].remove(queue)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def broadcast_to_user(self, user_id: str, event_type: str, data: dict):
        """Pushes an event payload onto all queues registered for user_id."""
        if user_id in self.active_connections:
            # We serialize data using json.dumps to match the Spring Boot JSON format
            # Converting datetime fields to string format if present
            serialized_data = json.dumps(data)
            payload = {
                "event": event_type,
                "data": serialized_data
            }
            # Add to queues asynchronously
            for queue in self.active_connections[user_id]:
                await queue.put(payload)

# Global connection manager instance
sse_manager = SSEConnectionManager()
