# Buvva (OnFood) — Backend Server Specification & Integration Guide

This guide details all necessary **FastAPI (Python + SQLAlchemy Async + PostgreSQL)** server endpoints, database migrations, and WebSocket routers required to support the new dynamic features in the Buvva Android app.

---

## Table of Contents
1. [Database Schema Migrations](#1-database-schema-migrations)
2. [Dynamic Checkout Billing & Tax Breakdown API](#2-dynamic-checkout-billing--tax-breakdown-api)
3. [User Profile: Avatar & Gender Persistence](#3-user-profile-avatar--gender-persistence)
4. [Live Order Details: College & Canteen Sections with Photo & Maps](#4-live-order-details-college--canteen-sections-with-photo--maps)
5. [Real-Time Customer Support WebSocket](#5-real-time-customer-support-websocket)
6. [Loyalty Points & Coupon Redemption APIs](#6-loyalty-points--coupon-redemption-apis)

---

## 1. Database Schema Migrations

Run these SQL migrations on your PostgreSQL database to support avatars, canteen/college geolocation, and support tickets:

```sql
-- 1. Add avatar & gender columns to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS avatar VARCHAR(50) DEFAULT 'default',
ADD COLUMN IF NOT EXISTS gender VARCHAR(20) DEFAULT NULL;

-- 2. Add photo and location fields to colleges and canteens
ALTER TABLE colleges
ADD COLUMN IF NOT EXISTS photo_url TEXT DEFAULT NULL,
ADD COLUMN IF NOT EXISTS map_url TEXT DEFAULT NULL,
ADD COLUMN IF NOT EXISTS latitude DOUBLE PRECISION DEFAULT NULL,
ADD COLUMN IF NOT EXISTS longitude DOUBLE PRECISION DEFAULT NULL;

ALTER TABLE canteens
ADD COLUMN IF NOT EXISTS photo_url TEXT DEFAULT NULL,
ADD COLUMN IF NOT EXISTS map_url TEXT DEFAULT NULL,
ADD COLUMN IF NOT EXISTS location_description TEXT DEFAULT NULL,
ADD COLUMN IF NOT EXISTS latitude DOUBLE PRECISION DEFAULT NULL,
ADD COLUMN IF NOT EXISTS longitude DOUBLE PRECISION DEFAULT NULL;

-- 3. Support Tickets & Messages table for Real-Time WebSocket Support
CREATE TABLE IF NOT EXISTS support_tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject VARCHAR(255) NOT NULL DEFAULT 'Customer Support Inquiry',
    status VARCHAR(50) NOT NULL DEFAULT 'OPEN', -- OPEN, IN_PROGRESS, RESOLVED, CLOSED
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS support_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_id UUID NOT NULL REFERENCES support_tickets(id) ON DELETE CASCADE,
    sender_type VARCHAR(20) NOT NULL, -- 'USER', 'AGENT', 'BOT'
    sender_id VARCHAR NOT NULL,
    sender_name VARCHAR(100) DEFAULT 'Support',
    message TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_support_messages_ticket ON support_messages(ticket_id);
```

---

## 2. Dynamic Checkout Billing & Tax Breakdown API

### Goal
Replace hardcoded calculations in the Android app with a dynamic server-driven bill breakdown. Whenever the server adds new taxes (e.g., GST), packaging charges, platform fees, or discounts, the app displays them dynamically without needing a code update.

### Endpoint: `POST /api/cart/calculate-bill`
**Headers**:
- `Authorization: Bearer <access_token>`
- `X-App-Key: ONFOOD_SECURE_CLIENT_APP_KEY_2026`

**Request Body**:
```json
{
  "canteen_id": "canteen-123",
  "items": [
    {
      "menu_item_id": "item-001",
      "quantity": 2
    },
    {
      "menu_item_id": "item-002",
      "quantity": 1
    }
  ],
  "coupon_code": "WELCOME10" // Optional
}
```

**Response Body (200 OK)**:
```json
{
  "subtotal": 100.0,
  "grand_total": 92.50,
  "total_discount": 10.0,
  "items": [
    {
      "menu_item_id": "item-001",
      "item_name": "Veg Burger",
      "quantity": 2,
      "original_price": 50.0,
      "discount_amount": 5.0,
      "final_price": 45.0,
      "line_total": 90.0,
      "prep_time_minutes": 10
    },
    {
      "menu_item_id": "item-002",
      "item_name": "Cold Coffee",
      "quantity": 1,
      "original_price": 20.0,
      "discount_amount": 0.0,
      "final_price": 20.0,
      "line_total": 20.0,
      "prep_time_minutes": 5
    }
  ],
  "breakdown": [
    {
      "title": "Subtotal",
      "amount": 100.0,
      "is_discount": false,
      "is_highlighted": false
    },
    {
      "title": "Item Discount",
      "amount": 10.0,
      "is_discount": true,
      "is_highlighted": true
    },
    {
      "title": "Coupon (WELCOME10)",
      "amount": 2.50,
      "is_discount": true,
      "is_highlighted": true
    },
    {
      "title": "Packaging Fee",
      "amount": 3.00,
      "is_discount": false,
      "is_highlighted": false
    },
    {
      "title": "GST (5%)",
      "amount": 2.00,
      "is_discount": false,
      "is_highlighted": false
    },
    {
      "title": "Platform Fee",
      "amount": 0.0,
      "is_discount": false,
      "is_highlighted": false
    }
  ]
}
```

### FastAPI Implementation Snippet
```python
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/cart", tags=["Cart & Billing"])

class CartItemInput(BaseModel):
    menu_item_id: str
    quantity: int

class CalculateBillRequest(BaseModel):
    canteen_id: Optional[str] = None
    items: List[CartItemInput]
    coupon_code: Optional[str] = None

class BreakdownItem(BaseModel):
    title: str
    amount: float
    is_discount: bool = False
    is_highlighted: bool = False

class BillResponse(BaseModel):
    subtotal: float
    grand_total: float
    total_discount: float
    breakdown: List[BreakdownItem]

@router.post("/calculate-bill", response_model=BillResponse)
async def calculate_bill(
    payload: CalculateBillRequest,
    current_user = Depends(get_current_user)
):
    # 1. Fetch item prices from DB
    # 2. Calculate subtotal and discounts
    # 3. Apply taxes and fees dynamically
    # 4. Return structured breakdown list
    ...
```

---

## 3. User Profile: Avatar & Gender Persistence

### Goal
When a user selects "Male", "Female", or "Default" in the avatar dialog, persist this selection in the PostgreSQL database and return it on login and profile fetches.

### Updated Endpoint: `PATCH /api/auth/profile`
**Request Body**:
```json
{
  "name": "Karthik Reddy",
  "phone": "9876543210",
  "avatar": "male", // "male", "female", or "default"
  "gender": "MALE", // Optional: "MALE", "FEMALE", "OTHER"
  "college": "Engineering College",
  "college_id": "college-001",
  "preferred_canteen_id": "canteen-001"
}
```

**Response Body**:
```json
{
  "id": "user-uuid-123",
  "name": "Karthik Reddy",
  "phone": "9876543210",
  "avatar": "male",
  "gender": "MALE",
  "college": "Engineering College",
  "college_id": "college-001",
  "preferred_canteen_id": "canteen-001"
}
```

### SQLAlchemy Model Update (`app/models.py`)
```python
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    avatar = Column(String(50), default="default")  # "male", "female", "default"
    gender = Column(String(20), nullable=True)
    ...
```

---

## 4. Live Order Details: College & Canteen Sections with Photo & Maps

### Goal
In `GET /api/orders/{order_id}` and the WebSocket status update stream (`ws/orders/{user_id}`), include full details for both **College** and **Canteen** so the app can display them in separate cards with clickable photo dialogs and Google Maps links.

### Updated `OrderResponse` Schema
```json
{
  "id": "ord-98214",
  "user_id": "usr-101",
  "status": "PREPARING",
  "pickup_number": 42,
  "order_token": "T-42",
  "total_amount": 92.50,
  "estimated_ready_at": "2026-10-03T12:45:00Z",
  "college": {
    "id": "clg-1",
    "name": "JNTUH College of Engineering",
    "photo_url": "https://api1.krtech.online/uploads/colleges/jntuh.jpg",
    "map_url": "https://maps.google.com/?q=17.4933,78.3914",
    "latitude": 17.4933,
    "longitude": 78.3914
  },
  "canteen": {
    "id": "cnt-1",
    "name": "Main Campus Cafeteria",
    "photo_url": "https://api1.krtech.online/uploads/canteens/main_cafe.jpg",
    "location_description": "Ground Floor, Behind Academic Block B",
    "map_url": "https://maps.google.com/?q=17.4935,78.3916",
    "latitude": 17.4935,
    "longitude": 78.3916
  }
}
```

---

## 5. Real-Time Customer Support WebSocket

### Goal
Enable two-way live customer support messaging between the user and support agents/bots over WebSockets (`wss://`).

### WebSocket Endpoint: `wss://api1.krtech.online/ws/support/{user_id}`
**Handshake Parameters**:
- Query Param: `?token=<jwt_access_token>` or `?ticket=<stream_ticket>`
- Header: `X-App-Key: ONFOOD_SECURE_CLIENT_APP_KEY_2026`

### Message Payloads (JSON)

#### 1. Client ➔ Server (User Sends Message)
```json
{
  "type": "chat_message",
  "ticket_id": "optional-ticket-uuid",
  "message": "My order #42 is taking longer than expected. Can you check?"
}
```

#### 2. Server ➔ Client (Agent / Bot Replies)
```json
{
  "type": "chat_message",
  "message_id": "msg-8891",
  "ticket_id": "ticket-uuid",
  "sender_type": "AGENT",
  "sender_name": "Ramesh (Canteen Manager)",
  "message": "Hello! Your egg puff is in the oven, ready in 2 minutes!",
  "timestamp": "2026-10-03T03:35:00Z"
}
```

#### 3. Server ➔ Client (Ticket Status Changed)
```json
{
  "type": "status_update",
  "ticket_id": "ticket-uuid",
  "status": "RESOLVED"
}
```

### FastAPI WebSocket Handler Implementation
```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
import json
from datetime import datetime

ws_router = APIRouter(tags=["Support WebSocket"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)

    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(json.dumps(message))

manager = ConnectionManager()

@ws_router.websocket("/ws/support/{user_id}")
async def support_websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    token: Optional[str] = Query(None)
):
    # Verify auth token and X-App-Key
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)

            # Persist message to database
            # Forward to Admin Support Dashboard / Auto-reply
            reply = {
                "type": "chat_message",
                "sender_type": "BOT",
                "sender_name": "Buvva Assistant",
                "message": "Thanks for messaging! A canteen support agent has received your query.",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            await manager.send_personal_message(reply, user_id)
    except WebSocketDisconnect:
        manager.disconnect(user_id)
```

---

## 6. Loyalty Points & Coupon Redemption APIs

The Android app includes a "Redeem Coupon" section in Settings linking to points redemption. Verify the following endpoints are operational:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/rewards/summary` | Returns points balance (`rewardPointsBalance`) and lifetime earned. |
| `GET` | `/api/rewards/catalog` | Returns active coupons available for redemption with `pointsCost`. |
| `POST` | `/api/rewards/claim/{coupon_id}` | Deducts points and generates a usable `couponCode`. |
| `GET` | `/api/rewards/my-coupons` | Lists all claimed coupons for the authenticated user. |
| `POST` | `/api/coupons/apply` | Applies a coupon code to the current cart and returns the discount amount. |

---

## Verification Checklist for Server Developer
- [ ] Run SQL migrations for `users.avatar`, `colleges` & `canteens` geo/photo columns.
- [ ] Add `POST /api/cart/calculate-bill` endpoint returning dynamic `breakdown` array.
- [ ] Ensure `PATCH /api/auth/profile` accepts and returns `avatar: "male" | "female" | "default"`.
- [ ] Ensure `GET /api/orders/{id}` returns both `college` and `canteen` objects with `photo_url` and `map_url`.
- [ ] Deploy `/ws/support/{user_id}` WebSocket router on FastAPI server.
