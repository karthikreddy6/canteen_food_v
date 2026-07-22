import logging
import logging.handlers
import os
import time
import uuid
from contextlib import asynccontextmanager
from decimal import Decimal
import json
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.database import AsyncSessionLocal
from app.exceptions import register_exception_handlers
from app.models import User, MenuItem, Category, KitchenSettings, FaqCategory, FaqItem, TimeSlot, VendorAccount, College, Canteen, Banner, Campus, college_canteens
from app.security import hash_password, require_app_client
from app.routers import menu, orders, auth, cart, kitchen, help as help_router, vendor, vendor_auth, promotions, locations
from app.config import settings as app_config


# ─── Logging setup ────────────────────────────────────────────
# Write logs to a dedicated subdirectory with automatic rotation.
_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(_LOG_DIR, exist_ok=True)

request_logger = logging.getLogger("onfood.request")
response_logger = logging.getLogger("onfood.response")

# Redact these key names wherever they appear in logged request/response bodies
# or query parameters so tokens and credentials never reach log files.
_SENSITIVE_KEYS = {"password", "otp", "token", "access_token", "authorization", "hashed_password"}
# Query parameter names whose values should be redacted (e.g. ?token=<JWT> for SSE clients)
_SENSITIVE_QUERY_PARAMS = {"token", "access_token"}

for _logger, _filename in ((request_logger, "request.log"), (response_logger, "response.log")):
    if not _logger.handlers:
        _handler = logging.handlers.RotatingFileHandler(
            os.path.join(_LOG_DIR, _filename),
            maxBytes=10_000_000,   # 10 MB per file
            backupCount=5,
            encoding="utf-8",
        )
        _handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        _logger.addHandler(_handler)
    _logger.setLevel(logging.INFO)
    _logger.propagate = False

# Exception logger (unhandled 500s) also goes to logs/
_exc_handler = logging.handlers.RotatingFileHandler(
    os.path.join(_LOG_DIR, "errors.log"),
    maxBytes=10_000_000,
    backupCount=5,
    encoding="utf-8",
)
_exc_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logging.getLogger("onfood.exceptions").addHandler(_exc_handler)


