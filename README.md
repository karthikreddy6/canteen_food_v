# OnFood Backend Server (Python FastAPI Migration)

This project is a high-performance, asynchronous Python backend API for the **OnFood** Android application, migrated from Java Spring Boot 3. 

It replicates the exact database schemas, validation rules, HTTP status codes, camelCase request/response layouts, and JWT security requirements of the original backend, ensuring drop-in compatibility with the existing Android frontend.

---

## Technical Stack
* **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Asynchronous python web framework)
* **Database & ORM:** PostgreSQL with [SQLAlchemy 2.0 Async Session](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html) and `asyncpg`
* **Migrations:** [Alembic](https://alembic.otasa.org/)
* **Security & Auth:** PyJWT (stateless Firebase-style JWT authorization validation)
* **Real-time Server Push:** `sse-starlette` (Server-Sent Events)
* **In-Memory Caching:** `aiocache` (analogous to Spring Boot's `@Cacheable`)

---

## Project Structure

```
onfoodserver/
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuration loading using pydantic-settings
│   ├── database.py        # SQLAlchemy Async Database session and setup
│   ├── exceptions.py      # Custom exceptions and Spring-style JSON error responses
│   ├── models.py          # SQLAlchemy Models (User, MenuItem, Order, OrderItem)
│   ├── schemas.py         # Pydantic schemas (camelCase request/response validation)
│   ├── security.py        # JWT extraction & signature/issuer validation dependency
│   ├── sse.py             # Server-Sent Events stream connection manager
│   ├── cache.py           # Configured RAM caching using aiocache
│   ├── main.py            # FastAPI Entrypoint, lifespan events, seeding, CORS
│   └── routers/
│       ├── __init__.py
│       ├── menu.py        # CRefactored cached menu retrieval endpoints
│       └── orders.py      # Transactional order creation, status, and SSE stream endpoints
├── migrations/            # Alembic migrations scripts folder
├── alembic.ini            # Alembic configuration
├── .env                   # Local settings configurations
├── requirements.txt       # Python project dependencies
└── README.md              # Project documentation
```

---

## Getting Started

### 1. Prerequisites
Ensure you have **Python 3.11+** and **PostgreSQL** installed.

### 2. Environment Settings
Create a `.env` file in the root directory (one has been pre-created for local development):
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/onfood
JWT_SECRET=super_secret_key_for_development_purposes
JWT_ISSUER=onfood
```

### 3. Setup Virtual Environment and Install Dependencies
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install cryptography
```

### 4. Run Database Migrations
Alembic has been fully configured for async database operations. Run the following commands to initialize and update your database:

```bash
# Generate the initial migration script based on models.py definitions
alembic revision --autogenerate -m "Initial schema definition"

# Run migrations to update PostgreSQL
alembic upgrade head
```

---

## Running the Application
Start the FastAPI server locally:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Once running, you can access the Interactive API docs (Swagger UI) at:
* **Interactive Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Alternative ReDoc Docs:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## API Endpoints List

### 🍔 Menu Endpoints (Public Access)
* **`GET /api/menu`**
  * Returns all menu items. Results are cached in memory (ttl 5 minutes).
* **`GET /api/menu/specials`**
  * Returns menu items with `specialOffer` set to `true`. Results are cached in memory.

### 📦 Order Endpoints (JWT Bearer Token required)
* **`POST /api/orders`**
  * Places a new order. The business logic performs validation and inserts in a single transaction block. 
  * Aborts transaction and returns `400 Bad Request` if the calculated sum of database prices does not match the client's `totalAmount`.
* **`GET /api/orders/{orderId}`**
  * Retrieves details of a specific order. Returns `404 Not Found` if missing.
* **`PATCH /api/orders/{orderId}/status`**
  * Updates an order's status and broadcasts a real-time order update event to the user's SSE stream.
* **`GET /api/orders/stream/{userId}`**
  * Establishes a persistent Server-Sent Events (SSE) connection. Sends a `{"connected": "ok"}` event initially, and broadcasts changes dynamically as `"order-status"` events.

### Cart and Coupon Flow
* Cart storage sends only `menuItemId` and `quantity`; prices and totals are calculated by the server.
* **`POST /api/coupons/apply`** accepts `couponCode` plus cart item IDs and quantities and returns current item prices, subtotal, discount, and final preview total.
* Coupon preview does not create an order or consume coupon usage.
* Cart checkout/display is separate from `POST /api/orders`.

---

## Error Handling Format (Spring Boot style)
In the event of an error (e.g. 404 Not Found, 400 Bad Request, 401 Unauthorized), the response payload matches Spring Boot's error format:
```json
{
  "timestamp": "2026-07-08T13:22:43",
  "status": 404,
  "error": "Not Found",
  "message": "User not found: karthik_uid"
}
```
