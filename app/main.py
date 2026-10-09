import os
import asyncio
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from decimal import Decimal
import json
from fastapi import FastAPI, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.database import AsyncSessionLocal
from app.exceptions import register_exception_handlers, make_spring_error_response
from app.models import User, MenuItem, Category, KitchenSettings, FaqCategory, FaqItem, TimeSlot, VendorAccount, College, Canteen, Banner, college_canteens
from app.security import (
    hash_password,
    require_app_client,
    get_client_ip,
    is_static_media_path,
    verify_static_media_request,
)
from app.routers import menu, orders, auth, cart, kitchen, help as help_router, promotions, locations, rewards
from app.config import settings as app_config

# ─── NEW: Import middleware components ────────────────────────
from app.middleware.context import install_context_logging
from app.middleware.tracker import server_behavior_tracker, request_logger, response_logger, behavior_logger
from app.middleware.metrics import mount_metrics_endpoint
from app.middleware.resources import resource_monitor


# ─── Initialize middleware ────────────────────────────────────
# Inject request context (req_id, client_ip) into all Python log records
install_context_logging()
# Configure resource tracking from settings
resource_monitor.configure(enable_resource_tracking=app_config.ENABLE_RESOURCE_TRACKING)


@asynccontextmanager
async def lifespan(app: FastAPI):
    startup_data = {
        "event": "server_start",
        "service": "onfood-backend",
        "version": "2.0.0",
    }
    request_logger.info(json.dumps(startup_data))
    response_logger.info(json.dumps(startup_data))
    try:
        await seed_database()
    except Exception as e:
        print(f"[Seed Warning] {e} — Run Alembic migrations first.")
        
    # Start Postgres Event Bridge
    from app.pubsub import event_bridge
    from app.sse import sse_manager
    from app.websocket import ws_manager

    async def handle_incoming_event(event_data):
        if event_data.get("event") == "order_status_updated":
            data = event_data.get("data")
            user_id = data.get("userId")
            if user_id:
                await sse_manager.broadcast_to_user(user_id, "order-status", data)
                await ws_manager.broadcast_to_user(user_id, data)

                # High-Priority FCM Push for Mobile Devices
                try:
                    from app.services.fcm import send_order_status_push_async
                    order_token = str(data.get("token") or data.get("orderToken") or data.get("pickupNumber") or "")
                    async with AsyncSessionLocal() as session:
                        await send_order_status_push_async(
                            db=session,
                            user_id=user_id,
                            order_id=str(data.get("id") or data.get("orderId")),
                            order_token=order_token,
                            status=str(data.get("status")),
                            estimated_ready_at=data.get("estimatedReadyAt"),
                            items_details=data.get("itemsSummary") or data.get("itemsDetails")
                        )
                except Exception as fcm_err:
                    print(f"[FCM Error] Push dispatch failed: {fcm_err}")
        elif event_data.get("event") == "support_message_created":
            data = event_data.get("data", {})
            user_id = data.get("userId")
            if user_id:
                from app.websocket import support_ws_manager
                await support_ws_manager.broadcast_to_user(user_id, data)

    await event_bridge.start(handle_incoming_event)
    
    yield
    
    await event_bridge.stop()


app = FastAPI(
    title="OnFood Backend Server",
    description="Complete Python FastAPI backend for OnFood Android food ordering app.",
    version="2.0.0",
    lifespan=lifespan,
    dependencies=[Depends(require_app_client)],
    docs_url="/docs" if app_config.ENABLE_DOCS else None,
    redoc_url="/redoc" if app_config.ENABLE_DOCS else None,
    openapi_url="/openapi.json" if app_config.ENABLE_DOCS else None,
)

app.add_middleware(
    CORSMiddleware,
    # Use explicit origins from config in production.
    # When origins remain ["*"] (dev default), credentials must be disabled
    # because browsers reject wildcard + credentials per the CORS spec.
    allow_origins=app_config.CORS_ALLOWED_ORIGINS,
    allow_credentials=app_config.CORS_ALLOWED_ORIGINS != ["*"],
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Request-Id", app_config.APP_CLIENT_KEY_HEADER],
)
app.add_middleware(GZipMiddleware, minimum_size=500)