def _safe_log_data(value):
    """Return JSON-safe request/response data without credentials or OTPs."""
    if isinstance(value, dict):
        return {
            key: "[REDACTED]" if key.lower() in _SENSITIVE_KEYS else _safe_log_data(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_safe_log_data(item) for item in value]
    return value


def _json_body(raw_body: bytes):
    if not raw_body:
        return None
    try:
        return _safe_log_data(json.loads(raw_body))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return "[non-json body]"


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

    await event_bridge.start(handle_incoming_event)
    
    yield
    
    await event_bridge.stop()


app = FastAPI(
    title="OnFood Backend Server",
    description="Complete Python FastAPI backend for OnFood Android food ordering app.",
    version="2.0.0",
    lifespan=lifespan,
    dependencies=[Depends(require_app_client)]
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



# ─── Dev middleware helpers ──────────────────────
_SKIP_LOG_PREFIXES = ("/icons/", "/images/", "/sounds/", "/favicon")

# ANSI colors for terminal
_C = {
    "reset": "\033[0m",
    "bold":  "\033[1m",
    "green": "\033[92m",
    "yellow":"\033[93m",
    "red":   "\033[91m",
    "cyan":  "\033[96m",
    "grey":  "\033[90m",
    "blue":  "\033[94m",
    "magenta": "\033[95m",
}

def _status_color(status: int) -> str:
    if status < 300:
        return _C["green"]
    if status < 400:
        return _C["yellow"]
    return _C["red"]

def _method_color(method: str) -> str:
    return {
        "GET":    _C["cyan"],
        "POST":   _C["green"],
        "PATCH":  _C["yellow"],
        "PUT":    _C["yellow"],
        "DELETE": _C["red"],
    }.get(method, _C["reset"])


@app.middleware("http")
async def dev_request_logger(request: Request, call_next):
    # Assign a short request ID for tracing
    req_id = str(uuid.uuid4())[:8]
    request.state.request_id = req_id

    started = time.perf_counter()

    # Read body for logging (must be done before call_next)
    request_body = await request.body()

    # Skip verbose logging for static files and health check
    path = request.url.path
    skip = any(path.startswith(p) for p in _SKIP_LOG_PREFIXES) or path == "/"

    # ── Incoming request (dev console) ──
    if not skip:
        body_preview = ""
        if request_body:
            try:
                parsed = _safe_log_data(json.loads(request_body))
                body_preview = json.dumps(parsed, ensure_ascii=False)
                if len(body_preview) > 300:
                    body_preview = body_preview[:300] + "…"
                body_preview = f"\n    {_C['grey']}Body: {body_preview}{_C['reset']}"
            except Exception:
                pass

        # Scrub sensitive values from query params before logging
        safe_qs = {
            k: ("[REDACTED]" if k.lower() in _SENSITIVE_QUERY_PARAMS else v)
            for k, v in request.query_params.items()
        }
        qs_str = ("?" + "&".join(f"{k}={v}" for k, v in safe_qs.items())) if safe_qs else ""
        print(
            f"  {_C['grey']}>> [{req_id}]{_C['reset']} "
            f"{_method_color(request.method)}{_C['bold']}{request.method}{_C['reset']} "
            f"{_C['blue']}{path}{qs_str}{_C['reset']}"
            f"{body_preview}"
        )

    # ── Call actual endpoint ──
    response = await call_next(request)

    duration_ms = round((time.perf_counter() - started) * 1000, 2)

    # Capture response body for JSON logging if available without consuming stream
    response_body = getattr(response, "body", None)

    # Attach request-id to response so Android can trace it
    response.headers["X-Request-Id"] = req_id

    # ── Security headers ─────────────────────────────────────────────────────
    # Emitted on every response regardless of environment.
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    # HSTS only makes sense when serving over HTTPS (i.e. production behind ngrok/Nginx)
    if app_config.ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    # ── Outgoing response (dev console) ──
    if not skip:
        sc = response.status_code
        slow_warn = f" {_C['yellow']}SLOW{_C['reset']}" if duration_ms > 500 else ""
        resp_preview = ""
        if response_body:
            try:
                parsed = _safe_log_data(json.loads(response_body))
                resp_preview = json.dumps(parsed, ensure_ascii=False)
                if len(resp_preview) > 300:
                    resp_preview = resp_preview[:300] + "…"
                resp_preview = f"\n    {_C['grey']}Body: {resp_preview}{_C['reset']}"
            except Exception:
                pass

        print(
            f"  {_C['grey']}<< [{req_id}]{_C['reset']} "
            f"{_status_color(sc)}{_C['bold']}{sc}{_C['reset']} "
            f"{_C['grey']}{duration_ms}ms{_C['reset']}"
            f"{slow_warn}"
            f"{resp_preview}"
        )

    # ── File logger ──────────────────────────────────────────────────────────
    # In production, suppress full request/response bodies to avoid logging
    # sensitive order data, user details, etc. Log only routing metadata.
    is_production = app_config.ENVIRONMENT == "production"

    # Scrub query params for the file log too (SSE ?token= must not appear)
    safe_query = {
        k: ("[REDACTED]" if k.lower() in _SENSITIVE_QUERY_PARAMS else v)
        for k, v in request.query_params.items()
    }
    request_logger.info(json.dumps({
        "req_id": req_id,
        "event": "http_request",
        "method": request.method,
        "path": path,
        "query": safe_query,
        "request_json": None if is_production else _json_body(request_body),
    }, ensure_ascii=False, default=str))
    response_data = _json_body(response_body) if response_body is not None else None
    response_logger.info(json.dumps({
        "req_id": req_id,
        "event": "http_response",
        "method": request.method,
        "path": path,
        "status": response.status_code,
        "duration_ms": duration_ms,
        "response_json": None if is_production else response_data,
    }, ensure_ascii=False, default=str))

    return response

# ─── Register Routers ───────────────────────────
app.include_router(auth.router)
app.include_router(menu.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(kitchen.router)
app.include_router(help_router.router)
# Vendor endpoints temporarily disabled.
# Re-enable these two routers when vendor access is needed again.
# app.include_router(vendor_auth.router)
# app.include_router(vendor.router)
app.include_router(promotions.router)
app.include_router(locations.router)
app.mount("/icons", StaticFiles(directory="app/static/icons"), name="icons")
app.mount("/images", StaticFiles(directory="app/static/images"), name="images")
app.mount("/sounds", StaticFiles(directory="app/static/sounds"), name="sounds")

register_exception_handlers(app)


@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "UP", "version": "2.0.0", "message": "OnFood backend running"}


from fastapi import WebSocket, WebSocketDisconnect
from app.websocket import ws_manager
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
    await ws_manager.connect(userId, websocket)
    try:
        while True:
            # Keep connection alive; client messages are not processed.
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(userId, websocket)
    except Exception:
        ws_manager.disconnect(userId, websocket)


# ─── Seeder ────────────────────────────────────

async def seed_database():
    async with AsyncSessionLocal() as db:

        college_to_canteens = {
            "Engineering College": ["Central Canteen", "Hostel Canteen"],
            "Business College": ["MBA Canteen", "Food Court Express"],
            "Arts College": ["Arts Canteen"],
            "Science College": ["Science Canteen"],
        }
        vendor_specs = [
            ("central@onfood.local", "Central Canteen Vendor", "Central Canteen"),
            ("hostel@onfood.local", "Hostel Canteen Vendor", "Hostel Canteen"),
            ("mba@onfood.local", "MBA Canteen Vendor", "MBA Canteen"),
            ("express@onfood.local", "Food Court Express Vendor", "Food Court Express"),
            ("arts@onfood.local", "Arts Canteen Vendor", "Arts Canteen"),
            ("science@onfood.local", "Science Canteen Vendor", "Science Canteen"),
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
            "Central Canteen": [
                {"name": "Chicken Biryani", "price": "160", "original_price": "190", "discount_percent": "15.79", "category": "Biryani", "image_url": "/images/chicken-biryani.png", "prep": 18, "stock": 40, "special": True},
                {"name": "Veg Dum Biryani", "price": "130", "category": "Biryani", "image_url": "/images/Veg%20Dum%20Biryani.png", "prep": 15, "stock": 35},
                {"name": "Butter Chicken", "price": "180", "category": "Curries", "image_url": "/images/butter-chicken.png", "prep": 16, "stock": 25},
                {"name": "Garlic Naan", "price": "45", "category": "Breads", "image_url": "/images/garlic-naan.png", "prep": 6, "stock": 60},
            ],
            "Hostel Canteen": [
                {"name": "Idli", "price": "40", "category": "South Indian", "image_url": "/images/idli.png", "prep": 5, "stock": 60},
                {"name": "Masala Dosa", "price": "65", "category": "South Indian", "image_url": "/images/masala-dosa.png", "prep": 8, "stock": 40},
                {"name": "Pongal", "price": "55", "category": "South Indian", "image_url": "/images/pongal.png", "prep": 7, "stock": 35},
                {"name": "Tea", "price": "15", "category": "Beverages", "image_url": "/images/tea.png", "prep": 2, "stock": 100},
            ],
            "MBA Canteen": [
                {"name": "Paneer Tikka", "price": "155", "category": "Starters", "image_url": "/images/paneer-tikka.png", "prep": 14, "stock": 20},
                {"name": "Paneer Butter Masala", "price": "170", "category": "Curries", "image_url": "/images/paneer-butter-masala.png", "prep": 16, "stock": 18},
                {"name": "Butter Naan", "price": "40", "category": "Breads", "image_url": "/images/butter-naan.png", "prep": 5, "stock": 50},
                {"name": "Sweet Lassi", "price": "50", "category": "Beverages", "image_url": "/images/sweet-lassi.png", "prep": 3, "stock": 30},
            ],
            "Food Court Express": [
                {"name": "Veg Fried Rice", "price": "95", "category": "Chinese", "image_url": "/images/veg-fried-rice.png", "prep": 10, "stock": 30},
                {"name": "Chicken Noodles", "price": "120", "category": "Chinese", "image_url": "/images/chicken-noodles.png", "prep": 11, "stock": 25},
                {"name": "French Fries", "price": "70", "category": "Snacks", "image_url": "/images/french-fries.png", "prep": 6, "stock": 40},
                {"name": "Fresh Lime Soda", "price": "35", "category": "Beverages", "image_url": "/images/fresh-lime-soda.png", "prep": 3, "stock": 45},
            ],
            "Arts Canteen": [
                {"name": "Veg Puff", "price": "25", "category": "Snacks", "image_url": "/images/Veg%20Puff.png", "prep": 3, "stock": 50},
                {"name": "Samosa", "price": "20", "category": "Snacks", "image_url": "/images/Samosa.png", "prep": 3, "stock": 60},
                {"name": "Chocolate Brownie", "price": "80", "category": "Desserts", "image_url": "/images/chocolate-brownie.png", "prep": 4, "stock": 18, "special": True},
                {"name": "Cold Coffee", "price": "60", "category": "Beverages", "image_url": "/images/coffee.png", "prep": 4, "stock": 24},
            ],
            "Science Canteen": [
                {"name": "Egg Fried Rice", "price": "110", "category": "Chinese", "image_url": "/images/egg-fried-rice.png", "prep": 11, "stock": 28},
                {"name": "Gobi Manchurian", "price": "100", "category": "Starters", "image_url": "/images/gobi-manchurian.png", "prep": 9, "stock": 25},
                {"name": "Chilli Chicken", "price": "145", "category": "Starters", "image_url": "/images/chilli-chicken.png", "prep": 12, "stock": 22, "special": True},
                {"name": "Buttermilk", "price": "25", "category": "Beverages", "image_url": "/images/buttermilk.png", "prep": 2, "stock": 50},
            ],
        }
        banner_specs = [
            ("Engineering College", "Engineering Combo Week", "/images/banner1.png"),
            ("Business College", "Business Lunch Deals", "/images/banner2.png"),
            ("Arts College", "Arts Snack Festival", "/images/banner3.png"),
            ("Science College", "Science Fuel Specials", "/images/banner1.png"),
        ]

        campus = (await db.execute(select(Campus).where(Campus.name == "Main Campus"))).scalar_one_or_none()
        if not campus:
            campus = Campus(name="Main Campus")
            db.add(campus)
            await db.flush()

        existing_colleges = {row.name: row for row in (await db.execute(select(College))).scalars().all()}
        existing_canteens = {row.name: row for row in (await db.execute(select(Canteen))).scalars().all()}
        colleges = {}
        canteens = {}

        for college_name in college_to_canteens:
            colleges[college_name] = existing_colleges.get(college_name) or College(name=college_name, campus_id=campus.id)
            if colleges[college_name].id is None:
                db.add(colleges[college_name])
            else:
                colleges[college_name].campus_id = campus.id

        for canteen_name in {name for names in college_to_canteens.values() for name in names}:
            canteens[canteen_name] = existing_canteens.get(canteen_name) or Canteen(name=canteen_name, campus_id=campus.id)
            if canteens[canteen_name].id is None:
                db.add(canteens[canteen_name])
            else:
                canteens[canteen_name].campus_id = campus.id

        await db.flush()

        for college_name, canteen_names in college_to_canteens.items():
            for canteen_name in canteen_names:
                await db.execute(
                    pg_insert(college_canteens).values(
                        college_id=colleges[college_name].id,
                        canteen_id=canteens[canteen_name].id,
                    ).on_conflict_do_nothing()
                )

        for email, name, canteen_name in vendor_specs:
            account = (await db.execute(select(VendorAccount).where(VendorAccount.email == email))).scalar_one_or_none()
            if not account:
                db.add(
                    VendorAccount(
                        name=name,
                        email=email,
                        role="admin",
                        canteen_id=canteens[canteen_name].id,
                        hashed_password=hash_password("vendor_password"),
                    )
                )
            else:
                account.name = name
                account.canteen_id = canteens[canteen_name].id

        # ── Kitchen Settings ──
        ks_result = await db.execute(select(KitchenSettings).where(KitchenSettings.id == 1))
        if not ks_result.scalars().first():
            db.add(KitchenSettings(id=1, base_prep_buffer_minutes=3,
                                   max_concurrent_orders=20, is_accepting_orders=True))

        # ── Default User ──
        user_result = await db.execute(select(User).where(User.email == "karthik@example.com"))
        if not user_result.scalars().first():
            db.add(User(
                name="Karthik",
                email="karthik@example.com",
                phone="9876543210",
                phone_verified=True,
                campus_id=campus.id,
                college="Engineering College",
                college_id=colleges["Engineering College"].id,
                preferred_canteen_id=canteens["Central Canteen"].id,
                hashed_password=hash_password("karthik_password")
            ))

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
                    campus_id=campus.id,
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
            
            # Custom Time Slots per Canteen
            central_id = canteens["Central Canteen"].id if "Central Canteen" in canteens else None
            hostel_id = canteens["Hostel Canteen"].id if "Hostel Canteen" in canteens else None
            mba_id = canteens["MBA Canteen"].id if "MBA Canteen" in canteens else None
            express_id = canteens["Food Court Express"].id if "Food Court Express" in canteens else None
            arts_id = canteens["Arts Canteen"].id if "Arts Canteen" in canteens else None
            science_id = canteens["Science Canteen"].id if "Science Canteen" in canteens else None

            custom_canteen_slots = [
                # Central Canteen Custom Slots
                (central_id, "Breakfast", datetime.time(8, 0), datetime.time(10, 30), 20),
                (central_id, "Lunch", datetime.time(12, 0), datetime.time(15, 0), 50),
                (central_id, "Evening Snacks", datetime.time(16, 0), datetime.time(18, 30), 30),
                (central_id, "Dinner", datetime.time(19, 30), datetime.time(21, 30), 40),

                # Hostel Canteen Custom Slots
                (hostel_id, "Morning Tiffin", datetime.time(7, 30), datetime.time(10, 0), 25),
                (hostel_id, "Lunch Break", datetime.time(12, 30), datetime.time(14, 30), 45),
                (hostel_id, "Tea & Snacks", datetime.time(16, 30), datetime.time(18, 0), 25),
                (hostel_id, "Night Mess", datetime.time(20, 0), datetime.time(22, 0), 50),

                # MBA Canteen Custom Slots
                (mba_id, "Morning Coffee & Breakfast", datetime.time(8, 30), datetime.time(11, 0), 15),
                (mba_id, "Executive Lunch", datetime.time(12, 0), datetime.time(14, 30), 30),
                (mba_id, "Evening Refreshments", datetime.time(15, 30), datetime.time(18, 0), 20),

                # Food Court Express Custom Slots
                (express_id, "All-Day Fast Track", datetime.time(9, 0), datetime.time(21, 0), 100),

                # Arts Canteen Custom Slots
                (arts_id, "Morning Special", datetime.time(8, 30), datetime.time(11, 0), 20),
                (arts_id, "Afternoon Thali", datetime.time(12, 0), datetime.time(15, 0), 35),
                (arts_id, "Chai & Chat", datetime.time(16, 0), datetime.time(19, 0), 30),

                # Science Canteen Custom Slots
                (science_id, "Lab Quick Snack", datetime.time(9, 0), datetime.time(11, 30), 25),
                (science_id, "Science Lunch Hour", datetime.time(12, 30), datetime.time(14, 30), 40),
                (science_id, "Evening Energy Refill", datetime.time(16, 0), datetime.time(18, 30), 25),
            ]

            for cid, label, start, end, max_ord in custom_canteen_slots:
                if cid:
                    slots_to_add.append(TimeSlot(
                        canteen_id=cid,
                        label=label,
                        start_time=start,
                        end_time=end,
                        max_orders=max_ord,
                        is_active=True
                    ))
            
            db.add_all(slots_to_add)

        # ── Default Vendor Account ──
        vendor_result = await db.execute(select(VendorAccount).where(VendorAccount.email == "vendor@onfood.local"))
        legacy_vendor = vendor_result.scalars().first()
        if not legacy_vendor:
            db.add(VendorAccount(
                name="OnFood Vendor",
                email="vendor@onfood.local",
                role="admin",
                canteen_id=canteens["Central Canteen"].id,
                hashed_password=hash_password("vendor_password")
            ))
        else:
            if legacy_vendor.canteen_id is None:
                legacy_vendor.canteen_id = canteens["Central Canteen"].id

        await db.commit()

