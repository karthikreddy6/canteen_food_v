import json
from typing import Dict, List
from fastapi import WebSocket

class WebSocketConnectionManager:
    def __init__(self):
        # Maps user_id (str) to a list of active WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, user_id: str, websocket: WebSocket):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def broadcast_to_user(self, user_id: str, data: dict):
        if user_id in self.active_connections:
            # Broadcast JSON to all active WebSockets for this user
            serialized = json.dumps(data)
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_text(serialized)
                except Exception:
                    # Clean up broken connections
                    pass

ws_manager = WebSocketConnectionManager()