# ─── Server Behavior Tracking Middleware (replaces old dev_request_logger) ────
@app.middleware("http")
async def _behavior_tracker(request: Request, call_next):
    """
    Wraps every HTTP request with comprehensive behavior tracking:
    request correlation IDs, resource monitoring, Prometheus metrics,
    structured JSON logging, and pretty console output.

    Static media auth guard is preserved from the old middleware.
    """
    path = request.url.path

    # Preserve static media authorization guard from old middleware
    if request.method != "OPTIONS" and is_static_media_path(path) and not verify_static_media_request(request):
        response = make_spring_error_response(
            status_code=401,
            error_name="Unauthorized",
            message="Missing or invalid app client key. Access is restricted to the official app.",
        )
        return response

    return await server_behavior_tracker(request, call_next)

# Mount Prometheus /metrics endpoint (controlled by ENABLE_METRICS config)
mount_metrics_endpoint(app, enable_metrics=app_config.ENABLE_METRICS)


# ─── Register Routers ───────────────────────────
app.include_router(auth.router)
app.include_router(menu.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(kitchen.router)
app.include_router(help_router.router)
app.include_router(promotions.router)
app.include_router(locations.router)
app.include_router(rewards.router)
app.mount("/icons", StaticFiles(directory="app/static/icons"), name="icons")
app.mount("/images", StaticFiles(directory="app/static/images"), name="images")
app.mount("/sounds", StaticFiles(directory="app/static/sounds"), name="sounds")

register_exception_handlers(app)


@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "UP", "version": "2.0.0", "message": "OnFood backend running"}


@app.get("/api/monitoring/live", tags=["Monitoring"])
async def monitoring_live_stats():
    """
    Real-time snapshot of server behavior and active connections:
    - Active WebSocket connections and connected users
    - Active SSE streams
    - Recently active authenticated HTTP users
    - In-flight requests and system resource snapshots
    """
    from datetime import datetime, timezone
    from app.websocket import ws_manager
    from app.sse import sse_manager
    from app.middleware.active_users import active_user_tracker
    from app.middleware.resources import resource_monitor

    snapshot = resource_monitor.snapshot()
    ws_stats = ws_manager.get_stats()
    sse_stats = sse_manager.get_stats()
    http_active = active_user_tracker.get_active_users(window_seconds=900)  # last 15m

    return {
        "status": "UP",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "in_flight_requests": snapshot.in_flight_requests,
        "memory_rss_mb": snapshot.memory_rss_mb,
        "cpu_percent": snapshot.cpu_percent,
        "websockets": ws_stats,
        "sse": sse_stats,
        "http_active_users": http_active,
        "http_active_count": len(http_active),
    }


from fastapi import WebSocket, WebSocketDisconnect
from app.websocket import ws_manager, support_ws_manager
import jwt as _pyjwt

@app.websocket("/ws/orders/{userId}")
async def websocket_orders_endpoint(websocket: WebSocket, userId: str):
    """
    Authenticated real-time order status stream over WebSocket.

    Auth: Pass JWT in the `Authorization` header or as the `token` query param.
    The token subject (sub) must match the userId path parameter.
    Unauthenticated or mismatched connections are closed with code 4001.
    """
    from app.security import _decode_token, UnauthenticatedException

    # 1. Extract raw token — WebSocket clients can't always set headers, so we
    #    also accept ?token=<jwt> as a fallback (same pattern as SSE).
    raw_token: str | None = None
    auth_header = websocket.headers.get("authorization", "")
    if auth_header.lower().startswith("bearer "):
        raw_token = auth_header[7:].strip()
    if not raw_token:
        raw_token = websocket.query_params.get("token")

    if not raw_token:
        await websocket.close(code=4001, reason="Authentication required")
        return

    # 2. Validate JWT and enforce userId ownership.
    try:
        payload = _decode_token(raw_token)
        token_user_id = str(payload.get("sub", ""))
    except UnauthenticatedException as exc:
        await websocket.close(code=4001, reason=exc.message)
        return

    if token_user_id != userId:
        await websocket.close(code=4003, reason="User ID does not match token")
        return

    # 3. Auth passed — accept and maintain connection.
    client_ip = get_client_ip(websocket)
    ws_started = __import__('time').perf_counter()
    behavior_logger.info(json.dumps({
        "event": "ws_connect",
        "path": "/ws/orders/{userId}",
        "user_id": userId,
        "client_ip": client_ip,
    }, ensure_ascii=False))
    user_agent = websocket.headers.get("user-agent", "")
    await ws_manager.connect(userId, websocket, client_ip=client_ip, user_agent=user_agent)
    disconnect_reason = "client_closed"
    try:
        while True:
            # Keep connection alive; client messages are not processed.
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(userId, websocket)
    except Exception:
        disconnect_reason = "error"
        ws_manager.disconnect(userId, websocket)
    finally:
        duration_s = round(__import__('time').perf_counter() - ws_started, 2)
        behavior_logger.info(json.dumps({
            "event": "ws_disconnect",
            "path": "/ws/orders/{userId}",
            "user_id": userId,
            "client_ip": client_ip,
            "duration_seconds": duration_s,
            "reason": disconnect_reason,
        }, ensure_ascii=False))


