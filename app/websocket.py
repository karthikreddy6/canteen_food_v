import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional
from fastapi import WebSocket


class WebSocketSession:
    """Represents a single connected client session."""
    def __init__(self, websocket: WebSocket, user_id: str, client_ip: str = "", user_agent: str = ""):
        self.websocket = websocket
        self.user_id = user_id
        self.client_ip = client_ip
        self.user_agent = user_agent
        self.connected_at = datetime.now(timezone.utc)
        self._connected_perf = time.perf_counter()

    @property
    def duration_seconds(self) -> float:
        return round(time.perf_counter() - self._connected_perf, 1)

    def __eq__(self, other):
        if isinstance(other, WebSocket):
            return self.websocket == other
        if isinstance(other, WebSocketSession):
            return self.websocket == other.websocket
        return False


class WebSocketConnectionManager:
    def __init__(self):
        # Maps user_id (str) to a list of active WebSocketSession instances
        self.active_connections: Dict[str, List[WebSocketSession]] = {}

    async def connect(self, user_id: str, websocket: WebSocket, client_ip: str = "", user_agent: str = ""):
        await websocket.accept()
        session = WebSocketSession(websocket, user_id, client_ip, user_agent)
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(session)

    def disconnect(self, user_id: str, websocket: WebSocket):
        if user_id in self.active_connections:
            self.active_connections[user_id] = [
                s for s in self.active_connections[user_id] if s.websocket != websocket
            ]
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def broadcast_to_user(self, user_id: str, data: dict):
        if user_id in self.active_connections:
            # Broadcast JSON to all active WebSockets for this user
            serialized = json.dumps(data)
            for session in list(self.active_connections[user_id]):
                try:
                    await session.websocket.send_text(serialized)
                except Exception:
                    # Clean up broken connections
                    pass

    def get_stats(self) -> dict:
        """Returns structured information about active WebSocket connections."""
        total_connections = 0
        users_list = []
        now = datetime.now(timezone.utc)

        for uid, sessions in self.active_connections.items():
            count = len(sessions)
            total_connections += count
            latest_session = sessions[-1] if sessions else None

            users_list.append({
                "user_id": uid,
                "connections_count": count,
                "client_ip": latest_session.client_ip if latest_session else "",
                "user_agent": latest_session.user_agent if latest_session else "",
                "connected_at": latest_session.connected_at.isoformat() if latest_session else "",
                "duration_seconds": latest_session.duration_seconds if latest_session else 0,
            })

        return {
            "total_connections": total_connections,
            "active_users_count": len(self.active_connections),
            "users": users_list,
        }


ws_manager = WebSocketConnectionManager()
support_ws_manager = WebSocketConnectionManager()
