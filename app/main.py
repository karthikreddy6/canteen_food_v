from contextlib import asynccontextmanager
from decimal import Decimal
import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.future import select

from app.database import AsyncSessionLocal
from app.exceptions import register_exception_handlers
from app.models import User, MenuItem, Category, KitchenSettings, FaqCategory, FaqItem, TimeSlot
from app.security import hash_password
from app.routers import menu, orders, auth, cart, kitchen, help as help_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await seed_database()
    except Exception as e:
        print(f"[Seed Warning] {e} — Run Alembic migrations first.")
    yield


app = FastAPI(
    title="OnFood Backend Server",
    description="Complete Python FastAPI backend for OnFood Android food ordering app.",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Register Routers ───────────────────────────
app.include_router(auth.router)
app.include_router(menu.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(kitchen.router)
app.include_router(help_router.router)
app.mount("/icons", StaticFiles(directory="app/static/icons"), name="icons")
app.mount("/images", StaticFiles(directory="app/static/images"), name="images")
app.mount("/sounds", StaticFiles(directory="app/static/sounds"), name="sounds")

register_exception_handlers(app)


@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "UP", "version": "2.0.0", "message": "OnFood backend running"}


# ─── Seeder ────────────────────────────────────

async def seed_database():
    async with AsyncSessionLocal() as db:

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
                hashed_password=hash_password("karthik_password")
            ))

        # ── Categories ──
        cat_result = await db.execute(select(Category))
        existing_categories = cat_result.scalars().all()
        categories_map = {c.name: c for c in existing_categories}

        if not existing_categories:
            categories_map = {
                "Pizza": Category(name="Pizza", icon_url="/icons/pizza.png", display_order=1),
                "Burgers": Category(name="Burgers", icon_url="/icons/burger.png", display_order=2),
                "Drinks": Category(name="Drinks", icon_url="/icons/drink.png", display_order=3),
                "Desserts": Category(name="Desserts", icon_url="/icons/dessert.png", display_order=4),
            }
            for cat in categories_map.values():
                db.add(cat)
            await db.flush()  # Ensure IDs are assigned

        # ── Menu Items ──
        menu_result = await db.execute(select(MenuItem))
        if not menu_result.scalars().all():
            db.add_all([
                MenuItem(
                    name="Margherita Pizza",
                    price=Decimal("12.99"),
                    original_price=Decimal("15.99"),
                    discount_percent=Decimal("18.76"),
                    category_id=categories_map["Pizza"].id,
                    image_url="/images/pizza.png",
                    special_offer=True,
                    is_available=True,
                    preparation_time_minutes=15
                ),
                MenuItem(
                    name="Pepperoni Feast Pizza",
                    price=Decimal("15.99"),
                    category_id=categories_map["Pizza"].id,
                    image_url="/images/pepperoni.png",
                    special_offer=False,
                    is_available=True,
                    preparation_time_minutes=18
                ),
                MenuItem(
                    name="Double Cheeseburger",
                    price=Decimal("8.50"),
                    category_id=categories_map["Burgers"].id,
                    image_url="/images/burger.png",
                    special_offer=False,
                    is_available=True,
                    preparation_time_minutes=10
                ),
                MenuItem(
                    name="Crispy Chicken Burger",
                    price=Decimal("9.99"),
                    original_price=Decimal("11.99"),
                    discount_percent=Decimal("16.68"),
                    category_id=categories_map["Burgers"].id,
                    image_url="/images/chicken_burger.png",
                    special_offer=True,
                    is_available=True,
                    preparation_time_minutes=12
                ),
                MenuItem(
                    name="Coca-Cola",
                    price=Decimal("2.50"),
                    category_id=categories_map["Drinks"].id,
                    image_url="/images/cola.png",
                    special_offer=False,
                    is_available=True,
                    preparation_time_minutes=1
                ),
                MenuItem(
                    name="Chocolate Lava Cake",
                    price=Decimal("5.99"),
                    category_id=categories_map["Desserts"].id,
                    image_url="/images/lava_cake.png",
                    special_offer=True,
                    is_available=True,
                    preparation_time_minutes=8
                ),
            ])

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
        if not slots_result.scalars().all():
            import datetime
            # Seed 30-minute intervals from 09:00 to 21:00 (i.e. last slot is 20:30 - 21:00)
            start_hour = 9
            end_hour = 21
            slots_to_add = []
            current_time = datetime.datetime.combine(datetime.date.today(), datetime.time(start_hour, 0))
            end_time_limit = datetime.datetime.combine(datetime.date.today(), datetime.time(end_hour, 0))
            
            while current_time < end_time_limit:
                next_time = current_time + datetime.timedelta(minutes=30)
                slots_to_add.append(TimeSlot(
                    start_time=current_time.time(),
                    end_time=next_time.time(),
                    max_orders=5,
                    is_active=True
                ))
                current_time = next_time
            
            db.add_all(slots_to_add)

        await db.commit()