@app.websocket("/ws/support/{userId}")
async def websocket_support_endpoint(websocket: WebSocket, userId: str):
    """
    Real-time two-way Customer Support WebSocket.
    Allows students to chat live with customer support desk / AI assistant.
    Auth: Pass JWT via Authorization header or ?token=<jwt> or ?ticket=<ticket>.
    """
    from app.security import _decode_token, UnauthenticatedException
    from app.database import AsyncSessionLocal
    from app.models import SupportTicket, SupportMessage, TicketStatus, User
    from app.services.support_service import support_client
    from sqlalchemy.future import select
    import uuid

    # 1. Enforce App Client Key if configured
    app_key = websocket.headers.get("x-app-key") or websocket.query_params.get("app_key")
    if app_config.APP_CLIENT_KEY and app_key != app_config.APP_CLIENT_KEY:
        await websocket.close(code=4001, reason="Invalid app client key")
        return

    # 2. Extract token/ticket
    raw_token: str | None = None
    auth_header = websocket.headers.get("authorization", "")
    if auth_header.lower().startswith("bearer "):
        raw_token = auth_header[7:].strip()
    if not raw_token:
        raw_token = websocket.query_params.get("token") or websocket.query_params.get("ticket")

    authenticated_user_id = userId
    if raw_token and raw_token != "guest":
        try:
            payload = _decode_token(raw_token)
            token_user_id = str(payload.get("sub", ""))
            if userId != "guest" and token_user_id != userId:
                await websocket.close(code=4003, reason="User ID does not match token")
                return
            authenticated_user_id = token_user_id
        except UnauthenticatedException:
            pass  # Fallback to guest or continue if ticket was opaque

    client_ip = get_client_ip(websocket)
    user_agent = websocket.headers.get("user-agent", "")
    from app.websocket import support_ws_manager
    await support_ws_manager.connect(userId, websocket, client_ip=client_ip, user_agent=user_agent)

    try:
        while True:
            raw_data = await websocket.receive_text()
            try:
                msg_json = json.loads(raw_data)
            except Exception:
                continue

            msg_type = msg_json.get("type", "chat_message")
            if msg_type == "chat_message":
                user_msg = (msg_json.get("message") or "").strip()
                if not user_msg:
                    continue

                ticket_id_str = msg_json.get("ticket_id") or msg_json.get("ticketId")
                order_id_str = msg_json.get("order_id") or msg_json.get("orderId")
                ticket_uuid = None
                is_reopened = False

                # Persist ticket & message to PostgreSQL
                try:
                    async with AsyncSessionLocal() as db:
                        ticket = None
                        if ticket_id_str:
                            try:
                                ticket = (await db.execute(
                                    select(SupportTicket).where(SupportTicket.id == uuid.UUID(ticket_id_str))
                                )).scalars().first()
                            except Exception:
                                ticket = None

                        # If user references an order, continue old ticket for that order
                        if not ticket and order_id_str and authenticated_user_id != "guest":
                            try:
                                ticket = (await db.execute(
                                    select(SupportTicket)
                                    .where(SupportTicket.user_id == authenticated_user_id, SupportTicket.order_id == uuid.UUID(order_id_str))
                                    .order_by(SupportTicket.created_at.desc())
                                )).scalars().first()
                            except Exception:
                                ticket = None

                        if not ticket and authenticated_user_id != "guest":
                            ticket = (await db.execute(
                                select(SupportTicket)
                                .where(SupportTicket.user_id == authenticated_user_id, SupportTicket.status == TicketStatus.OPEN)
                                .order_by(SupportTicket.created_at.desc())
                            )).scalars().first()

                        if ticket and ticket.status in (TicketStatus.RESOLVED, TicketStatus.CLOSED):
                            is_reopened = True
                            ticket.status = TicketStatus.OPEN

                        if not ticket:
                            order_uuid = None
                            if order_id_str:
                                try:
                                    order_uuid = uuid.UUID(order_id_str)
                                except Exception:
                                    pass
                            ticket = SupportTicket(
                                user_id=authenticated_user_id,
                                subject="Customer Support Inquiry",
                                message=user_msg,
                                order_id=order_uuid,
                                status=TicketStatus.OPEN,
                            )
                            db.add(ticket)
                            await db.flush()

                        ticket_uuid = ticket.id
                        ticket.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

                        # Customer Message
                        customer_msg = SupportMessage(
                            ticket_id=ticket.id,
                            sender_type="USER",
                            sender_id=authenticated_user_id,
                            sender_name="Customer",
                            message=user_msg,
                            channel="APP",
                        )
                        db.add(customer_msg)

                        # Bot Auto-Reply Message
                        if is_reopened:
                            bot_text = "We've reopened your support request for this order. What seems to be the problem? Our support team will respond in a minute."
                        else:
                            bot_text = "Thanks for messaging! What is the problem with your order? Our support team will respond in a minute."

                        bot_msg = SupportMessage(
                            ticket_id=ticket.id,
                            sender_type="BOT",
                            sender_id="buvva-assistant",
                            sender_name="Buvva Assistant",
                            message=bot_text,
                            channel="APP",
                        )
                        db.add(bot_msg)
                        await db.commit()
                except Exception as db_err:
                    print(f"[Support WS DB Error] {db_err}")

                # Send Bot Response back over WebSocket
                reply = {
                    "type": "chat_message",
                    "messageId": str(uuid.uuid4()),
                    "ticketId": str(ticket_uuid) if ticket_uuid else ticket_id_str,
                    "senderType": "BOT",
                    "senderName": "Buvva Assistant",
                    "message": "Thanks for messaging! A canteen support agent has received your query.",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                await websocket.send_text(json.dumps(reply))

                # Forward to Support Desk asynchronously in background
                if authenticated_user_id != "guest":
                    async def _bg_forward(uid: str, msg: str):
                        try:
                            async with AsyncSessionLocal() as db:
                                user = (await db.execute(select(User).where(User.id == uid))).scalars().first()
                                phone = user.phone if user and user.phone else ""
                            if phone:
                                await support_client.send_customer_message(phone=phone, message=msg, channel="APP")
                        except Exception:
                            pass
                    asyncio.create_task(_bg_forward(authenticated_user_id, user_msg))

    except WebSocketDisconnect:
        support_ws_manager.disconnect(userId, websocket)
    except Exception:
        support_ws_manager.disconnect(userId, websocket)


# ─── Seeder ────────────────────────────────────

async def seed_database():
    import hashlib
    async with AsyncSessionLocal() as db:

        college_to_canteens = {
            "Scient Institute of Technology": ["Main Canteen", "Demo Canteen"],
        }
        vendor_specs = [
            ("scient.vendor@onfood.com", "Scient Main Canteen Vendor", "Main Canteen", b"Scient@2026"),
            ("scient_main@onfood.local", "Scient Main Canteen Vendor", "Main Canteen", b"vendor_password"),
            ("demo.vendor@onfood.com", "Demo Canteen Vendor", "Demo Canteen", b"Demo@2026"),
            ("demo_canteen@onfood.local", "Demo Canteen Vendor", "Demo Canteen", b"vendor_password"),
        ]
        category_specs = [
            ("Biryani", "/icons/biryani.png", 1),
            ("South Indian", "/icons/south-indian.png", 2),
            ("Curries", "/icons/curries.png", 3),
            ("Breads", "/icons/breads.png", 4),
            ("Chinese", "/icons/chinese.png", 5),
            ("Snacks", "/icons/snacks.png", 6),
            ("Beverages", "/icons/beverages.png", 7),
            ("Desserts", "/icons/desserts.png", 8),
            ("Starters", "/icons/starters.png", 9),
            ("Tandoori", "/icons/tandoori.png", 10),
        ]
        menu_specs = {
            "Main Canteen": [
                {"name": "Chicken Biryani", "price": "160", "original_price": "190", "discount_percent": "15.79", "category": "Biryani", "image_url": "/images/chicken-biryani.png", "prep": 15, "stock": 50, "special": True},
                {"name": "Veg Dum Biryani", "price": "120", "category": "Biryani", "image_url": "/images/Veg%20Dum%20Biryani.png", "prep": 12, "stock": 40},
                {"name": "Masala Dosa", "price": "60", "category": "South Indian", "image_url": "/images/masala-dosa.png", "prep": 8, "stock": 50},
                {"name": "Tea", "price": "15", "category": "Beverages", "image_url": "/images/tea.png", "prep": 2, "stock": 100},
                {"name": "Samosa", "price": "20", "category": "Snacks", "image_url": "/images/Samosa.png", "prep": 3, "stock": 60},
            ],
            "Demo Canteen": [
                {"name": "Veg Fried Rice", "price": "90", "category": "Chinese", "image_url": "/images/veg-fried-rice.png", "prep": 10, "stock": 30},
                {"name": "Paneer Butter Masala", "price": "160", "category": "Curries", "image_url": "/images/paneer-butter-masala.png", "prep": 15, "stock": 25},
                {"name": "Butter Naan", "price": "40", "category": "Breads", "image_url": "/images/butter-naan.png", "prep": 5, "stock": 50},
                {"name": "Cold Coffee", "price": "50", "category": "Beverages", "image_url": "/images/coffee.png", "prep": 4, "stock": 30},
            ],
        }
        banner_specs = [
            ("Scient Institute of Technology", "Scient Canteen Welcome Deals", "/images/banner1.png"),
        ]

        existing_colleges = {row.name: row for row in (await db.execute(select(College))).scalars().all()}
        existing_canteens = {row.name: row for row in (await db.execute(select(Canteen))).scalars().all()}
        colleges = {}
        canteens = {}

        for college_name in college_to_canteens:
            colleges[college_name] = existing_colleges.get(college_name) or College(name=college_name)
            if colleges[college_name].id is None:
                db.add(colleges[college_name])

        for canteen_name in {name for names in college_to_canteens.values() for name in names}:
            canteens[canteen_name] = existing_canteens.get(canteen_name) or Canteen(name=canteen_name)
            if canteens[canteen_name].id is None:
                db.add(canteens[canteen_name])

        await db.flush()

        for college_name, canteen_names in college_to_canteens.items():
            for canteen_name in canteen_names:
                await db.execute(
                    pg_insert(college_canteens).values(
                        college_id=colleges[college_name].id,
                        canteen_id=canteens[canteen_name].id,
                    ).on_conflict_do_nothing()
                )

        for email, name, canteen_name, raw_pwd in vendor_specs:
            account = (await db.execute(select(VendorAccount).where(VendorAccount.email == email))).scalar_one_or_none()
            pwd_hash = hash_password(hashlib.sha256(raw_pwd).hexdigest())
            if not account:
                db.add(
                    VendorAccount(
                        name=name,
                        email=email,
                        role="admin",
                        canteen_id=canteens[canteen_name].id,
                        hashed_password=pwd_hash,
                    )
                )
            else:
                account.name = name
                account.canteen_id = canteens[canteen_name].id
                account.hashed_password = pwd_hash

        # ── Kitchen Settings ──
        ks_result = await db.execute(select(KitchenSettings).where(KitchenSettings.id == 1))
        if not ks_result.scalars().first():
            db.add(KitchenSettings(id=1, base_prep_buffer_minutes=3,
                                   max_concurrent_orders=20, is_accepting_orders=True))

        # ── Categories ──
        cat_result = await db.execute(select(Category))
        existing_categories = cat_result.scalars().all()
        categories_map = {c.name: c for c in existing_categories}

        for name, icon_url, display_order in category_specs:
            category = categories_map.get(name)
            if not category:
                category = Category(name=name, icon_url=icon_url, display_order=display_order)
                db.add(category)
                categories_map[name] = category
            else:
                category.icon_url = icon_url
                category.display_order = display_order
        await db.flush()

        # ── Menu Items ──
        existing_menu_items = (await db.execute(select(MenuItem))).scalars().all()
        menu_items_by_key = {}
        for menu_item in existing_menu_items:
            menu_items_by_key.setdefault((menu_item.canteen_id, menu_item.name), []).append(menu_item)

        for canteen_name, items in menu_specs.items():
            canteen_id = canteens[canteen_name].id
            for item in items:
                key = (canteen_id, item["name"])
                matches = menu_items_by_key.get(key, [])
                if matches:
                    target = matches[0]
                    target.price = Decimal(item["price"])
                    target.original_price = Decimal(item["original_price"]) if item.get("original_price") else None
                    target.discount_percent = Decimal(item["discount_percent"]) if item.get("discount_percent") else None
                    target.category_id = categories_map[item["category"]].id
                    target.image_url = item["image_url"]
                    target.description = f"{item['name']} from {canteen_name}"
                    target.stock = item["stock"]
                    target.is_student_visible = True
                    target.special_offer = item.get("special", False)
                    target.is_available = True
                    target.preparation_time_minutes = item["prep"]
                else:
                    db.add(
                        MenuItem(
                            name=item["name"],
                            price=Decimal(item["price"]),
                            original_price=Decimal(item["original_price"]) if item.get("original_price") else None,
                            discount_percent=Decimal(item["discount_percent"]) if item.get("discount_percent") else None,
                            category_id=categories_map[item["category"]].id,
                            canteen_id=canteen_id,
                            image_url=item["image_url"],
                            description=f"{item['name']} from {canteen_name}",
                            stock=item["stock"],
                            is_student_visible=True,
                            special_offer=item.get("special", False),
                            is_available=True,
                            preparation_time_minutes=item["prep"],
                        )
                    )

        for display_order, (college_name, title, image_url) in enumerate(banner_specs, start=1):
            existing_banner = (await db.execute(select(Banner).where(Banner.title == title))).scalar_one_or_none()
            if not existing_banner:
                db.add(Banner(
                    title=title,
                    image_url=image_url,
                    college_id=colleges[college_name].id,
                    is_active=True,
                    display_order=display_order,
                ))

        # ── FAQ ──
        faq_result = await db.execute(select(FaqCategory))
        if not faq_result.scalars().all():
            faq_cat_orders = FaqCategory(title="Ordering", icon="🛒", display_order=1)
            faq_cat_pickup = FaqCategory(title="Pickup", icon="📦", display_order=2)
            faq_cat_payment = FaqCategory(title="Payment", icon="💳", display_order=3)
            db.add_all([faq_cat_orders, faq_cat_pickup, faq_cat_payment])
            await db.flush()

            db.add_all([
                FaqItem(category_id=faq_cat_orders.id, question="How do I place an order?",
                        answer="Browse the menu, add items to your cart, then tap 'Place Order'. You'll get a pickup number instantly."),
                FaqItem(category_id=faq_cat_orders.id, question="Can I modify my order after placing it?",
                        answer="Orders cannot be modified once placed. Please contact support via the Help section."),
                FaqItem(category_id=faq_cat_pickup.id, question="How do I pick up my order?",
                        answer="When your order is ready, you'll get a notification. Show your pickup number (#XX) at the counter."),
                FaqItem(category_id=faq_cat_pickup.id, question="How long does preparation take?",
                        answer="Estimated wait time is shown when you place your order. It depends on items ordered and kitchen queue."),
                FaqItem(category_id=faq_cat_payment.id, question="What payment methods are accepted?",
                        answer="We currently accept cash at pickup. Online payments coming soon!"),
            ])

        # ── Time Slots ──
        slots_result = await db.execute(select(TimeSlot))
        existing_slots = slots_result.scalars().all()
        if not existing_slots:
            import datetime
            slots_to_add = []
            
            # Generate continuous 30-minute time slots (08:00 to 21:30) for each canteen
            for canteen_obj in canteens.values():
                curr = datetime.datetime.combine(datetime.date.today(), datetime.time(8, 0))
                limit = datetime.datetime.combine(datetime.date.today(), datetime.time(21, 30))
                while curr < limit:
                    nxt = curr + datetime.timedelta(minutes=30)
                    slots_to_add.append(TimeSlot(
                        canteen_id=canteen_obj.id,
                        label=None,
                        start_time=curr.time(),
                        end_time=nxt.time(),
                        max_orders=5,
                        is_active=True
                    ))
                    curr = nxt
            
            db.add_all(slots_to_add)

        await db.commit()

